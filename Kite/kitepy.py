
from kite_trade import *
import pandas as pd
import pyotp
import datetime
from dateutil.relativedelta import relativedelta

pd.set_option('display.max_columns', None)


class TradeApp:
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
	trigger_price = None

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
		enctoken = "AvEx7gMqAGiLLIE69s2KTpEWl2AYMg+pcejtVz18ido/aqDQM5JxaBptZ6CjxGanzZCs8KDIiKYnfrgLhg5vaCJXoZDlIZZu5FsPIrb0hS+zn6Pvj2LREQ=="
		self.kite = KiteApp(enctoken=enctoken)

	def get_data(self, interval="15minute"):
		from_datetime = datetime.datetime.now() - relativedelta(days=200)
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
		data = data.tail(1)
		return data

	def get_instrument_token(self):
		nse = self.kite.instruments('NSE')
		nse_data = pd.DataFrame(nse)
		self.instrument_token = nse_data[nse_data.tradingsymbol == self.symbol].instrument_token.values[0]
		return self.instrument_token

	def buy_trade_strategy(self, position_quantity):
		# Get Data
		data = self.get_data()
		# Create TRADE column with default value NO assuming no trade on the record
		data['TRADE'] = 'NO'
		buy_num = list(data['5EMA'])[0] / 1000
		buy_num = buy_num + buy_num * 0.15
		print("EXPECTED BUY Trigger: ", list(data['5EMA'])[0] + buy_num)
		buy_quantity = self.get_buy_sell_quantity(data)
		# Check Buy condition meets or not if yes then update the value in TRADE Column to YES
		condition1_1 = ((data['5EMA'] - data['prev_5EMA']) > buy_num)
		condition1_2 = ((data['pre_prev_5EMA'] - data['prev_5EMA']) > 0)
		# Higher high checks
		condition2_1 = (data['5EMA'] > data['prev_5EMA'])
		condition2_2 = (data['prev_5EMA'] > data['pre_prev_5EMA'])
		# condition2_3 = ((data['close'] > data['prev_close']) & (data['close'] > data['open']) & datetime.datetime.now() > self.today9_45am)
		condition2_3 = ((data['5EMA'] - data['pre_prev_5EMA']) > buy_num)
		condition2_4 = (list(data['close'])[0] > list(data['prev_close'])[0]) if (list(data['prev_close'])[0] > list(data['prev_open'])[0]) else\
			(list(data['close'])[0] > list(data['prev_open'])[0])
		# For short covering
		condition3_1 = False
		# To avoid early 9:15 to 9:30 trade volatility
		data['DECIDE'] = (data['close'] - data['5EMA']) / (data['close'] * 0.01)

		if position_quantity < 0:
			# condition3_1 = ((data['prev_low'] < data['low']) | (data['prev_high'] < data['high'])) \
			#                | ( self.unrealised_pnl < -self.stop_loss) | (self.unrealised_pnl > self.target)
			condition3_1 = (((data['5EMA'] - data['pre_prev_5EMA']) > buy_num) | (self.unrealised_pnl < -self.stop_loss)
			                | (self.unrealised_pnl > self.target))

		print("condition1_1: " + str(condition1_1) + " condition1_2: " + str(condition1_2) + " condition2_1: " + str(
			condition2_1) + " condition2_2: " + str(condition2_2) + " condition2_3: " + str(
			condition2_3) + " condition2_4: " + str(condition2_4) + " condition3_1: " + str(condition3_1))
		# print("condition1_1: " + str(condition1_1) + " condition1_2: " + str(condition1_2) + " condition3_1: " + str(condition3_1))

		data.loc[((condition1_1 & condition1_2) | (
					condition2_1 & condition2_2 & condition2_3 & condition2_4) | condition3_1), 'TRADE'] = 'YES'

		data.loc[(datetime.datetime.now() > self.today9_15am) & (datetime.datetime.now() < self.today9_30am) & (
				data['DECIDE'] > 0.75), 'TRADE'] = 'NO'

		print("pre_prev_5EMA: " + str(list(data['pre_prev_5EMA'])[0]) + " prev_5EMA: " + str(
			list(data['prev_5EMA'])[0]) + " 5EMA: " + str(list(data['5EMA'])[0]))

		# Keep rows only if TRADE col is YES
		data = data.loc[data['TRADE'] == 'YES']

		return data, int(buy_quantity)

	def buy_trade_strategy1(self, position_quantity):
		# Get Data
		data = self.get_data()
		# Create TRADE column with default value NO assuming no trade on the record
		data['TRADE'] = 'NO'
		buy_num = list(data['5EMA'])[0] / 1000
		buy_num = buy_num + buy_num * 0.15
		print("EXPECTED BUY Trigger: ", list(data['5EMA'])[0] + buy_num)
		buy_quantity = self.get_buy_sell_quantity(data)
		# Check Buy condition meets or not if yes then update the value in TRADE Column to YES
		condition1_1 = (data['prev_5EMA'] > data['prev_high'])
		condition1_2 = (data['5EMA'] < data['high'])


		print("condition1_1: " + str(condition1_1) + " condition1_2: " + str(condition1_2))

		data.loc[(condition1_1 & condition1_2), 'TRADE'] = 'YES'

		# Keep rows only if TRADE col is YES
		data = data.loc[data['TRADE'] == 'YES']

		return data, int(buy_quantity)

	def sell_trade_strategy1(self, position_quantity):
		# Get Data
		data = self.get_data()
		# Create TRADE column with default value NO assuming no trade on the record
		data['TRADE'] = 'NO'
		buy_num = list(data['5EMA'])[0] / 1000
		buy_num = buy_num + buy_num * 0.15
		print("EXPECTED BUY Trigger: ", list(data['5EMA'])[0] + buy_num)
		buy_quantity = self.get_buy_sell_quantity(data)
		# Check Buy condition meets or not if yes then update the value in TRADE Column to YES
		condition1_1 = (data['prev_5EMA'] < data['prev_low'])
		condition1_2 = (data['5EMA'] < data['low'])


		print("condition1_1: " + str(condition1_1) + " condition1_2: " + str(condition1_2))

		data.loc[(condition1_1 & condition1_2), 'TRADE'] = 'YES'

		# Keep rows only if TRADE col is YES
		data = data.loc[data['TRADE'] == 'YES']

		return data, int(buy_quantity)

	def place_order_sl(self, buy_or_sell, product, quantity, tradingsymbol):
		kite = self.kite
		print(self.symbol, buy_or_sell, quantity, product)
		order = kite.place_order(variety=kite.VARIETY_REGULAR,
		                         exchange=kite.EXCHANGE_NSE,
		                         tradingsymbol=self.tradingsymbol,
		                         transaction_type=buy_or_sell,
		                         quantity=quantity,
		                         product=product,
		                         order_type=kite.ORDER_TYPE_SLM,
		                         price=None,
		                         validity=None,
		                         disclosed_quantity=None,
		                         trigger_price=self.trigger_price,
		                         squareoff=None,
		                         stoploss=None,
		                         trailing_stoploss=None,
		                         tag="TradeViaPython")

		self.whatsapp_msg = "stock: " + str(self.symbol) + " Quantity: " + str(quantity) + " Order id: " + str(
			order) + " transaction type: " + str(buy_or_sell)

		return order

	def place_order(self, buy_or_sell, product, quantity, tradingsymbol):
		trading_symbol = self.symbol if tradingsymbol is None else tradingsymbol
		kite = self.kite
		print(self.symbol, buy_or_sell, quantity, product)
		order = kite.place_order(variety=kite.VARIETY_REGULAR,
		                         exchange=kite.EXCHANGE_NSE,
		                         tradingsymbol=trading_symbol,
		                         transaction_type=buy_or_sell,
		                         quantity=quantity,
		                         product=product,
		                         order_type=kite.ORDER_TYPE_MARKET,
		                         price=None,
		                         validity=None,
		                         disclosed_quantity=None,
		                         trigger_price=None,
		                         squareoff=None,
		                         stoploss=None,
		                         trailing_stoploss=None,
		                         tag="TradeViaPython")

		self.whatsapp_msg = "stock: " + str(self.symbol) + " Quantity: " + str(quantity) + " Order id: " + str(
			order) + " transaction type: " + str(buy_or_sell)

		return order

	def get_holding_quantity(self, tradingsymbol):
		holding_list = self.kite.holdings()
		t1_quantity = 0
		total_quantity = 0
		position_quantity = 0
		holding_quantity = 0
		now = datetime.datetime.now()
		today3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)
		product = self.kite.PRODUCT_MIS if now < today3pm else self.kite.PRODUCT_CNC
		for holding in holding_list:
			if holding['tradingsymbol'] == tradingsymbol:
				holding_quantity = holding['quantity']
				t1_quantity = holding["t1_quantity"]
				product = self.kite.PRODUCT_CNC
		position_list = self.kite.positions()['net']
		for position in position_list:
			if position['tradingsymbol'] == tradingsymbol:
				position_quantity += position['quantity']
				self.unrealised_pnl = position['unrealised']
		total_quantity = holding_quantity + t1_quantity + position_quantity
		print(str(total_quantity) + " HOLDING or POSITION for: " + str(tradingsymbol) + " Product: " + str(
			product) + " Unrealised pnl: " + str(self.unrealised_pnl))
		return position_quantity, product, total_quantity

	def sell_trade_strategy(self, total_quantity):
		data = self.get_data()
		data['TRADE'] = 'NO'
		sell_num = list(data['prev_5EMA'])[0] / 1000
		sell_num = sell_num + sell_num * 0.15
		print("SELL NUM: ", sell_num)
		condition1_1 = ((data['5EMA'] - data['prev_5EMA']) < -sell_num)
		condition1_2 = (data['pre_prev_5EMA'] < data['prev_5EMA'])
		condition2_1 = (data['prev_5EMA'] > data['5EMA'])
		condition2_2 = (data['pre_prev_5EMA'] > data['prev_5EMA'])
		# condition2_3 = (data['close'] < data['prev_close']) & (data['close'] < data['open'] & datetime.datetime.now() > self.today9_45am)
		condition2_3 = ((data['5EMA'] - data['pre_prev_5EMA']) < -sell_num)
		condition2_4 = (list(data['close'])[0] < list(data['prev_close'])[0]) if (list(data['prev_close'])[0] < list(data['prev_open'])[0]) else (
				list(data['close'])[0] < list(data['prev_open'])[0])
		# Booking profit or loss at 1% gain or 0.5% loss
		condition3_1: bool = (
					((data['5EMA'] - data['pre_prev_5EMA']) < -sell_num) | (self.unrealised_pnl > self.target) | (
								self.unrealised_pnl < -self.stop_loss)) if total_quantity > 0 else False
		data['DECIDE'] = (data['5EMA'] - data['close']) / (data['5EMA'] * 0.01)

		print("Sell trigger on 5EMA: ", (list(data['prev_5EMA'])[0] - sell_num))
		print("condition1_1: " + str(condition1_1) + " condition1_2: " + str(condition1_2) + " condition2_1: " + str(
			condition2_1) + " condition2_2: " + str(condition2_2) + " condition2_3: " + str(
			condition2_3) + " condition2_3: " + str(condition2_3) + " condition3_1: " + str(condition3_1))

		data.loc[((condition1_1 & condition1_2) | (
				condition2_1 & condition2_2 & condition2_3 & condition2_4) | condition3_1), 'TRADE'] = 'YES'

		data.loc[(datetime.datetime.now() > self.today9_15am) & (datetime.datetime.now() < self.today9_30am) & (
				data['DECIDE'] > 0.75), 'TRADE'] = 'NO'

		print(
			"pre_prev_5EMA: " + str(list(data['pre_prev_5EMA'])[0]) + " prev_5EMA: " + str(
				list(data['prev_5EMA'])[0]) + " 5EMA: " + str(list(
				data['5EMA'])[0]))

		# Keep rows only if TRADE col is YES
		data = data.loc[data['TRADE'] == 'YES']

		return data

	def poll_uptrend(self):
		print("=====UPTREND=========")
		position_quantity, product, total_quantity = self.get_holding_quantity(self.symbol)
		if position_quantity <= 0:
			self.buy_opportunity(product, position_quantity)
		if total_quantity > 0:
			self.sell_opportunity(product, total_quantity)

	def poll_downtrend(self):
		print("=======DOWNTREND======")
		position_quantity, product, total_quantity = self.get_holding_quantity(self.symbol)
		if total_quantity >= 0:
			self.sell_opportunity(product, total_quantity)
		if position_quantity < 0:
			self.buy_opportunity(product, position_quantity)

	def get_trend(self):
		print("======= TREND CHECK==========")
		data = self.get_data("day")
		close = list(data['close'])[0]
		open_price = list(data['open'])[0]
		print("NIFTY 50: CLOSE: " + str(close) + " OPEN: " + str(open_price))
		if close > open_price:
			return "UPTREND"
		else:
			return "DOWNTREND"

	def buy_opportunity(self, product, position_quantity):
		print(str(self.symbol) + " BUY Check: ", datetime.datetime.now())
		data, buy_quantity = self.buy_trade_strategy1(position_quantity)
		quantity = abs(position_quantity) if position_quantity < 0 else buy_quantity
		if len(data) > 0:
			print(data)
			self.place_order(self.kite.TRANSACTION_TYPE_BUY, product, int(quantity), None)
			print("BUY Triggered for quantity: ", quantity)

	def sell_opportunity(self, product, total_quantity):
		data = self.sell_trade_strategy(total_quantity)
		print(str(self.symbol) + " SELL Check: ", datetime.datetime.now())
		if len(data) > 0:
			quantity = total_quantity if total_quantity > 0 else self.get_buy_sell_quantity(data)
			print(data)
			self.place_order(self.kite.TRANSACTION_TYPE_SELL, product, int(quantity), None)
			print("SELL Triggered for quantity: ", quantity)

	def update_all_positions_mis_cnc(self):

		position_list = self.kite.positions()['net']
		print("=====================Updating MIS to CNC================================")
		for position in position_list:
			if position['quantity'] > 0:
				print("Updating MIS to CNC: ", position['tradingsymbol'])
				response = self.kite.update_position(self.kite.PRODUCT_MIS, self.kite.PRODUCT_CNC,
				                                     position['tradingsymbol'], position['quantity'])
				print(response)

	def check_black_list_stock(self):
		orders_list: list = self.kite.orders()
		count = 0
		order_completed = []
		for order in orders_list:
			if order['status'] == "COMPLETE":
				order_completed.append(order['tradingsymbol'])
			if order['tradingsymbol'] == self.symbol and order['status'] == "COMPLETE":
				count += 1
			if count > 1 and order['tradingsymbol'] == self.symbol:
				self.is_black_listed = True
				break
		order_set = set(order_completed)
		if len(order_set) > 6 and not (order_set.__contains__(self.symbol)):
			self.is_black_listed = True

	def get_buy_sell_quantity(self, data):
		close = list(data['close'])[0]
		quantity = self.BUDGET / close
		return int(quantity)

	def mis_square_off(self):
		position_list = self.kite.positions()['net']
		for position in position_list:
			if position['tradingsymbol'] == self.symbol:
				print(position)
				print(str(position['tradingsymbol']) + " : " + str(position['unrealised']))
				self.unrealised_pnl = position['unrealised']
				if (self.unrealised_pnl < -self.stop_loss) and position['quantity'] > 0:
					print("MIS Squaring off loss on: " + str(position['tradingsymbol']))
					self.place_order(self.kite.TRANSACTION_TYPE_SELL, self.kite.PRODUCT_MIS, position['quantity'], None)
				elif (self.unrealised_pnl < -self.stop_loss) and position['quantity'] < 0:
					print("MIS Squaring off loss on: " + str(position['tradingsymbol']))
					self.place_order(self.kite.TRANSACTION_TYPE_BUY, self.kite.PRODUCT_MIS, position['quantity'], None)

	def check_unique_order(self):
		orders_list: list = self.kite.orders()
		order_list = []
		for order in orders_list:
			if order['status'] == "COMPLETE":
				order_list.append(order['tradingsymbol'])
		order_set = set(order_list)
		if len(order_set) > 6 and not (order_set.__contains__(self.symbol)):
			self.is_black_listed = True
