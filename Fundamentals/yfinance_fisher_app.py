import math
from datetime import datetime
import time

import numpy as np
import pandas as pd
import yfinance as yf
import warnings
import requests
from bs4 import BeautifulSoup
from future.backports.datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException,ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define the path to your chromedriver
#chromedriver_path = '/path/to/chromedriver'  # Replace with the actual path to your chromedriver
chrome_options = Options()

# Add argument to mimic a normal browser session
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)
# Suppress the SettingWithCopyWarning
pd.options.mode.chained_assignment = None

pd.set_option('display.max_columns', None)
# Create a new Chrome session


class FisherApp:
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

	#now = datetime.datetime.now()
	def __init__(self):
		self.symbol = None
		self.df = pd.DataFrame()

	def log_in(self):
		# Go to the Screener login page
		self.driver.get("https://www.screener.in/login/")

		# Wait for the page to load
		time.sleep(2)
		# Locate the username and password input fields and fill them in
		email_input = self.driver.find_element(By.NAME, "username")
		password_input = self.driver.find_element(By.NAME, "password")
		email_input.send_keys("anant.pukale@gmail.com")  # Replace with your email
		password_input.send_keys("277401anant")  # Replace with your password
		# Press the Enter key or click the submit button
		password_input.send_keys(Keys.RETURN)
		# Wait for a few seconds to allow the login process to complete
		time.sleep(5)

	def get_historic_pe_eps(self):
		stock_symbol = self.symbol
		symbol = ""
		if "-" in stock_symbol:
			split_val = self.symbol.split("-")
			if len(split_val) > 2:
				symbol = self.symbol.split("-")[0]
				for i in range(1, len(split_val) - 1):
					symbol = symbol + "-" + self.symbol.split("-")[i]
				stock_symbol = symbol
			# print(f"FOR LOOP: {stock_symbol}")
			elif len(split_val) == 2:
				if len(split_val[1]) == 2:
					stock_symbol = self.symbol.split("-")[0]

		stock = yf.Ticker(f"{stock_symbol}.NS")
		df = stock.history(period="max")
		specific_date = '2013-01-01'
		filtered_df = df.loc[specific_date:]

		# Extract month and year from the index
		filtered_df['Month'] = filtered_df.index.month
		filtered_df['Year'] = filtered_df.index.year
		filtered_df['Day'] = filtered_df.index.day


		# Rename the 'index' column to 'Date' if it doesn't automatically take the index name
		filtered_df = filtered_df.rename(columns={'index': 'Date'})
		print(filtered_df)
		q_eps_df = self.get_quarter_profit_loss_data(url = f'https://www.screener.in/company/{stock_symbol}/consolidated/')
		eps_df = self.get_profit_loss_data(q_eps_df, url = f'https://www.screener.in/company/{stock_symbol}/consolidated/')

		merged_df = pd.merge(filtered_df, eps_df , on=['Month', 'Year'], how='inner')
		merged_df['PE'] = merged_df['Close'].astype(float) / merged_df['EPS'].astype(float)
		print(merged_df)
		now = datetime.now().strftime("%Y-%m-%d")
		print(merged_df.columns)
		merged_df.drop(['Dividends', 'Stock Splits'], axis=1, inplace=True)
		merged_df.to_csv(f'data/pe_eps_value_{stock_symbol}_{now}.csv', mode='w')
		print("")


	def get_profit_loss_data(self, q_eps_df, url):
		self.driver.get(url)
		#try:
		# Wait for the table to be visible
		WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located(
				(By.XPATH, "//section[@id='profit-loss']//table[@class='data-table responsive-text-nowrap']"))
		)

		# Locate the specific row that contains "EPS in Rs" using XPath
		eps_row = self.driver.find_element(By.XPATH, "//section[@id='profit-loss']//table[@class='data-table responsive-text-nowrap']//tr[td[contains(text(),'EPS in Rs')]]")
		row_header = self.driver.find_element(By.XPATH,
		                                   "//section[@id='profit-loss']//table[@class='data-table responsive-text-nowrap']//tr[th[contains(text(),'Mar')]]")

		row_header_values = row_header.find_elements(By.TAG_NAME, "th")[1:]
		month_year_arr = [value.text.split(" ") for value in row_header_values]
		# Print or return the EPS values
		print("Row Header Values:", month_year_arr)
		# Find all the <td> elements in the EPS row (excluding the first one which is the label)
		eps_values = eps_row.find_elements(By.TAG_NAME, "td")[1:]

		# Extract the text from each <td> and store it in a list
		eps_values_text = [value.text for value in eps_values]
		# Extract months (first element) and years (second element if present, else 'TTM')
		months = [sub[0] for sub in month_year_arr]
		# Mapping of month names to numeric values
		month_mapping = {
			'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
			'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
		}

		months1 = [1,2,3]
		months2 = [4, 5, 6, 7, 8, 9, 10, 11, 12]

		current_year = datetime.now().year
		years = [sub[1]  if len(sub) > 1 else current_year for sub in month_year_arr]
		# Print or return the EPS values
		print("EPS Values:", eps_values_text)
		i = 0
		df = pd.DataFrame()
		count = 0
		q_eps_df['Month'] = q_eps_df['Month'].map(month_mapping)
		q_eps_df['Year'] = q_eps_df['Year'].astype(int)
		q_eps_df['Year'] = q_eps_df['Year'].astype(int)
		for year in years:
			if int(year) == int(current_year):
				prev_year = year
				count = count+1
				if count >1:
					print("do something")
			if count <= 1:
				new_df = pd.DataFrame({
					'Month': months1,  # Assuming March for all rows
					'Year': year,
					'EPS': eps_values_text[i]
				})
				df = df._append(new_df)
				new_df = pd.DataFrame({
					'Month': months2,  # Assuming March for all rows
					'Year': int(year) -1,
					'EPS': eps_values_text[i]
				})
				i = i + 1
				#local_df = pd.concat([local_df,new_df])
				df = df._append(new_df)
			if count > 1:
				q_eps_df_filter = q_eps_df[(q_eps_df['Year'] == current_year)]
				#q_eps_df_filter = q_eps_df_filter[(q_eps_df_filter['Month'] > 3)]
				print(q_eps_df_filter)
				q_eps_df_filter['EPS'] = q_eps_df_filter['Last_4_EPS_Sum']
				q_eps_df_filter = q_eps_df_filter.drop(columns=['Last_4_EPS_Sum'])
				q_eps = self.add_previous_months(q_eps_df_filter)
				df = df._append(q_eps)
				print(df)

		# Replace the month names with numeric values
		#df['Month'] = df['Month'].map(month_mapping)
		current_month = datetime.now().month
		# Fill NaN values in the 'Month' column with the current month number
		df['Month'] = df['Month'].fillna(current_month)
		df['Month'] = df['Month'].astype(int)
		# current_year = datetime.now().year
		#
		# # Replace the last row's 'Year' value from 'TTM' to the current year
		# df.at[len(df) - 1, 'Year'] = current_year
		df['Year'] = df['Year'].astype(int)
		print(df)
		return df

	def add_previous_months(self,df):
		new_rows = []
		for _, row in df.iterrows():
			month = row['Month']
			year = row['Year']
			eps = row['EPS']

			# Calculate two previous months
			for i in range(1, 3):
				new_month = month + i
				new_year = year
				if new_month <= 0:
					new_month += 12
					new_year -= 1

				# Create new row for each previous month
				new_rows.append({'Month': int(new_month), 'Year': int(new_year), 'EPS': eps})

		# Append new rows to DataFrame
		new_df = pd.DataFrame(new_rows)
		return pd.concat([df, new_df], ignore_index=True).sort_values(by=['Year', 'Month']).reset_index(drop=True)


	def get_quarter_profit_loss_data(self,url):
		self.driver.get(url)
		#try:
		# Wait for the table to be visible
		WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located(
				(By.XPATH, "//section[@id='quarters']//table[@class='data-table responsive-text-nowrap']"))
		)

		# Locate the specific row that contains "EPS in Rs" using XPath
		eps_row = self.driver.find_element(By.XPATH, "//section[@id='quarters']//table[@class='data-table responsive-text-nowrap']//tr[td[contains(text(),'EPS in Rs')]]")
		row_header = self.driver.find_element(By.XPATH,
		                                   "//section[@id='quarters']//table[@class='data-table responsive-text-nowrap']//tr[th[contains(text(),'Mar')]]")

		row_header_values = row_header.find_elements(By.TAG_NAME, "th")[1:]
		month_year_arr = [value.text.split(" ") for value in row_header_values]
		# Print or return the EPS values
		print("Row Header Values:", month_year_arr)
		# Find all the <td> elements in the EPS row (excluding the first one which is the label)
		eps_values = eps_row.find_elements(By.TAG_NAME, "td")[1:]

		# Extract the text from each <td> and store it in a list
		eps_values_text = [value.text for value in eps_values]
		# Extract months (first element) and years (second element if present, else 'TTM')
		months = [sub[0] for sub in month_year_arr]
		# Mapping of month names to numeric values
		month_mapping = {
			'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
			'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
		}

		# Print or return the EPS values
		print("EPS Values:", eps_values_text)
		i = 0
		df = pd.DataFrame()
		for sub in month_year_arr:
			month = sub[0]
			year = sub[1]
			eps = eps_values_text[i]
			new_df = pd.DataFrame({
				'Month': [month],  # Assuming March for all rows
				'Year': [year],
				'EPS': [eps]
			})
			df = pd.concat([df, new_df], ignore_index=True)
			i = i + 1
		df['Last_4_EPS_Sum'] = df['EPS'].rolling(window=4).sum()
		print(df)
		return df


	def get_tradingview_code_fisher_index(self,config):
		stock_symbol = self.symbol
		symbol=""
		if "-" in stock_symbol:
			split_val = self.symbol.split("-")
			if len(split_val)>2:
				symbol = self.symbol.split("-")[0]
				for i in range(1,len(split_val) - 1):
					symbol = symbol + "-" +self.symbol.split("-")[i]
				stock_symbol=symbol
			#print(f"FOR LOOP: {stock_symbol}")
			elif len(split_val) == 2:
				if len(split_val[1]) == 2:
					stock_symbol=self.symbol.split("-")[0]



		# Calculate 50-day moving average
		current_price=''
		pe_ratio = ''
		eps = ''
		expected_quarterly_eps=''
		peg_ratio=''
		roe = ''
		roce = ''
		roa=''


		try:
			top_ratio_dict = self.get_top_ratios(url = f'https://www.screener.in/company/{stock_symbol}/consolidated/')
			roe = top_ratio_dict.get('ROE')
			roce = top_ratio_dict.get('ROCE')
			market_cap = top_ratio_dict.get('Market Cap')
			pe_ratio = top_ratio_dict.get('Stock P/E')
			current_price  = top_ratio_dict.get('Current Price')
			eps = top_ratio_dict.get('EPS')
			expected_quarterly_eps= top_ratio_dict.get('Exp Qtr EPS')
			roa = top_ratio_dict.get('Return on assets')
			peg_ratio = top_ratio_dict.get('PEG Ratio')
		except Exception as e:
			#print(f"For {stock_symbol} ROE and ROCE getting from Screener.in")
			print(f"EXCEPTION: {stock_symbol} An error occurred: {e}")
			time.sleep(1)
			is_roe = False
		# if is_roe == False or roe== '' or roce == '' or market_cap == '' or pe_ratio == '':
		# 	#if top_ratio_dict.get('Market Cap') == '':  # Return on Equity
		# 	try:
		# 		top_ratio_dict = self.get_top_ratios(url=f'https://www.screener.in/company/{stock_symbol}')
		# 		if roe == '':
		# 			roe = top_ratio_dict.get('ROE')
		# 		if roce == '':
		# 			roce = top_ratio_dict.get('ROCE')
		# 		if market_cap == '':
		# 			market_cap = top_ratio_dict.get('Market Cap')
		# 		if pe_ratio == '':
		# 			pe_ratio = top_ratio_dict.get('Stock P/E')
		# 		if yoy_sales_growth == '':
		# 			yoy_sales_growth = top_ratio_dict.get('salesTTM:')  # YoY Sales Growth
		# 		if yoy_profit_growth == '':
		# 			yoy_profit_growth = top_ratio_dict.get('profitTTM:')
		# 	except Exception as e:
		# 		# print(f"For {stock_symbol} ROE and ROCE getting from Screener.in")
		# 		print(f"EXCEPTION: {} An error occurred: {e}")
		# 		is_roe = False

		date = datetime.datetime.now()

		#print(f"end stock.info {datetime.datetime.now()}")
		new_df = pd.DataFrame({
			'symbol': [self.symbol],
			'date': [date.strftime("%Y-%m-%d")],
			'current_price' : [current_price],
			'pe_ratio' :[pe_ratio],
			'eps' : [eps],
			'expected_quarterly_eps' : [expected_quarterly_eps],
			'peg_ratio' : [peg_ratio],
			'roe' : [roe],
			'roce' : [roce],
			'roa' : [roa],


		})
		# if roe == "" or pe_ratio == "":
		# 	return None
		self.df = pd.concat([self.df, new_df])
	#print(f"end pd.concat {datetime.datetime.now()}")

	def get_top_ratios(self, url):
		# URL of the company's financial page on screener
		#stock_symbol = "RELIANCE"
		#url = f'https://www.screener.in/company/{stock_symbol}/consolidated/'

		# Make the request to get the page content
		response = self.driver.get(url)
		sleep_time = 0
		time.sleep(2)
		ul_element = self.driver.find_element(By.ID, "top-ratios")

		# Get all <li> elements within the <ul>
		li_elements = ul_element.find_elements(By.TAG_NAME, "li")
		ratio_dict = {}

		# Iterate through each <li> and extract the name and value
		for li in li_elements:
			name = li.find_element(By.CLASS_NAME, "name").text
			value = li.find_element(By.CLASS_NAME, "number").text
			unit = li.find_element(By.CLASS_NAME, "value").text.split(value)[1].strip() if value in li.find_element(
				By.CLASS_NAME, "value").text else ''
			ratio_dict[name] = value
			# Print the extracted data
			print(f"{name}: {value} {unit}")

		return ratio_dict

