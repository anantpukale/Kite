
from pandas import read_csv, to_datetime, DataFrame

from fbprophet import Prophet

# load data
path = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv'

df = read_csv(path)

model = Prophet()
# prepare expected column names
df.columns = ['ds', 'y']
df['ds'] = to_datetime(df['ds'])
model.fit(df)
future = list()
future.append("1990-01")
futureDf= DataFrame(future)
print("FUTURE DF")

futureDf.columns = ['ds']

futureDf['ds'] = to_datetime(futureDf['ds'])
print(futureDf.head())
y = model.predict(futureDf)

print(y)

