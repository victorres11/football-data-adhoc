#!/usr/bin/env python3
"""
Fetch play-by-play data for game 401752873
"""

import json
import requests
import os
from datetime import datetime

def fetch_game_data(game_id):
    """Fetch basic game data from ESPN API"""
    print(f"Fetching game data for {game_id}...")
    
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Successfully fetched game data")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching game data: {e}")
        return None

def fetch_play_by_play(game_id):
    """Fetch play-by-play data from ESPN API"""
    print(f"Fetching play-by-play data for {game_id}...")
    
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Successfully fetched play-by-play data")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching play-by-play data: {e}")
        return None

def fetch_boxscore(game_id):
    """Fetch boxscore data from ESPN API"""
    print(f"Fetching boxscore data for {game_id}...")
    
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/boxscore"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Successfully fetched boxscore data")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching boxscore data: {e}")
        return None

def save_game_data(game_id, data):
    """Save game data to local file"""
    if data is None:
        return False
    
    # Create directory if it doesn't exist
    os.makedirs(f'data/game_{game_id}', exist_ok=True)
    
    filename = f'data/game_{game_id}/raw_game_data.json'
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"  ✓ Saved to {filename}")
    return True

def get_game_summary(data):
    """Extract basic game information"""
    if not data:
        return "No data"
    
    try:
        # Try to get game info from header or competitions
        if 'header' in data:
            header = data['header']
            name = header.get('name', 'Unknown Game')
            date = header.get('date', 'Unknown Date')
        else:
            name = data.get('name', 'Unknown Game')
            date = data.get('date', 'Unknown Date')
        
        # Get drives count
        drives = data.get('drives', {})
        drives_count = 0
        if 'items' in drives:
            drives_count = len(drives['items'])
        elif 'previous' in drives:
            drives_count = len(drives['previous'])
        
        return f"{name} ({date}) - {drives_count} drives"
    except Exception as e:
        return f"Could not parse game info: {e}"

def main():
    print("Game 401752873 Complete Data Fetcher")
    print("=" * 50)
    
    game_id = 401752873
    
    # Fetch all data
    game_data = fetch_game_data(game_id)
    play_by_play = fetch_play_by_play(game_id)
    boxscore = fetch_boxscore(game_id)
    
    if not game_data or not play_by_play:
        print("Error: Could not fetch essential data (game_data and play_by_play)")
        return
    
    # Combine data into single structure
    combined_data = {
        "header": game_data,
        "plays": play_by_play,
        "drives": play_by_play.get("drives", {}),
        "fetched_at": datetime.now().isoformat()
    }
    
    # Add boxscore if available
    if boxscore:
        combined_data["boxscore"] = boxscore
        print("  ✓ Boxscore data included")
    else:
        print("  ⚠ Boxscore data not available")
    
    if save_game_data(game_id, combined_data):
        summary = get_game_summary(combined_data)
        print(f"  Game info: {summary}")
        
        # Get file size
        filename = f'data/game_{game_id}/raw_game_data.json'
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  File size: {size:,} bytes")
    else:
        print("  ✗ Failed to save data")

if __name__ == "__main__":
    main()
