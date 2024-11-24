import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import to_datetime
from sklearn.ensemble import BaggingClassifier
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier
import datetime as dt

dataset= pd.read_csv("D:\data\DataScience\data\Google_Stock_Price_Train.csv")

dataset['Volume'] = dataset['Volume'].str.replace(',', '').astype(int)
dataset['Close']= dataset['Close'].str.replace(',', '').astype(float).astype(int)
print(dataset.head())
X = np.array( to_datetime(dataset['Date']).map(dt.datetime.toordinal))
y= np.array( dataset['Close'])
print(X.cumprod())
print(type(X))

# X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=20)
# print(type(X_test))
# #Create sub samples to train data sets
# seed= 7
# kfold = KFold(n_splits=10)
#
# #define decision tree
# cart = DecisionTreeClassifier()
# num_trees= 100
# #
# # #Classification model for bagging
# model = BaggingClassifier(base_estimator=cart, n_estimators=num_trees, random_state=seed)
# #
# #Cross validation
# result = cross_val_score(model, X_test.reshape(-1,1), y_test, cv=kfold)
# for i in range(len(result)):
#     print("Model: "+str(i)+ " Accuracy is "+ str(result[i]))
#
# model.fit(X_train.reshape(-1,1), y_train.reshape(-1,1))
#
# #plt.plot(X_test, y_test, 'o', color= 'blue')
# plt.plot(X_test, model.predict(X_test.reshape(-1,1)),'o' ,color='red')
#
# plt.show()