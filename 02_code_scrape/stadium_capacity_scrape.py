#%%
from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import codecs
import os
import pandas as pd
from datetime import datetime
import time # To put the system to sleep
import random # for random numbers
import numpy as np
import re
#%%

# The stadium table from Wikipedia only has static capacity, but some of these stadiums change max capacity every few seasons. Solutions? I'm going to hard code it.

# Read in the long main_stadiums file
df = pd.read_csv("../05_data_clean/main_stadiums_long.csv")

# Get the list of URL
links = df.URL.unique()
links = list(links)

# %%
#Build a scraper
#url = 'https://en.wikipedia.org/wiki/Lambeau_Field'
#url = 'https://en.wikipedia.org/wiki/Angel_Stadium'
#url = 'https://en.wikipedia.org/wiki/Bills_Stadium'
#url = 'https://en.wikipedia.org/wiki/Oakland_Coliseum'
#url = 'https://en.wikipedia.org/wiki/Busch_Memorial_Stadium#Seating_capacity'
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')

links.where('https://en.wikipedia.org/wiki/Lambeau_Field')
dir(links)
links.ite
#%%

def scraper_capacity(urls = None, sleep = 5):
    scraped_data = []
    for url in urls:

        # Download the webpage
        page = requests.get(url)

            # If a connection was reached
        if page.status_code == 200:
                #Parse the html content
            soup = BeautifulSoup(page.content,'html.parser')

                #Keep track of where we are by printing the current time, the index of the url in the url list, and the url itself
            print(datetime.now().strftime("%H:%M:%S"),":", urls.index(url),":",url)

            ###################################
            # Look for headers with "apacity" #
            ###################################

            header2 = soup.select('h2:contains("apacity")')
            header3 = soup.select('h3:contains("apacity")')

            # Only one of the 2 above should work
            # Combine them
            header_list = header2 + header3

            # Get the first element of the list (of one element)
            try:
                h = header_list[0]
            # Index error means there are no header found with "apacity"
            except IndexError:
                print("Header not found")
                continue
            ################################################################
            # Get the html chunk after that header, before the next header #
            ################################################################

            # Empty html
            html = u""
            # Empty cap_list
            cap_list = []

            for tag in h.find_next_siblings():
                if tag.name == h.name:
                    break

                else:
                    for ref in tag.find_all("sup"):
                            ref.extract()
                    html += str(tag)

                    try:
                        cap_text = tag.find_all('caption')


                        cap_list.append(cap_text)

                    except AttributeError:
                        continue

                    #Remove the empty element
                    cap_list = [x for x in cap_list if x!= []]

                    # Check is cap_list is already is a nested list
                    if any(isinstance(i, list) for i in cap_list) is True:

                    # Flatten the list
                        flat_list = [item for sublist in cap_list for item in sublist]

                    # If the list is already a normal, non-nested list:
                    else:
                        flat_list = cap_list

            # Read the table in that chunk
            try:
                df = pd.read_html(html, attrs ={'class':'wikitable'})
            # There can still be links where there's a Capacity header, but no table
            except ValueError:
                print("Header found, no tables")
                #break
                continue

            for i in range(len(df)):
                try:
                    df[i]['Sports'] = flat_list[i].get_text(strip=True)
                except IndexError:
                    df[i]['Sports'] = 'Football'

            # Concat the dataframes in df to one long, flat df
            df_flat = pd.concat(df)
            df_flat["URL"] = url
        # Append the scraped data
        scraped_data.append(df_flat)

        # Good night
        time.sleep(random.uniform(0,sleep))

    #Concat the list
    concat_data = pd.concat(scraped_data)
    concat_data = concat_data.reset_index(drop=True)
    return concat_data
    #return scraped_data
#%%
# Run the scraper
data = scraper_capacity(urls=links,sleep =3)

data.columns

#Clean up - only need Football
data = data.loc[data.Sports == "Football"]
data = data[["Years","Capacity","URL"]]

#Drop US Bank
data.drop(data[data['URL']=='https://en.wikipedia.org/wiki/U.S._Bank_Stadium'].index, inplace = True)
#Export
data.to_csv('../03_data_scrape/stadium_capacity.csv', index=False,encoding='utf-8-sig')

# %%
###############
# 2nd scraper #
###############
# Only 24 out of the 62 links had a capacity table in the text
# Now I will get the capacity info from the infobox

# Out of those 24 links, the data for US Bank Stadium bad, so will use the next scraper for it

# Get the links where the first scraper worked
links_with_capacity = list(data.URL.unique())
# Leftover links
leftover_links = list(set(links) - set(links_with_capacity))

# Append US Bank Stadium to that
leftover_links.append('https://en.wikipedia.org/wiki/U.S._Bank_Stadium')

# %%
########################
# Scraper for infocard #
########################

def infocard_scrape(urls = None, sleep = 3):
    scraped_data = []
    for url in urls:

        # Download the webpage
        page = requests.get(url)

            # If a connection was reached
        if page.status_code == 200:
                #Parse the html content
            soup = BeautifulSoup(page.content,'html.parser')

                #Keep track of where we are by printing the current time, the index of the url in the url list, and the url itself
            print(datetime.now().strftime("%H:%M:%S"),":", urls.index(url),":",url)

            ###################################
            # Look for the info card #
            ###################################
            # Get the info card
            infobox = soup.find('table', {"class":"infobox vcard"})
            # Find the header cell for Capacity
            cap_str = infobox.find('th', string ="Capacity")
            # Next sibling is the number
            cap_sibling = cap_str.find_next_sibling()

            ############
            # Clean it #
            ############
            # Remove the reference
            for ref in cap_sibling.find_all("sup"):
                ref.extract()
            for br in cap_sibling.find_all("br"):
                br.replace_with("//")

            # Get the text
            cap_string = cap_sibling.get_text()
            # Split it
            cap_string_list = cap_string.split("//")

            #################################
            # Put the string list into a df #
            #################################
            df = pd.DataFrame(cap_string_list, columns =['original_column'])
            df['URL'] = url
            # column_split = df.original_column.str.rsplit(' ', expand = True)
            # df = pd.concat([df,column_split],axis=1,sort=False)

            #try:
            # Create Capacity & Years columns from the original
                #df['Capacity'] = df.original_column.str.split('(', expand = True)[0]
            df['Capacity'] = df.original_column.str.extract('(\d*,\w*)')
            # Check for years in yyyy-* format
            df['Years'] = df.original_column.str.extract('(\d*–\w*)',expand=True)
            # Check for single years
            df['Single_year'] = df.original_column.str.extract('(\d\d\d\d)',expand=True)
            # Fill NA
            df['Years'] = df['Years'].fillna(df['Single_year'])


            # Remove ")" from Years column
                #df.Years = df.Years.str.split(")",expand=True)[0]
            # except ValueError:
            #     df['Capacity'] = df.original_column
            #     df['Years'] = df.original_column.str.extract('(\d*–\w*)',expand=True)

        # Append the scraped data
        scraped_data.append(df)

        # Good night
        time.sleep(random.uniform(0,sleep))

    #Concat the list
    concat_data = pd.concat(scraped_data)
    concat_data = concat_data.reset_index(drop=True)
    return concat_data
# %%
# Run the scraper
data2 = infocard_scrape(urls = leftover_links)
data2.columns

# Clean it up
data2 = data2[["original_column","URL","Capacity","Years"]]

# Export to csv
data2.to_csv('../03_data_scrape/stadium_capacity_infocard.csv', index=False,encoding='utf-8-sig')
