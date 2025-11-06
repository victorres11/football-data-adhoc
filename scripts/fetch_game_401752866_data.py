#!/usr/bin/env python3
"""
Fetch complete game data for Northwestern vs Penn State (Game ID: 401752866)
"""

import requests
import json
import os
from datetime import datetime

def fetch_complete_game_data():
    """Fetch complete game data including plays and drives"""
    print("Fetching complete game data for Northwestern vs Penn State...")
    
    # Fetch the main game data
    game_url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=401752866"
    response = requests.get(game_url)
    
    if response.status_code != 200:
        print(f"Error fetching game data: {response.status_code}")
        return None
    
    game_data = response.json()
    
    # Create directory for this game
    os.makedirs('data/game_401752866', exist_ok=True)
    
    # Save the main game data
    with open('data/game_401752866/complete_game_data.json', 'w') as f:
        json.dump(game_data, f, indent=2)
    
    print("✓ Complete game data saved")
    return game_data

def fetch_teams_data():
    """Fetch teams data"""
    print("Fetching teams data...")
    
    teams_data = {}
    
    # Northwestern (Team ID: 77)
    nu_url = "http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/teams/77?lang=en&region=us"
    response = requests.get(nu_url)
    if response.status_code == 200:
        teams_data['77'] = response.json()
        print("✓ Northwestern team data fetched")
    
    # Penn State (Team ID: 213)
    psu_url = "http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/teams/213?lang=en&region=us"
    response = requests.get(psu_url)
    if response.status_code == 200:
        teams_data['213'] = response.json()
        print("✓ Penn State team data fetched")
    
    # Save teams data
    with open('data/game_401752866/teams_data.json', 'w') as f:
        json.dump(teams_data, f, indent=2)
    
    print("✓ Teams data saved")
    return teams_data

def fetch_win_probability_data():
    """Fetch win probability data"""
    print("Fetching win probability data...")
    
    win_prob_url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=401752866"
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
    with open('data/game_401752866/win_probability_data.json', 'w') as f:
        json.dump(win_prob_data, f, indent=2)
    
    print(f"✓ Win probability data saved ({len(win_prob_data)} entries)")
    return win_prob_data

def main():
    print("=" * 60)
    print("Fetching Northwestern vs Penn State Game Data")
    print("Game ID: 401752866 | Date: October 11, 2025")
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
    print("  - data/game_401752866/complete_game_data.json")
    print("  - data/game_401752866/teams_data.json")
    print("  - data/game_401752866/win_probability_data.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
