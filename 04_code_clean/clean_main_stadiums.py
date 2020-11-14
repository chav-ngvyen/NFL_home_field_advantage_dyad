#%%
import csv
import pandas as pd
import math
import requests # For downloading the website
from bs4 import BeautifulSoup # For parsing the website
import numpy as np
# %%

# Read the scraped main stadiums table as pandas df

main_stadiums = pd.read_csv("../03_data_scrape/main_stadiums_raw.csv")

# Drop irrelevant rows
main_stadiums.drop(main_stadiums[main_stadiums["Stadium"].isin(["AFC ","AFC East ","Stadium (former names)","AFC North ","AFC South ","AFC West ","NFC ","NFC East ","NFC North ","NFC South ","NFC West "])].index, inplace=True)

# %%
# Read in stadium coordinates
main_stadiums_coord = pd.read_csv("../03_data_scrape/main_stadiums_coord_raw.csv")

# Drop rows with no lat & lon data:
main_stadiums_coord = main_stadiums_coord.dropna()

# %%
# Check the names & unique URLs
len(main_stadiums)
len(main_stadiums_coord)

main_stadiums.URL.nunique()
main_stadiums_coord.URL.nunique()

# %%
#Merge the 2 on URL
main_stadiums_merge = main_stadiums.merge(main_stadiums_coord, on = "URL", how = "left")

# Check the df after merge
len(main_stadiums_merge)
main_stadiums_merge.URL.nunique()

# Drop duplicates
main_stadiums_merge = main_stadiums_merge.drop_duplicates()

# %%
#Split the Years used column

main_stadiums_merge["Year_start"] = main_stadiums_merge["Years used"].str.split("–", expand=True)[0]

main_stadiums_merge["Year_end"] = main_stadiums_merge["Years used"].str.split("–", expand=True)[1]

# %%
# Export it

#main_stadiums_merge.to_csv("../05_data_clean/main_stadiums_merge.csv", index=False)


# %%
# See if a team goes back to a stadium
main_stadiums_merge["multi_start"] = main_stadiums_merge["Year_start"].str.split(" ",expand=False)
main_stadiums_merge["multi_end"] = main_stadiums_merge["Year_end"].str.split(" ",expand=False)

# %%
# Split the Year_start & Year_end columns into many columns
start = main_stadiums_merge["Year_start"].str.split(" ",expand=True)
start= start.add_prefix('start_')
end = main_stadiums_merge["Year_end"].str.split(" ",expand=True)
end = end.add_prefix('end_')
len(start)
len(end)
# %%
# Merge them back with each other
df = pd.concat([main_stadiums_merge,start,end], axis = 1)

df.head()
df[df["Years used"].str.contains("present")]

# %%
#Convert what can be converted to float
df[['start_0', 'start_1', 'start_2', 'start_3', 'end_0', 'end_1', 'end_2', 'end_3', 'end_4']] = df[['start_0', 'start_1', 'start_2', 'start_3', 'end_0', 'end_1', 'end_2','end_3', 'end_4']].apply(pd.to_numeric, errors='coerce')

df.head()
# %%

# Check the ends first
df[['end_0','end_1','end_2','end_3','end_4']].describe()
#There is one instance where end_4 = 1994. It's the Seahawks in 1994. Keep it.
df.loc[(df['end_4'] == 1994)]

# Only 1 instance where end_2 is 1937. This can be dropped
df.loc[(df['end_2'] == 1937)]
df.drop(df[df["end_2"] == 1937].index,inplace=True)

# Next, drop if BOTH end_1 and end_0 are less than 1992
df.loc[(df['end_1'] < 1992) & (df['end_0'] < 1992)]
df = df.drop(df[(df['end_0'] < 1992) & (df['end_1'] <1992)].index)

#Finally, drop where end_0 is less than 1992
df.loc[(df['end_0'] < 1992)]
df = df.drop(df[(df['end_0'] < 1992)].index)


# %%
df["Years used"].unique()

# Now I have to deal with the single years start

df[["start_0","start_1","start_2","start_3"]].describe()


# Find the rows where the start and end were both before 1992

df.loc[(df['start_0'] < 1992)][["end_0","end_1","end_2","end_3","end_4"]].describe()

# Drop where the start is before 1992, the end is empty, and it's "present" is not in Years used
df.loc[(df["start_0"]<1992) & (df["end_0"].isnull()) & (~df["Years used"].str.contains("present"))]
df = df.drop(df[(df["start_0"]<1992) & (df["end_0"].isnull()) & (~df["Years used"].str.contains("present"))].index)


# %%
df.reset_index(drop=True,inplace=True)

df = df.drop(columns=["multi_end","multi_start","start_0","start_1","start_2","start_3","end_0","end_1","end_2","end_3","end_4"])



# %%

df.to_csv("../05_data_clean/main_stadiums_merge.csv", index=False,encoding='utf-8-sig')

#%%

# Turf types
df.loc[(df["Surface"].str.contains("urf")), "Turf"] = "Turf"
df.loc[(df["Surface"].str.contains("rass")), "Turf"] = "Grass"
df.loc[(df["Surface"].str.contains("urf")) & (df["Surface"].str.contains("rass")), "Turf"] ="Both"
df.loc[df.Turf.isnull(), "Turf"] = "Turf"


#%%
df.Year_start.nunique()



# %%
# Clean year end


#Change present to 2020
df.loc[(df.Year_end == "present"),"Year_end"] = "2020"
df.loc[(df.Year_end == "present 1975"), "Year_end"] = "2020"
df.loc[(df.Year_end == "2019 1946"), "Year_end"] = "2019"
df.loc[(df.Year_end == "2019 1966"), "Year_end"] = "2019"

#Change where Year_end is NA to Year_start
df.loc[(df.Year_end.isna()), "Year_end"] = df["Year_start"]

# Packers weirdness
df.loc[(df.Year_end == "1994 (2"), "Year_end"] = "2 - 4 games per year"

# Husky Stadium - Seattle
df.loc[(df.Year_end == "2001 Three games in 1994"), "Year_end"] = "2001"

# Saints
df.loc[df.Stadium == "Mercedes-Benz Superdome ", "Year_start"] = "1975"

df.Year_end.unique()

# %%



# %%
df[["Year_start_num","Year_end_num"]] = df[["Year_start","Year_end"]].apply(pd.to_numeric, errors='coerce')
df[["Year_start_num","Year_end_num"]] = df[["Year_start_num","Year_end_num"]].fillna(0).astype(int)

df["Years"] = [list(range(i, j+1)) for i, j in df[["Year_start_num","Year_end_num"]].values]

# %%

#From Years get a list of relevant years to reshape
relevant_years = []
for row in df["Years"]:
    relevant = [i for i in row if i >= 1992]
    relevant_years.append(relevant)
df["Years_relevant"] = relevant_years




#%%
# Wide to long

lst_col = 'Years_relevant'
res = pd.DataFrame({
    col:np.repeat(df[col].values, df[lst_col].str.len())
    for col in df.columns.drop(lst_col)}
                   ).assign(**{lst_col:np.concatenate(df[lst_col].values)})[df.columns]
res.columns

# %%
# Manually change the turf
unique_surface = res.loc[res.Turf == "Both"]["Surface"].unique()
unique_surface

res.loc[(res["Surface"] == unique_surface[0]) & (res["Years_relevant"]<2006),"Turf"] = "Grass"
res.loc[(res["Surface"] == unique_surface[0]) & (res["Years_relevant"]>=2006),"Turf"] = "Turf"

res.loc[(res["Surface"] == unique_surface[1]) & (res["Years_relevant"]>1991),"Turf"] = "Grass"

res.loc[(res["Surface"] == unique_surface[2]) & (res["Years_relevant"]>=2003),"Turf"] = "Turf"
res.loc[(res["Surface"] == unique_surface[2]) & (res["Years_relevant"]<2003) & (res["Years_relevant"]>=2000),"Turf"] = "Grass"
res.loc[(res["Surface"] == unique_surface[2]) & (res["Years_relevant"]<=1999),"Turf"] = "Turf"

res.loc[(res["Surface"] == unique_surface[3]) & (res["Years_relevant"]>=2016),"Turf"] = "Grass"
res.loc[(res["Surface"] == unique_surface[3]) & (res["Years_relevant"]<=2002),"Turf"] = "Grass"
res.loc[(res["Surface"] == unique_surface[3]) & (res["Years_relevant"]>=2003) & (res["Years_relevant"]<=2015),"Turf"] = "Turf"

res.loc[(res["Surface"] == unique_surface[4]) & (res["Years_relevant"]>=2003),"Turf"]  = "Turf"
res.loc[(res["Surface"] == unique_surface[4]) & (res["Years_relevant"]<2003),"Turf"] = "Grass"

res.loc[(res["Surface"] == unique_surface[5]) & (res["Years_relevant"]>=1994),"Turf"] = "Grass"
res.loc[(res["Surface"] == unique_surface[5]) & (res["Years_relevant"]<1994),"Turf"] = "Turf"

#RealGrass is fucking turf
res.loc[(res["Surface"] == unique_surface[6]),"Turf"] = "Turf"

res.loc[(res["Surface"] == unique_surface[7]) & (res["Years_relevant"]>=2003),"Turf"] = "Turf"
res.loc[(res["Surface"] == unique_surface[7]) & (res["Years_relevant"]<2003) & (res["Years_relevant"]>=2000),"Turf"] = "Grass"
res.loc[(res["Surface"] == unique_surface[7]) & (res["Years_relevant"]<2000),"Turf"] = "Turf"

res.loc[(res["Surface"] == unique_surface[8]) & (res["Years_relevant"]>=1988),"Turf"] = "Grass"

res.loc[(res["Surface"] == unique_surface[9]) & (res["Years_relevant"]>=1979),"Turf"] = "Grass"

# %%
# export turf data to csv
turf = res[["Stadium","Surface","Turf"]].drop_duplicates()
turf.to_csv("../05_data_clean/turf.csv", index=False,encoding='utf-8-sig')


res.loc[(res.Team=="New Orleans Saints"),"Years_relevant"].unique()

# %%
res.to_csv("../05_data_clean/main_stadiums_long.csv", index=False,encoding='utf-8-sig')

# %%
#Next I'll need to think about how to merge the stadium  & turf to the teams

df.loc[df["Team"] == "New Orleans Saints"]

df["Years used"].unique()
