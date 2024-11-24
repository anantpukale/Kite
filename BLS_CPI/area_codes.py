import pandas as pd
import requests
import os

# URL of the BLS area codes file
area_codes_url = 'https://download.bls.gov/pub/time.series/cu/cu.area'

# Use requests to fetch the file content
response = requests.get(area_codes_url, headers={'User-Agent': 'Mozilla/5.0'})

# Check if the request was successful
if response.status_code == 200:
	# Write the content to a local file
	with open('cu.area', 'wb') as file:
		file.write(response.content)
	print("File downloaded successfully.")
else:
	print(f"Failed to download file. Status code: {response.status_code}")
	exit()

# Check if the file exists before reading
if os.path.exists('cu.area'):
	# Read the downloaded file into a DataFrame
	area_codes_df = pd.read_csv('cu.area', sep='\t')

	# Filter for metropolitan areas
	metro_area_codes = area_codes_df[area_codes_df['area_name'].str.contains("MSA|CSA|Metropolitan", na=False)]

	# Extract the relevant area codes
	area_codes = metro_area_codes['area_code'].tolist()

	# Print a few area codes to verify
	print(area_codes[:10])
else:
	print("The file 'cu.area' does not exist.")
