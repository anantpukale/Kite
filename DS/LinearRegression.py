import datetime

import numpy as np
from matplotlib.dates import DateFormatter
from pandas import read_csv, to_datetime
from sklearn.linear_model import LinearRegression
import datetime as dt
from matplotlib import pyplot as plt
from pandas import read_csv, to_datetime, DataFrame
from sklearn import *

# load data
path = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv'

df = read_csv(path)

df.columns = ['ds', 'y']

df['ds'] = to_datetime(df['ds'])

df['ds']=df['ds'].map(dt.datetime.toordinal)

from sklearn.model_selection import train_test_split
x = df['ds'].values
y = df['y'].values
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train.reshape(-1,1),y_train)
y_pred = model.predict(X_test.reshape(-1,1))

fig, ax = plt.subplots(figsize=(8, 5))
plt.plot(X_test, y_test,'o', color='red')
plt.plot(X_test, y_pred, color='blue', linewidth=3)

date_form = DateFormatter("%d-%m-%y")

ax.xaxis.set_major_formatter(date_form)
#plt.xscale('linear')
# plt.xticks(())
# plt.yticks(())
plt.show()

#print(res)
