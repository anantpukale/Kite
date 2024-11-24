# import yfinance as yf
#
# # Define the ticker for NIFTY Bank
# ticker = "^NIFTY200MOM30"
#
# # Fetch the historical data
#
# nifty_bank_data = yf.download(ticker, start="2023-01-01", end="2024-11-15", interval='1d')
#
# # Display the data
# print(nifty_bank_data.head())

import datetime
import time

from dateutil.relativedelta import relativedelta
from nselib import capital_market
import pandas as pd

index_df= pd.DataFrame()
def get_data(inddex):
	#df = capital_market.market_watch_all_indices()
	#indices = list(df['indexSymbol'].values)
	print(index)
	now = datetime.datetime.now()
	end_date = now.strftime('%d-%m-%Y')
	df = pd.DataFrame()
	for days in range(1000, 2001, 1000):
		from_datetime1 = now - relativedelta(days=days)
		start_date = from_datetime1.strftime('%d-%m-%Y')
		# Fetch the data using yfinance
		index_data = capital_market.capital_market_data.index_data(index=index,
		                                                           from_date=start_date,
		                                                           to_date=end_date)
		index_data['TIMESTAMP'] = pd.to_datetime(index_data['TIMESTAMP'], format='%d-%m-%Y')
		index_data = index_data.sort_values('TIMESTAMP').reset_index(drop=True)
		df = pd.concat([df, index_data])
		#print(index_data)
		end_date = start_date
	#print(df.columns)
	print(df)
	print("")
	return df

def get_indices_scan(data):

	#data = self.get_data(interval='week')
	# Index(['TIMESTAMP', 'INDEX_NAME', 'OPEN_INDEX_VAL', 'HIGH_INDEX_VAL',
	#        'CLOSE_INDEX_VAL', 'LOW_INDEX_VAL', 'TRADED_QTY', 'TURN_OVER']

	data['5EMA'] = data['CLOSE_INDEX_VAL'].ewm(span=5, adjust=False).mean()
	data['89EMA'] = data['CLOSE_INDEX_VAL'].ewm(span=89, adjust=False).mean()
	data['prev_89EMA'] = data['89EMA'].shift(1)
	data['5EMA'] = pd.to_numeric(data['5EMA'], errors='coerce')
	data['89EMA'] = pd.to_numeric(data['89EMA'], errors='coerce')
	data['percentage_difference'] = ((data['CLOSE_INDEX_VAL'] - data['89EMA']) / data['89EMA'] ) * 100
	data['is_increased'] = data['89EMA'] > data['prev_89EMA']
	true_count = data['is_increased'].sum()
	false_count = len(data) - true_count

	min = data['percentage_difference'].round(2).min()
	max = data['percentage_difference'].round(2).max()
	avg = data['percentage_difference'].mean().round(2)
	per_diff = data['percentage_difference'].tail(1).round(2).min()

	new_df = pd.DataFrame({
		'symbol': [index],
		'percent_diff': [str(per_diff)],
		'min': [str(min)],
		'max': [str(max)],
		'avg': [str(avg)],
		'relative_diff': [str(avg - per_diff)]
	})
	# index_df = pd.concat([index_df, new_df], ignore_index=True)
	print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	print(index + " per diff: " + str(per_diff) + " min:" + str(min) + " max:" + str(max) + " avg:" + str(
		avg) + " relative_diff:" + str(avg - per_diff))

	if (false_count < true_count):

		print(f"BEST FIT: {index} and true count: {true_count} and flase count: {false_count}")
		#print("====================")
	return  new_df


indices = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY 500', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100', 'NIFTY SMLCAP 100', 'NIFTY MIDCAP 150', 'NIFTY SMLCAP 50', 'NIFTY SMLCAP 250', 'NIFTY MIDSML 400', 'NIFTY500 MULTICAP', 'NIFTY LARGEMID250', 'NIFTY MID SELECT', 'NIFTY TOTAL MKT', 'NIFTY MICROCAP250', 'NIFTY BANK', 'NIFTY AUTO', 'NIFTY FIN SERVICE', 'NIFTY FINSRV25 50', 'NIFTY FMCG', 'NIFTY IT', 'NIFTY MEDIA', 'NIFTY METAL', 'NIFTY PHARMA', 'NIFTY PSU BANK', 'NIFTY PVT BANK', 'NIFTY REALTY', 'NIFTY HEALTHCARE', 'NIFTY CONSR DURBL', 'NIFTY OIL AND GAS', 'NIFTY MIDSML HLTH', 'NIFTY DIV OPPS 50', 'NIFTY GROWSECT 15', 'NIFTY100 QUALTY30', 'NIFTY50 VALUE 20', 'NIFTY50 TR 2X LEV', 'NIFTY50 PR 2X LEV', 'NIFTY50 TR 1X INV', 'NIFTY50 PR 1X INV', 'NIFTY50 DIV POINT', 'NIFTY ALPHA 50', 'NIFTY50 EQL WGT', 'NIFTY100 EQL WGT', 'NIFTY100 LOWVOL30', 'NIFTY200 QUALTY30', 'NIFTY ALPHALOWVOL', 'NIFTY200MOMENTM30', 'NIFTY M150 QLTY50', 'NIFTY200 ALPHA 30', 'NIFTYM150MOMNTM50', 'NIFTY500MOMENTM50', 'NIFTYMS400 MQ 100', 'NIFTYSML250MQ 100', 'NIFTY TOP 10 EW', 'NIFTY COMMODITIES', 'NIFTY CONSUMPTION', 'NIFTY CPSE', 'NIFTY ENERGY', 'NIFTY INFRA', 'NIFTY100 LIQ 15', 'NIFTY MID LIQ 15', 'NIFTY MNC', 'NIFTY PSE', 'NIFTY SERV SECTOR', 'NIFTY100ESGSECLDR', 'NIFTY IND DIGITAL', 'NIFTY100 ESG', 'NIFTY INDIA MFG', 'NIFTY TATA 25 CAP', 'NIFTY MULTI MFG', 'NIFTY MULTI INFRA', 'NIFTY IND DEFENCE', 'NIFTY IND TOURISM', 'NIFTY CAPITAL MKT', 'NIFTY GS 8 13YR', 'NIFTY GS 10YR', 'NIFTY GS 10YR CLN', 'NIFTY GS 4 8YR', 'NIFTY GS 11 15YR', 'NIFTY GS 15YRPLUS', 'NIFTY GS COMPSITE', 'BHARATBOND-APR25', 'BHARATBOND-APR30', 'BHARATBOND-APR31', 'BHARATBOND-APR32', 'BHARATBOND-APR33']
print(indices)

for index in indices:
	try:
		data = get_data(index)
		index_df = pd.concat([index_df,get_indices_scan(data)],  ignore_index=True)
		time.sleep(5)
	except Exception as e:
		print("EXCEPTION: ", index)
		print(repr(e))
print(index_df)
index_df.to_csv('index_scan.csv')

