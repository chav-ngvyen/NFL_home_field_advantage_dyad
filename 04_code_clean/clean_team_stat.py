#%%
import csv
import pandas as pd
import numpy as np
import re
from math import radians, degrees, sin, cos, asin, acos, sqrt
## This file picks up where clean_games_historical left off
## It will merge division information, team stat, coach info, etc to the df
import datetime
import pytz
from dateutil.relativedelta import relativedelta
from tzwhere import tzwhere

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
#div91 = pd.read_csv("../03_data_scrape/divisions_ranking_1991.csv")

#div = pd.concat([div,div91])

# %%

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
# Do the same for divisions_ranking_1991
div91 = pd.read_csv("../03_data_scrape/divisions_ranking_1991.csv")

#Make 2 true copies of it to merge
div91_home = div91.copy(deep=True)
div91_away = div91.copy(deep=True)


# Split Tm to just the team name
div91_home["Tm"]=div91_home["Tm"].str.split("\+|\*", expand=True)[0]
# Rename it
div91_home = div91_home.rename(columns={"Tm":"team"})
#Add prefix
div91_home = div91_home.add_prefix('Home_')
#rename Seaseon
div91_home = div91_home.rename(columns={"Home_Season":"Season"})

#Do the same steps for div91_away
div91_away["Tm"]=div91_away["Tm"].str.split("\+|\*", expand=True)[0]
# Rename it
div91_away = div91_away.rename(columns={"Tm":"team"})
#Add prefix
div91_away = div91_away.add_prefix('Away_')
#rename Seaseon
div91_away = div91_away.rename(columns={"Away_Season":"Season"})

div91.columns

# %%
d = data.copy()

# %%
# Combine the 2 data
div_home_lag = pd.concat([div_home, div91_home])
# Add 1 to Season to lag it
div_home_lag["Season"] = div_home_lag["Season"]+1

# Add the lag suffix
div_home_lag = div_home_lag.add_suffix('_lag')

# Rename
div_home_lag = div_home_lag.rename(columns={"Home_team_lag":"Home_team","Season_lag":"Season"})

# %%
#Do the same with away
# Combine the 2 data
div_away_lag = pd.concat([div_away, div91_away])
# Add 1 to Season to lag it
div_away_lag["Season"] = div_away_lag["Season"]+1

# Add the lag suffix
div_away_lag = div_away_lag.add_suffix('_lag')

# Rename
div_away_lag = div_away_lag.rename(columns={"Away_team_lag":"Away_team","Season_lag":"Season"})

#%%
# Fudge the team names
# Cardinal
div_home_lag.loc[(div_home_lag.Home_team == "Phoenix Cardinals") & (div_home_lag.Season == 1994), "Home_team"] = "Arizona Cardinals"
div_away_lag.loc[(div_away_lag.Away_team == "Phoenix Cardinals") & (div_away_lag.Season == 1994), "Away_team"] = "Arizona Cardinals"

# Raiders
div_home_lag.loc[(div_home_lag.Home_team == "Los Angeles Raiders") & (div_home_lag.Season == 1995), "Home_team"] = "Oakland Raiders"
div_away_lag.loc[(div_away_lag.Away_team == "Los Angeles Raiders") & (div_away_lag.Season == 1995), "Away_team"] = "Oakland Raiders"

# Rams
div_home_lag.loc[(div_home_lag.Home_team == "Los Angeles Rams") & (div_home_lag.Season == 1995), "Home_team"] = "St. Louis Rams"
div_away_lag.loc[(div_away_lag.Away_team == "Los Angeles Rams") & (div_away_lag.Season == 1995), "Away_team"] = "St. Louis Rams"

# Rams again
div_home_lag.loc[(div_home_lag.Home_team == "St. Louis Rams") & (div_home_lag.Season == 2016), "Home_team"] = "Los Angeles Rams"
div_away_lag.loc[(div_away_lag.Away_team == "St. Louis Rams") & (div_away_lag.Season == 2016), "Away_team"] = "Los Angeles Rams"

# Chargers
div_home_lag.loc[(div_home_lag.Home_team == "San Diego Chargers") & (div_home_lag.Season == 2017), "Home_team"] = "Los Angeles Chargers"
div_away_lag.loc[(div_away_lag.Away_team == "San Diego Chargers") & (div_away_lag.Season == 2017), "Away_team"] = "Los Angeles Chargers"

# Tennessee
div_home_lag.loc[(div_home_lag.Home_team == "Houston Oilers") & (div_home_lag.Season == 1997), "Home_team"] = "Tennessee Oilers"
div_away_lag.loc[(div_away_lag.Away_team == "Houston Oilers") & (div_away_lag.Season == 1997), "Away_team"] = "Tennessee Oilers"

div_home_lag.loc[(div_home_lag.Home_team == "Tennessee Oilers") & (div_home_lag.Season == 1999), "Home_team"] = "Tennessee Titans"
div_away_lag.loc[(div_away_lag.Away_team == "Tennessee Oilers") & (div_away_lag.Season == 1999), "Away_team"] = "Tennessee Titans"


# %%

#Merge with div_home
data = data.merge(div_home, how="left",left_on=["Season","Home_team"],right_on=["Season","Home_team"])
#Merge with div_away
data = data.merge(div_away, how="left",left_on=["Season","Away_team"],right_on=["Season","Away_team"])

# %%
# Merge with div_home_lag
d = data.merge(div_home_lag, how="left",left_on=["Season","Home_team"],right_on=["Season","Home_team"])

d = d.merge(div_away_lag, how="left",left_on=["Season","Away_team"],right_on=["Season","Away_team"])






#%%

# Next, I want Offense & Defense ranking
# Whether the team had a coaching change

# %%
######################
# Time between games #
######################
df = d.copy(deep=True)
#Create Year column
df["Year"] = df["Season"]
#If Jan or Feb then year is the year after
df.loc[(df["Date"].str.contains("January"))|(df["Date"].str.contains("February")),"Year"] = df["Season"] +1
#Convert Year to string
df["Year"]=df["Year"].astype(str)
# %%

#Merge together Date, Year and Time to create datetime object
df["datetime"]=df["Date"] + ' ' + df["Year"] + ' ' +df["Time"]
#Convert that to datetime
df["datetime"] = pd.to_datetime(df["datetime"])

# %%

#df.groupby(["Season","Home_team"])["datetime"].diff().describe()


#%%
# #Calculate the time between games
#
# #Time difference for home team
# home_diff=df.groupby(["Season","Home_team"])["datetime"].diff().rename("Home_timerest")
# #Time difference for away team
# away_diff=df.groupby(["Season","Away_team"])["datetime"].diff().rename("Away_timerest")
#
# # %%
# #Merge back to df
# df = df.merge(home_diff, left_index=True,right_index=True)
# df = df.merge(away_diff, left_index=True, right_index=True)

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

# %%
# Time zone

from tzwhere import tzwhere
tz = tzwhere.tzwhere()

tz.tzNameAt(df['Home_lat'][1],df['Home_lon'][1])

df['Home_tz'] = df.apply(lambda row: tz.tzNameAt(row['Home_lat'],row['Home_lon']), axis =1 )

df['Away_tz'] = df.apply(lambda row: tz.tzNameAt(row['Away_lat'],row['Away_lon']), axis =1 )

df['Stadium_tz'] = df.apply(lambda row: tz.tzNameAt(row['lat'],row['lon']), axis =1 )
# %%
# Methods here: https://stackoverflow.com/questions/46736529/how-to-compute-the-time-difference-between-two-time-zones-in-python

# Generitc time
utcnow = pytz.timezone('utc').localize(datetime.datetime.utcnow())

df['Home_tz_now'] = df.apply(lambda row: utcnow.astimezone(pytz.timezone(row['Home_tz'])).replace(tzinfo=None), axis = 1)

df['Away_tz_now'] = df.apply(lambda row: utcnow.astimezone(pytz.timezone(row['Away_tz'])).replace(tzinfo=None), axis = 1)

df['Stadium_tz_now'] = df.apply(lambda row: utcnow.astimezone(pytz.timezone(row['Stadium_tz'])).replace(tzinfo=None), axis = 1)



df['Home_timediff'] = df.apply(lambda row: relativedelta(row['Home_tz_now'],row['Stadium_tz_now']), axis =1)

df['Away_timediff'] = df.apply(lambda row: relativedelta(row['Away_tz_now'],row['Stadium_tz_now']), axis =1)



df['Home_timediff'] = df.apply(lambda row: row['Home_timediff'].hours, axis = 1)
df['Away_timediff'] = df.apply(lambda row: row['Away_timediff'].hours, axis = 1)

# Absoluate value
df['Home_timediff'] = abs(df['Home_timediff'])
df['Away_timediff'] = abs(df['Away_timediff'])
# %%
# Export to csv
df.to_csv("../05_data_clean/df_team_stat.csv",index=False,encoding='utf-8-sig')
