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

df.dtypes
# Convert Time_rest to time delta
df["Time_rest"] = pd.to_timedelta(df["Time_rest"])

# Convert Time_rest to number of hours
df['Time_rest_hours'] = df['Time_rest'] / np.timedelta64(1, 'h')

# Convert categorial variables to categories
for col in ['Week','Game_type','Surface','Outcome','Rivalry','Same_surface','Field']: df[col] = df[col].astype("category")

#%%
#Outcome_code
df["Outcome_code"] = ""
df.loc[df.Points_diff < 0, "Outcome_code"] = -1
df.loc[df.Points_diff == 0, "Outcome_code"] = 0
df.loc[df.Points_diff > 0, "Outcome_code"] = 1

#%%

# Convert to ordinal values
ord_enc = OrdinalEncoder()
df[['Week_code','Game_type_code','Surface_code','Rivalry_code','Same_surface_code','Field_code']] = ord_enc.fit_transform(df[['Week','Game_type','Surface','Rivalry','Same_surface','Field']])

df[["Surface","Surface_code","Same_surface","Same_surface_code","Field","Field_code","Rivalry","Rivalry_code"]]
# %%
#########
# Split #
#########

#Drop missing
df.dropna(inplace=True)


y = df[['Outcome_code']]
X = df[['Surface_code','attendance','Time_rest_hours','Miles_traveled','Same_surface_code']]
#train_X, test_X, train_y, test_y = train_test_split(X,y,test_size = .25,random_state=123)

print(train_X.shape[0]/df.shape[0])
print(test_X.shape[0]/df.shape[0])
col_names = list(train_X)

# %%
# mod = DT_reg(max_depth=5) # Initialize the modeling object (just as we did)
# mod.fit(train_X,train_y) # Fit the mode
# #%%
# # Plot the tree
# plt.figure(figsize=(30,10))
# rules = tree.plot_tree(mod,feature_names = col_names,fontsize=7)



# %%
####
# Modeling pipeline
#

# (0) Split the data
train_X, test_X, train_y, test_y = train_test_split(X,y,test_size=.25,random_state=1988)

# (1) Set the folds index to ensure comparable samples
fold_generator = KFold(n_splits=5, shuffle=True,random_state=111)

# (2) Next specify the preprocessing steps
#preprocess = ColumnTransformer(transformers=[('num', pp.MinMaxScaler(), ['BATHRM','ROOMS','LANDAREA'])])
#%%

# (3) Next Let's create our model pipe (note for the model we leave none as a placeholder)
pipe = Pipeline(steps=[('pre_process', pp.MinMaxScaler()),('model',None)])


# (4) Specify the models and their repsective tuning parameters.
# Note the naming convention here to reference the model key
search_space = [
    # Linear Model
    {'model' : [LM()]},

    # KNN with K tuning param
    {'model' : [KNN()],
     'model__n_neighbors':[10,15,20,25,30]},

    # Decision Tree with the Max Depth Param
    {'model': [DT()],
     'model__max_depth':[1,2,3,5]},

    # The Bagging decision tree model
    {'model': [Bag()]},

    # Random forest with the N Estimators tuning param
    {'model' : [RF()],
     'model__max_depth':[1,2,3],
     'model__n_estimators':[100,200,300]},
]


# (5) Put it all together in the grid search
search = GridSearchCV(pipe, search_space,
                      cv = fold_generator,
                      scoring='neg_mean_squared_error',
                      n_jobs=4)

# (6) Fit the model to the training data
search.fit(train_X,train_y)


# %%
search.best_score_
search.best_params_

# %%
# Test performance

# Predict() method will use the best model out of the scan
pred_y = search.predict(test_X)

pred_y = pd.DataFrame(pred_y)
m.mean_squared_error(test_y,pred_y)

m.r2_score(test_y,pred_y)

#%%
type(pred_y)

dict(pred=pred_y,truth=test_y)

pd.DataFrame.from_records([{'pred':pred_y,'truth':test_y}])
#%%
# (
#     ggplot(pd.DataFrame.from_records([{'pred':pred_y,'truth':test_y}])), aes(x='pred',y="truth") +
#     geom_point(alpha=.75) +
#     geom_abline(linetype="dashed",color="darkred",size=1) +
#     theme_bw() +
#     theme(figure_size=(10,7))
# )


# %%

rf_mod = search.best_estimator_
m.roc_auc_score(train_y,rf_mod.predict_proba(train_X)[:,1])
