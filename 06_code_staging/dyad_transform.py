#%%
import csv
import pandas as pd
import numpy as np

# %%
# Read-in the clean-ish df
data = pd.read_csv("../05_data_clean/games_historical_clean.csv")


# Merge division data in
div = pd.read_csv("../03_data_scrape/divisions_ranking.csv")
div["Team"]
