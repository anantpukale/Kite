import sys

from kite_trade import *
import pandas as pd
import pyotp
import datetime
from dateutil.relativedelta import relativedelta
from pyxirr import xirr
#import matplotlib.pyplot as plt
from rsi_calculator import rsi

pd.set_option('display.max_columns', None)


class WeekTradeApp:
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
	target = BUDGET * 0.01
	stop_loss = BUDGET * 0.005

	def __init__(self, symbol):
		self.whatsapp_msg = ""
		self.symbol = symbol
		self.is_black_listed = False
		# qr_code = 'DL3EP6ZJHJU6R54G2STJGHYAHQCIKX3R'
		# totp = pyotp.TOTP(qr_code)
		# twofa = totp.now()  # Login Pin or TOTP
		# user_id = "BF6533"  # Login Id
		# password = " "  # Login password
		# enctoken = get_enctoken(user_id, password, twofa)
		enctoken = "AvEx7gMqAGiLLIE69s2KTpEWl2AYMg+pcejtVz18ido/aqDQM5JxaBptZ6CjxGanzZCs8KDIiKYnfrgLhg5vaCJXoZDlIZZu5FsPIrb0hS+zn6Pvj2LREQ=="
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
	def get_week_data(self, from_datetime, to_datetime):
		#delta_days=2000
		self.get_instrument_token()
		interval="day"
		res_list = self.kite.historical_data(self.instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
		max= 0
		count=0
		lenth = len(res_list)
		sip=100000
		investable_date= res_list[0]['date']

		for stock in res_list:
			if investable_date >= stock['date']:
				self.monthy_investable_count+=1
				self.monthy_investable_amount+=sip
				self.ten_percent_investable_amount+=sip
				investable_date = investable_date + relativedelta(months=1)
				self.date_mthly_arr.append(stock['date'].date())
				self.amt_mthly_arr.append(100000)


			if stock['close'] > max:
				max= stock['close']
				stock_less_than_10_percent_from_max=max-(max * 0.05)
				#print("date: ", stock['date']," stock_less_than_10_percent_from_max: ", stock_less_than_10_percent_from_max)
			if stock_less_than_10_percent_from_max > stock['close']:
				count = count + 1
				self.ten_percent_investable_count+=1
				if(self.ten_percent_investable_amount > 0):
					amt = self.ten_percent_investable_amount * 0.9
					mul = amt / stock['close']
					self.ten_percent_invested_amount+= amt
					self.ten_percent_investable_amount-= amt
					self.date_ten_per_arr.append(stock['date'].date())
					self.amt_ten_per_arr.append(amt)
					#print("ten percent investable: ", self.ten_percent_investable_amount, mul , stock['close'])
				#print(stock['date'], stock['close'], max, count)

		self.date_mthly_arr.append(investable_date)
		self.amt_mthly_arr.append(-1)
		self.date_ten_per_arr.append(investable_date )
		self.amt_ten_per_arr.append(-1)
		#data = pd.DataFrame.from_dict(res_list)
		return count

	def get_data(self, interval="15minute", isTail5=True):
		from_datetime = datetime.datetime.now() - relativedelta(days=800)
		to_datetime = datetime.datetime.now()
		self.get_instrument_token()
		if self.instrument_token == 0:
			return self.instrument_token, self.instrument_token
		res_list = self.kite.historical_data(self.instrument_token, from_datetime, to_datetime, interval,
		                                     continuous=False, oi=False)
		data = pd.DataFrame.from_dict(res_list)
		try:
			data['5EMA'] = data['close'].ewm(span=5, adjust=False).mean()
		except:
			print("EXCEPTION: " + str(self.symbol))
			return 0, 0
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
		data['close_open'] =  data['close'] - data['open']
		data['binary'] = data['close'] > data['open']

		# data['div'] = (data['5EMA'] - data['close']) / data['5EMA'] * 100
		if isTail5:
			#data = data.tail(5)
			data['5_avg_volume'] = data['volume'].mean()
			#data = data.tail(1)
		else:
			data['consecutive'] = data['binary'].groupby(data['binary'].diff().ne(0).cumsum()).cumsum()
			df = data.groupby('consecutive')['consecutive'].count()
			print(df)
		return data , 1

	def get_instrument_token(self):
		nse = self.kite.instruments('NSE')
		nse_data = pd.DataFrame(nse)
		try:
			self.instrument_token = nse_data[nse_data.tradingsymbol == self.symbol].instrument_token.values[0]
		except:
			#print("Exception: ",self.symbol)
			self.instrument_token = 0
		return self.instrument_token

	def get_weekly_scan(self):
		data, check = self.get_data(interval='week')
		if check == 0:
			return 0
		# Create TRADE column with default value NO assuming no trade on the record
		data['TRADE'] = 'NO'
		# Check Buy condition meets or not if yes then update the value in TRADE Column to YES
		condition1_1 = (data['prev_5EMA'] > data['prev_high'])
		condition1_2 = ((data['prev_close'] < data['prev_open']) & (data['close'] > data['prev_open']))
		condition1_3 = (data['5_avg_volume'] > 1000000)

		data.loc[condition1_1 & condition1_2 & condition1_3, 'TRADE'] = 'YES'
		data = data.loc[data['TRADE'] == 'YES']
		# print(data)
		if (len(data) > 0):
			print(self.symbol)
			print("data['prev_5EMA']: "+ str(data['prev_5EMA'])+ " data['prev_high']: "+ str(data['prev_high']) + " data['prev_close'] "+ str(data['prev_close'])
			      + " data['prev_open'] " + str(data['prev_open']) + " data['close'] " + str(data['close']))
			print("====================")


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

	def continous_rise_score(self):
		 self.get_data(interval='week', isTail5=False)
		#print(data)

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
