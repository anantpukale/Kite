from kite_trade import *
import pandas as pd

user_id = "BF6533"       # Login Id
password = "Vinod@277401"      # Login password
import pyotp
QR_CODE='DL3EP6ZJHJU6R54G2STJGHYAHQCIKX3R'
totp = pyotp.TOTP('DL3EP6ZJHJU6R54G2STJGHYAHQCIKX3R')
totp.now()
#'DL3EP6ZJHJU6R54G2STJGHYAHQCIKX3R'
twofa =  totp.now()      # Login Pin or TOTP

#enctoken = get_enctoken(user_id, password, twofa)
#enctoken="EgampJEySCVN3vF/rQWv7lJLYOrT3FAdclQ7hLey/qTbCVr/Y2RNwglfJ1sOl2ZPvo1ac9WSPQ5LAljY896diVbxdHIZPohoddLCu4QR9CcHLoRvet9Q3g=="
#print(enctoken)
#kite = KiteApp(enctoken=enctoken)
# gtt_order_price_SL = 7129
# gtt_order_price_target = 7350
# order_oco = [{
#         "exchange":"NSE",
#         "tradingsymbol": "BAJFINANCE",
#         "transaction_type": kite.TRANSACTION_TYPE_SELL,
#         "quantity": 1,
#         "order_type": "LIMIT",
#         "product": "CNC",
#         "price": gtt_order_price_SL
#         },{
#         "exchange":"NSE",
#         "tradingsymbol": "BAJFINANCE",
#         "transaction_type": kite.TRANSACTION_TYPE_SELL,
#         "quantity": 1,
#         "order_type": "LIMIT",
#         "product": "CNC",
#         "price": gtt_order_price_target
#     }]
# order_single = [{
# 			"exchange": "NSE",
# 			"tradingsymbol": "BAJFINANCE",
# 			"transaction_type": kite.TRANSACTION_TYPE_SELL,
# 			"quantity": 1,
# 			"order_type": "LIMIT",
# 			"product": "CNC",
# 			"price": gtt_order_price,
# 		}]

# #gtt_oco = kite.place_gtt(trigger_type=kite.GTT_TYPE_OCO, tradingsymbol="SBIN", exchange="NSE", trigger_values=[470,480], last_price=473, orders=order_oco)
# condition, gtt_orders = kite._get_gtt_payload(trigger_type=kite.GTT_TYPE_OCO, tradingsymbol="BAJFINANCE", exchange="NSE",
#                             trigger_values=[gtt_order_price_SL, gtt_order_price_target], last_price=7300, orders=order_oco)
# trigger_type= kite.GTT_TYPE_OCO
# #condition, gtt_orders = kite._get_gtt_payload(trigger_type, tradingsymbol, exchange, trigger_values, last_price, orders)
# params={
#             "condition": json.dumps(condition),
#             "orders": json.dumps(gtt_orders),
#             "type": trigger_type}
#
# gtt = kite.session.post(f"{kite.root_url}/gtt/triggers",
#                                      data=params, headers=kite.headers).json()
#
# print(gtt)


# import datetime
#
# nse = kite.instruments('NSE')
# nse_data = pd.DataFrame(nse)
#
# token = nse_data[nse_data.tradingsymbol == 'HDFCBANK'].instrument_token.values[0]
# instrument_token = token
# from dateutil.relativedelta import relativedelta
# from_datetime = datetime.datetime.now() - relativedelta(days=500)
# to_datetime = datetime.datetime.now()
# interval = "week"

# res_list = kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False)
# data =  pd.DataFrame.from_dict(res_list)
# data['5EMA'] = data['close'].ewm(span=5, adjust=False).mean()
# data = data[['date', 'close', '5EMA', 'volume']]
# data['div'] =  (data['5EMA'] - data['close']) / data['5EMA'] * 100
# data.loc[(data['div'] > 4) , 'TRADE'] = 'YES'
# data.loc[(data['div'] <= 4) , 'TRADE'] = 'NO'
# pd.set_option('display.max_columns', None)
#
# data = data.loc[data['TRADE'] == 'YES']
# res = kite.positions()
# print(res)

from kite_trade1 import *

# user_id = "BF6533"       # Login Id
# password = "Vinod@277401"      # Login password
# twofa = "947570"         # Login Pin or TOTP
#
# enctoken = get_enctoken(user_id, password, twofa)
enctoken = "nQCwortBEkQpcxd5n9YUYoI6CSOEzvY6K0goBdWrdLYHldiT6a7susTOG5mFgXG1M3+I2sfvmQJfbHrDrsxNyISwG7LV6R+vODV6UJolFKEPy46i28WC+g=="
print(enctoken)
kite = KiteApp(enctoken=enctoken)

#print(kite.profile())
#print(kite.margins())
#print(kite.orders())
#print(kite.positions())

# Get instrument or exchange
#print(kite.instruments())
print(kite.instruments("NSE"))
print(kite.instruments("HDFCBANK"))
#print(kite.instruments("NFO"))

