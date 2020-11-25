#%%
import csv
import pandas as pd
import numpy as np
import re
from math import radians, degrees, sin, cos, asin, acos, sqrt
## This file picks up where clean_games_historical left off
## It will merge division information, team stat, coach info, etc to the df


# %%
# Read-in the clean-ish df
data = pd.read_csv("../05_data_clean/games_historical_clean.csv")
len(data)

# %%
################################
# Team's divisions and ranking #
################################

# Read in scraped division ranking. Note that the scraped data is really clean, so there is no separate cleaning file for this
div = pd.read_csv("../03_data_scrape/divisions_ranking.csv")

#Make 2 true copies of it to merge
div_home = div.copy(deep=True)
div_away = div.copy(deep=True)


# Split Tm to just the team name
div_home["Tm"]=div_home["Tm"].str.split("\+|\*", expand=True)[0]
# Rename it
div_home = div_home.rename(columns={"Tm":"team"})
#Add prefix
div_home = div_home.add_prefix('Home_')
#rename Seaseon
div_home = div_home.rename(columns={"Home_Season":"Season"})


#Do the same steps for div_away
div_away["Tm"]=div_away["Tm"].str.split("\+|\*", expand=True)[0]
# Rename it
div_away = div_away.rename(columns={"Tm":"team"})
#Add prefix
div_away = div_away.add_prefix('Away_')
#rename Seaseon
div_away = div_away.rename(columns={"Away_Season":"Season"})

# %%
data.columns

div_home
#%%
#Merge with div_home
data = data.merge(div_home, how="left",left_on=["Season","Home_team"],right_on=["Season","Home_team"])
#Merge with div_away
data = data.merge(div_away, how="left",left_on=["Season","Away_team"],right_on=["Season","Away_team"])

#%%
data.loc[data.Season==1995]





#%%

# Next, I want Offense & Defense ranking
# Whether the team had a coaching change

# %%
######################
# Time between games #
######################
df = data.copy(deep=True)
#Create Year column
df["Year"] = df["Season"]
#If Jan or Feb then year is the year after
df.loc[(df["Date"].str.contains("January"))|(df["Date"].str.contains("February")),"Year"] = df["Season"] +1
#Convert Year to string
df["Year"]=df["Year"].astype(str)

#Merge together Date, Year and Time to create datetime object
df["datetime"]=df["Date"] + ' ' + df["Year"] + ' ' +df["Time"]
#Convert that to datetime
df["datetime"] = pd.to_datetime(df["datetime"])
#%%
#Calculate the time between games

#Time difference for home team
home_diff=df.groupby(["Season","Home_team"])["datetime"].diff().rename("Home_timerest")
#Time difference for away team
away_diff=df.groupby(["Season","Away_team"])["datetime"].diff().rename("Away_timerest")

# %%
#Merge back to df
df = df.merge(home_diff, left_index=True,right_index=True)
df = df.merge(away_diff, left_index=True, right_index=True)

#%%
#####################
# Distance traveled #
#####################

# Next will be to calculate the distance traveled of each team
# Using the Great-Circle distance suggested by Prof Dunford
# Source: https://medium.com/@petehouston/calculate-distance-of-two-locations-on-earth-using-python-1501b1944d97

# Define great_circle formula
def great_circle(lon1, lat1, lon2, lat2):
    '''
    This formula calculates the shortest distance in miles between 2 GPS coordinates
    '''
    if (lon1 != lon2) & (lat1 != lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        distance = 3958.756 * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))
    # If lon1 = lon2 and lat1 = lat2 (meaning that the Home team played at home)
    elif (lon1 == lon2) & (lat1 == lat2):
        distance = 0
    return distance


# %%
# Distance away team traveled
df["Away_travel"] = df.apply(lambda row: great_circle(row['lon'],row['lat'],row['Away_lon'],row['Away_lat']),axis=1)

# Distance Away team traveled
df["Home_travel"] = df.apply(lambda row: great_circle(row['lon'],row['lat'],row['Home_lon'],row['Home_lat']),axis=1)

df["Home_travel"].describe()

# %%
# Has time rest and distance traveled
# Tomorrow I can try turning the (preliminary) data into a dyad, split it and see if any ML model will run.
