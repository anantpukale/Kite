
class gtt:
	def place_gtt_order(self, last_price,gtt_order_price_SL, gtt_order_price_target, quantity):
		print("gtt order in", self.symbol)
		self.kite.place_gtt(last_price=last_price,gtt_order_price_SL=gtt_order_price_SL+1, gtt_order_price_target=gtt_order_price_target+1, symbol= self.symbol, quantity=quantity)

	def get_trigger_id(self, tradingsymbol):
		gtt_json = self.kite.get_all_gtt()
		gtt_list = gtt_json['data']
		for gtt in gtt_list:
			if gtt['condition']['tradingsymbol'] == tradingsymbol:
				return gtt['id']
		return None

	def modify_gtt_order(self, last_price, gtt_order_price_sl, gtt_order_price_target, quantity):

		trigger_id = self.get_trigger_id(self.symbol)

		if trigger_id != None:
			self.kite.modify_gtt(trigger_id=trigger_id, last_price=last_price, gtt_order_price_SL=gtt_order_price_sl,
		                    gtt_order_price_target=gtt_order_price_target, symbol=self.symbol, quantity= quantity)
		else:
			print("No gtt present")

	def trade_decision(self, data):

		last_price, gtt_order_price_sl, gtt_order_price_target = 0, 0, 0
		if (len(data) > 0):
			tailed_data = data.tail(1)
			last_price = list(tailed_data['close'])[0]
			gtt_order_price_sl = list(tailed_data['prev_low'])[0]
			gtt_order_price_target = round(list(tailed_data['5EMA'])[0] + list(tailed_data['5EMA'])[0] * 0.04, 2)
			self._take_trade(last_price, gtt_order_price_sl, gtt_order_price_target)
			print(data)
		else:
			print("Strategy data frame empty")
			print(data)

	def _take_trade(self, last_price, gtt_order_price_sl, gtt_order_price_target):
		trigger_id = self.get_trigger_id(self.symbol)
		if ((last_price > 0.0) & (gtt_order_price_sl > 0.0) & (gtt_order_price_target > 0.0) & (trigger_id == None)):
			# self.place_order()
			if trigger_id != None:
				quantity = self.get_holding_quantity(self.symbol)
				# self.modify_gtt_order(last_price, gtt_order_price_sl, gtt_order_price_target, quantity)
				print("Took trade and updated gtt")
			else:
				quantity = 1
				# self.place_gtt_order(last_price, gtt_order_price_sl, gtt_order_price_target, quantity)
				print("Placed new gtt order")
		else:
			print("One of is zero: ", last_price, gtt_order_price_sl, gtt_order_price_target,
			      " trigger id is already present and hence not taking double trade")

	def buy_trade_strategy(self):
		data = self.get_data()
		# data = data[['date','high','prev_high','low', 'prev_low', 'close', '5EMA', 'volume']]
		# data = data.tail(2)
		data['TRADE'] = 'NO'
		buy_num = list(data['close'])[0] / 1000
		buy_quantity = 10000 / list(data['close'])[0]
		# data.loc[(data['prev_high'] < data['prev_5EMA'])  & (data['div'] > 1)  & (data['prev_low'] <  data['low']), 'TRADE'] = 'YES'
		data.loc[(((data['5EMA'] - data['prev_5EMA']) > buy_num) & (
					(data['pre_prev_5EMA'] - data['prev_5EMA']) > 0)), 'TRADE'] = 'YES'
		# data.loc[(data['pre_prev_high'] < data['pre_prev_5EMA']) & (data['div'] < 0) & (data['close'] > data['prev_low']) & (data['pre_prev_low'] < data['prev_low']), 'TRADE'] = 'YES'
		# data.loc[(data['div'] <= 1), 'TRADE'] = 'NO'

		print("pre_prev_5EMA: " + str(list(data['pre_prev_5EMA'])[0]) + " prev_5EMA: " + str(
			list(data['prev_5EMA'])[0]) + " 5EMA: " + str(list(data['5EMA'])[0]))
		# Keep rows only if TRADE col is YES
		data = data.loc[data['TRADE'] == 'YES']

		return data, int(buy_quantity)
