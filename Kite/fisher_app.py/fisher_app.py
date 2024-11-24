import math
import sys
import time

from kite_trade import *
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
import yfinance as yf
from nsetools import Nse


pd.set_option('display.max_columns', None)


class FisherApp:

	now = datetime.datetime.now()
	def __init__(self,enctoken):
		self.symbol = None
		self.nse = None
		self.df = pd.DataFrame()
		self.days = 10
		self.enctoken = enctoken
		self.kite = KiteApp(enctoken=self.enctoken)

	def get_data(self, interval="15minute", isTail5=True):
		now = datetime.datetime.now()
		from_datetime = now - relativedelta(days=self.days)
		to_datetime = now
		self.get_instrument_token()
		if self.instrument_token == 0:
			return self.instrument_token, self.instrument_token
		time.sleep(1)
		res_list = self.kite.historical_data(self.instrument_token, from_datetime, to_datetime, interval,continuous=False, oi=False)
		data = pd.DataFrame.from_dict(res_list)
		try:
			data['date'] = pd.to_datetime(data['date'])
			data.set_index('date', inplace=True)

			data['high_'] = data['high']
			data['low_'] = data['low']
		except:
			print("EXCEPTION: " + str(self.symbol))
			return 0
		return data

	def get_nse_instruments(self):
		return self.kite.instruments('NSE')

	def get_nse_trading_symbol(self):
		if self.nse == None:
			self.nse = self.kite.instruments('NSE')
		nse_data = pd.DataFrame(self.nse)
		filtered_df = nse_data[(~nse_data['tradingsymbol'].str.contains('-S|-N|-Z|SGB|-GS|-Y|-A|-E|-X')) & (nse_data['name'] != "") & (nse_data['lot_size'] == 1) & (nse_data['exchange'] == 'NSE') & (nse_data['segment'] == 'NSE') & (nse_data['instrument_type'] == 'EQ')]
		filtered_df.to_csv(f'data/stock_symbol.csv', mode='w')
		sys.exit()
		return filtered_df['tradingsymbol'].values

	def get_instrument_token(self):
		if self.nse == None:
			self.nse = self.kite.instruments('NSE')
		nse_data = pd.DataFrame(self.nse)
		try:
			self.instrument_token = nse_data[nse_data.tradingsymbol == self.symbol].instrument_token.values[0]
		except:
			self.instrument_token = 0
		return self.instrument_token

	def round_value(self,val):
		return max(min(val, 0.999), -0.999)

	def get_tradingview_code_fisher_index(self):

		#df = self.get_data(interval='day')
		# df_len =0
		# if isinstance(df, int):
		# 	return None
		# else:
		# 	df_len = len(df)
		# 	if df_len < 100:
		# 		return None
		df = stock_code = 'HEROMOTOCO.NS'

		# Fetch stock data using yfinance
		stock = yf.Ticker(stock_code)

		# Get current stock data (delayed by a few minutes)
		stock_info = stock.history(period="1y")

		df['hl2'] = (df['High'] + df['Low']) / 2  # Calculate hl2
		# Set parameters
		length = 9  # Length for the Fisher Transform

		# Initialize columns
		df['value'] = np.nan  # This will store the normalized values
		df['fish1'] = np.nan  # Fisher Transform 1
		df['fish2'] = np.nan  # Fisher Transform 2
		date = df.index.tolist()
		# Calculate Fisher Transform
		for i in range(length, len(df)):

			# Calculate high_ and low_ over the look-back period
			high_ = df['hl2'].iloc[i - length + 1:i + 1].max()  # Highest high over the look-back period
			low_ = df['hl2'].iloc[i - length + 1:i + 1].min()  # Lowest low over the look-back period

			# Normalize the value with epsilon to avoid division by zero
			previous_value = np.nan_to_num(df['value'].iloc[i - 1], nan=0.0)
			epsilon = 1e-9  # A small constant to prevent division by zero
			# Fisher value normalization
			value = 0.66 * ((df['hl2'].iloc[i] - low_) / (high_ - low_ + epsilon) - 0.5) + 0.67 * previous_value

			# Clip the value to avoid logarithmic issues
			value = self.round_value(value)
			df.at[df.index[i], 'value'] = value

			# Calculate the Fisher Transform
			previous_fish = np.nan_to_num(df['fish1'].iloc[i - 1], nan=0.0)
			fish1 = 0.5 * math.log((1 + value) / (1 - value)) + 0.5 * previous_fish

			# Store the result in the DataFrame
			df.at[df.index[i], 'fish1'] = fish1
			df.at[df.index[i], 'value'] = value
			df.at[df.index[i], 'high'] = high_
			df.at[df.index[i], 'low'] = low_

		# Set fish2 to be the previous value of fish1 (shifted by 1 period)
		df['fish2'] = df['fish1'].shift(1)

		# Print or return the resulting DataFrame
		print(f"Fisher Value for {self.symbol} {df['fish1'].tail(1).values[0]}")
		new_df = pd.DataFrame({
			'symbol': [self.symbol],
			'date': [str(date[i])],
			'fisher_value': [str(df['fish1'].tail(1).values[0])]
		})
		self.df = pd.concat([self.df, new_df], ignore_index=True)

