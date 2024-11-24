query = """CREATE VIEW unified_odds AS
SELECT
    event_id,
    market_id,
    market_name,
    outcome_name,
    odds AS odds_value,
    'Primobet' AS provider
FROM primobet_odds

UNION ALL

SELECT
    event_id,
    market_id,
    market_name,
    outcome_name,
    outcome_odd AS odds_value,
    'Balkanbet' AS provider
FROM balkanbet_odds

UNION ALL

SELECT
    match_id AS event_id,
    NULL AS market_id,
    odds_key AS market_name,
    odds_name AS outcome_name,
    odds_value,
    'Maxbet' AS provider
FROM maxbet_odds

UNION ALL

SELECT
    event_id,
    market_id,
    market_name,
    outcome_name,
    outcome_odd AS odds_value,
    'Meridianbet' AS provider
FROM meridianbet_odds; """

import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
# Specify the path to your SQLite database file
db_path = 'tennis.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

