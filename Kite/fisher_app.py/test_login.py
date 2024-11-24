# # from configparser import ConfigParser
# # from kiteconnect import KiteConnect
# #
# # # read config.ini
# # config = ConfigParser()
# # config.read('config.ini')
# #
# # # Zerodha_APP details section
# # api_key         = config.get('Zerodha_APP', 'api_Key')
# # api_secret      = config.get('Zerodha_APP', 'api_secret')
# #
# # kite = KiteConnect(api_key=api_key)
# # print(kite.login_url())
# # # https://kite.zerodha.com/connect/login?api_key=*********&v=3
# #
# # # data = kite.generate_session("4ncy2e4av4064byp", api_secret=api_secret)
# # # access_token = data["access_token"]
# # # print('access token ', access_token)
# # #
# # access_token = config.get('Zerodha_APP', 'enctoken')
# # kite.set_access_token(access_token)
#
# import yfinance as yf
#
#
# def get_yfinance_fisher_index():
# 	# Specify the stock symbol (for NSE, append '.NS')
# 	stock_code = 'HEROMOTOCO.NS'
#
# 	# Fetch stock data using yfinance
# 	stock = yf.Ticker(stock_code)
#
# 	# Get current stock data (delayed by a few minutes)
# 	stock_info = stock.history(period="1y")
# 	print(stock_info)
# 	print("")
# 	# Extract data for today
# 	# open_price = stock_info['Open'][0]
# 	# close_price = stock_info['Close'][0]
# 	# high_price = stock_info['High'][0]
# 	# low_price = stock_info['Low'][0]
# 	# volume = stock_info['Volume'][0]
#
# 	# print(f"Open: {open_price}")
# 	# print(f"Close: {close_price}")
# 	# print(f"High: {high_price}")
# 	# print(f"Low: {low_price}")
# 	# print(f"Volume: {volume}")
#
# 	return stock_info
#
#
# # Call the function
# get_yfinance_fisher_index()
import requests
from bs4 import BeautifulSoup

print("start")
# URL to fetch NSE stock symbols
url = "https://www.nseindia.com/market-data/equity-stockIndices"

# Custom headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Send a request to the URL
response = requests.get(url, headers=headers)
print(response)
# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing stock symbols (you may need to inspect the page to adjust this)
    table = soup.find('table', {'class': 'equityStockIndices'})
    symbols = []

    # Loop through rows in the table to extract symbols
    for row in table.find_all('tr')[1:]:  # Skip the header row
        columns = row.find_all('td')
        if columns:
            stock_symbol = columns[0].text.strip()  # Adjust the index based on the correct column
            symbols.append(stock_symbol)

    # Print the list of stock symbols
    print("List of NSE Stock Symbols:")
    for symbol in symbols:
        print(symbol)
else:
    print(f"Error: Unable to fetch data, status code {response.status_code}")
