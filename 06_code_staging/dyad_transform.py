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
# %%

# Field is "Home" for all the Team_A in home_away except for the SuperBowl and the international games
home_away["Field"] = "Home"
home_away.loc[home_away.Week=="SuperBowl","Field"] = "Neutral"
home_away.loc[home_away.Stadium.isin(['Tottenham Hotspur Stadium','Estadio Azteca','Wembley Stadium','Twickenham Stadium']), "Field"] = "Neutral"

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

# Field is "Away" for all the Team_A in away_home except for the SuperBowl & the international games
away_home["Field"] = "Away"
away_home.loc[away_home.Week == "SuperBowl","Field"] = "Neutral"
away_home.loc[away_home.Stadium.isin(['Tottenham Hotspur Stadium','Estadio Azteca','Wembley Stadium','Twickenham Stadium']), "Field"] = "Neutral"
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

# %%
# Reset index
df.reset_index(drop=True, inplace=True)

df.head()

# Rename Team_A and Team_B columns
df.rename(columns={'Team_A_team':'Team_A','Team_B_team':'Team_B'}, inplace=True)

# %%
# Time rest between games

df["datetime"] = pd.to_datetime(df["datetime"])
df["Time_rest"] = df.groupby(["Season","Team_A"])["datetime"].diff()

df["Time_rest"].describe()

# %%

# Points differential
df["Game_pts_diff"] = df["Team_A_Pts"] - df["Team_B_Pts"]
#%%

# Win/Loss

# Conditions
conditions = [
    (df["Game_pts_diff"] < 0),
    (df["Game_pts_diff"] > 0),
    (df["Game_pts_diff"] == 0)
    ]

# Outcome for team A
values = ["Lose","Win","Tie"]

# create a new column and use np.select to assign values to it using our lists as arguments
df['Game_outcome'] = np.select(conditions, values)




# %%

# Yards differential
df["Game_yards_diff"] = df["Team_A_Yds"] - df["Team_B_Yds"]

# Turnover differential
df['Game_TO_diff'] = df["Team_A_TO"] - df["Team_B_TO"]

# %%
# Game yards
df.rename(columns={'Team_A_Yds':'Game_yds'}, inplace=True)

# Game TO
df.rename(columns={'Team_A_TO':'Game_TO'}, inplace=True)


# %%
# Season points diff
df.rename(columns={'Team_A_PD':'Season_pts_diff'}, inplace=True)

# Season margins of victory
df.rename(columns={'Team_A_MoV':'Season_victory_margin'}, inplace=True)

# Season Win-Loss percent
df.rename(columns={'Team_A_W-L%':'Season_WL_pct'}, inplace=True)

# Season Strength of schedule
df.rename(columns={'Team_A_SoS':'Season_SoS'}, inplace=True)

# Season Offense
df.rename(columns={'Team_A_OSRS':'Season_offense'}, inplace=True)

# Season Defense
df.rename(columns={'Team_A_DSRS':'Season_defense'}, inplace=True)


df.columns


# %%
# Miles traveled
df.rename(columns={'Team_A_travel':'Miles_traveled'}, inplace=True)

# Time rest
df.rename(columns={'Team_A_timerest':'Time_rest'}, inplace=True)


#%%
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

# %%
# Attendance/ Capacity

df.rename(columns={'attendance':'Attendance'}, inplace=True)

df["Attendance_pct"] = df["Attendance"]/df["Capacity"]*100
df.Attendance_pct.describe()


# %%
################
# Get the dyad #
################

df.columns


dyad = df[["Week","Season","Game_type","Team_A","Team_B","Game_TO","Game_yds","Game_pts_diff","Game_yards_diff","Game_TO_diff","Game_outcome","Time_rest","Miles_traveled","Field","Stadium","Location","Surface","Attendance","Capacity","Attendance_pct","Team_A_Division","Division_rank","Rivalry","Same_surface","Season_WL_pct","Season_pts_diff","Season_victory_margin", "Season_SoS", "Season_offense", "Season_defense"]]


# %%
#export the dyad to csv
dyad.to_csv("../07_data_staged/dyadic_data.csv", index=False,encoding='utf-8-sig')
