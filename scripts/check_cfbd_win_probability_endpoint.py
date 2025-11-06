#!/usr/bin/env python3
"""
Check if CFBD has a separate win probability endpoint
"""

import json
import requests

def check_cfbd_win_probability_endpoint():
    """Check CFBD win probability endpoint"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Checking CFBD win probability endpoint...")
    print("=" * 50)
    
    # Try different win probability endpoints
    endpoints_to_try = [
        '/winprobability',
        '/win-probability', 
        '/games/401752873/winprobability',
        '/games/401752873/win-probability',
        '/plays/winprobability',
        '/plays/win-probability'
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n🧪 Trying endpoint: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, params={
                'gameId': 401752873,
                'year': 2025,
                'week': 8
            })
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Success! Found win probability data")
                print(f"  Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"  Number of entries: {len(data)}")
                    if data:
                        print(f"  Sample entry: {data[0]}")
                elif isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")
                return data
            else:
                print(f"  ❌ Failed: {response.status_code}")
                print(f"  Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Try to get win probability from the game endpoint
    print(f"\n🧪 Trying to get win probability from game endpoint...")
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2025,
            'week': 8,
            'team': 'Michigan'
        })
        
        if response.status_code == 200:
            games = response.json()
            target_game = None
            
            for game in games:
                if game.get('id') == 401752873:
                    target_game = game
                    break
            
            if target_game:
                print(f"  ✅ Found target game")
                print(f"  Game keys: {list(target_game.keys())}")
                
                # Check for win probability fields
                wp_fields = [key for key in target_game.keys() if 'win' in key.lower() or 'prob' in key.lower()]
                print(f"  Win probability fields: {wp_fields}")
                
                for field in wp_fields:
                    print(f"    {field}: {target_game[field]}")
            else:
                print(f"  ❌ Target game not found")
        else:
            print(f"  ❌ Failed to get games: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print(f"\n🔍 Checking CFBD documentation for win probability...")
    print(f"  CFBD might not have win probability data")
    print(f"  Or it might be in a different format/location")
    print(f"  ESPN has separate winprobability endpoint")
    print(f"  CFBD might require different approach")
    
    return None

if __name__ == "__main__":
    check_cfbd_win_probability_endpoint()
