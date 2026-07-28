import requests
import json
import os
from datetime import datetime
import time

# List of all 32 current NHL team abbreviations
TEAMS = [
    "ANA", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ", 
    "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", 
    "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA", 
    "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WPG", "UTA"
]

def fetch_all_teams():
    print("Initiating league-wide data extraction...")
    
    # Ensure the data directory exists inside the container
    os.makedirs('/app/data', exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    for team in TEAMS:
        print(f"Fetching schedule data for {team}...")
        url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/now"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            file_path = f"/app/data/{team}_games_{date_str}.json"

            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
        else:
            print(f"Failed to fetch {team}: HTTP {response.status_code}")

        # Sleep for 1 second to be a polite scraper
        time.sleep(1)

    print("Success: Pipeline execution complete. All team data saved.")
    
if __name__ == "__main__":
    fetch_all_teams()