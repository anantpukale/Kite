from datetime import datetime
import requests
import sqlite3

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,de;q=0.8,sr-Latn-RS;q=0.7,sr;q=0.6,pl;q=0.5',
    'content-type': 'application/json',
    'medium': 'WEB',
    'origin': 'https://www.mozzartbet.com',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
}

json_data = {
    'date': 'today',
    'sort': 'bycompetition',
    'currentPage': 0,
    'pageSize': 300,
    'sportId': 5,
    'competitionIds': [],
    'search': '',
    'matchTypeId': 0,
}


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Create mozzart_matches table to store match details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mozzart_matches (
            match_id INTEGER PRIMARY KEY,
            sport_id INTEGER,
            sport_name TEXT,
            competition_id INTEGER,
            competition_name TEXT,
            home_team_id INTEGER,
            home_team TEXT,
            visitor_team_id INTEGER,
            visitor_team TEXT,
            start_time TEXT,
            status_name TEXT
        )
    ''')

    # Create mozzart_odds table to store odds details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mozzart_odds (
            match_id INTEGER,
            odd_id INTEGER,
            game_name TEXT,
            subgame_name TEXT,
            description TEXT,
            value REAL,
            FOREIGN KEY (match_id) REFERENCES mozzart_matches (match_id)
        )
    ''')

    conn.commit()
    conn.close()


# Save match and odds details to the database
def save_to_db(match_details):
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Extract match details
    match_id = match_details['match']['id']
    sport_id = match_details['match']['sport']['id']
    sport_name = match_details['match']['sport']['name']
    competition_id = match_details['match']['competition']['id']
    competition_name = match_details['match']['competition']['name']
    home_team_id = match_details['match']['home']['id']
    home_team_name = match_details['match']['home']['name']
    visitor_team_id = match_details['match']['visitor']['id']
    visitor_team_name = match_details['match']['visitor']['name']
    start_time = datetime.fromtimestamp(match_details['match']['startTime'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    status_name = match_details['match']['status']['name']

    try:
        # Insert match details
        cursor.execute('''
            INSERT INTO mozzart_matches (
                match_id, sport_id, sport_name, competition_id, competition_name,
                home_team_id, home_team, visitor_team_id, visitor_team, start_time, status_name
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id, sport_id, sport_name, competition_id, competition_name, home_team_id, home_team_name,
            visitor_team_id,
            visitor_team_name, start_time, status_name))
    except sqlite3.IntegrityError:
        print(f"Match ID {match_id} already exists in the database.")

    # Insert odds details
    for odd in match_details['match']['odds']:
        odd_id = odd['id']
        game_name = odd['game']['name']
        subgame_name = odd['subgame']['name']
        description = odd['subgame'].get('description', '')
        try:
            value = odd['value']
        except:
            value = odd['specialOddValue']

        cursor.execute('''
            INSERT INTO mozzart_odds (match_id, odd_id, game_name, subgame_name, description, value)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (match_id, odd_id, game_name, subgame_name, description, value))

    conn.commit()
    conn.close()


# Function to print match details (for debugging or logging purposes)
def print_match_details(match_data):
    print(f"Match ID: {match_data['match']['id']}")
    # print(f"Teams: {match_data['match']['home']['name']} vs {match_data['match']['visitor']['name']}")

    # print("\nOdds:")
    # for odd in match_data['match']['odds']:
    #     try:
    #         print(
    #             f"{odd['game']['name']} - {odd['subgame']['name']}: {odd['subgame'].get('description', '')} (Odd Value: {odd['value']})")
    #     except:
    #         print(
    #             f"{odd['game']['name']} - {odd['subgame']['name']}: {odd['subgame'].get('description', '')} (Odd Value: {odd['specialOddValue']})")
    #
    # print("\nOdds Group:")
    # for odds_group in match_data['match']['oddsGroup']:
    #     print(f"\n{odds_group['groupName']}:")
    #     for odd in odds_group['odds']:
    #         try:
    #             print(
    #                 f"{odd['game']['name']} - {odd['subgame']['name']}: {odd['subgame'].get('description', '')} (Odd Value: {odd['value']})")
    #         except:
    #             print(
    #                 f"{odd['game']['name']} - {odd['subgame']['name']}: {odd['subgame'].get('description', '')} (Odd Value: {odd['specialOddValue']})")


# Main function to fetch and process data
def main():
    init_db()  # Initialize the database

    # First-level request to fetch matches
    response = requests.post('https://www.mozzartbet.com/betting/matches', headers=headers,
                             json=json_data)
    data = response.json()

    # Iterate over the matches and process each one
    for match in data.get('items', []):
        match_id = match.get('id')

        # Second-level request for each match id
        subgame_data = {'subgameIds': []}
        match_response = requests.post(f'https://www.mozzartbet.com/match/{match_id}', headers=headers,
                                       json=subgame_data)

        # Parse and save the second-level response
        match_data = match_response.json()
        print_match_details(match_data)  # Optional: Print match details for debugging
        save_to_db(match_data)  # Save to the database


if __name__ == "__main__":
    main()
