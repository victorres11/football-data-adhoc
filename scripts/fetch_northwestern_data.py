#!/usr/bin/env python3
"""
Fetch Northwestern vs Penn State game data from ESPN API
"""

import requests
import json
import os
from datetime import datetime

def fetch_game_data(game_id):
    """Fetch game data from ESPN API"""
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game data: {e}")
        return None

def fetch_play_by_play(game_id):
    """Fetch play-by-play data from ESPN API"""
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching play-by-play data: {e}")
        return None

def fetch_boxscore(game_id):
    """Fetch boxscore data from ESPN API"""
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/boxscore"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching boxscore data: {e}")
        return None

def main():
    """Main function to fetch Northwestern game data"""
    game_id = "401752866"  # Northwestern vs Penn State
    
    print(f"Fetching Northwestern vs Penn State game data (ID: {game_id})...")
    
    # Fetch all data
    game_data = fetch_game_data(game_id)
    play_by_play = fetch_play_by_play(game_id)
    boxscore = fetch_boxscore(game_id)
    
    if not all([game_data, play_by_play, boxscore]):
        print("Error: Could not fetch all required data")
        return
    
    # Combine data into single structure
    combined_data = {
        "header": game_data,
        "plays": play_by_play,
        "boxscore": boxscore,
        "drives": play_by_play.get("drives", {}),
        "fetched_at": datetime.now().isoformat()
    }
    
    # Create directory if it doesn't exist
    os.makedirs("../data/northwestern", exist_ok=True)
    
    # Save combined data
    output_file = f"../data/northwestern/game_{game_id}.json"
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"Data saved to: {output_file}")
    print(f"Game: {game_data.get('name', 'Unknown')}")
    print(f"Date: {game_data.get('date', 'Unknown')}")

if __name__ == "__main__":
    main()
