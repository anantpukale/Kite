from kitepy import *

# -*- coding: utf-8 -*-
'''
Stock Prices Prediction Project with Neptune.ai
'''
###### Create Neptune project
## update: pip install neptune-client==0.9.8
import neptune
import os

# Connect your script to Neptune
# project = neptune.init(api_token=os.getenv('NEPTUNE_API_TOKEN'),
#                       project_qualified_name='YourUserName/YourProjectName')

###### Import all the packages for analysis
import pandas as pd
import numpy as np

# for reproducibility of our results
np.random.seed(42)

from datetime import date
from matplotlib import pyplot as plt

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from keras.models import Sequential, Model
from keras.models import Model
from keras.layers import Dense, Dropout, LSTM, Input, Activation, concatenate

import tensorflow as tf

tf.random.set_seed(42)

import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import urllib.request, json

#os.chdir('YOUR_WORKING_DIRECTORY')

data_source = 'a'  # alphavantage

if data_source == 'alphavantage':
	# ====================== Loading Data from Alpha Vantage ==================================
	api_key = 'YOUR_API'
	# stock ticker symbol
	ticker = 'AAPL'

	# JSON file with all the stock prices data
	url_string = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s" % (
	ticker, api_key)

	# Save data to this file
	fileName = 'stock_market_data-%s.csv' % ticker

	### get the low, high, close, and open prices
	if not os.path.exists(fileName):
		with urllib.request.urlopen(url_string) as url:
			data = json.loads(url.read().decode())
			# pull stock market data
			data = data['Time Series (Daily)']
			df = pd.DataFrame(columns=['date', 'Low', 'High', 'close', 'Open'])
			for key, val in data.items():
				date = dt.datetime.strptime(key, '%Y-%m-%d')
				data_row = [date.date(), float(val['3. low']), float(val['2. high']),
				            float(val['4. close']), float(val['1. open'])]
				df.loc[-1, :] = data_row
				df.index = df.index + 1
		df.to_csv(fileName)

	else:
		print('Loading data from local')
		df = pd.read_csv(fileName)

# Sort DataFrame by date
#stockprices = df.sort_values('date')
trader = TradeApp("NIFTY 50")
stockprices = trader.get_data(interval='day')
# tail = stockprices.tail(4)
# print("tail len: ", len(tail))
# tail['date'] = tail['date'] + pd.DateOffset(1)
# stockprices = stockprices.append(tail)
print(stockprices)
#### Define helper functions to calculate the metrics RMSE and MAPE ####
def calculate_rmse(y_true, y_pred):
	"""
	Calculate the Root Mean Squared Error (RMSE)
	"""
	rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
	return rmse


### The effectiveness of prediction method is measured in terms of the Mean Absolute Percentage Error (MAPE) and RMSE
def calculate_mape(y_true, y_pred):
	"""
	Calculate the Mean Absolute Percentage Error (MAPE) %
	"""
	y_pred, y_true = np.array(y_pred), np.array(y_true)
	mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
	return mape


## Split the time-series data into training seq X and output value Y
def extract_seqX_outcomeY(data, N, offset):
	"""
	Split time-series into training sequence X and outcome value Y
	Args:
		data - dataset
		N - window size, e.g., 60 for 60 days
		offset - position to start the split
	"""
	X, y = [], []

	for i in range(offset, len(data)):
		X.append(data[i - N:i])
		y.append(data[i])

	return np.array(X), np.array(y)


#### Train-Test split for time-series ####
test_ratio = 0.2
training_ratio = 1 - test_ratio

train_size = int(training_ratio * len(stockprices))
test_size = int(test_ratio * len(stockprices))

print("train_size: " + str(train_size))
print("test_size: " + str(test_size))

train = stockprices[:train_size][['date', 'close']]
test = stockprices[train_size:][['date', 'close']]

###================= simple MA
stockprices = stockprices.set_index('date')


### For meduim-term trading
def plot_stock_trend(var, cur_title, stockprices=stockprices, logNeptune=True, logmodelName='Simple MA'):
	ax = stockprices[['close', var, '200day']].plot(figsize=(20, 10))
	plt.grid(False)
	plt.title(cur_title)
	plt.axis('tight')
	plt.ylabel('Stock Price ($)')

	# if logNeptune:
	# 	npt_exp.log_image(f'Plot of Stock Predictions with {logmodelName}', ax.get_figure())


def calculate_perf_metrics(var, logNeptune=True, logmodelName='Simple MA'):
	### RMSE
	rmse = calculate_rmse(np.array(stockprices[train_size:]['close']), np.array(stockprices[train_size:][var]))
	### MAPE
	mape = calculate_mape(np.array(stockprices[train_size:]['close']), np.array(stockprices[train_size:][var]))

	# if logNeptune:
	# 	npt_exp.send_metric('RMSE', rmse)
	# 	npt_exp.log_metric('RMSE', rmse)
	#
	# 	npt_exp.send_metric('MAPE (%)', mape)
	# 	npt_exp.log_metric('MAPE (%)', mape)

	return rmse, mape


# 20 days to represent the 22 trading days in a month
window_size = 50
CURRENT_MODEL = 'LSTM'

# if CURRENT_MODEL == 'SMA':
# 	# Create an experiment and log the model
# 	npt_exp = project.create_experiment(name='SMA',
# 	                                    description='stock-prediction-machine-learning',
# 	                                    tags=['stockprediction', 'MA_Simple', 'neptune'])
#
# 	window_var = str(window_size) + 'day'
#
# 	stockprices[window_var] = stockprices['close'].rolling(window_size).mean()
# 	### Include a 200-day SMA for reference
# 	stockprices['200day'] = stockprices['close'].rolling(200).mean()
#
# 	### Plot and performance metrics for SMA model
# 	plot_stock_trend(var=window_var, cur_title='Simple Moving Averages', logmodelName='Simple MA')
# 	rmse_sma, mape_sma = calculate_perf_metrics(var=window_var, logmodelName='Simple MA')
#
# elif CURRENT_MODEL == 'EMA':
# 	npt_exp = project.create_experiment(name='EMA',
# 	                                    description='stock-prediction-machine-learning',
# 	                                    tags=['stockprediction', 'MA_Exponential', 'neptune'])
# 	window_var = str(window_size) + 'day'
# 	###### Exponential MA
# 	window_ema_var = window_var + '_EMA'
# 	# Calculate the N-day exponentially weighted moving average
# 	stockprices[window_ema_var] = stockprices['close'].ewm(span=window_size, adjust=False).mean()
# 	stockprices['200day'] = stockprices['close'].rolling(200).mean()
#
# 	### Plot and performance metrics for EMA model
# 	plot_stock_trend(var=window_ema_var, cur_title='Exponential Moving Averages', logmodelName='Exp MA')
# 	rmse_ema, mape_ema = calculate_perf_metrics(var=window_ema_var, logmodelName='Exp MA')

if CURRENT_MODEL == 'LSTM':

	# layer_units, optimizer = 50, 'adam'
	# cur_epochs = 15
	# cur_batch_size = 20
	layer_units, optimizer = 100, 'adam'
	cur_epochs = 5
	cur_batch_size = 20

	cur_LSTM_pars = {'units': layer_units,
	                 'optimizer': optimizer,
	                 'batch_size': cur_batch_size,
	                 'epochs': cur_epochs
	                 }

	# npt_exp = project.create_experiment(name='LSTM',
	#                                     params=cur_LSTM_pars,
	#                                     description='stock-prediction-machine-learning',
	#                                     tags=['stockprediction', 'LSTM', 'neptune'])

	## use the past N stock prices for training to predict the N+1th closing price

	# scale
	scaler = StandardScaler()
	scaled_data = scaler.fit_transform(stockprices[['close']])
	scaled_data_train = scaled_data[:train.shape[0]]

	X_train, y_train = extract_seqX_outcomeY(scaled_data_train, window_size, window_size)


	### Build a LSTM model and log model summary to Neptune ###
	def Run_LSTM(X_train, layer_units=50, logNeptune=True, NeptuneProject=None):
		inp = Input(shape=(X_train.shape[1], 1))

		x = LSTM(units=layer_units, return_sequences=True)(inp)
		x = LSTM(units=layer_units)(x)
		out = Dense(1, activation='linear')(x)
		model = Model(inp, out)

		# Compile the LSTM neural net
		model.compile(loss='mean_squared_error', optimizer='adam')

		## log to Neptune, e.g., set NeptuneProject = npt_exp
		if logNeptune:
			model.summary(print_fn=lambda x: NeptuneProject.log_text('model_summary', x))

		return model


	model = Run_LSTM(X_train, layer_units=layer_units, logNeptune=False, NeptuneProject=None)

	history = model.fit(X_train, y_train, epochs=cur_epochs, batch_size=cur_batch_size,
	                    verbose=1, validation_split=0.1, shuffle=True)


	# predict stock prices using past window_size stock prices
	def preprocess_testdat(data=stockprices, scaler=scaler, window_size=window_size, test=test):
		raw = data['close'][len(data) - len(test) - window_size:].values
		raw = raw.reshape(-1, 1)
		raw = scaler.transform(raw)

		X_test = []
		for i in range(window_size, raw.shape[0]):
			X_test.append(raw[i - window_size:i, 0])

		X_test = np.array(X_test)

		X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
		return X_test


	X_test = preprocess_testdat()

	predicted_price_ = model.predict(X_test)
	predicted_price = scaler.inverse_transform(predicted_price_)

	# Plot predicted price vs actual closing price
	test['Predictions_lstm'] = predicted_price

	# Evaluate performance
	rmse_lstm = calculate_rmse(np.array(test['close']), np.array(test['Predictions_lstm']))
	mape_lstm = calculate_mape(np.array(test['close']), np.array(test['Predictions_lstm']))
	print(test)
	print("RMSE: ", rmse_lstm)
	print("MAPE: ", mape_lstm)



	# npt_exp.send_metric('RMSE', rmse_lstm)
	# npt_exp.log_metric('RMSE', rmse_lstm)
	#
	# npt_exp.send_metric('MAPE (%)', mape_lstm)
	# npt_exp.log_metric('MAPE (%)', mape_lstm)


	### Plot prediction and true trends and log to Neptune
	def plot_stock_trend_lstm(train, test, logNeptune=True):
		fig = plt.figure(figsize=(200, 10))
		plt.plot(train['date'], train['close'], label='Train Closing Price')
		plt.plot(test['date'], test['close'], label='Test Closing Price')
		plt.plot(test['date'], test['Predictions_lstm'], label='Predicted Closing Price')
		plt.title('LSTM Model')
		plt.xlabel('date')
		plt.ylabel('Stock Price ($)')
		plt.legend(loc="upper left")
		plt.show()

		# if logNeptune:
		# 	npt_exp.log_image('Plot of Stock Predictions with LSTM', fig)


	plot_stock_trend_lstm(train, test, logNeptune=False)


	# generate the multi-step forecasts
	def multi_step_forecasts(n_past, n_future):

		pred = test.tail(window_size + 1)
		pred.loc[:, ('close')] = pred['Predictions_lstm']
		pred['date'] = pred['date'] + pd.DateOffset(1)
		print("PRED: ")
		print(pred)
		X_test1 = preprocess_testdat(data=pred)

		predicted_price1_ = model.predict(X_test1)
		predicted_price1 = scaler.inverse_transform(predicted_price1_)
		pred = pred.tail(1)
		pred['Predictions_lstm'] = predicted_price1
		print(pred)


	# forecast the next 30 days
	# df1 = multi_step_forecasts(n_past=0, n_future=30)
	# print("DF1: ===========")
	# print(df1)