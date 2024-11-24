import json
import sys
import time
from Notification import notification
from kitepy import *
from week_strategy import *
from weekly_uptrend import *
import threading
from datetime import datetime
from niftystocks import ns
from nselib import capital_market

def read_stocks_from_json():
	stock_list = []
	f = open('process_parameters.json')

	# returns JSON object as
	# a dictionary
	data = json.load(f)

	# Iterating through the json
	# list
	stock_list.append(data['portfolio']['holding'])
	stock_list.append(data['portfolio']['positions'])
	merged_stock_list = []
	for i in stock_list:
		merged_stock_list += i

	# Closing file
	f.close()
	return set(merged_stock_list)


#stock_list = ns.get_nse_trading_symbol()
now = datetime.now().strftime("%Y-%m-%d")
#app.df['date'] = now
global_queue = []
equity_list = pd.read_csv("data/nifty_indices.csv")
#equity_yf_list = pd.read_csv("data/yf_indices.csv")
#equity_yf_list = capital_market.capital_market_data.market_watch_all_indices()
stock_list = list(equity_list['tradingsymbol'].values)
# equity_list = pd.read_csv("data/nse500")
#equity_yf_list['STOCK'] = equity_yf_list['Yahoo_Finance_Ticker_Symbol']
# equity_list.loc[equity_list['SERIES'] != 'EQ', 'STOCK'] = equity_list['SYMBOL'] + "-" + equity_list['SERIES']5    TUR
#stock_list = list(equity_list['STOCK'])
#stock_list = ["NIFTY200MOMENTM30","NIFTY BANK","NIFTY FMCG"]
black_list_queue = []
print("START")
count = 1
breakthrough = False
app = WeekUptrendTradeApp()
#stock_list = app.get_nse_trading_symbol()
app.days = 1800
app.symbol = "NIFTY200MOMENTM30"
# app.get_tradingview_code_fisher_index()

for stock in stock_list:
	count = count+1
	time.sleep(1)
	app.symbol = stock
	try:
		app.get_indices_scan()
		#app.get_plot()
	except Exception as e:
		print("EXCEPTION: ",stock )
		print(repr(e))
	if count%10==0:
		print("Completed count of shares: ", count)

	if count%3==0:
		time.sleep(2)
now = datetime.now().strftime("%Y-%m-%d")
app.df['date'] = now
app.df.to_csv(f'data/output_nifty_50_{now}.csv', mode='w')
# sys.exit()
# for stock in stock_list:
# 	trader = WeekTradeApp(stock)
# 	rsi =trader.cal_rsi_calculator()
# 	# print("STOCK: ", stock)
# 	# print("RSI: ", rsi)
#
# 	if(rsi > 60):
# 		print("########################################")
# 		print("STOCK: "+ stock+" RSI: ", + rsi)



# def sleep_func(num):
# 	now = datetime.now()
# 	time_array = [29,44,59,14]
# 	mis_square_off_time = [2, 4, 6, 8, 10, 12, 16, 18, 20, 22, 24, 26, 32, 34, 36, 38, 40, 42, 46, 48, 50, 52, 54, 56]
# 	while True:
# 		time.sleep(10)
# 		now = datetime.now()
# 		minute = now.minute
# 		if time_array.__contains__(minute):
# 			break
# 		# if mis_square_off_time.__contains__(minute):
# 		# 	print("=======MIS Square off start ==========" + str(now))
# 		# 	for s in stock_list:
# 		# 		trade_app = TradeApp(s)
# 		# 		trade_app.mis_square_off()
# 		# 		if trade_app.whatsapp_msg.__ne__(""):
# 		# 			global_queue.append(trade_app.whatsapp_msg)
# 		# 	print("========== MIS Square off END =========")
# 		# 	time.sleep(60)
#
# def whatsapp_msg_func(queue):
# 	msg = ""
# 	while len(queue) > 0:
# 		msg += queue.pop() + " ; "
# 	if msg.__ne__(""):
# 		print(msg)
# 		notify = notification().send_msg(str(msg))
# 	else:
# 		print("No Trade Placed")
#
# def update_stock_list_func(input):
# 	while len(black_list_queue) > 0:
# 		stock_name = black_list_queue.pop()
# 		if stock_list.__contains__(stock_name):
# 			print("Removing stock from list: " + str(stock_name))
# 			stock_list.remove(stock_name)
# 	print("======Present working stock list========")
# 	for stock in stock_list:
# 		print(str(stock)+" ", end="")
# 	print("")
# 	return 0
#
#
#
# def waiting_func():
# 	print("Waiting started: ", datetime.now())
# 	sleep_thread = threading.Thread(target=sleep_func, args=(720,))
# 	whatsapp_msg_thread = threading.Thread(target=whatsapp_msg_func, args=(global_queue,))
# 	update_stock_list = threading.Thread(target=update_stock_list_func, args=(1,))
# 	# starting thread 1
# 	whatsapp_msg_thread.start()
# 	# starting thread 2
# 	sleep_thread.start()
# 	# starting thread 3
# 	update_stock_list.start()
# 	# wait until thread 1 is completely executed
# 	whatsapp_msg_thread.join()
# 	# wait until thread 2 is completely executed
# 	sleep_thread.join()
# 	# wait until thread 3 is completely executed
# 	update_stock_list.join()
# 	print("Waiting Ended: ", datetime.now())
#
# now = datetime.now()
# today9_15am = now.replace(hour=9, minute=15, second=0, microsecond=0)
# today2_55pm = now.replace(hour=14, minute=55, second=0, microsecond=0)
#
# def time_based_checks():
# 	for s in stock_list:
# 		t = TradeApp(s)
# 		t.check_black_list_stock()
# 		if t.is_black_listed:
# 			black_list_queue.append(t.symbol)
# 	update_stock_list_func(1)
# 	while datetime.now() < today9_15am:
# 		print("Waiting for market start time i.e. 9:15 am")
# 		time.sleep(60)
# 	if datetime.now() > today2_55pm:
# 		print("Market hour completed. Closing the session for the day")
# 		sys.exit()
#
# while (True):
# 	time_based_checks()
# 	waiting_func()
# 	nse_index = TradeApp("NIFTY200MOMENTM30")
# 	trend = nse_index.get_trend()
# 	for stock in stock_list:
# 		trader = TradeApp(stock)
# 		trader.check_black_list_stock()
# 		if trader.is_black_listed:
# 			black_list_queue.append(trader.symbol)
# 		else:
# 			if trend == "UPTREND":
# 				trader.poll_uptrend()
# 			else:
# 				trader.poll_downtrend()
# 			if trader.whatsapp_msg.__ne__(""):
# 				global_queue.append(trader.whatsapp_msg)
# 	time.sleep(60)
# 	print("########## END ##########")