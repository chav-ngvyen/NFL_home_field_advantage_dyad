#%%
import csv
import pandas as pd
import numpy as np

# %%
# Read-in the clean-ish df
data = pd.read_csv("../05_data_clean/games_historical_clean.csv")


data.head()
# %%
# This dataset is not dyadic. I need to make it dyadic
# Also need to find a way to calculate time rest and distance traveled


# %%
# First I'll attempt to make it dyadic
df = data[["Season","Week","Winner/tie","Loser/tie","Home_team","Stadium","lat","lon"]]

df.head()

df = df.rename(columns={"Winner/tie":"Team_A","Loser/tie":"Team_B"})
df = df.rename(columns={"Winner/tie":"Team_A","Loser/tie":"Team_B"})
