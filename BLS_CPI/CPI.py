import requests
import time

# Your BLS API key
API_KEY = 'a1796fadf3704a91a7a48be926bc3a88'

# Base URL for the BLS API
BASE_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'

area_codes=[
	"0100",
"A213",
"A214",
"A311",
"A421",
"A425",
"D000",
	"D200",
	"D300",
	"N000",
	"N100",
	"N200",
	"N300",
	"N400",
	"S000",
	"S100",
	"S11A",
	"S12A",
	"S12B",
	"S200",
	"S23A",
	"S23B",
	"S24A",
	"S24B",
	"S300",
	"S35A",
	"S35B",
	"S35C",
	"S35D",
	"S35E",
	"S37A",
	"S37B",
	"S400",
	"S48A",
	"S48B",
	"S49A",
	"S49B",
	"S49C",
	"S49D",
	"S49E",
	"S49F",
	"S49G"
]

# List of area codes for metropolitan areas
# You need to replace these with actual area codes from the BLS documentation.
area_codes = [
	'0110',  # Example national average
	# Add actual metropolitan area codes here
]

# Construct series IDs for CPI-W All Items
series_ids = [f'CWUR{area_code}SA0' for area_code in area_codes]
#print(series_ids)


def fetch_bls_data(series_ids, api_key):
	data = []
	start_year = '2016'
	end_year = '2023'
	for series_id in series_ids:
		response = requests.post(
			BASE_URL,
			json={
				"seriesid": [series_id],
				"registrationkey": api_key,
				"startyear": start_year,
				"endyear": end_year,
			}
		)
		if response.status_code == 200:
			data.append(response.json())
		else:
			print(f"Error fetching data for series ID {series_id}: {response.status_code}")
			print(response.text)

		# Respect API rate limits
		time.sleep(1)
	return data


# Fetch the data
data = fetch_bls_data(series_ids, API_KEY)

# Process and display the data
for series_data in data:
	print(series_data)
	if "Results" in series_data and "series" in series_data["Results"]:
		for series in series_data["Results"]["series"]:
			print(f"Series ID: {series['seriesID']}")
			for item in series['data']:
				print(f"Year: {item['year']}, Period: {item['period']}, Value: {item['value']}")
	else:
		print("No data found for some series IDs.")

