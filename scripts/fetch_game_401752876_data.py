#!/usr/bin/env python3
"""
Fetch complete game data for Game ID: 401752876
"""

import requests
import json
import os
from datetime import datetime

def fetch_complete_game_data():
    """Fetch complete game data from public API"""
    print("Fetching complete game data for Game ID: 401752876...")
    
    # Fetch the main game data
    game_url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=401752876"
    response = requests.get(game_url)
    
    if response.status_code != 200:
        print(f"Error fetching game data: {response.status_code}")
        return None
    
    game_data = response.json()
    
    # Create directory for this game
    os.makedirs('data/game_401752876', exist_ok=True)
    
    # Save the main game data
    with open('data/game_401752876/complete_game_data.json', 'w') as f:
        json.dump(game_data, f, indent=2)
    
    print("✓ Complete game data saved")
    return game_data

def fetch_teams_data():
    """Fetch teams data"""
    print("Fetching teams data...")
    
    teams_data = {}
    
    # We'll need to determine team IDs from the game data
    # For now, let's fetch some common team IDs
    team_ids = ['77', '213', '333', '356']  # Northwestern, Penn State, and others
    
    for team_id in team_ids:
        try:
            team_url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/teams/{team_id}?lang=en&region=us"
            response = requests.get(team_url)
            if response.status_code == 200:
                teams_data[team_id] = response.json()
                print(f"✓ Team {team_id} data fetched")
        except:
            pass
    
    # Save teams data
    with open('data/game_401752876/teams_data.json', 'w') as f:
        json.dump(teams_data, f, indent=2)
    
    print("✓ Teams data saved")
    return teams_data

def fetch_win_probability_data():
    """Fetch win probability data"""
    print("Fetching win probability data...")
    
    win_prob_url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=401752876"
    response = requests.get(win_prob_url)
    
    if response.status_code != 200:
        print(f"Error fetching win probability data: {response.status_code}")
        return None
    
    data = response.json()
    win_prob_data = data.get('winprobability', [])
    
    if not win_prob_data:
        print("No win probability data found")
        return None
    
    # Save win probability data
    with open('data/game_401752876/win_probability_data.json', 'w') as f:
        json.dump(win_prob_data, f, indent=2)
    
    print(f"✓ Win probability data saved ({len(win_prob_data)} entries)")
    return win_prob_data

def main():
    print("=" * 60)
    print("Fetching Game Data for Analysis")
    print("Game ID: 401752876")
    print("=" * 60)
    
    # Fetch all data
    game_data = fetch_complete_game_data()
    if not game_data:
        print("Failed to fetch game data")
        return
    
    teams_data = fetch_teams_data()
    win_prob_data = fetch_win_probability_data()
    
    print("\n" + "=" * 60)
    print("Data fetch complete!")
    print("Files saved:")
    print("  - data/game_401752876/complete_game_data.json")
    print("  - data/game_401752876/teams_data.json")
    print("  - data/game_401752876/win_probability_data.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
