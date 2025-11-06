#!/usr/bin/env python3
"""
Fetch Purdue play-by-play data for multiple games using ESPN API
Game IDs: 401752864, 401752861, 401752848, 401752832, 401752819, 401752801
"""

import json
import requests
import os
from datetime import datetime

def fetch_game_data(game_id):
    """Fetch play-by-play data for a specific game from ESPN API"""
    print(f"Fetching data for game {game_id}...")
    
    url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}"
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
        header = data.get('header', {})
        name = header.get('name', 'Unknown Game')
        date = header.get('date', 'Unknown Date')
        
        # Get teams from competitors
        competitors = header.get('competitions', [{}])[0].get('competitors', [])
        teams = []
        for comp in competitors:
            team_ref = comp.get('team', {}).get('$ref', '')
            if 'teams' in team_ref:
                team_id = team_ref.split('/')[-1]
                teams.append(team_id)
        
        return f"{name} ({date}) - Teams: {', '.join(teams)}"
    except:
        return "Could not parse game info"

def main():
    print("Purdue Games Data Fetcher")
    print("=" * 50)
    
    # Game IDs to fetch
    game_ids = [
        401752864,  # Purdue vs Minnesota (we already have this)
        401752861,  # Illinois vs Purdue (we already have this)
        401752848,  # Purdue vs [Unknown]
        401752832,  # Purdue vs [Unknown]
        401752819,  # Purdue vs [Unknown]
        401752801   # Purdue vs [Unknown]
    ]
    
    print(f"Fetching data for {len(game_ids)} games...")
    print()
    
    successful_fetches = 0
    failed_fetches = 0
    
    for game_id in game_ids:
        # Check if we already have this data
        existing_file = f'data/purdue_games/game_{game_id}.json'
        if os.path.exists(existing_file):
            print(f"Game {game_id} already exists locally, skipping...")
            successful_fetches += 1
            continue
        
        # Fetch new data
        data = fetch_game_data(game_id)
        
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
    
    # List all Purdue game files
    print("\nPurdue game files:")
    purdue_dir = 'data/purdue_games'
    if os.path.exists(purdue_dir):
        files = [f for f in os.listdir(purdue_dir) if f.startswith('game_') and f.endswith('.json')]
        for file in sorted(files):
            game_id = file.replace('game_', '').replace('.json', '')
            print(f"  {game_id}")

if __name__ == "__main__":
    main()
