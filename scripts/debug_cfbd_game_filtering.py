#!/usr/bin/env python3
"""
Debug CFBD API game filtering to understand why gameId parameter isn't working
"""

import json
import requests

def debug_cfbd_game_filtering():
    """Debug why gameId parameter isn't filtering properly"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("Debugging CFBD API game filtering...")
    print("=" * 50)
    
    # Try different parameter combinations
    test_cases = [
        {
            'name': 'gameId only',
            'params': {'gameId': 401752873}
        },
        {
            'name': 'gameId + year',
            'params': {'gameId': 401752873, 'year': 2025}
        },
        {
            'name': 'gameId + year + week',
            'params': {'gameId': 401752873, 'year': 2025, 'week': 8}
        },
        {
            'name': 'year + week only (no gameId)',
            'params': {'year': 2025, 'week': 8}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"Params: {test_case['params']}")
        
        try:
            response = requests.get(f"{base_url}/plays", headers=headers, params=test_case['params'])
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                plays = response.json()
                print(f"✅ Success! Found {len(plays)} plays")
                
                if plays:
                    # Check game IDs
                    game_ids = set(play.get('gameId') for play in plays)
                    print(f"Unique Game IDs: {len(game_ids)}")
                    
                    if 401752873 in game_ids:
                        target_plays = [play for play in plays if play.get('gameId') == 401752873]
                        print(f"✅ Found {len(target_plays)} plays for game 401752873")
                        
                        if len(target_plays) > 0:
                            print(f"First target play: {target_plays[0].get('playText')}")
                    else:
                        print(f"❌ Game 401752873 not found in results")
                        print(f"Sample Game IDs: {list(game_ids)[:5]}")
                        
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Let's try a different approach...")
    
    # Try to get plays for a specific team in a specific week
    print("\n🧪 Testing: Get plays for Michigan in week 8, 2025")
    try:
        response = requests.get(f"{base_url}/plays", headers=headers, params={
            'year': 2025,
            'week': 8,
            'team': 'Michigan'
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            plays = response.json()
            print(f"✅ Success! Found {len(plays)} plays")
            
            if plays:
                # Check game IDs
                game_ids = set(play.get('gameId') for play in plays)
                print(f"Unique Game IDs: {len(game_ids)}")
                print(f"Game IDs: {sorted(game_ids)}")
                
                if 401752873 in game_ids:
                    target_plays = [play for play in plays if play.get('gameId') == 401752873]
                    print(f"✅ Found {len(target_plays)} plays for game 401752873")
                    
                    # Save just the target plays
                    with open('cfbd_plays_401752873_filtered.json', 'w') as f:
                        json.dump(target_plays, f, indent=2)
                    
                    print(f"📁 Filtered plays saved to: cfbd_plays_401752873_filtered.json")
                    return target_plays
                else:
                    print(f"❌ Game 401752873 not found in results")
                    
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return []

if __name__ == "__main__":
    plays = debug_cfbd_game_filtering()
    if plays:
        print(f"\n✅ Successfully retrieved {len(plays)} plays for game 401752873")
    else:
        print(f"\n❌ Failed to retrieve plays for game 401752873")
