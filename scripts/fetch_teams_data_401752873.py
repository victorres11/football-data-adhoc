#!/usr/bin/env python3
"""
Fetch team data for game 401752873
"""

import json
import requests
import os
from datetime import datetime

def fetch_team_data(team_id):
    """Fetch team data from ESPN API"""
    print(f"Fetching team data for team {team_id}...")
    
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/seasons/2025/teams/{team_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Successfully fetched team {team_id}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching team {team_id}: {e}")
        return None

def main():
    print("Team Data Fetcher for Game 401752873")
    print("=" * 50)
    
    # Team IDs from the game data
    team_ids = [130, 264]  # Michigan and Washington based on the references
    
    teams_data = {}
    
    for team_id in team_ids:
        team_data = fetch_team_data(team_id)
        if team_data:
            teams_data[team_id] = team_data
    
    # Save team data
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/teams_data.json', 'w') as f:
        json.dump(teams_data, f, indent=2)
    
    print(f"\nTeam data saved to: data/game_401752873/teams_data.json")
    
    # Print team names
    for team_id, team_data in teams_data.items():
        name = team_data.get('displayName', 'Unknown')
        print(f"Team {team_id}: {name}")

if __name__ == "__main__":
    main()
