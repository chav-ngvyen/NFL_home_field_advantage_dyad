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
###############################################################
# Create a list of links of Wiki playoff pages to scrape from #
###############################################################

four_digits = list(range(1992,2020))
four_digits = [str(x) for x in four_digits]

len(two_digits)
two_digits = list(range(93,100)) + list(range(00,21))
two_digits = [str(x) for x in two_digits]
two_digits = [str(0) + str(x) if len(str(x)) == 1 else str(x) for x in two_digits]


# %%
links = []
for i in range(len(two_digits)):
    link = "https://en.wikipedia.org/wiki/" + four_digits[i] + "-" + two_digits[i] +"_NFL_playoffs"
    links.append(link)
links
# %%


url = "https://en.wikipedia.org/wiki/1992%E2%80%9393_NFL_playoffs"
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')


for header in soup.select('h2:contains("Schedule")'):
    schedule_table = header.find_next_siblings()

schedule = pd.read_html(str(schedule_table))[0]


get

soup.select('h2')[7].get_text()
div.toccolours:nth-child(27) > div:nth-child(1) > ul:nth-child(4) > li:nth-child(3) > b:nth-child(1)
html.client-js.ve-available body.mediawiki.ltr.sitedir-ltr.mw-hide-empty-elt.ns-0.ns-subject.mw-editable.page-1992–93_NFL_playoffs.rootpage-1992–93_NFL_playoffs.skin-vector.action-view.skin-vector-legacy div#content.mw-body div#bodyContent.mw-body-content div#mw-content-text.mw-content-ltr div.mw-parser-output div.toccolours div ul li b


soup.select('li:contains("ttendance")')
attendance = soup.select('li:contains("ttendance")')

game_attendance = []
for i in attendance:
    att = i.text
    game_attendance.append(att)

game_attendance

game = pd.Series(game_attendance).to_frame(name="attendance")
game

test = test.to_frame(name="attendance")
test


# Get rid of the multi-index
schedule.columns = schedule.columns.droplevel(1)
# Lowercase
schedule = schedule.rename(columns=lambda x: x.lower())
# Drop rows where home team = away team (meaning that the rows just have playoff/ conference champ/ superbowl across all cells)
schedule = schedule.loc[schedule["away team"] != schedule["home team"]].reset_index(drop=True)

schedule_test = schedule.merge(test, left_index = True, right_index=True)

schedule_test


# %%
# Put scraped coordinates into table format
def playoff_attendance(urls = None, sleep = 10):
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

                #################################
                # First, get the table schedule #
                #################################

                # Schedule table is the table that's immediately next to h2 "Schedule"
            for header in soup.select('h2:contains("Schedule")'):
                schedule_table = header.find_next_siblings()
                schedule_df = pd.read_html(str(schedule_table))[0]

                # Clean it
                    # Get rid of the multi-index
                schedule_df.columns = schedule_df.columns.droplevel(1)
                    # Lowercase
                schedule_df = schedule_df.rename(columns=lambda x: x.lower())
                    # Drop rows where home team = away team (meaning that the rows just have playoff/ conference champ/ superbowl across all cells)
                schedule_df = schedule_df.loc[schedule_df["away team"] != schedule_df["home team"]].reset_index(drop=True)

                ##########################################################
                # Next, get attendance data from other parts of the page #
                ##########################################################
                #print(datetime.now().strftime("%H:%M:%S"),":", urls.index(url),":",url)

            game_attendance = []

            attendance = soup.select('li:contains("ttendance")')
            for i in attendance:
                att = i.text
                game_attendance.append(att)

                # Put that into its own frame
            attendance_df = pd.Series(game_attendance).to_frame(name="attendance")

                ##################
                # Merge the 2 df #
                ##################
            schedule = schedule_df.merge(attendance_df, left_index = True, right_index=True)

                #Append scraped data
        scraped_data.append(schedule)

            # Concat them together
    concat_data = pd.concat(scraped_data)
    concat_data = concat_data.reset_index(drop=True)
    return concat_data

# %%

links_test = links[0:4]
links_test

# %%
playoff_attendance_table = playoff_attendance(urls = links, sleep = 10)

len(playoff_attendance_table)
playoff_attendance_table.to_csv("../03_data_scrape/playoff_attendance.csv", index=False,encoding='utf-8-sig')
