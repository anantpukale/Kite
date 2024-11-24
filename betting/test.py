import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
# Specify the path to your SQLite database file
db_path = 'tennis.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

tables=['mozzart_matches','primobet_matches','meridianbet_matches','maxbet_odds','balkanbet_matches']
for table in tables:
	print(f"Table {table}")
	# Query to select data from a specific table
	query = f"SELECT * FROM {table} limit 10"

	# Read the data into a Pandas DataFrame
	df = pd.read_sql_query(query, conn)

	# Display the DataFrame
	print(df)
	print("==============================")

# Close the database connection
conn.close()
