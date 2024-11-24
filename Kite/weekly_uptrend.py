import math
import time

from kite_trade1 import *
import datetime
from dateutil.relativedelta import relativedelta
from pyxirr import xirr
from rsi_calculator import rsi
import plotly.express as px
import plotly.graph_objs as go
from tradingview_ta import TA_Handler, Interval
from nselib import capital_market


#from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
import numpy as np
import pandas as pd
import yfinance as yf

pd.set_option('display.max_columns', None)


class WeekUptrendTradeApp:
	BUDGET: int = 10000

	now = datetime.datetime.now()
	today9_45am = now.replace(hour=9, minute=45, second=0, microsecond=0)
	today9_30am = now.replace(hour=9, minute=30, second=0, microsecond=0)
	today9_15am = now.replace(hour=9, minute=15, second=0, microsecond=0)

	unrealised_pnl = 0
	sell_value = 0
	buy_value = 0
	sell_quantity = 0
	buy_quantity = 0

	def __init__(self):
		self.whatsapp_msg = ""
		self.symbol = None
		self.is_black_listed = False
		self.nse = None
		self.df = pd.DataFrame()
		self.days = 10
		# qr_code = 'DL3EP6ZJHJU6R54G2STJGHYAHQCIKX3R'
		# totp = pyotp.TOTP(qr_code)
		# twofa = totp.now()  # Login Pin or TOTP
		# user_id = "BF6533"  # Login Id
		# password = " "  # Login password
		# enctoken = get_enctoken(user_id, password, twofa) 
		enctoken = "aeqKJ0OslipU8tq/TDO1MB7w8LLuMPq+nXBqNRQHra0zGQgxkYIds0gYeU7NNZgYT4/HH3qy7a9hGoPDiFV35uxN3nLxAA3SPD7FynLT4yRYFXD8dOg5aw=="
		self.kite = KiteApp(enctoken=enctoken)

	monthy_investable_count = 0
	monthy_investable_amount = 0
	ten_percent_investable_count = 0
	ten_percent_invested_count = 0
	ten_percent_investable_amount = 0
	ten_percent_invested_amount =0
	xirr_monthly=0
	xirr_ten_percent=0
	date_mthly_arr=[]
	amt_mthly_arr=[]
	date_ten_per_arr = []
	amt_ten_per_arr = []


	def  get_data(self, interval="15minute", isTail5=True):
		# Example string date input
		date_string = "2022-01-01 14:30:00"
		# Convert the string to a datetime object
		#now = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
		now = datetime.datetime.now()
		from_datetime1 = now - relativedelta(days=self.days)
		#from_datetime = from_datetime1.strftime('%Y-%m-%d %H:%M:%S')
		#to_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		from_datetime = from_datetime1
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

			data['5EMA'] = data['close'].ewm(span=5, adjust=False).mean()
			data['89EMA'] = data['close'].ewm(span=89, adjust=False).mean()
			data['5ema_volume'] = data['volume'].ewm(span=5, adjust=False).mean()
		except:
			print("EXCEPTION: " + str(self.symbol))
			return 0
		data['prev_open'] = data['open'].shift(1)
		data['pre_prev_open'] = data['open'].shift(2)
		data['prev_low'] = data['low'].shift(1)
		data['pre_prev_low'] = data['low'].shift(2)
		data['prev_high'] = data['high'].shift(1)
		data['pre_prev_high'] = data['high'].shift(2)
		data['prev_5EMA'] = data['5EMA'].shift(1)
		data['pre_prev_5EMA'] = data['5EMA'].shift(2)
		data['prev_89EMA'] = data['89EMA'].shift(1)
		data['pre_prev_89EMA'] = data['89EMA'].shift(2)
		data['prev_close'] = data['close'].shift(1)
		data['pre_prev_close'] = data['close'].shift(2)
		data['close_open'] =  data['close'] - data['open']
		data['binary'] = data['close'] > data['open']

		#data = data.tail(1)
		return data

	def get_yf_data(self, period='1wk'):
		df = pd.DataFrame()
		now = datetime.datetime.now()
		end_date = now.strftime('%Y-%m-%d')
		for days in range(1000,self.days,1000):
			from_datetime1 = now - relativedelta(days=days)
			start_date = from_datetime1.strftime('%Y-%m-%d')
			# Fetch the data using yfinance
			index_data = capital_market.capital_market_data.index_data(index=self.symbol,
			                                       from_date=start_date,
			                                       to_date=end_date)
			index_data['TIMESTAMP'] = pd.to_datetime(index_data['TIMESTAMP'], format='%d-%m-%Y')
			index_data = index_data.sort_values('TIMESTAMP').reset_index(drop=True)
			df = pd.concat([df,index_data])
			print(index_data)
			end_date = start_date
		return df

	def get_nse_instruments(self):
		return self.kite.instruments('NSE')

	def get_nse_trading_symbol(self):
		if self.nse == None:
			self.nse = self.kite.instruments('NSE')
		nse_data = pd.DataFrame(self.nse)
		filtered_df = nse_data[(nse_data['exchange'] == 'NSE') & (nse_data['segment'] == 'NSE') & (nse_data['instrument_type'] == 'EQ')]
		return filtered_df['tradingsymbol'].values

	def get_instrument_token(self):
		if self.nse == None:
			self.nse = self.kite.instruments('NSE')
		nse_data = pd.DataFrame(self.nse)
		#nse_data = pd.read_csv("out.csv")
		#nse_data.to_csv('out.csv', sep=',', encoding='utf-8')
		#filtered_df = nse_data[(nse_data['exchange'] == 'NSE') & (nse_data['segment'] == 'NSE') & (nse_data['instrument_type'] == 'EQ')]
		#filtered_df = nse_data[nse_data['segment'].str.contains('INDICES', case=False, na=False)]
		#filtered_df.to_csv('data/nse.csv', index=False)
		try:
			self.instrument_token = nse_data[nse_data.tradingsymbol == self.symbol].instrument_token.values[0]
		except:
			#print("Exception: ",self.symbol)
			self.instrument_token = 0
		return self.instrument_token

	def get_weekly_scan(self):
		data = self.get_data(interval='week')
		if self.instrument_token == 0:
			return 0
		# Create TRADE column with default value NO assuming no trade on the record
		data['TRADE'] = 'NO'
		# Check Buy condition meets or not if yes then update the value in TRADE Column to YES
		condition1_1 = (data['close'] > data['89EMA']) | ((data['close'] * 0.01) > (abs(data['close'] - data['89EMA'])))
		condition1_2 = (data['close'] > data['5EMA'])
		#condition1_3 = ((abs(data['5EMA'] - data['89EMA']) > data['close'] * 0.01) & (data['close'] * 0.01 > abs(data['close'] - data['89EMA'])))
		#condition1_3 = (((data['89EMA'] - data['5EMA']) < data['close'] * 0.01) & (
		#			data['close'] * 0.01 > abs(data['close'] - data['89EMA'])))
		condition1_3 = ((data['close'] * 0.01) > (data['close'] - data['89EMA'])) | ((data['5EMA'] * 0.01) > (abs(data['5EMA'] - data['89EMA'])))
		condition1_4 = (data['5EMA'] > data['prev_5EMA']) & (data['prev_5EMA'] > data['pre_prev_5EMA'])
		# condition1_1 = (data['89EMA'] > data['prev_89EMA']) & (data['prev_89EMA'] > data['pre_prev_89EMA'])
		# condition2_1 = (data['89EMA'] * 0.001) > (abs(data['89EMA'] - data['prev_89EMA']))
		condition2_2 = (data['5EMA'] * 0.01) > (data['5EMA'] - data['89EMA'])
		condition_4 = (data['5ema_volume'] > 1000000)
		#| (condition2_1 & condition2_2)
		data.loc[ condition1_1 & condition1_2 & condition1_3  & condition_4 & condition1_4  , 'TRADE'] = 'YES'
		data = data.loc[data['TRADE'] == 'YES']

		if (len(data) > 0):
			print("BEST FIT:", self.symbol)
			#print("data['close'] -data['89EMA']: "+ str(data['close'] -data['89EMA'])+ "data['close'] * 0.01: "+ str(data['close'] * 0.01) + " data['prev_close'] "+ str(data['prev_close'])
			#      + " data['prev_open'] " + str(data['prev_open']) + " data['close'] " + str(data['close']))
			#print("====================")

	def get_indices_scan(self):
		data = self.get_data(interval='week')
		#data = self.get_yf_data(period='1w')
		if self.instrument_token == 0:
			return 0
		data['5EMA'] = pd.to_numeric(data['5EMA'], errors='coerce')
		data['89EMA'] = pd.to_numeric(data['89EMA'], errors='coerce')
		data['percentage_difference'] = ((data['close'] - data['89EMA']) / data['89EMA'] ) * 100
		data['is_increased'] = data['89EMA'] > data['prev_89EMA']
		true_count = data['is_increased'].sum()
		false_count =  len(data) - true_count

		min = data['percentage_difference'].round(2).min()
		max = data['percentage_difference'].round(2).max()
		avg = data['percentage_difference'].mean().round(2)
		per_diff = data['percentage_difference'].tail(1).round(2).min()

		new_df = pd.DataFrame({
			'symbol': [self.symbol],
			'percent_diff': [str(per_diff)],
			'min': [str(min)],
			'max': [str(max)],
			'avg': [str(avg)],
			'relative_diff': [str(avg - per_diff)]
		})
		self.df = pd.concat([self.df, new_df], ignore_index=True)
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print(self.symbol + " per diff: " + str(per_diff) + " min:" + str(min) + " max:" + str(max) + " avg:" + str(
			avg) + " relative_diff:" + str(avg - per_diff))

		if (false_count < true_count):

			print(f"BEST FIT: {self.symbol} and true count: {true_count} and flase count: {false_count}")
			#print("====================")

	def get_plot(self):
		data = self.get_data(interval='week')
		if self.instrument_token == 0:
			return 0
		data['5EMA'] = pd.to_numeric(data['5EMA'], errors='coerce')
		data['89EMA'] = pd.to_numeric(data['89EMA'], errors='coerce')
		data['percentage_difference'] = ((data['close'] - data['89EMA']) / data['89EMA'] ) * 100
		min = data['percentage_difference'].round(2).min()
		max = data['percentage_difference'].round(2).max()
		avg = data['percentage_difference'].mean().round(2)
		data['rolling_average_close'] = data['percentage_difference'].rolling(window=12).mean()
		current_diff = data['percentage_difference'].tail(1).round(2).min()
		rolling_average_close = data['rolling_average_close'].tail(1).round(2).min()
		data['prev_close'] = data['close'].shift(1)
		rolling_average_close_prev = data['rolling_average_close'].shift(2).min()
		print(self.symbol +" current diff: "+str( current_diff )  + " min:"+ str(min) + " max:"+ str(max) + " avg:"+ str(avg) + " relative_diff:"+ str(avg - current_diff) + " rolling_average_close_prev:" + str(rolling_average_close_prev))
		new_df = pd.DataFrame({
			'symbol': [self.symbol],
			'percent_diff': [str(current_diff)],
			'min': [str(min)],
			'max': [str(max)],
			'avg': [str(avg)],
			'relative_diff': [str(avg - current_diff)]
		})
		self.df = pd.concat([self.df, new_df], ignore_index=True)

		#if( current_diff > rolling_average_close and rolling_average_close_prev > current_diff):
		fig = px.line(data, x=data.index, y='percentage_difference', title=f'Percent Difference: {current_diff} Over Time for {self.symbol} ')
		fig.add_trace(go.Scatter(x=data.index, y=[avg]*len(data), mode='lines', name=f'Average: {avg}', line=dict(dash='dash',color='red')))
		fig.add_trace(go.Scatter(x=data.index, y=data['rolling_average_close'], mode='lines', name=f'Rolling 12 Week Average: {rolling_average_close}', line=dict(dash='dash')))
		fig.show()

	def get_probability_next_value(self, data, val):
		total_records = data.shape[0]
		close_above_threshold = data[data['close'] > val].shape[0]
		probability = close_above_threshold / total_records
		return probability

	def round_value(self,val):
		return max(min(val, 0.999), -0.999)

	def get_tradingview_code_fisher_index(self):

		df = self.get_data(interval='day')
		df_len =0
		if isinstance(df, int):
			return None
		else:
			df_len = len(df)
			if df_len < 100:
				return None
		#symbol = "HEROMOTOCO.NS"  # NSE ticker symbol for Hero MotoCorp
		#df = yf.download(f"{self.symbol}.NS", start="2023-09-01", end="2024-09-20")
		# df1 = df
		# high = df['high']
		# low = df['low']
		# df['high'] = df['high']
		# df['low'] = df['low']
		df['hl2'] = (df['high'] + df['low']) / 2  # Calculate hl2
		#df['hl2'] =  df['hl2'].round(2)
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
			epsilon = 1e-9  # A small constant to prevent division by zero
			previous_value = np.nan_to_num(df['value'].iloc[i - 1], nan=0.0)

			# Fisher value normalization
			#print(f"{date[i]}: 0.66 * (({df['hl2'].iloc[i]} - {low_}) / ({high_} - {low_} ) - 0.5) + 0.67 * {previous_value}")
			value = 0.66 * ((df['hl2'].iloc[i] - low_) / (high_ - low_ + epsilon ) - 0.5) + 0.67 * previous_value

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
		#print(df[['hl2','high','low','value', 'fish1']])
		print(f"Fisher Value for {self.symbol} {df['fish1'].tail(1).values[0]}")
		new_df = pd.DataFrame({
			'symbol': [self.symbol],
			'date': [str(date[i])],
			'fisher_value': [str(df['fish1'].tail(1).values[0])]
		})
		self.df = pd.concat([self.df, new_df], ignore_index=True)

	def get_fisher_index(self):


		# Step 1: Download historical stock data for Hero MotoCorp (HEROMOTOCO) from Yahoo Finance
		#self.symbol = 'HEROMOTOCO.NS'
		#data = yf.download(ticker, start="2023-01-01", end="2023-12-31")
		data = self.get_data(interval='day')
		# Step 2: Define base and current period (use your chosen periods)
		# Assuming base period is Jan 2023 and current period is Dec 2023
		look_back_period = 9
		base_period = data.loc['2024-09'].tail(9)
		current_period = data.loc['2024-09-20']
		# for i in range(1,look_back_period):
		# 	df = data.iloc[-i]
		# 	df['close'] = 0
		# 	current_period.append(df)

		# Step 3: Extract closing prices and volumes
		P0 = base_period['close'].values
		Q0 = base_period['volume'].values
		Pt = current_period['close']#.values
		Qt = current_period['volume']#.values
		# day_shift = int(self.days / 2)
		# P0 = data['close'].shift(day_shift).fillna(0).values
		# Q0 =  data['volume'].shift(day_shift).fillna(0).values
		# Pt = data['close'].values
		# Qt =  data['volume'].values

		# # Step 4: Calculate Laspeyres Index
		laspeyres_index = np.sum(Pt * Q0) / np.sum(P0 * Q0)
		#laspeyres_index = Pt * Q0 / P0 * Q0
		# # Step 5: Calculate Paasche Index
		paasche_index = np.sum(Pt * Qt) / np.sum(P0 * Qt)
		#paasche_index = Pt * Qt / P0 * Qt
		# # Step 6: Calculate Fisher Index
		fisher_index = np.sqrt(laspeyres_index * paasche_index)
		#LPI = (np.sum(Pt * Q0) / np.sum(P0 * Q0))

		# Paasche Price Index (PPI)
		#PPI = (np.sum(Pt * Qt) / np.sum(P0 * Qt))

		# Fisher Price Index
		#fisher_index = np.sqrt(LPI * PPI)

		# Step 7: Store the results in a pandas DataFrame
		data_output = {
			'Index': [ 'Fisher Index'],
			'Value': [ fisher_index]
		}
		#'Laspeyres Index', 'Paasche Index',
		df_output = pd.DataFrame(data_output)

		# Step 8: Write the DataFrame to an Excel file
		#output_filename = 'heromotocorp_fisher_index_results.xlsx'
		#df_output.to_excel(output_filename, index=False)

		print(f"Fisher Index calculated and results saved to {data_output}")

	def get_fisher_log(self):
		# import numpy as np
		# import pandas as pd
		#
		# # Sample price data (replace with actual price data)
		# price_data = [50, 52, 51, 53, 55, 54, 56, 58, 57, 59, 60, 61]

		# Convert to pandas DataFrame
		#df = pd.DataFrame(price_data, columns=['Price'])
		df = self.get_data(interval='day')
		# Choose the look-back period
		look_back_period = 9

		# Initialize a list to store Fisher Transform values
		fisher_values = []

		# Calculate Fisher Transform
		for i in range(len(df)):
			if i < look_back_period - 1:
				# Not enough data for look-back period
				fisher_values.append(np.nan)
				continue

			# Select the look-back period prices
			look_back_prices = df['close'][i - look_back_period + 1:i + 1]

			# Calculate X
			max_price = look_back_prices.max()
			min_price = look_back_prices.min()

			# Normalize price to -1 to +1
			X = (2 * (df['close'].iloc[i] - min_price) / (max_price - min_price)) - 1

			# Apply Fisher Transform formula
			if X > 0.99:
				X = 0.99  # Capping to avoid division by zero
			elif X < -0.99:
				X = -0.99  # Capping to avoid division by zero

			fisher_transform = 0.5 * np.log((1 + X) / (1 - X))

			# Add the Fisher Transform value to the list
			fisher_values.append(fisher_transform)

		# Add Fisher Transform values to DataFrame
		df['Fisher Transform'] = fisher_values

		# Display the result
		print(df)

	# def get_prob_by_ARIMA(self, df):
	# 	# Load and prepare the data
	#
	# 	#df[df.date] = pd.to_datetime(df[df.date])
	# 	#df.set_index('date', inplace=True)
	#
	# 	# Ensure the data is sorted by date
	# 	df = df.sort_index()
	#
	# 	# Extract the 'close' column
	# 	close_series = df['close']
	#
	# 	# Step 2: Check Stationarity and Differencing if necessary
	# 	# (using pmdarima to automatically determine the differencing term)
	# 	model = pm.auto_arima(close_series, seasonal=False, stepwise=True, suppress_warnings=True)
	#
	# 	# Fit the ARIMA model
	# 	arima_model = ARIMA(close_series, order=model.order)
	# 	arima_result = arima_model.fit()
	#
	# 	# Forecast future values (let's say next 30 days)
	# 	forecast = arima_result.get_forecast(steps=30)
	# 	forecast_mean = forecast.predicted_mean
	# 	forecast_ci = forecast.conf_int()
	#
	# 	# Step 5: Simulate future values
	# 	simulations = []
	# 	for i in range(1000):  # 1000 simulations
	# 		simulation = arima_result.simulate(nsimulations=10, steps=30)
	# 		simulations.append(simulation[-1])  # Get the value on the target date
	#
	# 	# Step 6: Calculate probability
	# 	simulations = np.array(simulations)
	# 	num = 48000
	# 	probability = np.mean(simulations > num)
	# 	print(f'Probability that close > {num}: {probability:.2%}')
	#
	# def get_bayes_probability(self, df):
	# 	num = 51000
	# 	recent_days = 89
	# 	# Calculate Prior Probability P(A)
	# 	# P(A): Probability that the close value exceeds 49,000
	# 	prior_probability = len(df[df['close'] < num]) / len(df)
	#
	# 	# Calculate Likelihood P(B|A)
	# 	# P(B|A): Probability of observing the current pattern given that the close value exceeds 49,000
	# 	# Here we'll assume a simplistic pattern check (e.g., last 5 days trend)
	# 	#df['close'].shift(-1) < 49000) &
	# 	recent_data = df['close'].tail(30) #.loc['2024-08-04':'2024-08-15']
	# 	recent_mean = recent_data.mean()
	# 	similar_patterns = df[(df['close'].shift(-1) > num) | (df['close'].rolling(30).mean() > recent_data.mean())]
	# 	rolling_mean = df['close'].rolling(30).mean()
	# 	len_df = len(df[df['close'] > num])
	# 	likelihood = len(similar_patterns) / len(df[df['close'] > num])
	#
	# 	# Calculate Marginal Probability P(B)
	# 	# P(B): Probability of observing the current pattern regardless of the close value
	# 	overall_pattern_occurrence = len(df[df['close'].rolling(30).mean() > recent_data.mean()])
	# 	marginal_probability = overall_pattern_occurrence / len(df)
	#
	# 	# Apply Bayes' Theorem P(A|B)
	# 	posterior_probability = (likelihood * prior_probability) / marginal_probability
	#
	# 	print(f'Prior Probability P(A): {prior_probability:.4f}')
	# 	print(f'Likelihood P(B|A): {likelihood:.4f}')
	# 	print(f'Marginal Probability P(B): {marginal_probability:.4f}')
	# 	print(f'Posterior Probability P(A|B): {posterior_probability:.4f}')
	#
	# 	# Interpretation
	# 	print(f'The probability that the close value will exceed {num} on 16-08-2024 is {posterior_probability:.2%}')

	def get_weekly_scan1(self):
		data = self.get_data(interval='week')
		count = 1
		# Create TRADE column with default value NO assuming no trade on the record
		data['TRADE'] = 'NO'
		# Check Buy condition meets or not if yes then update the value in TRADE Column to YES
		condition1_1 = (data['prev_5EMA'] > data['prev_high'])
		condition1_2 = ((data['high'] > data['5EMA']) & (data['close'] > data['open']))
		#condition1_3 = data['low'] >
		data.loc[condition1_1 & condition1_2, 'TRADE'] = 'YES'

		#data['close_count'] =
		data = data.loc[data['TRADE'] == 'YES']
		if (len(data) > 0):
			print(self.symbol)



	def get_10_percent_dip_count(self):
		delta_days=4000
		from_count = delta_days
		to_count = delta_days - 2000
		count = 0
		for i in range(0,delta_days,2000):

			from_datetime = datetime.datetime.now() - relativedelta(days=from_count)
			to_datetime = datetime.datetime.now() - relativedelta(days=to_count)
			#print(from_datetime, to_datetime)
			count = count+ self.get_week_data(from_datetime, to_datetime)
			from_count = to_count
			to_count = to_count - 2000
			#print(count)
		print("Monthly invested avg: ", self.monthy_investable_amount)
		print("XIRR of monthly inversted: ", xirr(self.date_mthly_arr, self.amt_mthly_arr))
		print("XIRR of ten perncent inversted: ", xirr(self.date_ten_per_arr, self.amt_ten_per_arr))
		print("Remaining ten percent investable amount: ", self.ten_percent_investable_amount)
		print("ten percent down investable avg: ", self.ten_percent_invested_amount)
		return count

	def cal_rsi(self):
		n=14
		data = self.get_data(interval='week')[0]
		#data = data['close']
		#data['close'] = data1['close']
		data['delta'] = data['close'].diff()
		data['dUp'] = data['delta']
		data['dDown'] = data['delta']
		#up = data['close'].clip(lower=0)
		# data.loc[data['dUp'] < 0, 'dUp'] = 0
		# data.loc[data['dDown'] > 0, 'dDown'] = 0
		data['dUp'] =  data['dUp'].clip(lower=0)
		data['dDown'] = -1 * data['dDown'].clip(upper=0)
		#data.loc[data['dDown'] > 0, 'dDown'] = 0
		#data['dUp'][data['dUp'] < 0] = 0
		#data['dDown'][data['dDown'] > 0] = 0
		data['RolUp'] = data['dUp'].rolling(n).mean()
		data['RolDown'] = data['dDown'].rolling(n).mean()
		data['RS'] = data['RolUp'] / data['RolDown']
		data['RSI'] =    100 - (100/(1 + data['RS']))
		#RolUp = dUp.rolling(n).mean()
		#RolDown = dDown.rolling(n).mean().abs()

		#RS = RolUp / RolDown
		#print(data)
		#print("==============")
		print(data['date'],data['RSI'])

		#plt.plot(x, y1)
		#plt.plot(x, y2, '-.')
		# plt.plot(data["date"], data["RSI"], label="RSI")
		# plt.plot(data["date"], data["close"], label="price", '-.')
		#
		# plt.yticks(data["RSI"],data["close"])
		#
		# ax2 = plt.gca().twinx()
		# ax2.set_yticks(data["RSI"])
		# ax2.set_yticklabels(data["close"])
		# ax2.set_ylabel("Another Y-axis data")
		#
		# plt.xlabel("X-axis data")
		# plt.ylabel("Y-axis data")
		# plt.title('multiple plots')
		# plt.show()
		#plt.plot(data["date"], data["RSI"], label="RSI")
		#plt.plot(data["date"], data["close"], label="price")
		#plt.show()
		length = len(data)
		return data["RSI"].values[length-1]

	def cal_rsi_calculator(self):
		data = self.get_data(interval='week')[0]
		data_list = list(data['close'])
		rsi1 = rsi(data_list)
		print(rsi1)
		#3457
		return rsi1

	stop_loss = BUDGET * 0.005
	target = BUDGET * 0.01
