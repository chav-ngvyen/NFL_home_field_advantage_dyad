#%%
import csv
import pandas as pd
import numpy as np


# %%

# Read in historical attendance (from PFR)
attendance = pd.read_csv("../03_data_scrape/attendance_historical_raw.csv")

# %%
# Drop where Tm is null (because it's the season total)
attendance = attendance.dropna(subset=["Tm"])

# Drop Total, Home, Away
attendance = attendance.drop(columns = ["Total","Home","Away"])

# Rename Team to Home_team
attendance = attendance.rename(columns={"Tm":"Home_team"})
# %%
# Sort by Season
attendance = attendance.sort_values(by="Season")
attendance = attendance.reset_index(drop=True)

# %%
# Reshape wide to long
attendance = attendance.melt(id_vars=["Home_team","Season"])

# %%
# Only the 1993 season had Week 18, so drop it for the other seasons
attendance = attendance.dropna(subset=["value"])


# %%
# Get Week number
attendance["Week"] = attendance.variable.str.split(" ",expand = True)[1]


#%%
# Sort by Season & Week
attendance = attendance.sort_values(by=["Season","Week"])
attendance = attendance.reset_index(drop=True)

# Drop variable
attendance = attendance.drop(columns="variable")

# Rename value "attendance"
attendance = attendance.rename(columns={"value":"attendance"})




# %%
# Export to csv
attendance.to_csv("../05_data_clean/regular_attendance_clean.csv",index=False,encoding='utf-8-sig')
