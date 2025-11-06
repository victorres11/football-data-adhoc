#!/usr/bin/env python3
"""
Test CFBD win probability endpoint for play-by-play data
"""

import json
import requests

def test_cfbd_win_probability_endpoint():
    """Test CFBD win probability endpoint"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing CFBD win probability endpoint...")
    print("=" * 50)
    
    # Try different win probability endpoints
    endpoints_to_try = [
        {
            'name': 'Win Probability by Game ID',
            'url': f'{base_url}/winprobability',
            'params': {'gameId': 401752873}
        },
        {
            'name': 'Win Probability by Game ID + Year',
            'url': f'{base_url}/winprobability',
            'params': {'gameId': 401752873, 'year': 2025}
        },
        {
            'name': 'Win Probability by Game ID + Year + Week',
            'url': f'{base_url}/winprobability',
            'params': {'gameId': 401752873, 'year': 2025, 'week': 8}
        },
        {
            'name': 'Win Probability by Team + Year + Week',
            'url': f'{base_url}/winprobability',
            'params': {'team': 'Michigan', 'year': 2025, 'week': 8}
        },
        {
            'name': 'Win Probability by Team + Year + Week (Washington)',
            'url': f'{base_url}/winprobability',
            'params': {'team': 'Washington', 'year': 2025, 'week': 8}
        }
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n🧪 Testing: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        print(f"Params: {endpoint['params']}")
        
        try:
            response = requests.get(endpoint['url'], headers=headers, params=endpoint['params'])
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success! Found win probability data")
                    print(f"Data type: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"Number of entries: {len(data)}")
                        if data:
                            print(f"Sample entry keys: {list(data[0].keys())}")
                            print(f"Sample entry: {data[0]}")
                            
                            # Check if it has play-by-play data
                            if 'playId' in data[0] or 'play_id' in data[0]:
                                print(f"✅ Found play-by-play win probability data!")
                                return data
                            else:
                                print(f"❌ No play-by-play data found")
                    elif isinstance(data, dict):
                        print(f"Keys: {list(data.keys())}")
                        if 'items' in data:
                            print(f"Items count: {len(data['items'])}")
                            if data['items']:
                                print(f"Sample item: {data['items'][0]}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Response text: {response.text[:200]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Try alternative endpoints
    print(f"\n🔍 Trying alternative win probability endpoints...")
    
    alternative_endpoints = [
        f'{base_url}/games/401752873/winprobability',
        f'{base_url}/games/401752873/win-probability',
        f'{base_url}/plays/401752873/winprobability',
        f'{base_url}/plays/401752873/win-probability'
    ]
    
    for endpoint in alternative_endpoints:
        print(f"\n🧪 Trying: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success! Found data")
                    print(f"Data type: {type(data)}")
                    if isinstance(data, list):
                        print(f"Number of entries: {len(data)}")
                        if data:
                            print(f"Sample entry: {data[0]}")
                    elif isinstance(data, dict):
                        print(f"Keys: {list(data.keys())}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Check if win probability is embedded in the plays data
    print(f"\n🔍 Checking if win probability is embedded in plays data...")
    
    try:
        response = requests.get(f"{base_url}/plays", headers=headers, params={
            'gameId': 401752873,
            'year': 2025,
            'week': 8
        })
        
        if response.status_code == 200:
            plays = response.json()
            print(f"✅ Got {len(plays)} plays")
            
            # Check for win probability fields in plays
            wp_fields = set()
            for play in plays[:5]:  # Check first 5 plays
                for key in play.keys():
                    if 'win' in key.lower() or 'prob' in key.lower():
                        wp_fields.add(key)
            
            if wp_fields:
                print(f"✅ Found win probability fields in plays: {wp_fields}")
            else:
                print(f"❌ No win probability fields found in plays")
                
    except Exception as e:
        print(f"❌ Error checking plays: {e}")
    
    print(f"\n🔍 Summary:")
    print(f"  CFBD may not have play-by-play win probability data")
    print(f"  ESPN has separate winprobability endpoint")
    print(f"  CFBD focuses on advanced metrics like PPA")
    
    return None

if __name__ == "__main__":
    test_cfbd_win_probability_endpoint()
