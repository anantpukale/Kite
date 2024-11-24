import pandas as pd

data = pd.read_csv("D:\\data\\DataScience\\data\\test.csv")

data = data.sort_values(by=['Server','Date'])
#if data['Server'] == data['Server'].shift(1):
#	data['daily_usage'] = data['current_used']-data['current_used'].shift(1)

data['avg'] = data['daily_usage'].rolling(7).mean()
data['pred'] = data['Allocation']/data['avg']
print(data.head(20))