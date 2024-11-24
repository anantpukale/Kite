import requests
import json
import sqlite3
from datetime import datetime


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Create balkanbet_matches table (merged events and competitors)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS balkanbet_matches (
            event_id INTEGER PRIMARY KEY,
            event_name TEXT,
            starts_at TEXT,
            home_team_id INTEGER,
            home_team TEXT,
            home_team_short_name TEXT,
            home_team_type INTEGER,
            away_team_id INTEGER,
            away_team TEXT,
            away_team_short_name TEXT,
            away_team_type INTEGER
        )
    ''')

    # Create balkanbet_odds table with markets as a column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS balkanbet_odds (
            event_id INTEGER,
            market_id INTEGER,
            market_name TEXT,
            outcome_name TEXT,
            outcome_odd REAL,
            FOREIGN KEY (event_id) REFERENCES balkanbet_matches (event_id)
        )
    ''')

    conn.commit()
    conn.close()


# Save event and competitor details to the database
def save_to_db(event_details):
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Insert event and competitor details
    event_id = event_details.get('id')
    event_name = event_details.get('name')
    starts_at = event_details.get('startsAt')

    # Format the 'starts_at' date to "YYYY-MM-DD HH:MM:SS"
    starts_at_formatted = datetime.strptime(starts_at, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")

    competitors = event_details.get('competitors', [])
    if len(competitors) >= 2:
        # Ensure we have at least two competitors to save
        home_team = competitors[0]
        away_team = competitors[1]

        home_team_id = home_team.get('id')
        home_team_name = home_team.get('name')
        home_team_short_name = home_team.get('shortName')
        home_team_type = home_team.get('type')

        away_team_id = away_team.get('id')
        away_team_name = away_team.get('name')
        away_team_short_name = away_team.get('shortName')
        away_team_type = away_team.get('type')

        try:
            cursor.execute('''
                INSERT INTO balkanbet_matches (
                    event_id, event_name, starts_at, 
                    home_team_id, home_team, home_team_short_name, home_team_type,
                    away_team_id, away_team, away_team_short_name, away_team_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, event_name, starts_at_formatted,
                  home_team_id, home_team_name, home_team_short_name, home_team_type,
                  away_team_id, away_team_name, away_team_short_name, away_team_type))
        except sqlite3.IntegrityError:
            print(f"Event ID {event_id} already exists in the database.")
    else:
        print(f"Event ID {event_id} does not have enough competitors to save.")

    # Insert market and outcome details
    for market in event_details.get('markets', []):
        market_id = market.get('id')
        market_name = market.get('name')

        for outcome in market.get('outcomes', []):
            outcome_name = outcome.get('name')
            outcome_odd = outcome.get('odd')

            cursor.execute('''
                INSERT INTO balkanbet_odds (event_id, market_id, market_name, outcome_name, outcome_odd)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_id, market_id, market_name, outcome_name, outcome_odd))

    conn.commit()
    conn.close()


def get_event_details(event_id, headers):
    url = f'https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events/{event_id}?companyUuid=4f54c6aa-82a9-475d-bf0e-dc02ded89225&id={event_id}&language=%7B%22default%22:%22sr-Latn%22,%22events%22:%22sr-Latn%22,%22sport%22:%22sr-Latn%22,%22category%22:%22sr-Latn%22,%22tournament%22:%22sr-Latn%22,%22team%22:%22sr-Latn%22,%22market%22:%22sr-Latn%22%7D&timezone=Europe%2FBelgrade&dataFormat=%7B%22default%22:%22array%22,%22markets%22:%22array%22,%22events%22:%22array%22%7D'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        return

    event_details = data.get('data', {})
    if not event_details:
        print(f"No data found for Event ID: {event_id}")
        return

    print_event_details(event_details)
    save_to_db(event_details)  # Save to the database


def print_event_details(event_details):
    print(f"\nEvent ID: {event_details['id']}")
    # print(f"Event Name: {event_details['name']}")
    # starts_at_formatted = datetime.strptime(event_details['startsAt'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
    #     "%Y-%m-%d %H:%M:%S")
    # print(f"Starts At: {starts_at_formatted}")
    #
    # for market in event_details.get('markets', []):
    #     print(f"\nMarket Name: {market['name']}")
    #     print(f"Market ID: {market['id']}")
    #     for outcome in market.get('outcomes', []):
    #         print(f"  Outcome Name: {outcome['name']}")
    #         print(f"  Odd: {outcome['odd']}")
    #
    # for competitor in event_details.get('competitors', []):
    #     print(f"\nCompetitor Name: {competitor['name']}")
    #     print(f"Short Name: {competitor['shortName']}")
    #     print(f"Type: {competitor['type']}")


def main():
    init_db()  # Initialize the database
    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
        'origin': 'https://sports-sm-web.7platform.net',
        'referer': 'https://sports-sm-web.7platform.net/',
    }

    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    try:
        response = requests.get(
            f'https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events?deliveryPlatformId=3&dataFormat=%7B%22default%22:%22object%22,%22events%22:%22array%22,%22outcomes%22:%22array%22%7D&language=%7B%22default%22:%22sr-Latn%22,%22events%22:%22sr-Latn%22,%22sport%22:%22sr-Latn%22,%22category%22:%22sr-Latn%22,%22tournament%22:%22sr-Latn%22,%22team%22:%22sr-Latn%22,%22market%22:%22sr-Latn%22%7D&timezone=Europe%2FBelgrade&company=%7B%7D&companyUuid=4f54c6aa-82a9-475d-bf0e-dc02ded89225&filter[sportId]=78&filter[from]={current_time}&sort=categoryPosition,categoryName,tournamentPosition,tournamentName,startsAt&offerTemplate=WEB_OVERVIEW&shortProps=1',
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        return

    if 'errors' in data:
        print(f"Error: {data['errors'][0]['detail']}")
    else:
        print("Data retrieved successfully")
        events = data.get('data', {}).get('events', [])
        for event in events:
            event_id = event['a']
            print(f"Event ID: {event_id}")
            get_event_details(event_id, headers)


if __name__ == "__main__":
    main()
