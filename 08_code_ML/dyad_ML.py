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
import graphviz
from dtreeviz.trees import dtreeviz
import collections
import pydotplus

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
from sklearn.gaussian_process.kernels import RBF
from sklearn.gaussian_process.kernels import DotProduct
from sklearn.gaussian_process.kernels import Matern
from sklearn.gaussian_process.kernels import RationalQuadratic
from sklearn.gaussian_process.kernels import WhiteKernel



from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.tree import DecisionTreeClassifier as DT
from sklearn.tree import DecisionTreeRegressor as DT_reg
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.linear_model import LogisticRegression

from sklearn import tree # For plotting the decision tree rules

# For evaluating our model's performance
import sklearn.metrics as m

# For variable importances
from sklearn.inspection import partial_dependence
from sklearn.inspection import plot_partial_dependence
from sklearn.inspection import permutation_importance
from pdpbox import pdp



# Pipeline to combine modeling elements
from sklearn.pipeline import Pipeline

# Misc
import warnings
warnings.filterwarnings("ignore")


# %%

# Import the dyadic data
df = pd.read_csv("../07_data_staged/dyadic_data.csv")


len(df)


# %%

# Convert Time_rest to time delta
df["Time_rest"] = pd.to_timedelta(df["Time_rest"])

# Convert Time_rest to number of hours
df['Time_rest_hours'] = df['Time_rest'] / np.timedelta64(1, 'h')

# Convert number of hours to days
df['Time_rest_days'] = df['Time_rest_hours'] / 24
# %%
#Drop Tie
df = df[df.Game_pts_diff!=0]


#Win
df["Win"] = 1*(df.Game_pts_diff > 0)
# %%
# Convert categorial variables to categories
for col in ['Week','Game_type','Surface','Game_outcome','Rivalry','Same_surface','Field']: df[col] = df[col].astype("category")


# %%
#########################
# High level processing #
#########################

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
df.loc[df["Miles_traveled"]>0, 'Miles_traveled'].quantile()
dir(df.loc[df["Miles_traveled"]>0, 'Miles_traveled'])

# Miles
median_miles = df.loc[df["Miles_traveled"]>0, 'Miles_traveled'].median()
df["Miles"] = np.where(df['Miles_traveled']==0,0,np.where(df['Miles_traveled'] <= median_miles,1,2))
df.Miles.value_counts()

#%%
# Timerest
df["Time_rest_ordinal"] = np.where(df["Time_rest_days"] == 7, 1, np.where(df["Time_rest_days"] < 7, 0, 2))

#%%
# Rivalry
# Impose an order. 0 is no rivalry (meaning an AFC team is playing an NFC team), 1 is conference, and 2 is Division
rival = ['No','Conference','Division']
rival_types = CategoricalDtype(categories=rival, ordered=True)
df['Rivalry'] = df['Rivalry'].astype(rival_types)
df['Rivalry'] = df['Rivalry'].cat.codes
# %%
df['Division_Rival'] = 1*(df["Rivalry"] == 2)
df['Conference_Rival'] = 1*(df["Rivalry"] == 1)
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

#%%
# Order the weeks
df["Week"].unique()
week = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','WildCard','Division','ConfChamp','SuperBowl']

week_types = CategoricalDtype(categories=week, ordered=True)
df['Week'] = df['Week'].astype(week_types)
df['Week'] = df['Week'].cat.codes


# %%
###############
# Split again #
###############
d = df[["Win","Rivalry","Time_rest_days","Capacity","Attendance_pct","Attendance","Miles_traveled","Time_diff","Grass","Same_surface","Week","Season","Regular","Season_offense","Season_defense"]]

d = d.dropna()

y = d[['Win']]

#X = d[["Rivalry","Time_rest_days","Capacity","Attendance_pct","Miles_traveled","Time_diff","Grass","Same_surface","Week","Season","Regular","Season_offense","Season_defense"]]

X = d[["Rivalry","Time_rest_days","Capacity","Attendance_pct","Miles_traveled","Time_diff","Grass","Same_surface","Week","Season","Regular","Season_offense","Season_defense"]]


train_X, test_X, train_y, test_y = train_test_split(X,y,test_size = .25,random_state=123)




# %%
# Set the folds index to ensure comparable samples
fold_generator = KFold(n_splits=10, shuffle=True,random_state=1234)

#%%
pipe = Pipeline(steps=[('pre_process', pp.MinMaxScaler()),('model',None)])


search_space = [

    # NaiveBayes
    {'model': [NB()]},

    # KNN with K tuning param
    {'model' : [KNN()],
     'model__n_neighbors':[5,10,15,20,25,30,35,40,45,50]},

    # # Decision Tree with the Max Depth Param
    {'model': [DT()],
     'model__max_depth':[2,3,4,5,6,7,8,9,10]},

    # #Random forest with the N Estimators tuning param
    {'model' : [RF()],
    'model__max_depth':[2,3,4,5,7,8],
    'model__n_estimators':[100,200,300,400,500],
    'model__max_features':[2,3,4,5,6,7,8]}

]
# %%
search = GridSearchCV(pipe, search_space,
                      cv = fold_generator,
                      scoring='roc_auc',
                      verbose = 10 ,
                      n_jobs=4)
# %%
search.fit(train_X,train_y.values.ravel())

# %%
search.best_score_
search.best_params_
#search.cv_results_['mean_test_score']
pd.concat([pd.DataFrame(search.cv_results_["params"]),pd.DataFrame(search.cv_results_["mean_test_score"], columns=["Accuracy"])],axis=1)



#res.to_csv("../12_notes/res.csv")

rf_mod = search.best_estimator_
rf_mod



# %%
###############
# PERFORMANCE #
###############
# On training data
m.roc_auc_score(train_y,rf_mod.predict_proba(train_X)[:,1])
m.accuracy_score(train_y,rf_mod.predict(train_X))


# %%
# On test data
m.roc_auc_score(test_y,rf_mod.predict_proba(test_X)[:,1])
m.accuracy_score(test_y,rf_mod.predict(test_X))



test_auc_score = m.roc_auc_score(test_y,rf_mod.predict_proba(test_X)[:,1])

test_auc_score = test_auc_score.round(3).astype('str')
auc_label = np.array(['AUC Score: '],  dtype = np.str)
auc_score_legend = np.char.add(auc_label,test_auc_score)


# %%
#############
# ROC Curve #
#############

# Get the probability
probs = rf_mod.predict_proba(test_X)
probs =  pd.DataFrame(probs,columns=rf_mod.classes_)

# Generate FPR & TPR
fpr, tpr, thresholds = m.roc_curve(test_y, probs[1])
# %%
#Custom colors
nfl_red = "#d50a0a"
nfl_blue = "#013369"


# Plot it
plot_roc = (
    ggplot(pd.DataFrame(dict(fpr=fpr,tpr=tpr)),
           aes(x="fpr",y="tpr")) +
    geom_path(color=nfl_blue,size=1.5) +
    geom_abline(intercept=0,slope=1,linetype="dashed",color = nfl_red) +
    ggtitle("ROC Curve") +
    xlab("False Positive Rate") +
    ylab("True Positive Rate") +
    annotate('text', x = 0.85, y = 0, label = auc_score_legend ) +
    theme_classic() +
    theme(figure_size=(7,5),text=element_text(family="serif", size = 13),title=element_text(size=15), axis_text =element_text(color="black"))
)

plot_roc

# %%
# Save it

plot_roc.save("../09_figures/plot_roc.png")


# %%
from sklearn.inspection import permutation_importance
#%%

vi = permutation_importance(rf_mod,train_X,train_y,n_repeats=100)

#%%
# Organize as a data frame
vi_dat = pd.DataFrame(dict(variable=train_X.columns,
                           vi = vi['importances_mean'],
                           std = vi['importances_std']))

# Generate intervals
vi_dat['low'] = vi_dat['vi'] - 2*vi_dat['std']
vi_dat['high'] = vi_dat['vi'] + 2*vi_dat['std']

# But in order from most to least important
vi_dat = vi_dat.sort_values(by="vi",ascending=False).reset_index(drop=True)


vi_dat
#%%

plot_vi = (
    ggplot(vi_dat,
          aes(x="variable",y="vi")) +
    geom_col(alpha=.9,fill=nfl_blue) +
    geom_point(color=nfl_red) +
    geom_errorbar(aes(ymin="low",ymax="high"),width=0.5, size = 1,color = nfl_red) +
    theme_classic() +
    scale_x_discrete(limits=vi_dat.variable.tolist()) +

    coord_flip() +
    ggtitle("Varible importance") +
    labs(y="Reduction in AUC ROC",x="") +


    theme(figure_size=(10,4),title=element_text(size = 15,hjust=1),text=element_text(family="serif", size = 13),axis_text =element_text(color="black"))
)
plot_vi


# %%
plot_vi.save("../09_figures/plot_vi.png")

# %%
##########################
# Global surrogate model #
##########################

pr_y = rf_mod.predict_proba(train_X)[:,rf_mod.classes_ == 1]


surrogate_model = DT_reg(max_depth=4)
surrogate_model.fit(train_X,pr_y)

m.r2_score(pr_y,surrogate_model.predict(train_X)).round(2)
#%%

fig = plt.figure(figsize=(55,15))
_ = tree.plot_tree(surrogate_model,
                       feature_names=train_X.columns,
                       filled = True,
                       rounded =True,
                       fontsize=24)

fig.savefig("../09_figures/decision_tree.png")
#%%
########################
# Partial Dependencies #
########################
import matplotlib
matplotlib.rcParams.update({'font.size': 15, 'font.family':'serif'})


#%%
# Target three specific features mentioned above
features = ['Season_offense','Season_defense','Miles_traveled','Attendance_pct','Time_rest_days']

# Calculate the partial dependency
fig, ax2 = plt.subplots(figsize=(12, 4))
ax2.set_title("Partial dependency plot", fontsize = 18, family = "serif")
ax2.set_xlabel("Variables", fontsize=13, family='serif')
ax2.set_ylabel("", fontsize=13, family='serif')
display = plot_partial_dependence(
    rf_mod, train_X, features,n_cols=5,
    n_jobs=4, grid_resolution=30,ax=ax2, line_kw={"c":nfl_blue,"lw":2})


plt.savefig("../09_figures/plot_pdp.png")



# %%
###############################
# ICE plot for miles traveled #
###############################


pdp_dist = pdp.pdp_isolate(model = rf_mod,
                           dataset = train_X,
                           model_features = train_X.columns.tolist(),
                           feature="Miles_traveled")

fig = pdp.pdp_plot(pdp_dist,'Miles_traveled',plot_pts_dist=False,
                   center=True,plot_lines=True,
                   figsize=(15,10),
                   plot_params = {'font_family':'serif','title_fontsize':18,'fontsize':15})

pdp.plt.savefig('../09_figures/ice_plot.png')


# %%

##################################
# Interaction Partial Dependency #
##################################
inter1  =  pdp.pdp_interact(model = rf_mod,
                            dataset = train_X,
                            model_features = train_X.columns,
                            features=['Miles_traveled','Season_offense'])


fig,ax = pdp.pdp_interact_plot(pdp_interact_out=inter1,
                               feature_names=['Miles_traveled','Season_offense'],
                               plot_type="grid",plot_params = {'font_family':'serif','title_fontsize':15,'fontsize':15})

pdp.plt.savefig('../09_figures/inter_offense.png')

#%%

inter2  =  pdp.pdp_interact(model = rf_mod,
                            dataset = train_X,
                            model_features = train_X.columns,
                            features=['Miles_traveled','Season_defense'])


fig,ax = pdp.pdp_interact_plot(pdp_interact_out=inter2,
                               feature_names=['Miles_traveled','Season_defense'],
                               plot_type="grid",plot_params = {'font_family':'serif','title_fontsize':15,'fontsize':15})

pdp.plt.savefig('../09_figures/inter_defense.png')

# %%

inter3  =  pdp.pdp_interact(model = rf_mod,
                            dataset = train_X,
                            model_features = train_X.columns,
                            features=['Miles_traveled','Attendance_pct'])


fig,ax = pdp.pdp_interact_plot(pdp_interact_out=inter3,
                               feature_names=['Miles_traveled','Attendance_pct'],
                               plot_type="grid",plot_params = {'font_family':'serif','title_fontsize':15,'fontsize':15})

pdp.plt.savefig('../09_figures/home_attendance.png')


#%%
