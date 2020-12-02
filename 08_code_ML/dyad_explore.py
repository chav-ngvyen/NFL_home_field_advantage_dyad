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

#%%
# Convert Time_rest to time delta
df["Time_rest"] = pd.to_timedelta(df["Time_rest"])

# Convert Time_rest to number of hours
df['Time_rest_hours'] = df['Time_rest'] / np.timedelta64(1, 'h')

# Convert to days
df['Time_rest_days'] = df['Time_rest_hours']/24
#%%

# Convert week to category
df["Week"] = df["Week"].astype("category")

# Order the Week category
list(df["Week"].unique())
df["Week"] = pd.Categorical(df['Week'], ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','WildCard','Division','ConfChamp','SuperBowl'])

# %%
# Attendance_pct
plot = (
    ggplot(df,aes(x="Attendance_pct")) +
        geom_histogram()
        )
plot
#%%
df.Time_rest_hours.max()


df.loc[df.Time_rest_hours==df.Time_rest_hours.max()]

#%%
plot2 = (
    ggplot(df,aes(x="Week",y="Time_rest_days",color="Outcome")) +
        geom_jitter() +
        theme(figure_size = (15,5))
        )
plot2

#%%
plot3 = (
    ggplot(df, aes(x="Time_rest_days", color="Outcome")) +
        geom_density()
)

plot3
#%%
plot4 = (
    ggplot(df,aes(x="Miles_traveled",y="Time_rest_days",color="Outcome")) +
        geom_point() +
        geom_abline()
)
plot4
# # %%
# # Read-in the clean-ish df
# df = pd.read_csv("../05_data_clean/df_team_stat.csv")
#
#
# # %%
# # Drop some columns
# df.columns
#
#
# df.drop(columns =['Day', 'Date', 'Time', 'Home_lat', 'Home_lon', 'Away_lat', 'Away_lon','lat', 'lon','Year'], inplace = True)
#
# #%%
# plot4 = (
#     ggplot(df, aes(x="Home_timerest",y="Away_timerest")) +
#         geom_point()
# )
#
# plot4
