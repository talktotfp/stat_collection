# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 16:33:59 2017

@author: tpauley
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 10:16:29 2017

@author: tpauley
"""
import os

mingw_path = 'C:\\Program Files\\mingw-w64\\x86_64-5.3.0-posix-seh-rt_v4-rev0\\mingw64\\bin'

os.environ['PATH'] = mingw_path + ';' + os.environ['PATH']

import xgboost as xgb
from numpy import mean, sqrt, square, arange
import pandas as pd
import numpy as np
import math
from sklearn.metrics import mean_squared_error
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from scipy.stats import skew
plt.style.use('ggplot')


###--- Function to rename cateogrical columns to integers
def cat_cleanse(df,column):
    x=0
    for value in df[column].unique():
        df[column] = df[column].replace([value], [x])
        x= x+1

###--- Function to split categroical values into groups
def cat_ranker (df,column,metric,split_size, new_column):
    df[new_column] = df[column]
    mlist1 = []
    mlist2 = []
    for i in range(1,(split_size +2)): 
        ranked_set = df[[column,metric]].groupby([column]).mean().sort_values([metric])
        x = len(ranked_set)
        portion = int(x/split_size)
        to_range = i*portion
        from_range= to_range - portion
        ranked_set = pd.DataFrame(ranked_set.iloc[from_range:to_range])
        ranked_set[new_column] = i
        list1 = list(ranked_set.index)
        list2 = list(ranked_set[new_column])  
        if i == (split_size+1):
            portion = (x-(portion*split_size))
            ranked_set = df[[column,metric]].groupby([column]).mean().sort_values([metric])
            ranked_set = pd.DataFrame(ranked_set.iloc[(x-portion):])
            ranked_set[new_column] = i
            list1 = list(ranked_set.index)
            list2 = list(ranked_set[new_column])
        mlist1 = mlist1 + list1
        mlist2 = mlist2 + list2
    df[new_column] = df[new_column].replace(mlist1, mlist2)        
        
        

#import CSV to dataframes
train = pd.read_csv("C:/Users/tpauley/Documents/Python Scripts/Kaggle/House Prices/train.csv")
###--- Load test data in and set saleprice to zero to work with scripts (REAL RUNS)
test = pd.read_csv("C:/Users/tpauley/Documents/Python Scripts/Kaggle/House Prices/test.csv")
test['SalePrice'] = 0
train['type'] = 'train'
test['type'] = 'test'  

train = pd.concat([train,test])


prices = pd.DataFrame({"price":train["SalePrice"], "log(price + 1)":np.log1p(train["SalePrice"])})
prices.hist()
num_columns = train.dtypes[train.dtypes != "object"].index
cat_columns = train.dtypes[train.dtypes == "object"].index


for col_name in cat_columns:
    cat_cleanse(train,col_name)
    train[col_name] = train[col_name].fillna(train[col_name].mode())
#    train[col_name] = train[col_name].fillna(0)
for col_name in num_columns:
    train[col_name] = train[col_name].fillna(train[col_name].median())
#    train[col_name] = train[col_name].fillna(0)



#for cols in num_columns:
#    try:
#        plt.hist(train[cols])
#        plt.title(cols)
#        plt.show()
#    except:
#        print()
skewed_feats = train[num_columns].apply(lambda x: skew(x.dropna())) #compute skewness
skewed_feats = skewed_feats[skewed_feats > 0.75]
skewed_feats = skewed_feats.index

train[skewed_feats] = np.log1p(train[skewed_feats])



train = pd.get_dummies(train)



###--- Define categroical columns in the dataset




###--- Split train into a testing sample (TEST ONLY)




###--- Remove any outliers from sale price (3 standard deviations)
train_mean = train['SalePrice'].mean()
train_std = train['SalePrice'].std()
train = pd.DataFrame(train[train['SalePrice'] <= (train_mean + (train_std*3))])
price_corr = train.corr(method='pearson', min_periods=1)[['SalePrice']]
#print(price_corr.sort(['SalePrice'],ascending=[0]))

###--- Only choose attributes with a correlation >.125
#attr_list = list(price_corr[price_corr['SalePrice'] >  .25 ].index)
attr_list = list(price_corr.query('SalePrice > .125 or SalePrice < -.125').index)
attr_list.remove('SalePrice')



#print(train[['Neighborhood','SalePrice']].groupby(['Neighborhood']).mean().sort(['SalePrice']))


###--- Split categories into groups using cat_ranker function   
#cat_ranker(train,'Neighborhood','SalePrice',4,'Nhood_rank')
##train.drop(['Neighborhood'],inplace=True,axis=1)




    

#print(encode_test)
#print(X.shape)
#encoded_x = None
#for i in range(0, X.shape[1]):
#	label_encoder = LabelEncoder()
#	feature = label_encoder.fit_transform(X[:,i])
#	feature = feature.reshape(X.shape[0], 1)
#	onehot_encoder = OneHotEncoder(sparse=False)
#	feature = onehot_encoder.fit_transform(feature)
#	if encoded_x is None:
#		encoded_x = feature
#	else:
#		encoded_x = numpy.concatenate((encoded_x, feature), axis=1)
##print("X shape: : ", encoded_x.shape)
##print()

 

 
#cols_to_transform = cat_columns
#train = pd.get_dummies(train, columns = cols_to_transform )
#print(train.info())
train['SalePrice'] = np.log1p(train["SalePrice"])
#print(train)

print(train)
test = pd.DataFrame(train[train['type'] == 1])
train = pd.DataFrame(train[train['type'] == 0])
#train['type'] = 'train'
#test['type'] = 'test'  


  
trainArr = pd.DataFrame(train.as_matrix(attr_list))
trainRes = pd.DataFrame(train.as_matrix(['SalePrice']))
testArr = pd.DataFrame(test.as_matrix(attr_list))


#XGBoost Classification
gbm = xgb.XGBRegressor(max_depth=7, n_estimators=1000, learning_rate=.0025).fit(trainArr, trainRes)
xgb_res = gbm.predict(testArr)
test['predictions_xgb'] = xgb_res
#test['predictions_xgb'] =  round(test['predictions_xgb'] / 500.0) * 500.0
#test.predictions_xgb = test.predictions_xgb.astype(int)
xgb_results = pd.DataFrame(test[['Id','SalePrice','predictions_xgb']])
#xgb_results['SalePrice'] = np.exp(xgb_results["SalePrice"])
#xgb_results['predictions_xgb'] = np.exp(xgb_results["predictions_xgb"])
#xgb_results['predict_y'] =  np.log(xgb_results['predictions_xgb'])
#xgb_results['actual_y'] = np.log(xgb_results['SalePrice'])
score = sqrt(mean_squared_error(xgb_results['SalePrice'],xgb_results['predictions_xgb'] ))
print('Kaggle Score (XGB): ',round(score,3))
#print(xgb_results)



xgb_results[['Id','predictions_xgb']].to_csv("C:/Users/tpauley/Documents/Python Scripts/Kaggle/House Prices/train_results.csv", sep=',', index=False)
  
#OLS Analysis

model = sm.OLS(trainRes,trainArr)
ols_res = model.fit()
test['predictions_ols'] = ols_res.predict(testArr)
#test['predictions_ols'] =  round(test['predictions_ols'] / 500.0) * 500.0
#test.predictions_ols = test.predictions_ols.astype(int)
ols_results = pd.DataFrame(test[['Id','SalePrice','predictions_ols']])
#ols_results['predict_y'] =  np.log(ols_results['predictions_ols'])
#ols_results['actual_y'] = np.log(ols_results['SalePrice'])
score = sqrt(mean_squared_error(ols_results['SalePrice'],ols_results['predictions_ols'] ))
print('Kaggle Score (OLS): ',round(score,3))








##XGBoost Classification
#gbm = xgb.XGBRegressor(max_depth=7, n_estimators=10000, learning_rate=.0025).fit(trainArr, trainRes)
#xgb_res = gbm.predict(testArr)
#test['predictions_xgb'] = xgb_res
#test['SalePrice'] =  round(test['predictions_xgb'] / 500.0) * 500.0
#test.SalePrice = test.SalePrice.astype(int)
#xgb_results = test[['Id','SalePrice','predictions_xgb']]
#print(xgb_results)
#
#test[['Id','SalePrice']].to_csv("C:/Users/tpauley/Documents/Python Scripts/Kaggle/House Prices/results.csv", sep=',', index=False)
#  
