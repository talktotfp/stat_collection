# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 10:16:29 2017

@author: tpauley
"""
import os

mingw_path = 'C:\\Program Files\\mingw-w64\\x86_64-5.3.0-posix-seh-rt_v4-rev0\\mingw64\\bin'

os.environ['PATH'] = mingw_path + ';' + os.environ['PATH']

import xgboost as xgb

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC, SVC
import numpy as np
from sklearn import datasets, linear_model, svm
import math


#import CSV to dataframes
train = pd.read_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/train_ex.csv")
test = pd.read_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/test_ex.csv")
train['type'] = 'train'
test['type'] = 'test'

dataset = pd.concat([train, test])

#cleanse string data
dataset['Sex'] = dataset['Sex'].replace(['male','female'], [0,1])
dataset['Embarked'] = dataset['Embarked'].replace(['S','C','Q'], [0,1,2]).fillna(0)


#Update empty age values using 1 standard deviation from mean
age_std = .5#dataset['Age'].std()/2
age_mean = dataset['Age'].mean()
for index, row in dataset.iterrows():
    if math.isnan(row['Age']):
        dataset.set_value(index,'Age',np.random.randint((age_mean-age_std),(age_mean+age_std)))


trainArr = pd.DataFrame(dataset[dataset['type']=='train']).as_matrix(['Pclass','Age','SibSp','Embarked','Fare','Sex'])
trainRes = pd.DataFrame(dataset[dataset['type']=='train']).as_matrix(['Survived'])

test = pd.DataFrame(dataset[dataset['type']=='test'])
testArr = test.as_matrix(['Pclass','Age','SibSp','Embarked','Fare','Sex'])


#SVC Classification
clf = LinearSVC(random_state=0)
clf.fit(trainArr, trainRes.ravel()) 
clf_res =  clf.predict(testArr)
test['predictions_svc'] = clf_res
clf_results = test[['PassengerId','Survived','predictions_svc']]
correct_clf = len(clf_results[(clf_results['Survived']==clf_results['predictions_svc'])])
print('SVC (Linear):', round(correct_clf/len(test),3))

#clf_results[['PassengerId','predictions_clf']].to_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/results_svc.csv", sep=',')


#Random Forest Classification
rf= RandomForestClassifier(n_estimators=10, min_samples_leaf =8, random_state =0) # initialize
rf.fit(trainArr, trainRes.ravel()) # fit the data to the algorithm
rf_res = rf.predict(testArr)
test['predictions_rf'] = rf_res
rf_results = test[['PassengerId','Survived','predictions_rf']]
correct_rf = len(rf_results[(rf_results['Survived']==rf_results['predictions_rf'])])
print('Random Forest:', round(correct_rf/len(test),3))


gbm = xgb.XGBClassifier(max_depth=3, n_estimators=300, learning_rate=0.05).fit(trainArr, trainRes.ravel())
xgb_res = gbm.predict(testArr)
test['predictions_xgb'] = xgb_res
xgb_results = test[['PassengerId','Survived','predictions_xgb']]
correct_xgb = len(xgb_results[(xgb_results['Survived']==xgb_results['predictions_xgb'])])
print('XGB:', round(correct_xgb/len(test),3))