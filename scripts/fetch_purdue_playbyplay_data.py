#!/usr/bin/env python3
"""
Fetch Purdue play-by-play data using ESPN's play-by-play API endpoint
Game IDs: 401752864, 401752861, 401752848, 401752832, 401752819, 401752801
"""

import json
import requests
import os
from datetime import datetime

def fetch_playbyplay_data(game_id):
    """Fetch play-by-play data for a specific game from ESPN API"""
    print(f"Fetching play-by-play data for game {game_id}...")
    
    # Use ESPN's play-by-play endpoint
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}"
    params = {
        'lang': 'en',
        'region': 'us'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Add timestamp
        data['fetched_at'] = datetime.now().isoformat()
        
        print(f"  ✓ Successfully fetched {game_id}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {game_id}: {e}")
        return None

def save_game_data(game_id, data):
    """Save game data to local file"""
    if data is None:
        return False
    
    # Create directory if it doesn't exist
    os.makedirs(f'data/purdue_games', exist_ok=True)
    
    filename = f'data/purdue_games/game_{game_id}.json'
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
    print("Purdue Games Play-by-Play Data Fetcher")
    print("=" * 50)
    
    # Game IDs to fetch
    game_ids = [
        401752864,  # Purdue vs Minnesota
        401752861,  # Illinois vs Purdue
        401752848,  # Purdue vs Notre Dame
        401752832,  # USC vs Purdue
        401752819,  # Southern Illinois vs Purdue
        401752801   # Ball State vs Purdue
    ]
    
    print(f"Fetching play-by-play data for {len(game_ids)} games...")
    print()
    
    successful_fetches = 0
    failed_fetches = 0
    
    for game_id in game_ids:
        # Fetch new data (overwrite existing)
        data = fetch_playbyplay_data(game_id)
        
        if data:
            if save_game_data(game_id, data):
                successful_fetches += 1
                summary = get_game_summary(data)
                print(f"  Game info: {summary}")
            else:
                failed_fetches += 1
        else:
            failed_fetches += 1
        
        print()  # Add spacing between games
    
    print("=" * 50)
    print("SUMMARY:")
    print(f"Successful fetches: {successful_fetches}")
    print(f"Failed fetches: {failed_fetches}")
    print(f"Total games: {len(game_ids)}")
    
    # List all Purdue game files with details
    print("\nPurdue game files:")
    purdue_dir = 'data/purdue_games'
    if os.path.exists(purdue_dir):
        files = [f for f in os.listdir(purdue_dir) if f.startswith('game_') and f.endswith('.json')]
        for file in sorted(files):
            game_id = file.replace('game_', '').replace('.json', '')
            filepath = os.path.join(purdue_dir, file)
            size = os.path.getsize(filepath)
            print(f"  {game_id} ({size:,} bytes)")

if __name__ == "__main__":
    main()
