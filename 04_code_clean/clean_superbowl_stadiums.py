#%%
import csv
import pandas as pd
import math
import requests # For downloading the website
from bs4 import BeautifulSoup # For parsing the website
import numpy as np

# %%
#################
# Stadium table #
#################

# Read the scraped superbowl stadiums table as pandas df
superbowl_stadiums = pd.read_csv("../03_data_scrape/superbowl_stadiums_raw.csv")

#%%
# Repeat the exact same steps in the scraping code to turn items in "Year hosted" into int to concat later
#From Years get a list of relevant years to reshape
relevant_years = []
for row in superbowl_stadiums["Years hosted"]:
    # Split the string list of years into separate years
    row = row.split(", ")
    # Convert each year to int
    row = [int(year) for year in row]
    # Keep years after 1992
    row = [i for i in row if i >= 1992]

    relevant_years.append(row)
superbowl_stadiums["Years_relevant"] = relevant_years
#%%
# If Years_relevant is an empty list, then change to none
for i in range(0, len(superbowl_stadiums)):
    if (len(superbowl_stadiums["Years_relevant"][i]) == 0):
        superbowl_stadiums["Years_relevant"][i] = None


#%%
# Drop where Years_relevant is NA
superbowl_stadiums = superbowl_stadiums.dropna().reset_index(drop=True)

# %%
# Reshape superbowl_stadiums from wide to long
lst_col = 'Years_relevant'

long = pd.DataFrame({
    col:np.repeat(superbowl_stadiums[col].values, superbowl_stadiums[lst_col].str.len())
    for col in superbowl_stadiums.columns.drop(lst_col)}
                   ).assign(**{lst_col:np.concatenate(superbowl_stadiums[lst_col].values)})[superbowl_stadiums.columns]
# %%
####################
# Coordinate table #
####################

# Read the scraped superbowl stadiums coord table as pandas df
superbowl_stadiums_coord = pd.read_csv("../03_data_scrape/superbowl_stadiums_coord_raw.csv")

# %%
###############################
# Clean up the surface column #
###############################


superbowl_stadiums_coord.surface = superbowl_stadiums_coord.surface.str.split("Surface", expand = True)[1]

#%%
# Sort into Turf or Grass
superbowl_stadiums_coord.loc[(superbowl_stadiums_coord["surface"].str.contains("urf")), "Turf"] = "Turf"
superbowl_stadiums_coord.loc[(superbowl_stadiums_coord["surface"].str.contains("Helix")), "Turf"] = "Turf"

superbowl_stadiums_coord.loc[(superbowl_stadiums_coord["surface"].str.contains("rass")), "Turf"] = "Grass"
superbowl_stadiums_coord.loc[(superbowl_stadiums_coord["surface"].str.contains("Bermuda")), "Turf"] = "Grass"

superbowl_stadiums_coord.loc[(superbowl_stadiums_coord["surface"].str.contains("urf")) & (superbowl_stadiums_coord["surface"].str.contains("rass")), "Turf"] ="Both"

#Superdome has Turf
superbowl_stadiums_coord.loc[(superbowl_stadiums_coord["name"] =="Mercedes-Benz Superdome", "Turf" )] = "Turf"

superbowl_stadiums_coord.Turf.unique()

# Drop the surface column
superbowl_stadiums_coord =  superbowl_stadiums_coord.drop(columns=["surface"])

superbowl_stadiums
# %%
################################
# Clean up the capacity column #
################################

# This I'll just have to do by hand
superbowl_stadiums_coord["capacity"] = superbowl_stadiums_coord.capacity.str.split("Capacity",expand = True)[1]

superbowl_stadiums_coord.capacity.str.split("football")

# Putting in 2 numbers - football and expandable (if applicable). Will use judgement to pick later

superbowl_stadiums_coord["Capacity"] = ["73,208 or 76,468", "64,767 or 75,000", "92,542", "70,561", "65,618 or 75,000", "63,400 or 72,200","71,228","72,220","64,121","53,599 or 73,379","67,814 or 82,000","65,000 or 70,000","80,000 or 105,000","67,000 or 70,000","82,500","68,500 or 75,000","66,860 or 73,000","71,000 or 75,000","100,240"]

# Drop lowercase capacity

superbowl_stadiums_coord= superbowl_stadiums_coord.drop(columns = "capacity")

# %%
######################################
# Merge stadium with the coordinates #
######################################
long = long.merge(superbowl_stadiums_coord, on = "URL", how = "left")

# Drop the irrelevant columns
long = long.drop(columns = ["Stadium","Location","No. hosted", "Years hosted"])

# Rename
long = long.rename(columns = {"Years_relevant": "Year", "name":"Stadium"})

# Season is Year-1
long["Season"] = long["Year"] - 1

# Sort
long = long.sort_values(by="Season").reset_index(drop=True)

# Drop anything after 2021
long = long.loc[long["Season"] <=2020]

# Also drop Year == 1992 because it's the 1991 season
long = long.loc[long["Season"] > 1991]

# %%
# Attendance data
sb_attendance = pd.read_csv("../05_data_clean/sb_attendance.csv")

# %%
# Merge long and sb_attendance
long = long.merge(sb_attendance, on="Season", how = "left")

#%%
# Drop the 2 URL columns
long = long.drop(columns=["URL_x","URL_y"])


# %%
#############################
# More clean-up on capacity #
#############################

#Split the Capacity column into 2
long["Capacity_low"] = long.Capacity.str.split("or",expand=True)[0]
long["Capacity_high"] = long.Capacity.str.split("or",expand=True)[1]

# If Capacity_high is empty then there's one capacity
long.loc[long["Capacity_high"].isnull(), "Capacity_high"] = long["Capacity_low"]

# %%

# Take the thousandth comma separator out and convert to float
for i in ["Attendance","Capacity_low","Capacity_high"]:
    long[f'{i}'] = long[f'{i}'].str.replace(",","").astype(float)

# %%
# If attendance > capacity low then capacity is capacity high.
long.loc[long["Attendance"] >= long["Capacity_low"], "Capacity"] = long["Capacity_high"]
long.loc[long["Attendance"] < long["Capacity_low"], "Capacity"] = long["Capacity_low"]


#%%
#Drop irrelevant columns
long =long.drop(columns=["Capacity_low","Capacity_high"])
long = long.drop(columns="Year")
# Create Week = SuperBowl column for easy merging
long["Week"] = "SuperBowl"

# %%
# To csv
long.to_csv("../05_data_clean/superbowl_stadiums.csv", index=False,encoding='utf-8-sig')
