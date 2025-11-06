#!/usr/bin/env python3
"""
Debug CFBD API - Test different endpoints and parameters
"""

import json
import requests
from pprint import pprint

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

CFBD_API_KEY = config['api_key']
BASE_URL = config['base_url']

def test_cfbd_games():
    """Test fetching games for Minnesota"""
    print("=" * 70)
    print("Test 1: Fetching Minnesota Games")
    print("=" * 70)
    
    url = f"{BASE_URL}/games"
    params = {
        'year': 2025,
        'team': 'Minnesota',
        'seasonType': 'regular'
    }
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            games = response.json()
            print(f"✓ Successfully fetched {len(games)} games")
            if games:
                game = games[0]
                print(f"\nFirst game structure:")
                print(f"  ID: {game.get('id')}")
                print(f"  Away Team: {game.get('away_team')}")
                print(f"  Home Team: {game.get('home_team')}")
                print(f"  Week: {game.get('week')}")
                print(f"  Season: {game.get('season')}")
                print(f"  All keys: {list(game.keys())}")
                return games
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return []
    except Exception as e:
        print(f"✗ Exception: {e}")
        return []

def test_cfbd_plays(game_id, year=2025):
    """Test fetching plays for a specific game"""
    print("\n" + "=" * 70)
    print(f"Test 2: Fetching Plays for Game {game_id}")
    print("=" * 70)
    
    url = f"{BASE_URL}/plays"
    
    # Try different parameter combinations
    test_params = [
        {'gameId': game_id},
        {'gameId': game_id, 'year': year},
        {'gameId': game_id, 'seasonType': 'regular'},
        {'gameId': game_id, 'year': year, 'seasonType': 'regular'},
    ]
    
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    for i, params in enumerate(test_params, 1):
        print(f"\nAttempt {i}: Parameters = {params}")
        try:
            response = requests.get(url, params=params, headers=headers)
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                plays = response.json()
                print(f"  ✓ Success! Got {len(plays)} plays")
                if plays:
                    print(f"  First play keys: {list(plays[0].keys())}")
                    print(f"  First play sample:")
                    pprint(plays[0], depth=2, width=80)
                return plays
            else:
                print(f"  ✗ Error {response.status_code}")
                print(f"  Response: {response.text[:500]}")
                try:
                    error_json = response.json()
                    print(f"  Error JSON: {json.dumps(error_json, indent=2)[:500]}")
                except:
                    pass
        except Exception as e:
            print(f"  ✗ Exception: {e}")
    
    return []

def test_cfbd_plays_alternative_endpoints(game_id):
    """Test alternative endpoints or methods"""
    print("\n" + "=" * 70)
    print(f"Test 3: Alternative Endpoints for Game {game_id}")
    print("=" * 70)
    
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    # Try different endpoint variations
    endpoints = [
        f"{BASE_URL}/plays",
        f"{BASE_URL}/stats/plays",
        f"{BASE_URL}/game/plays",
    ]
    
    params = {
        'gameId': game_id,
        'year': 2025
    }
    
    for endpoint in endpoints:
        print(f"\nTrying endpoint: {endpoint}")
        try:
            response = requests.get(endpoint, params=params, headers=headers)
            print(f"  Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Success! Response type: {type(data)}")
                if isinstance(data, list):
                    print(f"  Got {len(data)} items")
                else:
                    print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return data
            else:
                print(f"  ✗ Error: {response.text[:300]}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")

def check_api_documentation():
    """Check if we can get API info"""
    print("\n" + "=" * 70)
    print("Test 4: API Information")
    print("=" * 70)
    
    # Try to access API docs or version
    endpoints = [
        f"{BASE_URL}",
        f"{BASE_URL}/",
    ]
    
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    for endpoint in endpoints:
        print(f"\nTrying: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers)
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")

def main():
    print("CFBD API Debugging Tool")
    print("=" * 70)
    
    # Test 1: Get games
    games = test_cfbd_games()
    
    if not games:
        print("\n⚠ No games found, cannot test plays endpoint")
        return
    
    # Test 2: Try to get plays for first game
    first_game = games[0]
    game_id = first_game.get('id')
    
    if game_id:
        plays = test_cfbd_plays(game_id)
        
        if not plays:
            # Test 3: Try alternative endpoints
            test_cfbd_plays_alternative_endpoints(game_id)
    
    # Test 4: Check API info
    check_api_documentation()
    
    print("\n" + "=" * 70)
    print("Debugging Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()

