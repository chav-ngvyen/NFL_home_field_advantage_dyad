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
import seaborn as sns
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
#Custom colors
nfl_red = "#d50a0a"
nfl_blue = "#013369"

#############
# Run these #
#############
df.Time_rest.describe()

# Convert Time_rest to time delta
df["Time_rest"] = pd.to_timedelta(df["Time_rest"])

# Convert Time_rest to number of hours
df['Time_rest_hours'] = df['Time_rest'] / np.timedelta64(1, 'h')

# Convert to days
df['Time_rest_days'] = df['Time_rest_hours']/24

# %%
#Drop Tie
df = df[df.Game_pts_diff!=0]


#Win
df["Win"] = 1*(df.Game_pts_diff > 0)



#%%

# Convert week to category
df["Week"] = df["Week"].astype("category")

# Order the Week category
list(df["Week"].unique())
df["Week"] = pd.Categorical(df['Week'], ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','WildCard','Division','ConfChamp','SuperBowl'])


# %%
# Grass
df["Grass"] = 1*(df["Surface"] == "Grass")

# Home
df["Home"] = 1*(df["Field"] == "Home")

# Same surface as the team's home field
df["Same_surface"] = 1*(df["Same_surface"] == "Yes")

# Regular season vs playoff
df["Regular"] = 1*(df["Game_type"] == "Regular")

#%%

# Time rest
# Set time rest for Week 1 as the longest time a team has to rest during the regular season
time_rest_max = df.groupby(["Season","Game_type"])["Time_rest"].max().reset_index(name="Time_rest_max")
time_rest_max = time_rest_max.loc[time_rest_max.Game_type=="Regular"]
time_rest_max.drop(columns="Game_type", inplace=True)

# Merge to df
df = pd.merge(df,time_rest_max, on=["Season"], how = "left")

# Fill NA
df["Time_rest"] = df["Time_rest"].fillna(df["Time_rest_max"])

# Convert Time_rest to number of hours
df['Time_rest_hours'] = df['Time_rest'] / np.timedelta64(1, 'h')

# Convert number of hours to days
df['Time_rest_days'] = df['Time_rest_hours'] / 24

# Drop Time_rest_max
df.drop(columns = "Time_rest_max", inplace = True)


#%%
# Rivalry
# Impose an order. 0 is no rivalry (meaning an AFC team is playing an NFC team), 1 is conference, and 2 is Division
rival = ['No','Conference','Division']
rival_types = CategoricalDtype(categories=rival, ordered=True)
df['Rivalry'] = df['Rivalry'].astype(rival_types)
df['Rivalry'] = df['Rivalry'].cat.codes

#%%
##################
# Split the data #
##################
d = df[["Win","Rivalry","Time_rest_days","Capacity","Attendance_pct","Attendance","Miles_traveled","Time_diff","Grass","Same_surface","Week","Season","Regular","Season_offense","Season_defense"]]


d = d.dropna()

y = d[['Win']]

X = d[["Rivalry","Time_rest_days","Capacity","Attendance_pct","Miles_traveled","Time_diff","Grass","Same_surface","Week","Season","Regular","Season_offense","Season_defense"]]


train_X, test_X, train_y, test_y = train_test_split(X,y,test_size = .25,random_state=123)

#%%
train_X.dtypes

#%%
###########
# Explore #
###########

d = train_X.select_dtypes(include=["int","float"]).drop(columns=["Season","Season_defense","Season_offense"]).melt()


(
    ggplot(d,aes(x="value")) +
    geom_histogram(bins=25) +
    facet_wrap("variable",scales='free') +
    theme(figure_size=(10,3),
          subplots_adjust={'wspace':0.25})
)

# %%

plot_offense = (
    ggplot(train_X,aes(x="Season_offense")) +
    geom_histogram(bins=25, fill = nfl_red) +
    theme_classic() +
    ggtitle("Distribution of Offensive SRS in the training dataset") +
    xlab("Offensive SRS") +
    theme(figure_size=(7,5),text=element_text(family="serif", size = 13),title=element_text(size=15), axis_text =element_text(color="black"))
    )
plot_offense

plot_defense = (
    ggplot(train_X,aes(x="Season_defense")) +
    geom_histogram(bins=25, fill = nfl_blue) +
    theme_classic() +
    ggtitle("Distribution of Defensive SRS in the training dataset") +
    xlab("Defensive SRS") +
    theme(figure_size=(7,5),text=element_text(family="serif", size = 13),title=element_text(size=15), axis_text =element_text(color="black"))
    )

plot_defense
# %%
plot_offense.save("../09_figures/plot_offense.png")
plot_defense.save("../09_figures/plot_defense.png")


#%%
df.loc[df.Time_rest_days >=20]
#%%

plot_hfa = (
    ggplot(train_X,aes(x="Miles_traveled",y="Time_rest_days",color="factor(Regular)",fill="factor(Time_diff)")) +
    geom_jitter(alpha=0.7, size =3) +
    theme_classic() +
    scale_color_manual(labels=["Playoff","Regular"],name="Game type",values=["black","lightgray"]) +
    ggtitle("Distribution of Home Field Advantage factors in training dataset") +
    xlab("Miles traveled") +
    ylab("Days since previous game") +
    xlim(0,7000)+
    labs(fill="Time difference") +
    #scale_size_continuous(range=[0,3]) +
    theme_classic() +
    theme(figure_size=(8,5),text=element_text(family="serif", size = 13),title=element_text(size=15), axis_text =element_text(color="black"),legend_position=(0.9,0.5),legend_box_just='left')
    )

plot_hfa.save("../09_figures/plot_hfa.png")

# %%
###################################
# NFL Team History & Organization #
###################################
df.Time_rest_days.max()

division_count_season = df.groupby(["Season","Team_A_Division"])["Team_A"].nunique().reset_index()

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
# %%
# Save it
plot_div_team_count.save("../09_figures/plot_div_team_count.png")

#%%
########
# City #
########

df["City"] = df.Location.str.split(" url:",expand=True)[0]
df["City"]= df.City.str.split(", ",expand=True)[0]
city = df.groupby(["Season","City"])["Stadium"].nunique().reset_index()

city.City.nunique()

# %%

plot_city = (
    ggplot(city, aes(x="Season",y="City",fill="City",color="Season")) +
    geom_tile(color="black") +
    scale_fill_discrete(guide=False) +
    scale_x_continuous(breaks = range(1992,2020)) +
    scale_color_continuous(guide=False) +
    ggtitle("NFL game location by season") +
    ylab("") +
    theme_classic() +
    theme(figure_size=(10,8)) +
    theme(axis_text_x=element_text(rotation=90, hjust=1))
)
plot_city

plot_city.save("../09_figures/plot_city.png")
# %%
################
# Lambeau plot #
################


lambeau = df[df.Stadium == "Lambeau Field"]

lambeau_test = lambeau[["Season","Capacity","Attendance"]]

lambeau_test = lambeau_test.groupby("Season").agg({"Attendance":["mean","max","min"],"Capacity":"mean"}).reset_index()

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

##################
# Time rest plot #
##################
plot_timerest = (
    ggplot(df.loc[(df.Game_outcome.isin(["Win","Lose"]))&(df.Game_type=="Regular")], aes(x="Game_outcome",y ="Time_rest_days",color="Game_outcome")) +
        geom_jitter() +
        labs(color = "Game outcome") +
        xlab("Game outcome") +
        ylab("Days since previous game") +
        ggtitle("Time rest and game outcome") +
        theme_classic()
    )
plot_timerest
# %%
# Save it
plot_timerest.save("../09_figures/plot_timerest.png")

# %%
##########################
# Miles traveled all #
##########################

plot_traveled_all = (
    ggplot(df.loc[((df.Game_outcome.isin(["Win","Lose"])))],aes(x="Game_outcome",y ="Miles_traveled",fill="Game_outcome")) +
        geom_boxplot() +
        xlab("Game outcome") +
        ylab("Miles traveled") +
        labs(fill = "Game outcome") +
        ggtitle("Miles traveled and game outcome in all games") +
        scale_y_continuous(breaks=[1000,2000,3000,4000,5000,6000]) +
        theme_classic()
)
plot_traveled_all
# %%
# Save it
plot_traveled_all.save("../09_figures/plot_traveled_all.png")

# %%
##########################
# Miles traveled facet #
##########################

plot_traveled_facet = (
    ggplot(df.loc[((df.Game_outcome.isin(["Win","Lose"])))],aes(x="Game_outcome",y ="Miles_traveled",fill="Game_outcome")) +
        geom_boxplot(outlier_shape="") +
        geom_jitter(aes(x="Game_outcome",y ="Miles_traveled",color="Game_outcome"), width = .07, alpha = .1, show_legend=False) +
        facet_wrap(["Game_type","Geography"]) +
        xlab("Game outcome") +
        ylab("Miles traveled") +
        labs(fill = "Game outcome") +
        ggtitle("Miles traveled and game outcome") +
        scale_y_continuous(breaks=[0, 1000,2000,3000,4000,5000,6000]) +
        scale_fill_discrete(guide=False) +
        theme_classic() +
        theme(figure_size=(6,3),
              panel_border=element_rect(color="black", size=.5))
)
plot_traveled_facet
# %%
# Save it
plot_traveled_facet.save("../09_figures/plot_traveled_facet.png")


# %%
######################
# Time rest & travel #
######################
df["Miles_log"] = np.log(df["Miles_traveled"] + 1)

density_traveled_ln = (ggplot(df.loc[(df.Game_outcome.isin(["Win","Lose"]))] ,aes(x ="Miles_log", fill="Game_outcome")) +
        geom_density(alpha=.4, size = 1) +
        #ylab("Days since previous game") +
        xlab("Log(Miles traveled)") +
        labs(fill = "Game outcome") +
        ggtitle("Distribution of log(Miles traveled) and game outcome") +
        #scale_y_continuous(breaks=[1000,2000,3000,4000,5000,6000]) +
        theme_classic())
density_traveled_ln

# %%
# Save it
density_traveled_ln.save("../09_figures/density_traveled_ln.png")
# %%
(
    ggplot(d,aes(x="value")) +
    geom_bar() +
    facet_wrap("variable",scales='free') +
    theme(figure_size=(15,7),
          subplots_adjust={'wspace':0.25,
                           'hspace':0.75},
         axis_text_x=element_text(rotation=45, hjust=1))
)

#%%
df["Win"] = 1*(df.Game_pts_diff > 0)
# Miles
median_miles = df.loc[df["Miles_traveled"]>0, 'Miles_traveled'].median()
df["Miles"] = np.where(df['Miles_traveled']==0,0,np.where(df['Miles_traveled'] <= median_miles,1,2))
df.Miles.value_counts()
# Rivalry
# Impose an order. 0 is no rivalry (meaning an AFC team is playing an NFC team), 1 is conference, and 2 is Division
rival = ['No','Conference','Division']
rival_types = CategoricalDtype(categories=rival, ordered=True)
df['Rivalry'] = df['Rivalry'].astype(rival_types)
df['Rivalry'] = df['Rivalry'].cat.codes
df['Rivalry'].value_counts()

# Grass
df["Grass"] = 1*(df["Surface"] == "Grass")

# Home
df["Home"] = 1*(df["Field"] == "Home")

# Same surface as the team's home field
df["Same_surface"] = 1*(df["Same_surface"] == "Yes")

# Regular season vs playoff
df["Regular"] = 1*(df["Game_type"] == "Regular")
#%%


y = df[['Win']]
#X = df[["Time_rest_hours","Miles_traveled","Attendance","Capacity","Grass","Same_surface","Home", "Regular"]]

X = df[["Rivalry","Time_rest_days","Attendance_pct","Capacity","Miles_traveled","Miles","Grass","Same_surface","Week","Regular","L.Season_offense","L.Season_defense","L.Season_SoS"]]

#X = d[["Rivalry","Time_rest_days","Attendance_pct","Attendance","Capacity","Miles","Grass","Same_surface","Week","Regular"]]


train_X, test_X, train_y, test_y = train_test_split(X,y,test_size = .50,random_state=123)


#%%

(
    ggplot(train_X,aes(x ="Miles_traveled")) +
           geom_density()
           )

train_y.values.ravel()


# %%

(ggplot(df, aes(x="Team_A",y="Team_B",fill="Win")) +
 geom_tile(stat="density")

 )
len(df)/2

df.Game_outcome.nunique()
12/7292*100


# %%
df.Field

d = df[df.Field == "Home"]


d.Stadium.nunique()

df.loc[(df.Stadium=="Lambeau Field") &(df.Season==2011), "Capacity"]
