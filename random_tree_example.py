# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 12:08:36 2017

@author: tpauley
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
import numpy as np
from sklearn import datasets, linear_model


#import CSV to dataframes
train = pd.read_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/train.csv")
test = pd.read_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/test.csv")

#cleanse string data
train['Sex'] = train['Sex'].replace(['male','female'], [0,1])
train['Embarked'] = train['Embarked'].replace(['S','C','Q'], [0,1,2])
train['Age'] = train['Age'].fillna(value=train['Age'].mean())

test['Sex'] = test['Sex'].replace(['male','female'], [0,1])
test['Embarked'] = test['Embarked'].replace(['S','C','Q'], [0,1,2])
test['Age'] = test['Age'].fillna(value=train['Age'].mean())

#fill empty values
test = test.fillna(value=0)
train = train.fillna(value=0)

#make column definition for RF
cols_men = ['Age','Pclass'] 
cols_women = ['Pclass','Age','SibSp','Embarked'] 
#column for RF results
colsRes = ['Survived']

#print Correlation Matrix


#Split samples by gender
train_men = train[(train['Sex']== 0)]
train_women = train[(train['Sex']== 1)]
test_men = pd.DataFrame(test[(test['Sex']== 0)])
test_women = pd.DataFrame(test[(test['Sex']== 1)])
print('Men')
print(train_men.corr(method='pearson')['Survived'])

print('Women')
print(train_women.corr(method='pearson')['Survived'])
#----------Start Men
#create arrays (MEN)
trainArr_men = train_men.as_matrix(cols_men) #training array
trainRes_men = train_men.as_matrix(colsRes) # training results

for x in range(1,2):
    #setup random forest (MEN)
    rf_men = RandomForestClassifier(n_estimators=10, min_samples_leaf =8, random_state =61) # initialize
    rf_men.fit(trainArr_men, trainRes_men.ravel()) # fit the data to the algorithm
    
    
    # put the test data in the same format!
    testArr_men = test_men.as_matrix(cols_men)
    
    #get prediciton results
    results_men = rf_men.predict(testArr_men)
    ## something I like to do is to add it back to the data frame, so I can compare side-by-side
    test_men['predictions'] = results_men
    rf_res_men = test_men[['PassengerId','Survived','predictions']]
    correct_men = len(rf_res_men[(rf_res_men['Survived']==rf_res_men['predictions'])])
    
    print(x,'  Men ',correct_men,'/',len(test_men))

#test[['PassengerId','predictions']].to_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/results.csv", sep=',')

#----------Start Women
#create arrays (women)
trainArr_women = train_women.as_matrix(cols_women) #training array
trainRes_women = train_women.as_matrix(colsRes) # training results


#setup random forest (women)
rf_women = RandomForestClassifier(n_estimators=10, min_samples_leaf =8, random_state =61) # initialize
rf_women.fit(trainArr_women, trainRes_women.ravel()) # fit the data to the algorithm


# put the test data in the same format!
testArr_women = test_women.as_matrix(cols_women)

#get prediciton results
results_women = rf_women.predict(testArr_women)
## something I like to do is to add it back to the data frame, so I can compare side-by-side
test_women['predictions'] = results_women
rf_res_women = test_women[['PassengerId','Survived','predictions']]
correct_women = len(rf_res_women[(rf_res_women['Survived']==rf_res_women['predictions'])])

print('women ',correct_women,'/',len(test_women))

results = pd.concat([rf_res_men,rf_res_women])
print(results)
results.to_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/results_gender.csv", sep=',')


#clf = LinearSVC()
#clf.fit(trainArr_men, trainRes_men.ravel()) 
#clf_res =  clf.predict(testArr_men)
#test_men['predictions_clf'] = clf_res
#clf_results = test_men[['PassengerId','Survived','predictions_clf']]
#correct_clf = len(clf_results[(clf_results['Survived']==clf_results['predictions_clf'])])
#print(correct_clf,'/',len(test))
#print(clf_results)

#clf_results[['PassengerId','predictions_clf']].to_csv("C:/Users/tpauley/Documents/Python Scripts/Data/Titanic/results_svc.csv", sep=',')
