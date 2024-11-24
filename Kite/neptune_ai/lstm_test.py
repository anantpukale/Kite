from kite_trade import *
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

from keras.layers import Dropout
from keras_tuner.tuners import RandomSearch

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


class lstm_trade:
	# 20 days to represent the 22 trading days in a month
	window_size = 50
	CURRENT_MODEL = 'LSTM'
	stockprices = ""

	def __init__(self, symbol):
		self.whatsapp_msg = ""
		self.symbol = symbol
		self.is_black_listed = False
		# qr_code = 'DL3EP6ZJHJU6R54G2STJGHYAHQCIKX3R'
		# totp = pyotp.TOTP(qr_code)
		# twofa = totp.now()  # Login Pin or TOTP
		# user_id = "BF6533"  # Login Id
		# password = "Vinod@277401"  # Login password
		# enctoken = get_enctoken(user_id, password, twofa)
		enctoken = "pofOPmSI2yg4kfioUa+1zaq/XHDoWW9MK8/zBONutvnZE/rPydnjql0qarxU3gjc1ecbdeQg1lDfeUjI0+VkYkA1KFTZIpC+oRIiBDrYahyjiWbxG4WZOw=="
		self.kite = KiteApp(enctoken=enctoken)

	def get_data(self, interval="15minute"):
		from_datetime = datetime.datetime.now() - relativedelta(days=800)
		to_datetime = datetime.datetime.now()
		self.get_instrument_token()
		res_list = self.kite.historical_data(self.instrument_token, from_datetime, to_datetime, interval,
		                                     continuous=False, oi=False)
		data = pd.DataFrame.from_dict(res_list)
		data['5EMA'] = data['close'].ewm(span=5, adjust=False).mean()
		data['prev_open'] = data['open'].shift(1)
		data['pre_prev_open'] = data['open'].shift(2)
		data['prev_low'] = data['low'].shift(1)
		data['pre_prev_low'] = data['low'].shift(2)
		data['prev_high'] = data['high'].shift(1)
		data['pre_prev_high'] = data['high'].shift(2)
		data['prev_5EMA'] = data['5EMA'].shift(1)
		data['pre_prev_5EMA'] = data['5EMA'].shift(2)
		data['prev_close'] = data['close'].shift(1)
		data['pre_prev_close'] = data['close'].shift(2)
		# data['div'] = (data['5EMA'] - data['close']) / data['5EMA'] * 100
		#data = data.tail(1)
		return data

	def get_instrument_token(self):
		nse = self.kite.instruments('NSE')
		nse_data = pd.DataFrame(nse)
		self.instrument_token = nse_data[nse_data.tradingsymbol == self.symbol].instrument_token.values[0]
		return self.instrument_token

	def get_stockprices(self):
		self.stockprices = self.get_data(interval='day')
		#### Train-Test split for time-series ####
		test_ratio = 0.2
		training_ratio = 1 - test_ratio

		train_size = int(training_ratio * len(self.stockprices))
		test_size = int(test_ratio * len(self.stockprices))

		print("train_size: " + str(train_size))
		print("test_size: " + str(test_size))

		self.train = self.stockprices[:train_size][['date', 'close']]
		self.test = self.stockprices[train_size:][['date', 'close']]
		# self.stockprices_tail = self.stockprices.tail(1)
		# self.stockprices_tail.loc[:, ('close')] = self.stockprices_tail['prev_close'] + 100
		# # self.stockprices_tail.loc[:, ('date')] = self.stockprices_tail['date']  + pd.DateOffset(1)
		# self.stockprices_tail['date'] = self.stockprices_tail['date'] + pd.DateOffset(1)
		# self.stockprices = self.stockprices.append(self.stockprices_tail)
		self.stockprices = self.stockprices.set_index('date')

	def build_model(self,hp):
		model = Sequential()
		model.add(LSTM(hp.Int('input_unit', min_value=32, max_value=512, step=32), return_sequences=True,
		               input_shape=(self.X_train.shape[1], self.X_train.shape[2])))
		for i in range(hp.Int('n_layers', 10, 20)):
			model.add(LSTM(hp.Int(f'lstm_{i}_units', min_value=32, max_value=512, step=32), return_sequences=True))
		model.add(LSTM(hp.Int('layer_2_neurons', min_value=32, max_value=512, step=32)))
		model.add(Dropout(hp.Float('Dropout_rate', min_value=0, max_value=0.05, step=0.05)))
		model.add(Dense(self.y_train.shape[1],
		                activation=hp.Choice('dense_activation', values=['relu', 'sigmoid'], default='relu')))
		model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mse'])
		return model

	def get_best_model(self):
		self.get_stockprices()

		print(self.stockprices)
		self.scaler = StandardScaler()
		scaled_data = self.scaler.fit_transform(self.stockprices[['close']])
		scaled_data_train = scaled_data[:self.train.shape[0]]
		self.X_train, self.y_train = self.extract_seqX_outcomeY(scaled_data_train, self.window_size, self.window_size)
		tuner = RandomSearch(
			self.build_model,
			objective='mse',
			max_trials=2,
			executions_per_trial=1
		)
		X_test = self.preprocess_testdat(data=self.stockprices, scaler=self.scaler, window_size=self.window_size,
		                                 test=self.test)

		tuner.search(
			x=self.X_train,
			y=self.y_train,
			epochs=15,
			batch_size=20
		)
		best_model = tuner.get_best_models(num_models=1)[0]
		#predicted_price_  = best_model.predict(X_test[0].reshape((1, X_test[0].shape[0], X_test[0].shape[1])))
		predicted_price_ = best_model.predict(X_test)
		predicted_price = self.scaler.inverse_transform(predicted_price_)

		# Plot predicted price vs actual closing price
		#self.test = self.test.tail(1)
		print(str(len(self.test)) + " " + str(len(predicted_price)))
		self.test['Predictions_lstm'] = predicted_price
		print(self.test)

		# Evaluate performance
		rmse_lstm = self.calculate_rmse(np.array(self.test['close']), np.array(self.test['Predictions_lstm']))
		mape_lstm = self.calculate_mape(np.array(self.test['close']), np.array(self.test['Predictions_lstm']))

		print("layer_units: " + str(layer_units) + " cur_epochs " + str(cur_epochs) + " RMSE: " + str(
			rmse_lstm) + " MAPE: " + str(mape_lstm))
		self.plot_stock_trend_lstm(self.train, self.test, logNeptune=False)

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

	def run(self,layer_units, optimizer, cur_epochs, cur_batch_size):
		self.get_stockprices()

		# layer_units, optimizer = 100, 'adam'
		# cur_epochs = 5
		# cur_batch_size = 20

		cur_LSTM_pars = {'units': layer_units,
		                 'optimizer': optimizer,
		                 'batch_size': cur_batch_size,
		                 'epochs': cur_epochs
		                 }

		# scale
		self.scaler = StandardScaler()
		scaled_data = self.scaler.fit_transform(self.stockprices[['close']])
		scaled_data_train = scaled_data[:self.train.shape[0]]

		X_train, y_train = self.extract_seqX_outcomeY(scaled_data_train, self.window_size, self.window_size)
		model = self.Run_LSTM(X_train, layer_units=layer_units, logNeptune=False, NeptuneProject=None)

		history = model.fit(X_train, y_train, epochs=cur_epochs, batch_size=cur_batch_size,
		                    verbose=1, validation_split=0.1, shuffle=True)

		X_test = self.preprocess_testdat(data=self.stockprices, scaler=self.scaler, window_size=self.window_size, test=self.test)

		predicted_price_ = model.predict(X_test)
		predicted_price = self.scaler.inverse_transform(predicted_price_)

		# Plot predicted price vs actual closing price
		self.test['Predictions_lstm'] = predicted_price
		print(self.test)

		# Evaluate performance
		rmse_lstm = self.calculate_rmse(np.array(self.test['close']), np.array(self.test['Predictions_lstm']))
		mape_lstm = self.calculate_mape(np.array(self.test['close']), np.array(self.test['Predictions_lstm']))

		print("layer_units: "+str(layer_units) + " cur_epochs " +  str(cur_epochs) + " RMSE: " + str(rmse_lstm)+" MAPE: " + str(mape_lstm))
		return ("layer_units: "+str(layer_units) + " cur_epochs " +  str(cur_epochs) + " RMSE: " + str(rmse_lstm)+" MAPE: " + str(mape_lstm))

	### Build a LSTM model and log model summary to Neptune ###
	def Run_LSTM(self, X_train, layer_units=50, logNeptune=True, NeptuneProject=None):
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

	#### Define helper functions to calculate the metrics RMSE and MAPE ####
	def calculate_rmse(self, y_true, y_pred):
		"""
		Calculate the Root Mean Squared Error (RMSE)
		"""
		rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
		return rmse

	### The effectiveness of prediction method is measured in terms of the Mean Absolute Percentage Error (MAPE) and RMSE
	def calculate_mape(self, y_true, y_pred):
		"""
		Calculate the Mean Absolute Percentage Error (MAPE) %
		"""
		y_pred, y_true = np.array(y_pred), np.array(y_true)
		mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
		return mape

	## Split the time-series data into training seq X and output value Y
	def extract_seqX_outcomeY(self, data, N, offset):
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

	def preprocess_testdat(self, data=stockprices, scaler=None, window_size=window_size, test=None):
		raw = data['close'][len(data) - len(test) - window_size:].values
		raw = raw.reshape(-1, 1)
		raw = scaler.transform(raw)

		X_test = []
		for i in range(window_size, raw.shape[0]):
			X_test.append(raw[i - window_size:i, 0])

		X_test = np.array(X_test)

		X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
		return X_test


repeat = 1
trader = lstm_trade("NIFTY 50")
layer_units, optimizer = 400, 'adam'
cur_epochs = 200
cur_batch_size = 20
results = []
trader.get_best_model()
# while(repeat > 0):
# 	# layer_units = layer_units + 100
# 	# cur_epochs = cur_epochs + 50
# 	results.append(trader.run(layer_units, optimizer, cur_epochs, cur_batch_size))
# 	repeat -=1
#
# while len(results)>0:
# 	print(results.pop())

print("Test END")

