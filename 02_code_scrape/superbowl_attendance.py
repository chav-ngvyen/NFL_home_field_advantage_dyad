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
#Create a class called py_solution that converts integer to roman numerals
#Source https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-1.php

class py_solution:
    def int_to_Roman(self, num):
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
            ]
        syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
            ]
        roman_num = ''
        i = 0
        while  num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num
# %%
# Create a list of superbowl URLs to scrape attendance data from
links = []

for i in range(27,56):
    sb = py_solution().int_to_Roman(i)
    link = "https://en.wikipedia.org/wiki/Super_Bowl_" + sb
    links.append(link)

# Create empty df to merge later
d = {'URL':links, 'Season':seasons}
df = pd.DataFrame(d)

#%%

# Put scraped coordinates into table format
def sb_attendance(urls = None, sleep = 10):
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
                    attendance = soup.select_one('tr:contains("Attendance")').get_text()


                except AttributeError:
                    print("No scrapeable info")
                    attendance = None
        # Append the scraped coordinates
                scraped_data.append([url, attendance])


        # Put the system to sleep for a random draw of tim
                time.sleep(random.uniform(0,sleep))

        #Build a pandas table from the scraped content
    dat =  pd.DataFrame(scraped_data,columns=["URL", "Attendance"])
    return dat

# %%
# Scrape the data
sb_attendance = sb_attendance(urls= links,sleep = 5)

#%%
# Merge the scraped data with the empty df (so we have a season column)
sb_attendance = sb_attendance.merge(df, on="URL", how = "left")

# %%
# Clean up the Attendance column
sb_attendance.Attendance = sb_attendance.Attendance.str.split("Attendance",expand= True)[1]

# Fix for 2011
sb_attendance.loc[sb_attendance.URL == "https://en.wikipedia.org/wiki/Super_Bowl_XLV", "Attendance"] = "103,219"

# %%
#Export to csv

sb_attendance.to_csv("../05_data_clean/sb_attendance.csv", index=False,encoding='utf-8-sig')
