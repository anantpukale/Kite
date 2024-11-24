import requests
import json
import sqlite3
from datetime import datetime, timedelta


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Create primobet_matches table to store match details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS primobet_matches (
            event_id INTEGER PRIMARY KEY,
            match_name TEXT,
            home_team TEXT,
            away_team TEXT,
            start_time TEXT
        )
    ''')

    # Create primobet_odds table to store market details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS primobet_odds (
            market_id INTEGER,
            event_id INTEGER,
            market_name TEXT,
            specifier TEXT,
            status TEXT,
            priority INTEGER,
            provider TEXT,
            most_balanced TEXT,
            market_groups TEXT,
            outcome_id INTEGER,
            outcome_name TEXT,
            odds REAL,
            active TEXT,
            FOREIGN KEY (event_id) REFERENCES primobet_matches (event_id)
        )
    ''')

    conn.commit()
    conn.close()


# Save match and market details to the database
def save_to_db(event_id, match_name, home_team, away_team, start_time, market_data):
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Save match details
    try:
        cursor.execute('''
            INSERT INTO primobet_matches (event_id, match_name, home_team, away_team, start_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (event_id, match_name, home_team, away_team, start_time))
    except sqlite3.IntegrityError:
        print(f"Match ID {event_id} already exists in the database.")

    # Save market details
    for market in market_data:
        market_id = market['id']
        market_name = market.get('name', 'Unknown Market Name')
        specifier = market.get('specifier', 'None')
        status = market.get('status', 'Unknown')
        priority = market.get('priority', 'Unknown')
        provider = market.get('provider', 'Unknown')
        most_balanced = market.get('most_balanced', 'Unknown')
        market_groups = ', '.join(market.get('market_groups', []))

        if 'outcomes' in market and market['outcomes']:
            for outcome in market['outcomes']:
                outcome_id = outcome['id']
                outcome_name = outcome.get('name', 'Unknown Outcome Name')
                odds = outcome.get('odds', 'Unknown Odds')
                active = outcome.get('active', 'Unknown')

                cursor.execute('''
                    INSERT INTO primobet_odds (
                        market_id, event_id, market_name, specifier, status, priority, provider,
                        most_balanced, market_groups, outcome_id, outcome_name, odds, active
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (market_id, event_id, market_name, specifier, status, priority, provider,
                      most_balanced, market_groups, outcome_id, outcome_name, odds, active))
        else:
            cursor.execute('''
                INSERT INTO primobet_odds (
                    market_id, event_id, market_name, specifier, status, priority, provider,
                    most_balanced, market_groups, outcome_id, outcome_name, odds, active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)
            ''', (market_id, event_id, market_name, specifier, status, priority, provider,
                  most_balanced, market_groups))

    conn.commit()
    conn.close()


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,de;q=0.8,sr-Latn-RS;q=0.7,sr;q=0.6,pl;q=0.5',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
}

# Get today's date and the date for one day from now
now = datetime.utcnow()
start_from = now.strftime('%Y-%m-%dT%H:%M:%S.000Z')
start_to = (now + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

# Define initial parameters for the API request
params = {
    'bettable': 'true',
    'limit': '50',
    'page': '1',
    'sort_by': [
        'start_time:asc',
        'tournament.priority:asc',
    ],
    'sport_key': 'tennis',
    'start_from': start_from,
    'start_to': start_to,
    'type': 'match',
}


def main():
    init_db()  # Initialize the database

    # Start from the first page
    current_page = 1
    while True:
        params['page'] = str(current_page)
        response = requests.get('https://primobet.com/api/v2/matches', params=params, headers=headers)
        response_data = response.json()

        if 'data' in response_data and response_data['data']:
            for match in response_data['data']:
                event_id = match['id']
                # Construct match name using home and away team names
                home_team = match['competitors']['home']['name']
                away_team = match['competitors']['away']['name']
                match_name = f"{home_team} vs {away_team}"
                start_time = datetime.strptime(match.get('start_time', '1970-01-01T00:00:00Z'),
                                               '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')

                # print(f"\n{'=' * 50}")
                # print(f"Processing match ID: {event_id} - {match_name}")

                # Second level request: Fetch market details for each match
                market_params = {'limit': '500'}
                # print(f'https://primobet.com/api/v2/matches/{event_id}/markets')
                market_response = requests.get(f'https://primobet.com/api/v2/matches/{event_id}/markets',
                                               params=market_params, headers=headers)
                market_data = market_response.json().get('data', [])

                # Save match and market details to the database
                save_to_db(event_id, match_name, home_team, away_team, start_time, market_data)

        else:
            # Break the loop if there are no more matches to process or if there's an error
            print("No more matches to process or error encountered.")
            break

        # Check for pagination and if it's time to stop
        if 'pagination' in response_data:
            total_pages = response_data['pagination']['last_page']
            if current_page >= total_pages:
                break
        else:
            break

        current_page += 1


if __name__ == "__main__":
    main()
