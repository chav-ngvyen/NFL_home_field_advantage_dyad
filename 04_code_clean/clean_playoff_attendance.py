#%%
import csv
import pandas as pd
import numpy as np

# %%

# Read in playoff attendace scraped data
playoff = pd.read_csv("../03_data_scrape/playoff_attendance.csv")

playoff

# Drop unneccessary columns
playoff = playoff.drop(columns = ['kickoff(et / utc–5)', 'tv','kickoff(et / utc−5)', 'unnamed: 6_level_0',
       'kickoff(et / utc-5)', 'score[2]', 'score[1]', 'kickoff(est / utc–5)',
       'kickoff(est / utc−5)', 'kickoff(et/utc–5)', 'tv[2]', 'score','unnamed: 7_level_0'])

# Clean up Game attendance column
playoff.attendance = playoff.attendance.str.split(": ", expand = True)[1]

# Remove the citations in square brackets, remove commas, convert to float
playoff.attendance = playoff.attendance.str.split("[", expand=True)[0]
playoff.attendance = playoff.attendance.str.replace(',', '').astype(float)

#%%
# Split the date column
playoff["Date"] = playoff.date.str.split(", ", expand=True)[0]
playoff["Year"] = playoff.date.str.split(", ", expand=True)[1]

# %%
# Create empty season column
playoff["Season"] = ""

# If the playoff game takes place in December, then Season = Year
playoff.loc[playoff.Date.str.contains("December"), "Season"] = playoff["Year"].astype(float)
# If not then "season" is the previous season
playoff.loc[playoff.Date.str.contains("December")==False, "Season"] = playoff["Year"].astype(float) - 1

# %%
#Rename
playoff.Season.unique()

playoff = playoff.rename(columns={"home team":"Home_team"})


# %%
# Replace the Home_team fo the superbowl with None

#playoff.loc[playoff.groupby("Season")["Home_team"].tail(1).index,"Home_team"] = "None"


# Drop more irrelevant columns
playoff = playoff.drop(columns=["date", "Year"])

# %%
# Export to csv
playoff.to_csv("../05_data_clean/playoff_attendance_clean.csv",index=False,encoding='utf-8-sig')
