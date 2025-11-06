#!/usr/bin/env python3
"""
Get CFBD plays specifically for game 401752873 (Michigan vs Washington)
"""

import json
import requests

def get_cfbd_plays_401752873():
    """Get CFBD plays for the specific game only"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("Getting CFBD plays for game 401752873 only...")
    print("=" * 50)
    
    # Get plays specifically for this game
    print("Getting plays for game 401752873...")
    print(f"URL: {base_url}/plays")
    print(f"Params: gameId=401752873, year=2025, week=8")
    
    try:
        response = requests.get(f"{base_url}/plays", headers=headers, params={
            'gameId': 401752873,
            'year': 2025,
            'week': 8
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            plays = response.json()
            print(f"✅ Success! Found {len(plays)} plays")
            
            if plays:
                print(f"\nFirst play details:")
                first_play = plays[0]
                print(f"Play ID: {first_play.get('id')}")
                print(f"Play Text: {first_play.get('playText')}")
                print(f"Offense: {first_play.get('offense')}")
                print(f"Defense: {first_play.get('defense')}")
                print(f"Game ID: {first_play.get('gameId')}")
                print(f"Period: {first_play.get('period')}")
                print(f"Down: {first_play.get('down')}")
                print(f"Distance: {first_play.get('distance')}")
                print(f"Yards Gained: {first_play.get('yardsGained')}")
                
                # Check if all plays are from the same game
                game_ids = set(play.get('gameId') for play in plays)
                print(f"\nGame IDs in plays: {game_ids}")
                
                if len(game_ids) == 1 and 401752873 in game_ids:
                    print("✅ All plays are from game 401752873")
                else:
                    print("⚠️  Plays from multiple games detected")
                
                # Save the data
                with open('cfbd_plays_401752873.json', 'w') as f:
                    json.dump(plays, f, indent=2)
                
                print(f"\n📁 Plays data saved to: cfbd_plays_401752873.json")
                return plays
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return []

if __name__ == "__main__":
    plays = get_cfbd_plays_401752873()
    if plays:
        print(f"\n✅ Successfully retrieved {len(plays)} plays for game 401752873")
    else:
        print(f"\n❌ Failed to retrieve plays")
