import sqlite3
import requests

odds_names_mapping = {
    '1': ['Konacan Ishod', '1'],
    '3': ['Konacan Ishod', '2'],
    '251': ['Hendikep gemovi', 'HG1'],
    '253': ['Hendikep gemovi', 'HG2'],
    '254': ['Ukupno gemova', 'G-'],
    '256': ['Ukupno gemova', 'G+'],
    '257': ['Ukupno gemova prvi set', 'PG-'],
    '259': ['Ukupno gemova prvi set', 'PG+'],
    '260': ['Tačan broj setova', 'S2'],
    '261': ['Tačan broj setova', 'S3'],
    '262': ['Tačan broj setova', 'S4'],
    '263': ['Tačan broj setova', 'S5'],
    '375': ['Mix Igre', '1&G-'],
    '376': ['Mix Igre', '1&G+'],
    '377': ['Mix Igre', '2&G-'],
    '378': ['Mix Igre', '2&G+'],
    '461': ['Ukupno gemova druga granica', 'UG2-'],
    '463': ['Ukupno gemova druga granica', 'UG2+'],
    '50510': ['Prvi Set', 'PS1'],
    '50511': ['Prvi Set', 'PS2'],
    '50512': ['Drugi Set', 'DS1'],
    '50513': ['Drugi Set', 'DS2'],
    '50520': ['Ukupno gemova drugi set', '2S-'],
    '50521': ['Ukupno gemova drugi set', '2S+'],
    '50528': ['Tie Break', 'TBDA'],
    '50529': ['Tie Break', 'TBNE'],
    '50538': ['Hendikep set', 'HS1'],
    '50539': ['Hendikep set', 'HS2'],
    '50540': ['Prvi set kraj', 'S1-1'],
    '50541': ['Prvi set kraj', 'S1-2'],
    '50542': ['Prvi set kraj', 'S2-1'],
    '50543': ['Prvi set kraj', 'S2-2'], \
    '50544': ['Tacan Rezultat 3', 'S2:0'],
    '50545': ['Tacan Rezultat 3', 'S0:2'],
    '50546': ['Tacan Rezultat 3', 'S3:0'],
    '50547': ['Tacan Rezultat 3', 'S0:3'],
    '50548': ['Tacan Rezultat 3', 'S2:1'],
    '50549': ['Tacan Rezultat 3', 'S1:2'],
    '50550': ['Tacan Rezultat 3', 'S3:1'],
    '50551': ['Tacan Rezultat 3', 'S1:3'],
    '50552': ['Tacan Rezultat 3', 'S3:2'],
    '50553': ['Tacan Rezultat 3', 'S2:3'],
    '51061': ['Pada vise gemova u setu', 'SI>'],
    '51062': ['Pada vise gemova u setu', 'SI=SII'],
    '51063': ['Pada vise gemova u setu', 'SII>'],
    '51196': ['Tie break prvi set', 'PTBDA'],
    '51197': ['Tie break prvi set', 'PTBNE'],
    '51198': ['Mix prvi set & gejmovi', '1S1&T.6'],
    '51199': ['Mix prvi set & gejmovi', '1S1&7-8'],
    '51200': ['Mix prvi set & gejmovi', '1S1&9-12'],
    '51201': ['Mix prvi set & gejmovi', '1S1&T.13'],
    '51202': ['Mix prvi set & gejmovi', '1S2&T.6'],
    '51203': ['Mix prvi set & gejmovi', '1S2&7-8'],
    '51204': ['Mix prvi set & gejmovi', '1S2&9-12'],
    '51205': ['Mix prvi set & gejmovi', '1S2&T.13'],
    '51206': ['Mix prvi set & manje/vise gemova', '1S1&0-9'],
    '51207': ['Mix prvi set & manje/vise gemova', '1S1&10+'],
    '51208': ['Mix prvi set & manje/vise gemova', '1S2&0-9'],
    '51209': ['Mix prvi set & manje/vise gemova', '1S2&10+'],
    '51210': ['Mix drugi set & gemovi', '2S1&0-9'],
    '51211': ['Mix drugi set & gemovi', '2S1&10+'],
    '51212': ['Mix drugi set & gemovi', '2S2&0-9'],
    '51213': ['Mix drugi set & gemovi', '2S2&10+'],
    '51370': ['Ukupno gemova prvi set druga granica', '1S2-'],
    '51372': ['Ukupno gemova prvi set druga granica', '1S2+'],
    '51373': ['Ukupno gemova prvi set treća granica', '1S3-'],
    '51375': ['Ukupno gemova prvi set treća granica', '1S3+'],
    '51376': ['Ukupno gemova prvi set cetvrta granica', '1S4-'],
    '51378': ['Ukupno gemova prvi set cetvrta granica', '1S4+'],
    '51379': ['Ukupno gemova prvi set peta granica', '1S5-'],
    '51381': ['Ukupno gemova prvi set peta granica', '1S5+'],
    '51657': ['Set-Set', 'NS'],
    '51658': ['Set-Set', 'SS']
}


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    # Create table for match details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maxbet_matches (
            match_id INTEGER PRIMARY KEY,
            home_team TEXT,
            away_team TEXT
        )
    ''')

    # Create table for odds details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maxbet_odds (
            match_id INTEGER,
            odds_name TEXT,
            odds_value REAL,
            odds_key TEXT,
            custom_number REAL,
            FOREIGN KEY (match_id) REFERENCES maxbet_matches (match_id)
        )
    ''')

    conn.commit()
    conn.close()


# Save match and odds details to the database
def save_to_db(matches_details):
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    for match_details in matches_details:
        # Extract match details
        match_id = match_details.get('id')
        home_team = match_details.get('home')
        away_team = match_details.get('away')

        try:
            # Insert match details
            cursor.execute('''
                INSERT INTO maxbet_matches (match_id, home_team, away_team)
                VALUES (?, ?, ?)
            ''', (match_id, home_team, away_team))
        except sqlite3.IntegrityError:
            # print(f"Match ID {match_id} already exists in the database.")
            pass
        # Extract custom numbers from the 'params' section
        params = match_details.get('params', {})
        # Extract custom numbers from the 'params' section
        custom_numbers = {
            '254': params.get('overUnderGames', None),  # Ukupno gemova 22.5
            '256': params.get('overUnderGames', None),  # Ukupno gemova 22.5
            '461': params.get('overUnderGamesSecondSet', None),  # Ukupno gemova drugi set 9.5
            '463': params.get('overUnderGamesSecondSet', None),  # Ukupno gemova drugi set 9.5
            '375': params.get('overUnderGames', None),  # Mix Igre 22.5
            '376': params.get('overUnderGames', None),  # Mix Igre 22.5
            '377': params.get('overUnderGames', None),  # Mix Igre 22.5
            '378': params.get('overUnderGames', None),  # Mix Igre 22.5
            '50520': params.get('overUnderGamesSecondSet', None),  # Ukupno gemova drugi set 9.5
            '50521': params.get('overUnderGamesSecondSet', None),  # Ukupno gemova drugi set 9.5
            '51370': params.get('overUnderGamesFirstSet2', None),  # Ukupno gemova prvi set druga granica 8.5
            '51372': params.get('overUnderGamesFirstSet2', None),  # Ukupno gemova prvi set druga granica 8.5
            '51373': params.get('overUnderGamesFirstSet3', None),  # Ukupno gemova prvi set treća granica 10.5
            '51375': params.get('overUnderGamesFirstSet3', None),  # Ukupno gemova prvi set treća granica 10.5
            '51376': params.get('overUnderGamesFirstSet4', None),  # Ukupno gemova prvi set četvrta granica 7.5
            '51378': params.get('overUnderGamesFirstSet4', None),  # Ukupno gemova prvi set četvrta granica 7.5
            '51379': params.get('overUnderGamesFirstSet5', None),  # Ukupno gemova prvi set peta granica 12.5
            '51381': params.get('overUnderGamesFirstSet5', None),  # Ukupno gemova prvi set peta granica 12.5
            '51206': params.get('overUnderGamesFirstSet', None),  # Mix prvi set & manje/vise gemova 9.5
            '51207': params.get('overUnderGamesFirstSet', None),  # Mix prvi set & manje/vise gemova 9.5
            '51208': params.get('overUnderGamesFirstSet', None),  # Mix prvi set & manje/vise gemova 9.5
            '51209': params.get('overUnderGamesFirstSet', None),  # Mix prvi set & manje/vise gemova 9.5
            '51210': params.get('overUnderGamesSecondSet', None),  # Mix drugi set & gemovi 9.5
            '51211': params.get('overUnderGamesSecondSet', None),  # Mix drugi set & gemovi 9.5
            '51212': params.get('overUnderGamesSecondSet', None),  # Mix drugi set & gemovi 9.5
            '51213': params.get('overUnderGamesSecondSet', None),  # Mix drugi set & gemovi 9.5
            '50538': params.get('hd2', None),  # Hendikep set 1.5
            '50539': params.get('hd2', None),  # Hendikep set 1.5
            '251': params.get('handicapGames', None),  # Hendikep gemovi 1.5
            '253': params.get('handicapGames', None),  # Hendikep gemovi 1.5
        }

        # Insert odds details
        match_odds = match_details.get('odds', {})
        for k, v in match_odds.items():
            odds_name = '-'.join(odds_names_mapping.get(str(k), [str(k)]))  # Map the odds name
            if '-' in odds_name:
                odds_key = odds_name.split('-')[-1]
                odds_name = odds_name.rsplit('-', 1)[0]
            else:
                odds_key = ''  # If no dash, no separate key

            # Extract the custom number for this odd if available
            custom_number = custom_numbers.get(str(k), None)

            cursor.execute('''
                INSERT INTO maxbet_odds (match_id, odds_name, odds_value, odds_key, custom_number)
                VALUES (?, ?, ?, ?, ?)
            ''', (match_id, odds_name, v, odds_key, custom_number))

    conn.commit()
    conn.close()


# Function to fetch leagues
def fetch_leagues():
    response = requests.get('https://www.maxbet.rs/restapi/offer/sr/categories/sport/T/l')
    if response.status_code == 200:
        data = response.json()
        leagues = data.get('categories', [])
        league_ids = {league.get('id'): league.get('name') for league in leagues if league.get('id')}
        return league_ids
    else:
        return {}


# Function to fetch match data
def fetch_match_data(match_id):
    response = requests.get(f'https://www.maxbet.rs/restapi/offer/sr/match/{match_id}')
    return response.json()


# Function to fetch matches for each league
def fetch_matches_for_league(league_id, league_name):
    detail_url = f"https://www.maxbet.rs/restapi/offer/sr/sport/T/league/{league_id}/mob"
    response = requests.get(detail_url)
    if response.status_code == 200:
        data = response.json()
        matches = data.get('esMatches', [])
        match_ids = [match.get('id') for match in matches if match.get('id')]
        return match_ids
    else:
        print(
            f"Failed to fetch matches for League: {league_name} (ID: {league_id}) with status code: {response.status_code}")
        return []


# Function to get odds details
def get_odds_details(match_details):
    match_odds = match_details.get('odds', {})
    print(f"Match ID: {match_details.get('id')}")
    # print(f"Home: {match_details.get('home')} vs Away: {match_details.get('away')}")
    # print("Odds Details:")

    for k, v in match_odds.items():
        odds_name = '-'.join(odds_names_mapping.get(str(k), [str(k)]))  # Use the odds mapping here
        if '-' in odds_name:
            odd_key = odds_name.split('-')[-1]
            odds_name = odds_name.rsplit('-', 1)[0]
        else:
            odd_key = ''  # If no dash, no separate key
        # print(f"{odds_name}: {v} [Key: {odd_key}]")


# Main function to execute the full flow
def main():
    init_db()  # Initialize the database
    leagues = fetch_leagues()
    all_matches_details = []  # To collect all match details

    for league_id, league_name in leagues.items():
        match_ids = fetch_matches_for_league(league_id, league_name)
        for match_id in match_ids:
            match_data = fetch_match_data(match_id)
            get_odds_details(match_data)
            all_matches_details.append(match_data)  # Add to the list of all matches

    # Save all matches to the database in one batch
    save_to_db(all_matches_details)


if __name__ == "__main__":
    main()
