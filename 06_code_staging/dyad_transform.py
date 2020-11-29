#%%
import csv
import pandas as pd
import numpy as np

# %%
# Read-in the clean-ish df
df = pd.read_csv("../05_data_clean/df_team_stat.csv")

# %%
# Drop some columns
df.columns


df.drop(columns =['Day', 'Date', 'Time', 'Home_lat', 'Home_lon', 'Away_lat', 'Away_lon','lat', 'lon','Year'], inplace = True)

# %%

# Create df where team_A is home

# Deep copy
home_away = df.copy(deep =True)

# Get the columns
Home_cols = [col for col in home_away if col.startswith("Home_")]
Away_cols = [col for col in home_away if col.startswith("Away_")]

# Rename Home columns
for col in Home_cols:
    dat = col.split("Home_")[1]
    home_away = home_away.rename(columns = {f'{col}':f'Team_A_{dat}'})

# Rename Away columns
for col in Away_cols:
    dat = col.split("Away_")[1]
    home_away = home_away.rename(columns = {f'{col}':f'Team_B_{dat}'})

# Field is "Home" for all the Team_A in home_away except for the SuperBowl
home_away["Field"] = "Home"
home_away.loc[home_away.Week=="SuperBowl","Field"] = "Neutral"
# %%
# Create df where team_A is away
# Exact same steps above

away_home = df.copy(deep =True)

# Rename Home columns
for col in Home_cols:
    dat = col.split("Home_")[1]
    away_home = away_home.rename(columns = {f'{col}':f'Team_B_{dat}'})

# Rename Away columns
for col in Away_cols:
    dat = col.split("Away_")[1]
    away_home = away_home.rename(columns = {f'{col}':f'Team_A_{dat}'})

# Field is "Away" for all the Team_A in away_home except for the SuperBowl
away_home["Field"] = "Away"
away_home.loc[away_home.Week == "SuperBowl","Field"] = "Neutral"

# %%
###################################
#Concat the 2 to make a dyadic df #
###################################

#Sort both by datetime so that 1992 season comes first
home_away.sort_values(by="datetime",inplace=True)
home_away.reset_index(drop=True, inplace=True)


away_home.sort_values(by="datetime",inplace=True)
away_home.reset_index(drop=True, inplace=True)

df = pd.concat([home_away,away_home],sort=False).sort_index()

# Eureka!

# %%
##################
# Clean the dyad #
##################

# Reset index
df.reset_index(drop=True, inplace=True)

df.head()

# Rename Team_A and Team_B columns
df.rename(columns={'Team_A_team':'Team_A','Team_B_team':'Team_B'}, inplace=True)


# %%

# Points differential
df["Points_diff"] = df["Team_A_Pts"] - df["Team_B_Pts"]
#%%

# Win/Loss

# Conditions
conditions = [
    (df['Points_diff'] < 0),
    (df['Points_diff'] > 0),
    (df['Points_diff'] == 0)
    ]

# Outcome for team A
values = ["Lose","Win","Tie"]

# create a new column and use np.select to assign values to it using our lists as arguments
df['Outcome'] = np.select(conditions, values)


# %%
# Yards differential
df["Yards_diff"] = df["Team_A_Yds"] - df["Team_B_Yds"]

# Turnover differential
df['Turnover_diff'] = df["Team_A_TO"] - df["Team_B_TO"]

# Season points diff
df.rename(columns={'Team_A_PD':'Season_points_diff'}, inplace=True)

# Season margins of victory
df.rename(columns={'Team_A_MoV':'Season_margins'}, inplace=True)

# Miles traveled
df.rename(columns={'Team_A_travel':'Miles_traveled'}, inplace=True)

# Time rest
df.rename(columns={'Team_A_timerest':'Time_rest'}, inplace=True)

#Rename Team_A_Division_Rank to Division_Rank
df.rename(columns={"Team_A_Division_Rank":"Division_rank"}, inplace = True)

# %%
# Rivalry

# Conditions
conditions = [
    (df['Team_A_Division'] == df['Team_B_Division']),
    (df['Team_A_Division'].str.contains("AFC") & df['Team_B_Division'].str.contains("AFC")),
    (df['Team_A_Division'].str.contains("NFC") & df['Team_B_Division'].str.contains("NFC")),
    (df['Team_A_Division'].str.contains("AFC") & df['Team_B_Division'].str.contains("NFC")),
    (df['Team_A_Division'].str.contains("NFC") & df['Team_B_Division'].str.contains("AFC")),
    ]

# Outcome for team A
values = ["Division","Conference","Conference","No","No"]

# Create a new column and use np.select to assign values to it using our lists as arguments
df['Rivalry'] = np.select(conditions, values)


# %%
# Is the Stadium surface the same as Team_A home surface?
df["Same_surface"] = np.where(df["Surface"]==df["Team_A_Surface"],"Yes","No")


# Next part is the attendance/ capacity thing - will leave that for now
#%%
# # Attendance/ Capacity
# # I am only noticing this because I'm checking for extremes in attendance percentage
#
# # Fix Capacity a little
# # Capacity for Cowboys is still not a number
# df.loc[df.Capacity=='80,000–100,000','Capacity'] = '105,000'
#
# #Main Wiki table had wrong capacity of Baltimore stadium https://en.wikipedia.org/wiki/Chronology_of_home_stadiums_for_current_National_Football_League_teams
# #(based on this https://en.wikipedia.org/wiki/Memorial_Stadium_(Baltimore)#cite_note-38)
# df.loc[(df.Stadium == "Memorial Stadium ") & (df.Team_A == "Baltimore Ravens"),"Capacity"] = '65,248'
# df.loc[(df.Stadium == "Memorial Stadium ") & (df.Team_B == "Baltimore Ravens"),"Capacity"] = '65,248'
#
# # Wiki table also wrong about capacity for Busch Stadium II
# # https://en.wikipedia.org/wiki/Busch_Memorial_Stadium
# df.loc[(df.Stadium == "Busch Stadium (II) "),"Capacity"] = '60,000'
#
#
# # Convert to float
# df.Capacity = df.Capacity.str.replace(',','').astype(float)
#
# df["Attendance"] = df["attendance"]/df["Capacity"]*100
# df.loc[df.Stadium=="AT&T Stadium"][["Capacity","attendance"]]
# df.loc[df.Attendance == df.Attendance.max()][["Season","Week","Team_A","Team_B","Stadium","Team_A_Stadium","Team_B_Stadium","attendance","Capacity"]]
#
# df.sort_values(by="Attendance")[["Season","Week","Team_A","Team_B","Stadium","Capacity","Attendance","attendance"]].tail(200)
#
#
# Stad
# df.loc[df.Attendance > 100]['Attendance'].describe()
#
# %%
################
# Get the dyad #
################

df.columns


dyad = df[["Week","Season","Game_type","Team_A","Team_B","Stadium","Surface","attendance","Time_rest","Miles_traveled","Points_diff","Outcome","Yards_diff","Turnover_diff","Rivalry","Same_surface","Season_points_diff","Season_margins","Division_rank", "Field"]]


# %%
#export the dyad to csv
dyad.to_csv("../07_data_staged/dyadic_data.csv", index=False,encoding='utf-8-sig')
