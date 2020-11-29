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
#url = 'https://en.wikipedia.org/wiki/Angel_Stadium'
#url = 'https://en.wikipedia.org/wiki/Bills_Stadium'
url = 'https://en.wikipedia.org/wiki/Oakland_Coliseum'
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')
#%%

for header in soup.select('h3:contains("apacity")'):
    capacity_table = header.find_next_siblings()
    #for caption in capacity_table.find_all("caption"):
    #    if "Football" in caption.text:
    #        table = caption.find_parent('table')
    #        table = pd.read_html(str(table))
    #table = capacity_table.find('table')
    #        print("Yes")
    for i in capacity_table:
        caption = i.find("caption")
        try:
            caption_text = caption.get_text()
            print(caption_text)
            if "Football" in caption_text:
                print("Ding Ding Ding")
                tab = caption.find_parent('table')
                print(tab)
        # try:
        #     if caption.get_text() == "Football":
        #         tab = caption.find_parent('table')
        #         print(tab)
        except AttributeError:
        #    tab = pd.read_html(str(capacity_table))[0]
            print("AttributeError: 'NoneType' object has no attribute 'get_text'")
#
# #%%
# for header in soup.select('h3:contains("apacity")'):
#     sib = header.find_next_sibling()
#     #print(sib)
#     sib2 = sib.find_next_sibling()
#     print(sib2)
#     caption = sib2.find("caption")
#     caption_text = caption.get_text()
#     print(sib2, caption_text)

#%%
for header in soup.select('h2:contains("apacity")'):
    # Get the immediate sibling
    sib = header.find_next_sibling()
    # Get the caption of the immediate sibling
    caption = sib.find("caption")

    # If the immediate sibling does not have a caption, it means that the stadium only serves 1 sport
    if caption == None:
        tablex = pd.read_html(str(sib))[0]
        #print(tablex)

    # If the immediate sibling HAS a caption, then more trouble
        # If the immediate caption is Football, get that table
    elif caption == "Football":
        tablex = pd.read_html(str(sib))[0]

        # If the immediate caption is not Football:

    elif caption != "Football":
        sib2 = sib.find_next_sibling()
        tablex = pd.read_html(str(sib2))[0]



for header in soup.select('h3:contains("apacity")'):
    # Get the immediate sibling
    sib = header.find_next_sibling()
    # Get the caption of the immediate sibling
    caption = sib.find("caption")

    # If the immediate sibling does not have a caption, it means that the stadium only serves 1 sport
    if caption == None:
        tablex = pd.read_html(str(sib))[0]
        #print(tablex)

    # If the immediate sibling HAS a caption, then more trouble
        # If the immediate caption is Football, get that table
    elif caption == "Football":
        tablex = pd.read_html(str(sib))[0]

        # If the immediate caption is not Football:

    elif caption != "Football":
        sib2 = sib.find_next_sibling()
        tablex = pd.read_html(str(sib2))[0]
        #print(sib2.find("caption").get_text(),tablex)
# %%
tablex

# %%
# Above code works for Oakland & Bills but not Angel
# This is for Angel

angel = None
angel_table = None
header = None
header2 = None
header3 = None
header2 = soup.select('h2:contains("apacity")')
header3 = soup.select('h3:contains("apacity")')

len(header2)
len(header3)

header_list = header2 + header3
header_list

# %%
angel = None
angel_table= None
for h in header_list:
    sib = h.find_next_siblings()
    #angel_table = pd.read_html(str(sib))[0]
    #print(angel_table)
    #angel = pd.read_html(str(sib))[0]
    #print(angel)
    for sibling in sib:
        cap = sibling.find_all("caption")
        if len(cap) == 0:
            #print("double yes")
            angel_table = pd.read_html(str(sib))[0]
            if angel_table.columns.is_numeric():
                print("Numeric index")
                angel_table = None
                break
        elif len(cap) != 0:

        #print(cap)
            for caption in cap:
                caption_text = caption.get_text()
                if "Football" not in caption_text:
                    pass
                if "Football" in caption_text:
                    print("found something")
                    angel = caption.find_parent('table')
                    angel_table = pd.read_html(str(angel))[0]
                    break
angel_table

#%%

angel_table
# %%
#pd.read_html(str(sib))[0]

#print(angel_table)

type(angel_table1)
type(angel_table0.columns)


#%%

for header in soup.select('h2:contains("apacity")'):
    # Get all siblings
    sib = header.find_next_siblings()
        #angel = pd.read_html(str(sib))[0]
    print(angel)
    for sibling in sib:
        cap = sibling.find_all("caption")
        print(cap)
        for caption in cap:
            caption_text = caption.get_text()
            if "Football" not in caption_text:
                pass
            if "Football" in caption_text:
                print("yes")
                angel = caption.find_parent('table')
                print(angel)

                #print(angel)
print(angel)

#%%
for header in soup.select('h2:contains("apacity")'):
    # Get all siblings
    sib = header.find_next_siblings()
    #angel = pd.read_html(str(sib))[0]
    print(angel)
    for sibling in sib:
        cap = sibling.find_all("caption")
        print(cap)
        for caption in cap:
            caption_text = caption.get_text()
            if "Football" in caption_text:
                print("yes")
                angel = caption.find_parent('table')
                print(angel)
            #print(angel)
print(angel)

#type(sib)
type(sib)
#sib[0]
