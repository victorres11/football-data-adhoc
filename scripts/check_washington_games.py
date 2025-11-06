#!/usr/bin/env python3
import json
import requests
import sys
from pathlib import Path

# Add parent directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

CFBD_API_KEY = config['api_key']
BASE_URL = config['base_url']

def check_washington_games():
    """Check all Washington games for 2025, specifically looking for Washington State in week 4"""
    url = f"{BASE_URL}/games"
    params = {
        'year': 2025,
        'team': 'Washington',
        'seasonType': 'regular'
    }
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        games = response.json()
        
        print(f"Found {len(games)} games for Washington in 2025:\n")
        for game in games:
            away_team = game.get('away_team', 'Unknown')
            home_team = game.get('home_team', 'Unknown')
            week = game.get('week', 'N/A')
            game_id = game.get('id', 'N/A')
            espn_id = game.get('espn_id', None)
            print(f"Week {week}: {away_team} @ {home_team}")
            print(f"  CFBD ID: {game_id}, ESPN ID: {espn_id}")
            
            # Check specifically for week 4 and Washington State
            if week == 4:
                print(f"  ⭐ WEEK 4 GAME FOUND!")
                if 'Washington State' in away_team or 'Washington State' in home_team:
                    print(f"  ✅ This is the Washington State game!")
            print()
        
        return games
    except requests.exceptions.RequestException as e:
        print(f"Error fetching games: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text[:500]}")
        return []

if __name__ == "__main__":
    check_washington_games()

