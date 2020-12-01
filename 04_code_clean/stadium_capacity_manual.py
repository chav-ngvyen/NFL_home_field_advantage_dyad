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

# %%
#Build a scraper
#url = 'https://en.wikipedia.org/wiki/Lambeau_Field'
#url = 'https://en.wikipedia.org/wiki/Angel_Stadium'
#url = 'https://en.wikipedia.org/wiki/Bills_Stadium'
#url = 'https://en.wikipedia.org/wiki/Oakland_Coliseum'
url = 'https://en.wikipedia.org/wiki/Busch_Memorial_Stadium#Seating_capacity'
page = requests.get(url)
soup = BeautifulSoup(page.content,'html.parser')



#%%

header2 = soup.select('h2:contains("apacity")')
header3 = soup.select('h3:contains("apacity")')

header_list = header2 + header3
h = header_list[0]
h
# %%
html = u""
cap_list = list()
flat_list = list()
df = None


for tag in h.find_next_siblings():
    if tag.name == h.name:
        break

    else:
        html += str(tag)
        #print(html)

        try:
            cap_text = tag.find_all('caption')
            #print(cap_text)
            cap_list.append(cap_text)

            #if len(cap_text.get_text(strip=True)) == 0:
            #    cap_text.extract()

        except AttributeError:
            continue
        #cap_list.append(cap_text)
        #Remove the empty element
        cap_list = [x for x in cap_list if x!= []]

        # Check is cap_list is already is a nested list
        if any(isinstance(i, list) for i in cap_list) is True:
        # Flatten the list
            #cap_list = [item for items in cap_list for item in items]
            flat_list = [item for sublist in cap_list for item in sublist]
            #print(flat_list)
        else:
            flat_list = cap_list
        #pr = tag.find_all('table',{'class':'wikitable'})

df = pd.read_html(html, attrs ={'class':'wikitable'})

for i in range(len(df)):
    try:
        df[i]['sports'] = flat_list[i].get_text(strip=True)
    except IndexError:
        df[i]['sports'] = 'Football'
df
#%%
for tag in h.find_next_siblings():
    if tag.name == h.name:
         break
    else:
        html += str(tag)
html
#%%

type(cap_list)
flat_list
any(isinstance(i, list) for i in cap_list)
cap_text
flat_list[i]
cap_list[i]
flat_list = [item for sublist in t for item in sublist]
df
#%%
len(cap)
print(html)
#%%
df
cap_list[0].get_text(strip=True)
df[0]['sports'] = cap_list[0].get_text(strip=True)
df[1]
len(df)

pd.DataFrame.from_dict(test, orient = 'index')
pd.DataFrame(test)

for i in range(len(df)):
    df[i]['Sports']= ""
    [df[i]['Sports'] = j for j in cap_list]
df[0]
pd.concat(pd.read_html(html))

#%%
for header in soup.find_all(h.name):
    thisNode = h
    nextNode = h.find_next(h.name)
    if header == thisNode:
        print(header)
# %%
for header in header_list:
    nextNode = header
    while True:
        nextNode = nextNode.nextSibling
        if nextNode.name == header.name:
            break
        try:
            tag_name = nextNode.name
        except AttributeError:
            continue
        if tag_name == "table":
            test = nextNode
        else:
            continue
        # if nextNode is None:
        #     break
        # # if isinstance(nextNode, NavigableString):
        # #     print (nextNode.strip())
        # # if isinstance(nextNode, Tag):
        #     if nextNode.name == "h3":
        #         break
        #     #table = nextNode.find('table')
        #     print (nextNode.get_text(strip=True).strip())
pd.read_html(str(test))[0]



#%%
nextNode = h
while True:
    nextNode = nextNode.Sibling
h.name
h
h.find_next(h.name)
next_table = h.find_next_siblings('table')
next_table
#captioncaption = h.find_next('caption')
len(tabletable)
tabletable
#len(captioncaption)
df = []
len = len(tabletable)/2
pd.read_html(str(next_table))
for i in range(0,1):
    tab = pd.read_html(str(tabletable))[i]
    df.append(tab)
df
#type(tabletable)

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
#%%
sib1 = None
sib1 = header_list[0].find_next_sibling()
caption1 = sib1.find("caption").get_text()
if "Baseball" in caption1:
    sib2 = sib1.find_next_sibling()
    #caption2 = sib2.find("caption").get_text()
caption1
# %%
cap = []
table = None
for h in header_list:
    siblings = h.find_next_siblings()
    for s in siblings:
        caption = s.find_all("caption")
        c_length = len(caption)
        if c_length == 0:
            break
        elif c_length != 0:
            for c in caption:
                t = c.find_parent("table")
                tab = pd.read_html(str(t))
                print(tab)
                print(type(tab[0]))
                #tab.append(c)
                #print(type(tab))
            #    df = pd.read_html(t)
#test =cap[1]
#pd.read_html(str(cap[0]))
#pd.read_html(tab)

#%%
pd.read_html(str(sib1))[2]
# %%
header2 = soup.select('h2:contains("apacity")')
header3 = soup.select('h3:contains("apacity")')

header_list = header2 + header3

h = header_list[0]
h
tabletable = h.find_next('table')
len(tabletable)
df = []
for i in range(len(tabletable)-1):
    tab = pd.read_html(str(tabletable))[i]
    df.append(tab)

pd.concat(df)

range(len(tabletable))
type(pd.read_html(str(tabletable))[0])
for i in range(len(tabletable)):
    print(i)
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


#%%
