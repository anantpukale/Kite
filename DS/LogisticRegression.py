import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from Cython.Distutils.old_build_ext import old_build_ext
from numpy.distutils.system_info import gdk_info
from sklearn.model_selection import train_test_split
import  datetime as dt

oecd_bli = pd.read_csv('D:\data\DataScience\handson-ml-master\datasets\lifesat\oecd_bli_2015.csv')

gdp_per_capita= pd.read_csv('D:\data\DataScience\handson-ml-master\datasets\lifesat\gdp_per_capita.csv',
                            encoding='latin1', delimiter='\t')
path = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv'

df = pd.read_csv(path)

df.columns = ['ds', 'y']
df['ds'] = pd.to_datetime(df['ds'])
df['ds']= df['ds'].apply(lambda x: x.toordinal())
x= df['ds'].values
y = df['y'].values
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=24)

model = LogisticRegression()
model.fit(X_train.reshape(-1, 1), y_train)

y_pred= model.predict(X_test.reshape(-1,1))
a = pd.DataFrame(X_test[1:,1:],index=X_test[1:,0],columns=X_test[0,1:])
print("-========")
print(a.columns)
print("-========")
 #   .map(dt.datetime.fromordinal)
plt.plot( a , y_pred, color='blue')
#plt.plot(X_train, y_train, 'o', color='red')
print(df.head())
plt.show()

