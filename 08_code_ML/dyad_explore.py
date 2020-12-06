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
df.Time_rest.describe()

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
division_count_season = df.groupby(["Season","Team_A_Division"])["Team_A"].nunique().reset_index()

#%%
team_in_season = df.groupby(["Season","Team_A_Division","Team_A"],as_index=False)["Team_A"].agg(['nunique']).reset_index()

div_count= team_in_season.groupby(["Season","Team_A_Division"]).size().reset_index()
div_team_count = team_in_season.merge(div_count, on=["Season","Team_A_Division"], how = "left")
div_team_count.rename(columns={0:"teams_in_div"},inplace=True)

# %%

# Fake scale to use for scale_color_manual
color_values = list(np.repeat("black",div_team_count.Team_A.nunique()
))
# %%
plot_div_team_count = (
    ggplot(div_team_count, aes(x="Season", color ="Team_A")) +
        geom_bar(aes(x="Season",fill="Team_A_Division"),position="stack", size = 0.5) +
        scale_color_manual(guide=False, values=color_values, size =0.5) +
        scale_x_continuous(breaks = range(1992,2020)) +
        ggtitle("Organization of the NFL through the years") +
        ylab("Number of teams") +
        labs(fill = "Divisions") +
        theme_classic() +
        theme(axis_text_x=element_text(rotation=90, hjust=1))
        )
plot_div_team_count

plot_div_team_count.save("../09_figures/plot_div_team_count.png")

#%%
df["City"] = df.Location.str.split(" url:",expand=True)[0]
df["City"]= df.City.str.split(", ",expand=True)[0]
city = df.groupby(["Season","City"])["Stadium"].nunique().reset_index()

# %%
test.City.nunique()

plot_city = (
    ggplot(city, aes(x="Season",y="City",fill="City",color="Season")) +
    geom_tile(color="black") +
    scale_fill_discrete(guide=False) +
    scale_x_continuous(breaks = range(1992,2020)) +
    scale_color_continuous(guide=False) +
    ggtitle("NFL game location by season") +
    theme_classic() +
    theme(figure_size=(10,8)) +
    theme(axis_text_x=element_text(rotation=90, hjust=1))
)
plot_city

plot_city.save("../09_figures/plot_city.png")
# %%
# Lambeau plot

lambeau = df[df.Stadium == "Lambeau Field "]

lambeau.loc[(lambeau.Season == 2011), "Capacity"] = 72928

lambeau_test = lambeau[["Season","Capacity","attendance"]]

lambeau_test = lambeau_test.groupby("Season").agg({"attendance":["mean","max","min"],"Capacity":"mean"}).reset_index()

lambeau_test.columns = ['_'.join(col).strip() for col in lambeau_test.columns.values]

lambeau_melt = lambeau_test.melt(id_vars=["Season_","Capacity_mean"])

#%%
plot_lambeau = (
    ggplot(lambeau_melt, aes(x="Season_",y="Capacity_mean")) +
        geom_bar(stat="identity",position="dodge",fill="green",alpha=0.1,show_legend=False) +
        coord_cartesian(ylim=(55000,82000)) +
        geom_point(aes(group="Season_",y="value", color= "variable"), size = 3) +
        scale_color_manual(values=["blue","yellow","red"], name="Attendance record", labels=["Season max","Season average","Season mean"])+
        scale_shape_manual(values=[6,0,2]) +
        ylab("Maximum Seasing Capacity") +
        xlab("Season") +
        scale_x_continuous(breaks = range(1992,2020)) +
        scale_y_continuous(breaks = [55000,60000,65000,70000,75000,80000]) +
        ggtitle("Lambeau Field: Seating capacity and attendnace records") +
        theme_classic() +
        theme(axis_text_x=element_text(rotation=90, hjust=1))

        )

plot_lambeau

plot_lambeau.save("../09_figures/plot_lambeau.png")



#%%

df.Time_rest_days.describe()

#%%
plot_timerest = (
    ggplot(df.loc[(df.Outcome.isin(["Win","Lose"]))&(df.Game_type=="Regular")], aes(x="Outcome",y ="Time_rest_days",fill="Outcome")) +
        #geom_jitter(aes(color="Outcome")) +
        geom_boxplot(notch=True)+
        #stat_summary(aes(group=1),fun_y = np.mean, geom="point",color="Black") +
        #stat_summary(aes(group=1),fun_y = np.mean, geom="line",color="Black") +
        ylab("Days since previous game") +
        ggtitle("NFL regular season games") +
        theme_classic()
    )
plot_timerest

plot_timerest.save("../09_figures/plot_timerest_wrong.png")
# %%
plot_traveled = (
    ggplot(df.loc[df.Outcome.isin(["Win","Lose"])],aes(x="Outcome",y ="Miles_traveled",fill="Outcome")) +
        geom_boxplot(notch=True) +
        ylab("Miles traveled") +
        ggtitle("Game outcome & Miles traveled") +
        scale_y_continuous(breaks=[1000,2000,3000,4000,5000,6000]) +
        theme_classic()
)
plot_traveled
plot_traveled.save("../09_figures/plot_traveled.png")

# %%
# Attendance_pct
plot = (
    ggplot(df,aes(x="Attendance_pct")) +
        geom_density()
        )
plot

# %%


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
        geom_point()
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
df.Season.nunique()
example = df.loc[(df.Week=="10") & (df.Season==2018)]

show = example[["Season","Week","Team_A","Team_B","Outcome","Miles_traveled","Time_rest_days","Capacity","attendance","Surface","Same_surface","Rivalry"]].head(10)
show.round(2)
