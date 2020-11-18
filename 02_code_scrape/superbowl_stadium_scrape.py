from bs4 import BeautifulSoup
import requests
import codecs
import os
import pandas as pd
from datetime import datetime
import time # To put the system to sleep
import random # for random numbers
import numpy as np

# %%
# The scraping method is very similar to stadium_scrape.py

# %%
###########################################
# Scrape the table for superbowl stadiums #
###########################################

#Set up page & soup
url = "https://en.wikipedia.org/wiki/Super_Bowl"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html")

# %%
#Remove the in-cell references (citations in square brackets)
for ref in soup.find_all("sup"):
    ref.extract()

# %%
# Define function to check if a string has any numbers in it

def hasNumbers(inputString):
    '''
    This function checks if a string has any number in it
    Args: string
    Returns: Boolean
    '''
    return any(char.isdigit() for char in inputString)


# %%
# For every cell in the table
for cell in soup.find_all("td"):

    #Find the attribute with href and title
    #(in stadium_scrape.py it's text=True)
    atty = cell.find_all("a", title = True, href=True)
    #If something was found
    if atty != None:

        #If the length of that attribute is longer than 0 (None type has length 0)
        if len(atty)>0  :

            #Get the text
            text = cell.a.text

            # If the text doesn't have numbers in it (to avoid complicating the Years used column)
            if hasNumbers(text)==False:
                #Get the href
                href = cell.a.get("href")

                #Make it a link with an identifier "url:" before so it's easy to split
                link = " url:https://en.wikipedia.org"+href

                #Append that link to the attribute of the cell
                cell.a.append(link)

    # If cell doesn't have the "a" tag then pass
    else:
        pass
# %%

# I need the html from this table
superbowl_stadiums = pd.read_html(str(soup))[5]


# %%
# Split the Stadium column into a separate URL column
for i in [superbowl_stadiums]:

    # If the Stadium column has "url:" in it
    try:
        i["URL"] = i.Stadium.str.split("url:",expand=True)[1]
        i["URL"] = i.URL.str.split(" ",expand=True)[0]
        i["Stadium"] = i.Stadium.str.split("url:",expand=True)[0]

    # If not then just pass (mainly for main_stadiums)
    except KeyError:
        pass

#%%

#From Years get a list of relevant years to reshape
relevant_years = []
for row in superbowl_stadiums["Years hosted"]:
    # Split the string list of years into separate years
    row = row.split(", ")
    # Convert each year to int
    row = [int(year) for year in row]
    # Keep years after 1992
    row = [i for i in row if i >= 1992]

    relevant_years.append(row)
superbowl_stadiums["Years_relevant"] = relevant_years
#%%
# If Years_relevant is an empty list, then change to none
for i in range(0, len(superbowl_stadiums)):
    if (len(superbowl_stadiums["Years_relevant"][i]) == 0):
        superbowl_stadiums["Years_relevant"][i] = None

#%%
# Drop where Years_relevant is NA
superbowl_stadiums = superbowl_stadiums.dropna().reset_index(drop=True)



# %%
#########################################
# Build scraper for stadium coordinates #
#########################################

# Put scraped coordinates into table format
def coord_table(urls = None, sleep = 10):
    scraped_data = []

    for url in urls:
        if url != None:
            # Download the webpage
            page = requests.get(url)

            # If a connection was reached
            if page.status_code == 200:
                #Parse the html content
                soup = BeautifulSoup(page.content,'html.parser')

                #Keep track of where we are by printing the current time, the index of the url in the url list, and the url itself
                print(datetime.now().strftime("%H:%M:%S"),":", urls.index(url),":",url)

                #If the URL has scrapeable data
                try:
                    #Scrape the content

                    #Delete citation in square brackets [ ]
                    for ref in soup.find_all("sup"):
                        ref.extract()

                    #Replace line break "br" with "; ""
                    for e in soup.find_all("br"):
                        e.replace_with("; ")

                    name = soup.find("h1").get_text()
                    capacity = soup.select_one('tr:contains("Capacity")').get_text()
                    surface = soup.select_one('tr:contains("Surface")').get_text()
                    coord = soup.find_all('span',{'class': 'geo'})[0].get_text()
                    lat = coord.split("; ")[0]
                    lon = coord.split("; ")[1]

                except IndexError:
                    print("No scrapeable info")
                    name = None
                    capacity = None
                    surface = None
                    lat = None
                    lon = None
        # Append the scraped coordinates
                scraped_data.append([name,lat,lon,url,surface, capacity])


        # Put the system to sleep for a random draw of tim
                time.sleep(random.uniform(0,sleep))

        #Build a pandas table from the scraped content
    dat =  pd.DataFrame(scraped_data,columns=["name","lat","lon","URL","surface","capacity"])
    return dat

# %%# %%
#############################
# Get the coordinate tables #
#############################
superbowl_stadiums_coord = coord_table(urls= superbowl_stadiums.URL.to_list(),sleep = 5)


superbowl_stadiums_coord


# %%
######################
# Export both to csv #
######################

superbowl_stadiums.to_csv("../03_data_scrape/superbowl_stadiums_raw.csv", index=False,encoding='utf-8-sig')
superbowl_stadiums_coord.to_csv("../03_data_scrape/superbowl_stadiums_coord_raw.csv", index=False,encoding='utf-8-sig')
