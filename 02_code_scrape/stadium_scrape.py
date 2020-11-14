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
######################################
# Scrape the table for main stadiums #
######################################

#Set up page & soup
url = "https://en.wikipedia.org/wiki/Chronology_of_home_stadiums_for_current_National_Football_League_teams"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html")

# %%
###################################################
# Mess with HTML before parsing into pandas table #
###################################################

#Replace line breaks in html with \n for parsing later
for e in soup.find_all("br"):
    e.replace_with("\n")

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
#Grab the links for each cell in the table and parse it into the text

# For every cell in the table
for cell in soup.find_all("td"):

    #Find the attribute with href and text
    atty = cell.find_all("a", text = True, href=True)
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
##################
# Stadium tables #
##################

# Parse the clean soup into pandas, create 3 separate tables

main_stadiums = pd.read_html(str(soup))[0]
int_stadiums = pd.read_html(str(soup))[1]
temp_stadiums = pd.read_html(str(soup))[2]


# %%
#################################
# Fix main stadium column names #
#################################

main_stadiums.columns = ["Team","Stadium","Years used","Capacity","Opened","Surface","Location"]

# %%

# Split the Stadium column into a separate URL column
for i in [main_stadiums, int_stadiums, temp_stadiums]:

    # If the Stadium column has "url:" in it
    try:
        i["URL"] = i.Stadium.str.split("url:",expand=True)[1]
        i["URL"] = i.URL.str.split(" ",expand=True)[0]
        i["Stadium"] = i.Stadium.str.split("url:",expand=True)[0]

    # If not then just pass (mainly for main_stadiums)
    except KeyError:
        pass
#%%
#Still a little bit to fix for main_stadiums
main_stadiums.URL = main_stadiums.URL.str.split(" ",expand=True)[0]

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
                    coord = soup.find_all('span',{'class': 'geo'})[0].get_text()
                    lat = coord.split("; ")[0]
                    lon = coord.split("; ")[1]

                except IndexError:
                    print("No scrapeable info")
                    lat = None
                    lon = None
        # Append the scraped coordinates
                scraped_data.append([lat,lon,url])


        # Put the system to sleep for a random draw of tim
                time.sleep(random.uniform(0,sleep))

        #Build a pandas table from the scraped content
    dat =  pd.DataFrame(scraped_data,columns=["lat","lon","URL"])
    return dat
                #except:
                #    print("No scrapeable info")
# %%
#############################
# Get the coordinate tables #
#############################



int_stadiums_coord = coord_table(urls = int_stadiums.URL.to_list(),sleep = 5)
temp_stadiums_coord = coord_table(urls = temp_stadiums.URL.to_list(),sleep = 5)
main_stadiums_coord = coord_table(urls= main_stadiums.URL.to_list(),sleep = 5)

len(main_stadiums)

main_stadiums_coord
# %%

###########################
# Save all outputs as csv #
###########################

main_stadiums.to_csv("../03_data_scrape/main_stadiums_raw.csv", index=False,encoding='utf-8-sig')
int_stadiums.to_csv("../03_data_scrape/int_stadiums_raw.csv", index=False,encoding='utf-8-sig')
temp_stadiums.to_csv("../03_data_scrape/temp_stadiums_raw.csv", index=False,encoding='utf-8-sig')

main_stadiums_coord.to_csv("../03_data_scrape/main_stadiums_coord_raw.csv", index=False,encoding='utf-8-sig')
int_stadiums_coord.to_csv("../03_data_scrape/int_stadiums_coord_raw.csv", index=False,encoding='utf-8-sig')
temp_stadiums_coord.to_csv("../03_data_scrape/temp_stadiums_coord_raw.csv", index=False,encoding='utf-8-sig')
