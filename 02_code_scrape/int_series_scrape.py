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
############################
# NFL International Series #
############################

url = "https://en.wikipedia.org/wiki/NFL_International_Series#Game_history"
page = requests.get(url)

tables = pd.read_html(page.text)
# %%
# Table for London games
london_games = tables[0]
# Remove citations from year
london_games.Year = london_games.Year.str.split("[", expand=True)[0]
# Remove citations from year

# %%
# Table for mexico games
mexico_games = tables[1]
# Remove citations from dates
mexico_games.Date = mexico_games.Date.str.split("[", expand=True)[0]
# Remove 2018 because that got canned
mexico_games = mexico_games.dropna()
# %%
########################
# Bills Toronto Seires #
########################
url2 = "https://en.wikipedia.org/wiki/Bills_Toronto_Series"
page2 = requests.get(url2)

tables2 = pd.read_html(page2.text)

#Table for regular season games
bills_toronto_series = tables2[1]
# Remove citations from attendance
bills_toronto_series.Attendance = bills_toronto_series.Attendance.str.split("[", expand=True)[0]

# %%
#############
# Save them #
#############

london_games.to_csv("../03_data_scrape/london_games.csv", index=False,encoding='utf-8-sig')
mexico_games.to_csv("../03_data_scrape/mexico_games.csv", index=False,encoding='utf-8-sig')
bills_toronto_series.to_csv("../03_data_scrape/bills_toronto_series.csv", index=False,encoding='utf-8-sig')
