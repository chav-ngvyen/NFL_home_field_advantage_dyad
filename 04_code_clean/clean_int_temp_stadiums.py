#%%
import csv
import pandas as pd
import math
import requests # For downloading the website
from bs4 import BeautifulSoup # For parsing the website
import numpy as np
# %%
# Read the london games in:
london_games = pd.read_csv("../03_data_scrape/london_games.csv")
# Read mexico games in
mexico_games = pd.read_csv("../03_data_scrape/mexico_games.csv")
# Concat the 2
int_series = pd.concat([london_games,mexico_games]).reset_index(drop=True)

# %%

# Read the int stadiums
int_stadiums = pd.read_csv("../03_data_scrape/int_stadiums_raw.csv")
# Read in coords
int_stadiums_coord = pd.read_csv("../03_data_scrape/int_stadiums_coord_raw.csv")

# Merge stadium with coords
int_stadiums = int_stadiums.merge(int_stadiums_coord, on = "URL", how = "left")

# %%
######################
# Clean int_stadiums #
######################

# Still missing capacity & surface - will do that by hand

int_stadiums["Capacity"] = ""
int_stadiums["Turf"] = ""

# Twickenham
int_stadiums.loc[int_stadiums.Stadium == "Twickenham Stadium ","Capacity"] = 75000
# Desso Grass Master - which is what Green Bay uses, so I'll put it as grass https://www.si.com/nfl/2015/09/29/nfl-stadium-turf-grass-rankings
int_stadiums.loc[int_stadiums.Stadium == "Twickenham Stadium ","Turf"] = "Grass"

# Wembley
int_stadiums.loc[int_stadiums.Stadium == "Wembley Stadium ","Capacity"] = 86000
# Also Desso Grassmaster
int_stadiums.loc[int_stadiums.Stadium == "Wembley Stadium ","Turf"] = "Grass"

# Tottenham Hotspur Stadium
int_stadiums.loc[int_stadiums.Stadium == "Tottenham Hotspur Stadium ","Capacity"] = 62303
#Turf https://talksport.com/sport/us-sports/609697/tottenham-hotspur-stadium-nfl-london-games/
int_stadiums.loc[int_stadiums.Stadium == "Tottenham Hotspur Stadium ","Turf"] = "Turf"

# Estadio Azteca
int_stadiums.loc[int_stadiums.Stadium == "Estadio Azteca ","Capacity"] = 87523
# Grass
int_stadiums.loc[int_stadiums.Stadium == "Estadio Azteca ","Turf"] = "Grass"
# Fix the Location
int_stadiums.loc[int_stadiums.Stadium == "Estadio Azteca ","Location"] = "Mexico City, Mexico"

# Drop 2 columns
int_stadiums = int_stadiums.drop(columns=["Years hosted", "URL", "No. hosted"])

# Strip trailing space
int_stadiums.Stadium = int_stadiums.Stadium.str.rstrip(" ")

# %%
####################
# Clean int_series #
####################

# Rename home team column
int_series = int_series.rename(columns={"Designatedhome team":"Home_team", "Year":"Season"})

# Drop the useless ones
int_series = int_series.drop(columns = ["Designatedvisitor", "Score", "Score.1", "Pre-game show"])

# %%
###############
# Merge the 2 #
###############

int_series = int_series.merge(int_stadiums, on = "Stadium", how = "left")

# %%
# Export to csv
int_series.to_csv("../05_data_clean/int_series.csv", index=False,encoding='utf-8-sig')


# %%
#################
# Temp stadiums #
#################

temp_stadiums = pd.read_csv("../03_data_scrape/temp_stadiums_raw.csv")

# Drop games before 1992
temp_stadiums = temp_stadiums.drop(range(0,8))
# Drop the game where Saints played at Giants after Superdome collapse but the called it their home field
temp_stadiums = temp_stadiums.drop(9)

temp_stadiums = temp_stadiums.reset_index(drop=True)

# %%
# More clean up
temp_stadiums["Date"] = temp_stadiums["Date played"].str.split(",", expand=True)[0]
temp_stadiums["Season"] = temp_stadiums["Date played"].str.split(",", expand=True)[1]

temp_stadiums["Home_team"] = temp_stadiums["Home team"].str.split(" url:",expand = True)[0]

temp_stadiums = temp_stadiums.drop(columns = ["Visiting team","Home team","Rationale", "Date played"])
# %%
# Read in coords
temp_stadiums_coord = pd.read_csv("../03_data_scrape/temp_stadiums_coord_raw.csv")

# Merge stadium with coords
temp_stadiums = temp_stadiums.merge(temp_stadiums_coord, on = "URL", how = "left")

#Drop duplicates
temp_stadiums = temp_stadiums.drop_duplicates()

# %%
# Still need the Turf & Capacity

temp_stadiums["Capacity"] = ""
temp_stadiums["Turf"] = ""

# Sun Devil - in 2003 it was https://en.wikipedia.org/wiki/Sun_Devil_Stadium
temp_stadiums.loc[temp_stadiums.Stadium == "Sun Devil Stadium ","Capacity"] = 73379
temp_stadiums.loc[temp_stadiums.Stadium == "Sun Devil Stadium ","Turf"] = "Grass"

temp_stadiums.loc[temp_stadiums.Stadium == "Ford Field ","Capacity"] = 65000
temp_stadiums.loc[temp_stadiums.Stadium == "Ford Field ","Turf"] = "Turf"

temp_stadiums.loc[temp_stadiums.Stadium == "TCF Bank Stadium ","Capacity"] = 50805
temp_stadiums.loc[temp_stadiums.Stadium == "TCF Bank Stadium ","Turf"] = "Turf"

# %%
# Export to csv

temp_stadiums.to_csv("../05_data_clean/temp_stadiums.csv", index=False,encoding='utf-8-sig')
