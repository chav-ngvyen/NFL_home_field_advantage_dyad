################
# Dependencies #
################
# Data Management/Investigation
import pandas as pd
from pandas.api.types import CategoricalDtype # Ordering categories
import numpy as np
import missingno as miss

# Plotting libraries
from plotnine import *
import matplotlib.pyplot as plt

# For pre-processing data
from sklearn import preprocessing as pp
from sklearn.compose import ColumnTransformer

# For splits and CV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold # Cross validation
from sklearn.model_selection import cross_validate # Cross validation
from sklearn.model_selection import GridSearchCV # Cross validation + param. tuning.

# Machine learning methods
from sklearn.naive_bayes import GaussianNB as NB
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.tree import DecisionTreeClassifier as DT
from sklearn.tree import DecisionTreeRegressor as DT_reg
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import tree # For plotting the decision tree rules

# For evaluating our model's performance
import sklearn.metrics as m

# Pipeline to combine modeling elements
from sklearn.pipeline import Pipeline

# Misc
import warnings
warnings.filterwarnings("ignore")



# %%

# Import the dyadic data
df = pd.read_csv("../07_data_staged/dyadic_data.csv")

df.columns
# %%

# Convert Time_rest to time delta
df["Time_rest"] = pd.to_timedelta(df["Time_rest"])

# Convert Time_rest to number of hours
df['Time_rest_hours'] = df['Time_rest'] / np.timedelta64(1, 'h')

# Convert number of hours to days
df['Time_rest_days'] = df['Time_rest_hours'] / 24


# %%

miss.matrix(df)
#%%
#Win
df["Win"] = ""
df.loc[df.Game_pts_diff < 0, "Win"] = 1
df.loc[df.Game_pts_diff > 0, "Win"] = 0

# %%
# Convert categorial variables to categories
for col in ['Week','Game_type','Surface','Game_outcome','Rivalry','Same_surface','Field','Win']: df[col] = df[col].astype("category")

df.dtypes
# %%
# Split

y = df[['Win']]
X = df.drop(columns=['Win'])
train_X, test_X, train_y, test_y = train_test_split(X,y,test_size = .25,random_state=123)

# %%

# Plot the continuous Variables
d_int = train_X.select_dtypes(include=["int"]).melt()
(
    ggplot(d_int,aes(x="value")) +
    geom_histogram(bins=25) +
    facet_wrap("variable",scales='free') +
    theme(figure_size=(10,3),
          subplots_adjust={'wspace':0.25})
)

# %%

d_float = train_X.select_dtypes(include=["float"]).melt()
(
    ggplot(d_float,aes(x="value")) +
    geom_histogram(bins=25) +
    facet_wrap("variable",scales='free') +
    theme(figure_size=(10,3),
          subplots_adjust={'wspace':0.25})
)
# %%
# Explore game specific stats
#Only usable ones are number of turnovers, number of yards, Attendance, Attendance_pct, Capacity, Miles traveled, time rest in hours
d = train_X.copy()
d['ln_attendance'] = np.log(d['Attendance_pct'])



d.ln_miles

(
    ggplot(d,aes(x="ln_attendance")) +
    geom_histogram() +
    theme(figure_size=(10,3))
    )
#%%

# Set time rest for Week 1 as the longest time a team has to rest during the regular season
time_rest_max = df.groupby(["Season","Game_type"])["Time_rest"].max().reset_index(name="Time_rest_max")
time_rest_max = time_rest_max.loc[time_rest_max.Game_type=="Regular"]

time_rest_max.drop(columns="Game_type", inplace=True)

time_rest_max
# %%

# Merge to df
df = pd.merge(df,time_rest_max, on=["Season"], how = "left")

# Fill NA
df["Time_rest"] = df["Time_rest"].fillna(df["Time_rest_max"])

df.Time_rest
# %%
# Convert Time_rest to number of hours
df['Time_rest_hours'] = df['Time_rest'] / np.timedelta64(1, 'h')

# Convert number of hours to days
df['Time_rest_days'] = df['Time_rest_hours'] / 24

# Drop Time_rest_max
df.drop(columns = "Time_rest_max", inplace = True)

#%%
df.columns

# %%
#########################
# High level processing #
#########################

# Rivalry
# Impose an order. 0 is no rivalry (meaning an AFC team is playing an NFC team), 1 is conference, and 2 is Division
rival = ['No','Conference','Division']
rival_types = CategoricalDtype(categories=rival, ordered=True)
df['Rivalry'] = df['Rivalry'].astype(rival_types)
df['Rivalry'] = df['Rivalry'].cat.codes

df.Surface
# %%
# Grass
df["Grass"] = 1*(df["Surface"] == "Grass")

# Home
df["Home"] = 1*(df["Field"] == "Home")

# Same surface as the team's home field
df["Same_surface"] = 1*(df["Same_surface"] == "Yes")

# %%
# Regular season vs playoff
df["Regular"] = 1*(df["Game_type"] == "Regular")

# %%
# Split again

# Split

y = df[['Win']]
X = df[["Time_rest_hours","Miles_traveled","Attendance","Capacity","Grass","Same_surface","Home", "Regular"]]
train_X, test_X, train_y, test_y = train_test_split(X,y,test_size = .25,random_state=123)

# %%

# Set the folds index to ensure comparable samples
fold_generator = KFold(n_splits=10, shuffle=True,random_state=1234)

pipe = Pipeline(steps=[('pre_process', pp.MinMaxScaler()),('model',None)])

search_space = [

    # NaiveBayes
    {'model': [NB()]},

    # KNN with K tuning param
    {'model' : [KNN()],
     'model__n_neighbors':[5,10,25]},

    # # Decision Tree with the Max Depth Param
    {'model': [DT()],
     'model__max_depth':[2,3,4]},

    # #Random forest with the N Estimators tuning param
    {'model' : [RF()],
    'model__max_depth':[2,3,4],
    'model__n_estimators':[100,200,300]}

]
# %%



search = GridSearchCV(pipe, search_space,
                      cv = fold_generator,
                      scoring='roc_auc',
                      n_jobs=4)

# %%
search.fit(train_X,train_y)
