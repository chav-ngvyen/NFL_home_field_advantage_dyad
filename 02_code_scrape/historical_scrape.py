
import pandas as pd
import requests # For downloading the website
from bs4 import BeautifulSoup # For parsing the website
import time # To put the system to sleep
import random # for random numbers
import numpy as np
from sqlalchemy import create_engine
import sqlite3
from datetime import datetime

# %%
#Define table scraper function
def table_scraper(url=None):

    """ Scrape attendance tables from pro-football-reference.com/years/****/attendance.htm
    Args:
        url (None): the input url where the table is to scrape from.
            set to None now so I can input a list into it later
    Returns:
        dataframe with the table, add a column for season
    """
    # Download the webpage
    page = requests.get(url)

    # If a connection was reached
    if page.status_code == 200:
        #Parse the html content
        soup = BeautifulSoup(page.content,'html.parser')
        #Get the season from the HTML data
        season = soup.select("div h1 span")[0].get_text()
        table = pd.read_html(page.text)
        season_table = table[0]
        season_table["Season"] = season
        return season_table


# %%
# Define link_scrape function to scrape tables from pro-football-reference

def link_scrape(urls= None, sleep = 10):
    """ Scrape multiple PFR URLS
    Args:
        urls (list): list of valid PFR URLs
        sleep (int): Integer value specifying how long the machine should be
                    put to sleep (random uniform). Defaults to 10.

    Returns:
        Concatinated dataframe of all the scraped tables
    """
    scraped_data = []
    for url in urls:
        #Keep track of where we are by printing the current time, the index of the url in the url list, and the url itself
        print(datetime.now().strftime("%H:%M:%S"),":", urls.index(url),":",url)

        #print(url) #Keep track of where we are

        # Scrape the content
        scraped_data.append(table_scraper(url))

        # Put the system to sleep for a random draw of time
        time.sleep(random.uniform(0,sleep))


    #Concatinate the returned dataframes from bit_scraper together
    concat_data = pd.concat(scraped_data)
    return concat_data


# %%
#################################
# Create sets of links to scrape#
#################################

links_attendance_historical = set()
links_games_historical = set()

#Update links for tables from 1992 to 2019:
for i in range(28):
    year = 1992 + i
    # Attendance links
    links_attendance_historical.update(["https://www.pro-football-reference.com/years/" + str(year) + "/attendance.htm"])
    # Game schedule
    links_games_historical.update(["https://www.pro-football-reference.com/years/" + str(year) + "/games.htm"])

# %%
############################
# Scrape attendance data ###
############################

# Attendance data
attendance_historical = link_scrape(urls=list(links_attendance_historical))

# Save the data to csv
attendance_historical.to_csv("../03_data_scrape/attendance_historical_raw.csv", index=False)

# %%
############################
# Scrape game data #########
############################

# Game data
games_historical = link_scrape(urls=list(links_games_historical))


# Save the data to csv
games_historical.to_csv("../03_data_scrape/games_historical_raw.csv", index=False)
