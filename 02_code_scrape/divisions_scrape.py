import pandas as pd
import requests # For downloading the website
from bs4 import BeautifulSoup # For parsing the website
import time # To put the system to sleep
import random # for random numbers
import numpy as np
from sqlalchemy import create_engine
import sqlite3
from datetime import datetime

#%%
######################################
# Build scraper to get division data #
######################################


#Define division scraper function
def division_scraper(urls=None,sleep=10):
    """
    This function will scrape tables from https://www.pro-football-reference.com/years/****/index.htm
    It then puts teams into divisions for each season, and preserve the within-division ranking for the season
    Args:
        url (None): the input url where the table is to scrape from.
            set to None now so I can input a list into it later
    Returns:
        dataframe with the table, add a column for season
    """
    # Create empty list
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

            #Parse the html content
            soup = BeautifulSoup(page.content,'html.parser')

            #Each page should have 2 tables, 1 for AFC and 1 for NFC

            #First, get the season year
            season = soup.select("div h1 span")[0].get_text()

            #Parse the tables in
            tables = pd.read_html(page.text)
            table1 = tables[0]
            table2 = tables[1]

            #Concat the 2 tables
            table = pd.concat([table1, table2]).reset_index(drop=True)

            #Create Season column
            table["Season"] = season

            #Create division column
                ##First, create empty column
            table["Division"] = None
                ##Fill the first row in the column with the division
            table.loc[(table.W.str.contains("AFC")) | (table.W.str.contains("NFC")),"Division"] = table["W"]
                ##Use forward fill to fill the rest of the column
            table = table.ffill(axis=0).reset_index(drop=True)

            #Drop the rows where division is the same across all columns (because it's a column span for Division name)
            table = table[table.W != table.Tm]

            #Get within-division ranking for the year
                ##Use cumcount()+1 to preserve the groupby order
            div_rank = table.groupby(["Division"]).cumcount()+1
                ##Name the pd series (so can merge later)
            div_rank = div_rank.rename("Division_Rank")
                ##Merge pd series to table
            table = table.merge(div_rank, left_index=True, right_index=True)

            #Append scraped data
            scraped_data.append(table)

        # Put the system to sleep for a random draw of time (be kind)
        time.sleep(random.uniform(0,sleep))

    # Concat
    concat_data = pd.concat(scraped_data)
    concat_data = concat_data.reset_index(drop=True)
    return concat_data

# %%
#####################
# Create list of links #
#####################

season = list(range(1992,2020))
season = [str(x) for x in season]

# %%
# Create a list of PFR links to scrape from
links = []
for i in range(len(season)):
    link = "https://www.pro-football-reference.com/years/" + season[i]  +"/"
    links.append(link)
links


# %%
###################
# Run the scraper #
###################
div_table = division_scraper(urls=links, sleep=10)
# %%
# Re-order the columns
div_table.columns
div_table = div_table[['Tm', 'W', 'L','T','W-L%', 'PF', 'PA', 'PD', 'MoV', 'SoS', 'SRS', 'OSRS',
       'DSRS', 'Season', 'Division', 'Division_Rank']]

# %%
# Export
div_table.to_csv("../03_data_scrape/divisions_ranking.csv", index=False,encoding='utf-8-sig')

# %%
# Scrape the table for 1991
div_table_1991 = division_scraper(urls=['https://www.pro-football-reference.com/years/1991/index.htm'], sleep = 10)

div_table_1991
div_table_1991 = div_table_1991[['Tm', 'W', 'L','W-L%', 'PF', 'PA', 'PD', 'MoV', 'SoS', 'SRS', 'OSRS','DSRS', 'Season', 'Division', 'Division_Rank']]

#Export
div_table_1991.to_csv("../03_data_scrape/divisions_ranking_1991.csv", index=False,encoding='utf-8-sig')
