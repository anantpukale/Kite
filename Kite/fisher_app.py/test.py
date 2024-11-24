import pandas as pd
import yfinance as yf


def get_tradingview_code_fisher_index(stock_code):
	stock = yf.Ticker(stock_code)
	df = stock.history(period="max")

	# Check if DataFrame is empty
	if df.empty:
		print(f"No data found for {stock_code}")
		return

	# Check the index type
	print(df.index)  # Print the index
	print(type(df.index))  # Check the index type

	# Ensure the index is a DatetimeIndex
	if not isinstance(df.index, pd.DatetimeIndex):
		df.index = pd.to_datetime(df.index)

	# Localize to UTC if not already localized
	if df.index.tz is None:
		df.index = df.index.tz_localize("UTC")

	print(df.head())  # Display the DataFrame


# Example usage
get_tradingview_code_fisher_index("HDFCBANK.NS")  # Replace with your desired stock code
