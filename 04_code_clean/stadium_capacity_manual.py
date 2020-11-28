#%%
from bs4 import BeautifulSoup
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

# %%
#Build a scraper

url = 'https://en.wikipedia.org/wiki/Bills_Stadium'
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')
#%%

for header in soup.select('h3:contains("apacity")'):
    capacity_table = header.find_next_sibling()
    # for caption in capacity_table.find_all("caption"):
    #     if "Football" in caption.text:
    #         table = caption.find_parent('table')
    #         table = pd.read_html(str(table))
    table = capacity_table.find('table')
    print(capacity_table)


#%%
table


# %%
# Build a scraper for playoff attendance
def stadium_capacity_h2(urls = None, sleep = 10):
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
            for header in soup.select('h2:contains("apacity")'):
                capacity = header.find_next_sibling()
                for caption in capacity.find_all("caption"):
                    if "Football" in caption.text:
                        table = caption.find_parent('table')
                        table = pd.read_html(str(table))
                    elif None in caption.text:
                        table = caption.find_parent('table')
                        table = pd.read_html(str(table))
            for header in soup.select('h3:contains("apacity")'):
                capacity = header.find_next_sibling()
                for caption in capacity.find_all("caption"):
                    if "Football" in caption.text:
                        table = caption.find_parent('table')
                        table = pd.read_html(str(table))
                    elif None in caption.text:
                        table = caption.find_parent('table')
                        table = pd.read_html(str(table))
