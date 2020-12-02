#%%
import csv
import pandas as pd
import numpy as np
# %%

# Read the scraped table as pandas df
games_historical = pd.read_csv("../03_data_scrape/games_historical_raw.csv")

games_historical
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

#%%
# September 19, Giants Staidum was "home" for the Saints but they still had to travel. Will change Home_team to Giants
games_historical.loc[(games_historical.Home_team == "New Orleans Saints") & (games_historical.Season == 2005) & (games_historical.Date == "September 19"), "Home_team"] = "New York Giants"

games_historical.head()


# %%
# If Home_team is Winner, then Away team is Loser and vice versa.
games_historical["Away_team"] = None
games_historical.loc[games_historical["Home_team"] == games_historical["Winner/tie"], "Away_team"] = games_historical["Loser/tie"]
games_historical.loc[games_historical["Home_team"] == games_historical["Loser/tie"], "Away_team"] = games_historical["Winner/tie"]

# %%
# SuperBowl fix

# Technically, the SuperBowl does not have a Home_team and an Away_team, but for the purpose of this cleaning file, I'll make the Winner the Home_team
# Sounds like it can be problematic down the line so take note
games_historical.loc[games_historical["Week"] == "SuperBowl", "Away_team"] = games_historical["Loser/tie"]
games_historical.loc[games_historical["Week"] == "SuperBowl", "Home_team"] = games_historical["Winner/tie"]

# %%
#Drop the 2 unnamed columns
games_historical = games_historical.drop(columns=["Unnamed: 5","Unnamed: 7"])

# %%
#Home team data
#games_historical[["Home_Pts","Home_Yds","Home_TO"]] = ""
#games_historical[["Away_Pts","Away_Yds","Away_TO"]] = ""

#If Home team is equal to Winner/tie, then Pnts,
games_historical.head(10)
# %%
games_historical["Winner/tie"] == games_historical["Home_team"]
# %%
# Put PtsW and PtsL into Home & Away data
# If the Home team won, then Pts, Yds and TOs for the winning team

for i in ["Pts","Yds","TO"]:
    games_historical[f'Home_{i}'] = np.where(games_historical["Winner/tie"] == games_historical["Home_team"],games_historical[f'{i}W'],games_historical[f'{i}L'])
    games_historical[f'Away_{i}'] = np.where(games_historical["Winner/tie"] == games_historical["Away_team"],games_historical[f'{i}W'],games_historical[f'{i}L'])

# %%
#############################
# Initial merge of stadiums #
#############################

# I will merge the stadium file here, creating columns for the Home team's stadium, the Away team's stadium, and the game Stadium (where the game is actually played at)

main_stadiums = pd.read_csv("../05_data_clean/main_stadiums_long_capacity_year.csv")
#main_stadiums = pd.read_csv("../05_data_clean/main_stadiums_long.csv")
# %%
# There are 32 teams but 65 stadiums
main_stadiums.Team.nunique()
main_stadiums.Stadium.nunique()
# %%
games_historical.Home_team.nunique()

# %%
# Get a list of teams each season
season_team = games_historical[["Season","Home_team"]].drop_duplicates()
# Drop the SuperBowl where Home_team == None
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

# Check to see if we missed anything
season_team.loc[season_team.Stadium.isnull(),"Home_team"]

# Create Away_team column to get the stadium names too
season_team["Away_team"] = season_team["Home_team"]

# %%
# Merge back to games_historical for the Home_team
#df = games_historical.merge(season_team, how = "left", on = ["Season", "Home_team"])
df = games_historical.merge(season_team, how = "left", left_on = ["Season", "Home_team"], right_on =  ["Season", "Home_team"])

#Drop irrelevant columns
df = df.drop(columns = ["Year_start","Year_end","Year_start_num","Year_end_num","Years_relevant", "Years", "Years used", "Opened", "Away_team_y"])

# %%
# Rename the columns for the Home team
df[['Home_Stadium', 'Home_Capacity','Home_Surface', 'Home_Location', 'Home_URL', 'Home_lat', 'Home_lon', 'Home_Turf']] = df[['Stadium', 'Capacity',
       'Surface', 'Location', 'URL', 'lat', 'lon', 'Turf']]

# %%
# Most of the time, the Game stadium is the same as the Home stadium - so just need to rename columns
# Will work on exceptions later
df = df.rename(columns={"Stadium":"Game_Stadium", "Capacity":"Game_Capacity", "Surface":"Game_Surface", "Location":"Game_Location","URL":"Game_URL","lat":"Game_lat","lon":"Game_lon","Turf":"Game_Turf"})

# %%
# Rename Away_team_x (remnant from the first merge)
df = df.rename(columns = {"Away_team_x":"Away_team"})
# Merge once again for the away team
df = df.merge(season_team, how = "left", left_on = ["Season", "Away_team"], right_on =  ["Season", "Away_team"])

#%%
# Drop the excess columns again
df = df.drop(columns = ["Home_team_y","Year_start","Year_end","Year_start_num","Year_end_num","Years_relevant", "Years", "Years used", "Opened"])

# Rename Home_team_x
df = df.rename(columns ={"Home_team_x": "Home_team"})

# Rename the columns for away
df = df.rename(columns={"Stadium":"Away_Stadium", "Capacity":"Away_Capacity", "Surface":"Away_Surface", "Location":"Away_Location","URL":"Away_URL","lat":"Away_lat","lon":"Away_lon","Turf":"Away_Turf"})

#%%
#Drop Team_y (this is the away team)
df = df.drop(columns="Team_y")

#Rename Team_x
df = df.rename(columns={"Team_x":"Team"})

#Rename the "Game_" columns back to normal
df = df.rename(columns={"Game_Stadium":"Stadium", "Game_Capacity":"Capacity", "Game_Surface":"Surface", "Game_Location":"Location","Game_URL":"URL","Game_lat":"lat","Game_lon":"lon","Game_Turf":"Turf"})


# %%
#############################
# Next, do the odd stadiums #
#############################

odd_stadiums = pd.read_csv("../05_data_clean/main_stadiums_merge.csv")

# %%
####################
# Rams 1995 season #
####################

# Because their Home Stadium was Edward Jones for the first 4 games of the season, there are some duplicates in both Home_ and Away_ sides
# Because this wasn't a collapse (Saints, Seahawks below) or an agreed upon arrangement (Packers, Bills)
# I will have to change both "Stadium" and "Home_Stadium"

df.columns
# Fix Home_ side first

df.loc[(df.Season==1995)&(df.Home_team.str.contains("Rams"))][['Week','Date','Home_team', 'Away_team','Stadium','Home_Stadium']]

# Drop where they used Edward Jones in the first 4 games
df.drop(df.loc[(df.Season==1995) & (df.Home_team=="St. Louis Rams") & (df.Date.isin(["September 10","September 24","October 12","October 22"])) & (df.Stadium=="Edward Jones Dome ")].index,inplace = True)

# Drop where they used Busch after Oct 22
df.drop(df.loc[(df.Season==1995) & (df.Home_team=="St. Louis Rams") & (~df.Date.isin(["September 10","September 24","October 12","October 22"])) & (df.Stadium=="Busch Stadium (II) ")].index, inplace = True)

# As an away team
# First game at Edward Jones was Nov 12, so it'll be the Away_Stadium will be Busch until before that day.
# Drop where Away_Stadium = Edward Jones
df.drop(df.loc[(df.Season==1995) & (df.Away_team=="St. Louis Rams") & (df.Date.isin(["September 3","September 17","October 1","October 29","November 5"])) & (df.Away_Stadium=="Edward Jones Dome ")].index, inplace = True)
# Drop Busch for the other dates
df.drop(df.loc[(df.Season==1995) & (df.Away_team=="St. Louis Rams")&(~df.Date.isin(["September 3","September 17","October 1","October 29","November 5"])) & (df.Away_Stadium=="Busch Stadium (II) ")].index, inplace = True)

#Done with Rams!
# %%
######################
# Saints 2005 season #
######################

# Their stadium collapsed, so although technically they had the same home stadium, the "stadium" where the games were played changed

# September 19 2005 already fixed above (Giants game after the dome collapsed)

# Alamodome https://en.wikipedia.org/wiki/2005_New_Orleans_Saints_season
df.loc[(df.Home_team == "New Orleans Saints") & (df.Season == 2005) & (df.Date.isin(["October 2","October 16","December 24"])),["Surface", "Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Alamodome ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

# Tiger Stadium
df.loc[(df.Home_team == "New Orleans Saints") & (df.Season == 2005) & (df.Date.isin(["October 30","November 6","December 4","December 18"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Tiger Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

# Changing Tiger Stadium capacity to 79,000 https://en.wikipedia.org/wiki/Tiger_Stadium_(LSU)
df.loc[(df.Home_team == "New Orleans Saints") & (df.Season == 2005) & (df.Stadium == "Tiger Stadium "), "Turf"] = "Grass"
# Also changing Turf to grass
df.loc[(df.Home_team == "New Orleans Saints") & (df.Season == 2005) & (df.Stadium == "Tiger Stadium "), "Capacity"] = 79000


# %%
###########
# Seattle #
###########

# Used Husky stadium for a few games after their ceiling collapsed in 1994

# Seattle - Husky stadium in 1994 https://en.wikipedia.org/wiki/1994_Seattle_Seahawks_season
df.loc[(df.Home_team == "Seattle Seahawks") & (df.Season == 1994) & (df.Date.isin(["September 18","September 25","October 9"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Husky Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()


# %%
# Packers, 1992 - 1994, plays 2-4 games a year at Milwaukee County Stadium

df.loc[(df.Home_team == "Green Bay Packers") & (df.Season == 1992) & (df.Date.isin(["November 15","November 29","December 6"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Milwaukee County Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Green Bay Packers") & (df.Season == 1993) & (df.Date.isin(["September 5","November 21","December 19"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Milwaukee County Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Green Bay Packers") & (df.Season == 1994) & (df.Date.isin(["September 11","November 6","December 18"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Milwaukee County Stadium ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()


# %%
#########################
# Bills Toronto series  #
#########################
# Had a series in Canada (so still had to travel even as Home team)

# Bills Roger Centre series https://en.wikipedia.org/wiki/Bills_Toronto_Series
df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2008) & (df.Date.isin(["December 7"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2008) & (df.Date.isin(["December 3"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2010) & (df.Date.isin(["November 7"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2011) & (df.Date.isin(["October 30"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2012) & (df.Date.isin(["December 16"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

df.loc[(df.Home_team == "Buffalo Bills") & (df.Season == 2013) & (df.Date.isin(["December 1"])),["Surface","Capacity","Stadium","Location","URL","lat","lon"]] = odd_stadiums.loc[odd_stadiums["Stadium"] == "Rogers Centre ", ["Surface","Capacity","Stadium","Location","URL","lat","lon"]].values.tolist()

# %%
#Think I'm done with The Odd games. Now I need temp stadiums & int stadiums, then the SB

# %%
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

# %%

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

######################
# Superbowl stadiums #
######################
df.columns

sb = pd.read_csv("../05_data_clean/superbowl_stadiums.csv")

# "Week" is just a column of "SuperBowl"
df = df.merge(sb, left_on=["Season","Week"], right_on=["Season","Week"],how="left")

# %%
# Similar drop as above
for i in ["Stadium","Capacity","lat","lon","Turf","Attendance"]:
    df[f'{i}'] = df[f'{i}_y'].fillna(df[f'{i}_x'])
    df = df.drop(columns = [f'{i}_x', f'{i}_y'])


# %%
##################################
# Merge playoff attendance to df #
##################################

# Playoff attendance
playoff = pd.read_csv("../05_data_clean/playoff_attendance_clean.csv")
playoff.Home_team.unique()


#%%
# Let the SB winner to be the Home_team for now
#df.loc[df["Week"]=="SuperBowl","Home_team"] = df["Winner/tie"]

# Merge
df = df.merge(playoff, left_on=["Season","Date","Home_team"], right_on=["Season","Date","Home_team"], how = "left")



# %%
# Drop "away team"
df = df.drop(columns = "away team")


# %%
#########################################
# Merge regular season attendance to df #
#########################################

# Read in the data
reg = pd.read_csv("../05_data_clean/regular_attendance_clean.csv")
reg["Week"] = reg["Week"].astype(str)

# Merge
df = df.merge(reg, left_on=["Home_team","Season","Week"], right_on=["Home_team","Season","Week"], how = "left")


# %%
df.loc[df.attendance_y.isnull()]

#%%

# Merge attendance_x and attendance_y
for i in ["attendance"]:
    df[f'{i}'] = df[f'{i}_x'].fillna(df[f'{i}_y'])
    #df = df.drop(columns = [f'{i}_x', f'{i}_y'])

# %%
# If attendance is still null, then use Attendance
df["attendance"] = df["attendance"].fillna(df["Attendance"])

# Drop duplicate columns
df = df.drop(columns=["Attendance","attendance_x","attendance_y"])

# %%
# df is in ok shape now!!!
# next step is to drop the irrelevant columns

df.columns
# Drop irrelevant columns
df = df.drop(columns=['Team','Surface','Location','URL','Away_Surface','Away_Location','Away_URL','Home_Surface','Home_Location','Home_URL' ])

# Rename Turf Surface
df = df.rename(columns={"Turf":"Surface","Home_Turf":"Home_Surface","Away_Turf":"Away_Surface"})

# Drop Winner Loser columns
df = df.drop(columns=['Winner/tie', 'Loser/tie', 'PtsW',
       'PtsL', 'YdsW', 'TOW', 'YdsL', 'TOL'])
# %%
df.columns
df.loc[df.Week.isnull()]


# %%
# Export to csv
df.to_csv("../05_data_clean/games_historical_clean.csv" ,index=False,encoding='utf-8-sig')

# Next, need to think about how to shape the data to calculate distance traveled and time rest
