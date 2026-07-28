import os
import json
import psycopg2
from datetime import datetime

# Database connection parameters matching the docker-compose settings
DB_PARAMS = {
    "host": "localhost",
    "database": "nhl_predictions_db",
    "user": "nhl_analytics_user",
    "password": "nhl_secure_password",
    "port": "5432"
}

def load_json_to_postgres():
    # Establish a connection to the running PostgreSQL container
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        print("Successfully connected to the PostgreSQL database.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return

    data_dir = "./data"
    inserted_count = 0

    # Loop through all 32 JSON files in the data directory
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            
            with open(file_path, 'r') as file:
                payload = json.load(file)
                
                # Navigate the nested NHL API structure to find the games list
                games = payload.get("games", [])
                
                for game in games:
                    # Extract and transform individual game attributes
                    game_id = game.get("id")
                    season = game.get("season")
                    
                    # Convert string date (YYYY-MM-DD) to a Python date object
                    game_date_str = game.get("gameDate")
                    game_date = datetime.strptime(game_date_str, "%Y-%m-%d").date() if game_date_str else None
                    
                    venue = game.get("venue", {}).get("default", "Unknown")
                    home_team = game.get("homeTeam", {}).get("abbrev")
                    away_team = game.get("awayTeam", {}).get("abbrev")
                    home_score = game.get("homeTeam", {}).get("score")
                    away_score = game.get("awayTeam", {}).get("score")

                    # Skip games that have not been played yet (scores will be missing)
                    if home_score is None or away_score is None:
                        continue

                    # SQL query utilizing an UPSERT (ON CONFLICT DO NOTHING) to prevent duplicate rows
                    insert_query = """
                        INSERT INTO nhl_games (game_id, season, game_date, venue, home_team, away_team, home_score, away_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (game_id) DO NOTHING;
                    """
                    
                    cursor.execute(insert_query, (game_id, season, game_date, venue, home_team, away_team, home_score, away_score))
                    inserted_count += cursor.rowcount

    # Commit changes permanently and close the session
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Data migration complete. Total rows added/verified: {inserted_count}")

if __name__ == "__main__":
    load_json_to_postgres()