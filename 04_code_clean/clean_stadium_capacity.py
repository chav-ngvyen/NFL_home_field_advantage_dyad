#%%
import csv
import pandas as pd
import math
import requests # For downloading the website
from bs4 import BeautifulSoup # For parsing the website
import numpy as np
#%%
# Import the first file
df = pd.read_csv('../03_data_scrape/stadium_capacity.csv')

# Year_start and Year_end (similar to clean_main_stadiums)
df['Year_start'] = df['Years'].str.split("–",expand=True)[0]
df['Year_end'] = df['Years'].str.split("–",expand=True)[1]


#%%
df.loc[df.URL == "https://en.wikipedia.org/wiki/Lambeau_Field"]


#%%


df.Year_end.unique()

# Replace present with 2019
df.loc[df.Year_end=="present","Year_end"] = "2020"
# If Year end is still empty then the end year was the start year
df.loc[df.Year_end.isnull(),"Year_end"] = df["Year_start"]

# Convert to number
df[["Year_start_num","Year_end_num"]] = df[["Year_start","Year_end"]].apply(pd.to_numeric, errors='coerce')

# Generate a list of all the years when the Capacity was correct
df["Years_list"] = [list(range(i, j+1)) for i, j in df[["Year_start_num","Year_end_num"]].values]

#From Years_list get a list of relevant years to reshape
relevant_years = []
for row in df["Years_list"]:
    relevant = [i for i in row if i >= 1992]
    relevant_years.append(relevant)

df["Years_relevant"] = relevant_years

# Drop rows where the Years_relevant list is empty (capacity before 1992)
df = df[df.astype(str)['Years_relevant'] != '[]']


# %%
#Convert from Wide to Long
lst_col = 'Years_relevant'
res = pd.DataFrame({
    col:np.repeat(df[col].values, df[lst_col].str.len())
    for col in df.columns.drop(lst_col)}
                   ).assign(**{lst_col:np.concatenate(df[lst_col].values)})[df.columns]
# %%
# Clean it up

# Damn it Saints
res.loc[res.Capacity=="73,208 (expandable to 76,468)", "Capacity"] ="76468"
# You too, Packers
res.loc[res.Capacity=="65,290/66,110", "Capacity"] ="66110"
res = res[["Years_relevant","Capacity","URL"]]
res.URL.nunique()

#%%
#Import the other file in
dat = pd.read_csv('../03_data_scrape/stadium_capacity_infocard.csv')

# Group by
dat = dat.groupby(["URL","Capacity"]).sum().reset_index()
# Count number of rows for each stadium
count = dat.groupby("URL").count().reset_index()
# Create a fake column to merge
count['Count'] = count["Years"]
# Merge but only keep the fake column from count
dat = pd.merge(dat,count[["URL","Count"]],on="URL",how="left")
#%%

dat['Count'].unique()
dat.dtypes
dat.reset_index(drop=True, inplace=True)

#Year_start and Year_end
dat['Year_start'] = dat['Years'].str.split("–",expand=True)[0]
dat['Year_end'] = dat['Years'].str.split("–",expand=True)[1]


# Replace present with 2019
dat.loc[dat.Year_end=="present","Year_end"] = "2020"
#If Year_end is null then the capacity was good for 1 year
dat.loc[dat.Year_end.isnull(),"Year_end"] = dat["Year_start"]

#%%
# Convert to number
#dat[["Year_start_num","Year_end_num"]] = dat[["Year_start","Year_end"]].apply(pd.to_numeric, errors='coerce')

# Look at stadium with years/capcity
has_year = dat.loc[(dat.Years!=0)].copy(deep=True)


# Generate a list of all the years when the Capacity was correct
has_year[["Year_start_num","Year_end_num"]] = has_year[["Year_start","Year_end"]].apply(pd.to_numeric, errors='coerce')

has_year["Years_list"] = [list(range(i, j+1)) for i, j in has_year[["Year_start_num","Year_end_num"]].values]


#From Years_list get a list of relevant years to reshape
relevant_years = []
for row in has_year["Years_list"]:
    relevant = [i for i in row if i >= 1992]
    relevant_years.append(relevant)

has_year["Years_relevant"] = relevant_years


# %%
# Wide to long

lst_col = 'Years_relevant'
res2 = pd.DataFrame({
    col:np.repeat(has_year[col].values, has_year[lst_col].str.len())
    for col in has_year.columns.drop(lst_col)}
                   ).assign(**{lst_col:np.concatenate(has_year[lst_col].values)})[has_year.columns]

res2 = res2[["URL","Capacity","Years_relevant"]]


# %%
# Concat
df = pd.concat([res,res2]).reset_index(drop=True)

# Check for duplicates
df.loc[df.duplicated(subset=["URL","Years_relevant"],keep = 'first')]

df.loc[df.duplicated(subset=["URL","Years_relevant"],keep = 'last')]

# Drop the first dup (first half of the year)
df = df.drop_duplicates(subset=["URL","Years_relevant"],keep = 'last')

# Out of the 62 stadiums, I have 41 with Capacity-Year. This is an improvement
df.URL.nunique()

# %%
# Export
df.to_csv("../05_data_clean/stadium_capacity_year.csv", index=False,encoding='utf-8-sig')

# %%

#Check for missingness
test = df.groupby(["URL"])["Years_relevant"].apply(list).reset_index()

test.loc[:, 'First'] = test.Years_relevant.map(lambda x: x[0])
test.loc[:, 'Last'] = test.Years_relevant.map(lambda x: x[-1])
test.URL.unique()

print(test.loc[test.URL == "https://en.wikipedia.org/wiki/Memorial_Stadium_(Champaign)"]["Years_relevant"])



#test.Years_relevant[0][-1]




#%%
# Now I will merge this to main_stadiums_long
dat = pd.read_csv("../05_data_clean/main_stadiums_long.csv")
# %%

dat.duplicated(subset=["Years","Stadium","Capacity"])



#%%
# Merge
m = dat.merge(df, left_on = ["URL","Years_relevant"],right_on = ["URL","Years_relevant"], how = "left", indicator=True)
m.Team.nunique()


# %%

m = m.sort_values(by=["Stadium","Years_relevant"])

#%%
# Drop duplicates
m.drop_duplicates(subset=["Team","Stadium","Years_relevant","Capacity_x"], inplace = True)

m.Team.nunique()





# %%
m.loc[m.Capacity_x.isnull()]


# %%
# Capacity_y is Capacity with year
m["Capacity"] = m["Capacity_y"].fillna(m["Capacity_x"])

m = m.drop(columns=["Capacity_x","Capacity_y","_merge"])


m.Team.nunique()

# %%
# All the duplicates are Jets & Giants (since *literally* forever) and Rams & Chargers at SoFi for the 2020 season onwards.

m.columns

# %%



m.Stadium = m.Stadium.str.rstrip()


# %%
# Export to csv
m.to_csv("../05_data_clean/main_stadiums_long_capacity_year.csv", index=False,encoding='utf-8-sig')
