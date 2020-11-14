#%%
import csv
import pandas as pd
import numpy as np
# %%

# Read the scraped table as pandas df
games_historical = pd.read_csv("../03_data_scrape/games_historical_raw.csv")
# %%
##########################
# Drop unneccessary rows #
##########################

#Drop rows where Week is "Week" (this marks a new season)
games_historical.drop(games_historical[games_historical["Week"] =="Week"].index, inplace=True)

#Drop rows where Date is "Playoffs"
games_historical.drop(games_historical[games_historical["Date"] =="Playoffs"].index, inplace=True)

# %%
# Create column for Game type
games_historical["Game_type"] = None

# Game type is either a Regular or Playoff game
games_historical.loc[(games_historical["Week"].isin(['WildCard', 'Division', 'ConfChamp', 'SuperBowl'])), "Game_type"] = "Playoff"
games_historical.loc[(games_historical["Week"].str.isnumeric()), "Game_type"] = "Regular"

# %%
# Create column for Home team
games_historical["Home_team"] = None

# If Unnamed: 5 is @ then the Loser is the home team. If isna() then the winner is the home team
games_historical.loc[(games_historical["Unnamed: 5"] == "@"), "Home_team"] = games_historical["Loser/tie"]
games_historical.loc[(games_historical["Unnamed: 5"].isna()), "Home_team"] = games_historical["Winner/tie"]

# %%
#Drop the 2 unnamed columns
games_historical = games_historical.drop(columns=["Unnamed: 5","Unnamed: 7"])

#%%
# September 19, Giants Staidum was "home" for the Saints but they still had to travel. Will change Home_team to Giants
games_historical.loc[(games_historical.Home_team == "New Orleans Saints") & (games_historical.Season == 2005) & (games_historical.Date == "September 19"), "Home_team"] = "New York Giants"


# %%
main_stadiums = pd.read_csv("../05_data_clean/main_stadiums_long.csv")
# %%
# There are 32 teams but 65 stadiums
main_stadiums.Team.nunique()
main_stadiums.Stadium.nunique()
# %%
games_historical.Home_team.nunique()

# %%
# Get a list of teams each season
season_team = games_historical[["Season","Home_team"]].drop_duplicates()
# Drop the superbowl where Home_team == None
season_team = season_team.dropna()
# Create Years_relevant column to merge
season_team["Years_relevant"] = season_team["Season"]



# %%
# Define get_name function to grab all names from main_stadiums
def get_name(x):
    return main_stadiums.loc[main_stadiums["Team"].str.contains(x), "Team"].iloc[0]
# %%
# Run it
season_team["Team"] =season_team["Home_team"].apply(get_name)

#%%
# Merge
season_team = season_team.merge(main_stadiums,how="outer",left_on=["Team", "Years_relevant"], right_on=["Team", "Years_relevant"])

season_team.loc[season_team.Stadium.isnull(),"Home_team"]

# %%
# Merge back to games_historical
df = games_historical.merge(season_team, how = "left", on = ["Season", "Home_team"])
df.columns
# drop some columnd
df = df.drop(columns = ["Year_start","Year_end","Year_start_num","Year_end_num","Years_relevant", "Years", "Years used", "Opened"])
# %%

odd_stadiums = pd.read_csv("../05_data_clean/main_stadiums_merge.csv")

# %%
# Weird stadiums for Saints 2005 season.
# September 19 2005 already fixed above

# Alamodome https://en.wikipedia.org/wiki/2005_New_Orleans_Saints_season
df.loc[(df.Team == "New Orleans Saints") & (df.Season == 2005) & (df.Date.isin(["October 2","October 16","December 24"])),["Surface", "Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Alamodome ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

# Tiger Stadium
df.loc[(df.Team == "New Orleans Saints") & (df.Season == 2005) & (df.Date.isin(["October 30","November 6","December 4","December 18"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Tiger Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

# Changing Tiger Stadium capacity to 79,000 https://en.wikipedia.org/wiki/Tiger_Stadium_(LSU)
df.loc[(df.Home_team == "New Orleans Saints") & (df.Season == 2005) & (df.Stadium == "Tiger Stadium "), "Turf"] = "Grass"
# Also changing Turf to grass
df.loc[(df.Home_team == "New Orleans Saints") & (df.Season == 2005) & (df.Stadium == "Tiger Stadium "), "Capacity"] = 79000


# %%
# Seattle - Husky stadium in 1994 https://en.wikipedia.org/wiki/1994_Seattle_Seahawks_season
df.loc[(df.Home_team == "Seattle Seahawks") & (df.Season == 1994) & (df.Date.isin(["September 18","September 25","October 9"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Husky Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()


# %%
# Packers, 1992 - 1994, plays 2-4 games a year at Milwaukee County Stadium

df.loc[(df.Home_team == "Green Bay Packers") & (df.Season == 1992) & (df.Date.isin(["November 15","November 29","December 6"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Milwaukee County Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Green Bay Packers") & (df.Season == 1993) & (df.Date.isin(["September 5","November 21","December 19"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Milwaukee County Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Green Bay Packers") & (df.Season == 1994) & (df.Date.isin(["September 11","November 6","December 18"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Milwaukee County Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()


# %%
# Bills Roger Centre series https://en.wikipedia.org/wiki/Bills_Toronto_Series
df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2008) & (df.Date.isin(["December 7"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2008) & (df.Date.isin(["December 3"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2010) & (df.Date.isin(["November 7"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2011) & (df.Date.isin(["October 30"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2012) & (df.Date.isin(["December 16"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2013) & (df.Date.isin(["December 1"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

# %%
#Think I'm done with The Odd games. Now I need temp stadiums & int stadiums, then the SB

########################
# International series #
########################
int_series = pd.read_csv("../05_data_clean/int_series.csv")

# Merge df with int_series
df = df.merge(int_series, left_on=["Season","Date","Home_team"], right_on=["Season","Date","Home_team"],how="left")

# Use a for loop to loop through the duplicated columns, fill one with the other, and drop the duplicates
# Similar to how I would use a local string list in `i' in Stata!
for i in ["Stadium","Capacity","Location","lat","lon","Turf"]:
    df[f'{i}'] = df[f'{i}_y'].fillna(df[f'{i}_x'])
    df = df.drop(columns = [f'{i}_x', f'{i}_y'])

#%%
#Only superbowl & temp stadiums left!!

#################
# temp_stadiums #
#################
temp_stadiums = pd.read_csv("../05_data_clean/temp_stadiums.csv")

# Similar merge as above
df = df.merge(temp_stadiums, left_on=["Season","Date","Home_team"], right_on=["Season","Date","Home_team"],how="left")

df.columns

# Similar drop as above
for i in ["Stadium","Capacity","URL","lat","lon","Turf"]:
    df[f'{i}'] = df[f'{i}_y'].fillna(df[f'{i}_x'])
    df = df.drop(columns = [f'{i}_x', f'{i}_y'])

# %%
# Only Superbowl left now
