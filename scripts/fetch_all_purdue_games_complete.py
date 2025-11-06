#!/usr/bin/env python3
"""
Fetch complete Purdue play-by-play data for multiple games using ESPN API
Game IDs: 401752864, 401752861, 401752848, 401752832, 401752819, 401752801
"""

import json
import requests
import os
from datetime import datetime

def fetch_complete_game_data(game_id):
    """Fetch complete game data including header, boxscore, and drives"""
    print(f"Fetching complete data for game {game_id}...")
    
    # Fetch header and boxscore
    header_url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}?lang=en&region=us"
    boxscore_url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}?lang=en&region=us"
    drives_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/drives?lang=en&region=us"
    
    try:
        # Fetch header
        header_response = requests.get(header_url)
        header_response.raise_for_status()
        header_data = header_response.json()
        
        # Fetch boxscore
        boxscore_response = requests.get(boxscore_url)
        boxscore_response.raise_for_status()
        boxscore_data = boxscore_response.json()
        
        # Fetch drives
        drives_response = requests.get(drives_url)
        drives_response.raise_for_status()
        drives_data = drives_response.json()
        
        # Combine all data
        complete_data = {
            'header': header_data,
            'boxscore': boxscore_data,
            'drives': drives_data,
            'fetched_at': datetime.now().isoformat()
        }
        
        print(f"  ✓ Successfully fetched {game_id}")
        return complete_data
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
        # Get game info from header
        header = data.get('header', {})
        name = header.get('name', 'Unknown Game')
        date = header.get('date', 'Unknown Date')
        short_name = header.get('shortName', 'Unknown')
        
        # Get drives count
        drives = data.get('drives', {})
        drives_count = 0
        if 'items' in drives:
            drives_count = len(drives['items'])
        
        return f"{name} ({date}) - {short_name} - {drives_count} drives"
    except Exception as e:
        return f"Could not parse game info: {e}"

def main():
    print("Purdue Games Complete Data Fetcher")
    print("=" * 50)
    
    # Game IDs to fetch with their known opponents
    game_info = {
        401752864: "Purdue vs Minnesota",
        401752861: "Illinois vs Purdue", 
        401752848: "Purdue vs Notre Dame",
        401752832: "USC vs Purdue",
        401752819: "Southern Illinois vs Purdue",
        401752801: "Ball State vs Purdue"
    }
    
    print(f"Fetching complete data for {len(game_info)} games...")
    print()
    
    successful_fetches = 0
    failed_fetches = 0
    
    for game_id, game_name in game_info.items():
        print(f"Fetching {game_name} (ID: {game_id})...")
        
        # Fetch complete data
        data = fetch_complete_game_data(game_id)
        
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
    print(f"Total games: {len(game_info)}")
    
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
