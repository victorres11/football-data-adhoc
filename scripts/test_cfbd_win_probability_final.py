#!/usr/bin/env python3
"""
Final test of CFBD win probability endpoint with correct parameters
"""

import json
import requests

def test_cfbd_win_probability_final():
    """Final test of CFBD win probability endpoint"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    print("🔍 Final test of CFBD win probability endpoint...")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # First, test that our API key works with a simple endpoint
    print("🧪 Testing API key with games endpoint...")
    
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2025,
            'week': 8,
            'team': 'Michigan'
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            games = response.json()
            print(f"✅ API key works! Got {len(games)} games")
            
            # Find our target game
            target_game = None
            for game in games:
                if game.get('id') == 401752873:
                    target_game = game
                    break
            
            if target_game:
                print(f"✅ Found target game: {target_game.get('away_team')} @ {target_game.get('home_team')}")
            else:
                print(f"❌ Target game not found")
        else:
            print(f"❌ Games endpoint failed: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error testing games endpoint: {e}")
        return None
    
    # Now test win probability endpoint
    print(f"\n🧪 Testing win probability endpoint...")
    
    # Try different parameter combinations for win probability
    wp_test_cases = [
        {
            'name': 'Game ID only',
            'params': {'gameId': 401752873}
        },
        {
            'name': 'Game ID + year',
            'params': {'gameId': 401752873, 'year': 2025}
        },
        {
            'name': 'Game ID + year + week',
            'params': {'gameId': 401752873, 'year': 2025, 'week': 8}
        },
        {
            'name': 'Year + week + team',
            'params': {'year': 2025, 'week': 8, 'team': 'Michigan'}
        }
    ]
    
    for test_case in wp_test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"Params: {test_case['params']}")
        
        try:
            response = requests.get(f"{base_url}/winprobability", headers=headers, params=test_case['params'])
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success! Got win probability data")
                    print(f"Data type: {type(data)}")
                    print(f"Data length: {len(data) if isinstance(data, list) else 'N/A'}")
                    
                    if data:
                        print(f"\n📋 Win Probability Data:")
                        if isinstance(data, list):
                            print(f"Number of entries: {len(data)}")
                            for i, entry in enumerate(data[:3]):  # Show first 3 entries
                                print(f"  {i+1}. {entry}")
                                
                            # Show the structure of the first entry
                            if data:
                                first_entry = data[0]
                                print(f"\n📋 First entry structure:")
                                print(f"  Type: {type(first_entry)}")
                                if isinstance(first_entry, dict):
                                    print(f"  Keys: {list(first_entry.keys())}")
                                    for key, value in first_entry.items():
                                        print(f"    {key}: {value}")
                                else:
                                    print(f"  Value: {first_entry}")
                        else:
                            print(f"Data: {data}")
                        
                        return data
                    else:
                        print(f"❌ Empty result")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📋 Summary:")
    print(f"  CFBD win probability endpoint tested with various parameters")
    print(f"  Check results above for successful data retrieval")
    
    return None

if __name__ == "__main__":
    test_cfbd_win_probability_final()
