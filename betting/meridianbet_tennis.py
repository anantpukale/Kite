from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from datetime import datetime
import requests
import sqlite3
import time
import json


def get_auth_token():
    chrome_driver_path = "C:\\Selenium Driver\\chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()

    # Run Chrome in headless mode
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Add options to Selenium Wire
    seleniumwire_options = {
        'disable_encoding': True  # Disable encoding to capture raw network requests
    }

    # Start the browser with Selenium Wire options
    driver = webdriver.Chrome(service=service, options=options, seleniumwire_options=seleniumwire_options)

    try:
        # Open the target URL
        driver.get("https://meridianbet.rs/sr/kladjenje/tenis")

        # Wait for the "SVE" button to be visible
        sve_button = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//div[text()=' Sve ']"))
        )

        # Start tracking the network events
        print("Tracking network events...")

        # Click the "SVE" button
        sve_button.click()

        # Wait for the network request to complete
        time.sleep(10)  # Adjust the sleep time as needed to capture the request

        # Iterate over captured requests
        for request in driver.requests:
            if request.url.startswith('https://online.meridianbet.com/betshop/api/v1/standard/sport/56/leagues'):
                if 'Authorization' in request.headers:
                    # Extract and return the Authorization token
                    auth_token = request.headers['Authorization']
                    print(f"Authorization Token Found")
                    return auth_token
        print("Authorization token not found in network requests.")
        return None

    finally:
        # Close the browser
        driver.quit()


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Create meridianbet_matches table without home_team_id, away_team_id, and team_type columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meridianbet_matches (
            event_id INTEGER PRIMARY KEY,
            event_name TEXT,
            starts_at TEXT,
            home_team_name TEXT,
            home_team_short_name TEXT,
            away_team_name TEXT,
            away_team_short_name TEXT
        )
    ''')

    # Create meridianbet_odds table with markets as a column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meridianbet_odds (
            event_id INTEGER,
            market_id INTEGER,
            market_name TEXT,
            outcome_name TEXT,
            outcome_odd REAL,
            FOREIGN KEY (event_id) REFERENCES meridianbet_matches (event_id)
        )
    ''')

    conn.commit()
    conn.close()


# Save event and team details to the database for Meridianbet
def save_meridianbet_to_db(event_details):
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Extract event details
    event_id = event_details.get('header', {}).get('eventId')
    event_name = f"{event_details.get('header', {}).get('rivals', [])[0]} vs {event_details.get('header', {}).get('rivals', [])[1]}"
    starts_at = event_details.get('header', {}).get('startTime')

    # Format the 'starts_at' date to "YYYY-MM-DD HH:MM:SS"
    starts_at_formatted = datetime.utcfromtimestamp(starts_at / 1000).strftime("%Y-%m-%d %H:%M:%S")

    rivals = event_details.get('header', {}).get('rivals', [])
    if len(rivals) >= 2:
        # Ensure we have at least two competitors to save
        home_team_name = rivals[0]
        away_team_name = rivals[1]

        try:
            cursor.execute('''
                INSERT INTO meridianbet_matches (
                    event_id, event_name, starts_at, 
                    home_team_name, home_team_short_name,
                    away_team_name, away_team_short_name
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, event_name, starts_at_formatted,
                  home_team_name, home_team_name,
                  away_team_name, away_team_name))
        except sqlite3.IntegrityError:
            print(f"Event ID {event_id} already exists in the database.")
    else:
        print(f"Event ID {event_id} does not have enough competitors to save.")

    # Insert market and outcome details
    for game in event_details.get('games', []):
        market_id = game.get('gameTemplateId')
        market_name = game.get('marketName')

        for market in game.get('markets', []):
            for outcome in market.get('selections', []):
                outcome_name = outcome.get('name')
                outcome_odd = outcome.get('price')

                cursor.execute('''
                    INSERT INTO meridianbet_odds (event_id, market_id, market_name, outcome_name, outcome_odd)
                    VALUES (?, ?, ?, ?, ?)
                ''', (event_id, market_id, market_name, outcome_name, outcome_odd))

    conn.commit()
    conn.close()


# First-level request to get leagues and events
def get_leagues_and_events(headers):
    page = 0
    all_events = []

    while True:
        params = {
            'page': str(page),
            'time': 'ALL',
        }

        response = requests.get(
            'https://online.meridianbet.com/betshop/api/v1/standard/sport/56/leagues',
            params=params,
            headers=headers,
        )

        # Decode bytes to string and load into Python dictionary
        data_dict = json.loads(response.content.decode('utf-8'))

        # Check for error code
        if data_dict.get('errorCode') is not None:
            print("Error code:", data_dict['errorCode'])
            break  # Stop if there's an error code

        # Check if leagues list is empty
        if not data_dict['payload']['leagues']:  # Empty list means no more data
            print("No more leagues to fetch. Stopping pagination.")
            break

        # Collect all events from the response
        leagues = data_dict['payload']['leagues']
        for league in leagues:
            for event in league['events']:
                all_events.append(event['header']['eventId'])

        page += 1

    return all_events


def print_event_details(event_details):
    # Print only the event name (match name)
    print(f"{event_details['header']['rivals'][0]} vs {event_details['header']['rivals'][1]}")


# def print_event_details(event_details):
#     print(f"\nEvent ID: {event_details['header']['eventId']}")
#     print(f"Event Name: {event_details['header']['rivals'][0]} vs {event_details['header']['rivals'][1]}")
#     starts_at_formatted = datetime.utcfromtimestamp(event_details['header']['startTime'] / 1000).strftime(
#         "%Y-%m-%d %H:%M:%S")
#     print(f"Starts At: {starts_at_formatted}")
#
#     for game in event_details.get('games', []):
#         print(f"\nMarket Name: {game['marketName']}")
#         for market in game.get('markets', []):
#             print(f"  Market ID: {market['marketId']}")
#             for outcome in market.get('selections', []):
#                 print(f"    Outcome Name: {outcome['name']}")
#                 print(f"    Odd: {outcome['price']}")


# Function to fetch and save event details for Meridianbet
def get_event_details(event_id, headers):
    response = requests.get(f'https://online.meridianbet.com/betshop/api/v2/events/{event_id}', headers=headers)
    try:
        response.raise_for_status()
        event_details = response.json().get('payload', {})
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        return

    if not event_details:
        print(f"No data found for Event ID: {event_id}")
        return

    print_event_details(event_details)
    save_meridianbet_to_db(event_details)  # Save to the database


# Main function to execute the first and second level requests
def main():
    auth_token = get_auth_token()
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'sr',
        'authorization': auth_token,
        'origin': 'https://meridianbet.rs',
        'priority': 'u=1, i',
        'referer': 'https://meridianbet.rs/',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    }

    # First-level request to get all event IDs
    event_ids = get_leagues_and_events(headers)

    # Second-level request for each event to get detailed data
    for event_id in event_ids:
        get_event_details(event_id, headers)


if __name__ == "__main__":
    init_db()
    main()
