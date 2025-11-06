#!/usr/bin/env python3
"""
Fetch complete play-by-play data for game 401752873
This will fetch all pages of plays and drives data
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

def fetch_all_plays(game_id):
    """Fetch all pages of play-by-play data from ESPN API"""
    print(f"Fetching all play-by-play data for {game_id}...")
    
    all_plays = []
    page = 1
    
    while True:
        print(f"  Fetching page {page}...")
        url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays"
        params = {
            'page': page,
            'pageSize': 25
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data or not data['items']:
                print(f"  No more plays on page {page}")
                break
                
            all_plays.extend(data['items'])
            print(f"  ✓ Fetched {len(data['items'])} plays from page {page}")
            
            # Check if this is the last page
            if page >= data.get('pageCount', 1):
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error fetching page {page}: {e}")
            break
    
    print(f"  ✓ Total plays fetched: {len(all_plays)}")
    return all_plays

def fetch_drives(game_id):
    """Fetch drives data from ESPN API"""
    print(f"Fetching drives data for {game_id}...")
    
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/drives"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Successfully fetched drives data")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching drives data: {e}")
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

def save_complete_data(game_id, game_data, all_plays, drives_data, boxscore_data):
    """Save complete game data to local file"""
    print(f"Saving complete data for game {game_id}...")
    
    # Create directory if it doesn't exist
    os.makedirs(f'data/game_{game_id}', exist_ok=True)
    
    # Combine all data
    complete_data = {
        "header": game_data,
        "plays": {
            "items": all_plays,
            "count": len(all_plays),
            "pageIndex": 1,
            "pageSize": len(all_plays),
            "pageCount": 1
        },
        "drives": drives_data,
        "boxscore": boxscore_data,
        "fetched_at": datetime.now().isoformat()
    }
    
    filename = f'data/game_{game_id}/complete_game_data.json'
    with open(filename, 'w') as f:
        json.dump(complete_data, f, indent=2)
    
    print(f"  ✓ Saved complete data to {filename}")
    return filename

def get_game_summary(complete_data):
    """Extract basic game information"""
    if not complete_data:
        return "No data"
    
    try:
        header = complete_data.get('header', {})
        name = header.get('name', 'Unknown Game')
        date = header.get('date', 'Unknown Date')
        
        plays_count = len(complete_data.get('plays', {}).get('items', []))
        drives_count = 0
        
        drives = complete_data.get('drives', {})
        if drives and 'items' in drives:
            drives_count = len(drives['items'])
        
        return f"{name} ({date}) - {plays_count} plays, {drives_count} drives"
    except Exception as e:
        return f"Could not parse game info: {e}"

def main():
    print("Complete Game 401752873 Data Fetcher")
    print("=" * 50)
    
    game_id = 401752873
    
    # Fetch all data
    game_data = fetch_game_data(game_id)
    all_plays = fetch_all_plays(game_id)
    drives_data = fetch_drives(game_id)
    boxscore_data = fetch_boxscore(game_id)
    
    if not game_data or not all_plays:
        print("Error: Could not fetch essential data (game_data and plays)")
        return
    
    # Save complete data
    filename = save_complete_data(game_id, game_data, all_plays, drives_data, boxscore_data)
    
    # Get summary
    complete_data = {
        "header": game_data,
        "plays": {"items": all_plays},
        "drives": drives_data,
        "boxscore": boxscore_data
    }
    
    summary = get_game_summary(complete_data)
    print(f"  Game info: {summary}")
    
    # Get file size
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"  File size: {size:,} bytes")
    
    print(f"\n✓ Complete data saved successfully!")

if __name__ == "__main__":
    main()
