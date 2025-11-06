#!/usr/bin/env python3
"""
Debug CFBD API calls for Michigan vs Washington 2025
Show exact API calls and responses
"""

import json
import requests

def debug_cfbd_api_calls():
    """Debug CFBD API calls step by step"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("=== DEBUGGING CFBD API CALLS ===")
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10]}...")
    print()
    
    # Step 1: Try to get Michigan games in 2025
    print("1. Getting Michigan games in 2025...")
    print(f"URL: {base_url}/games")
    print(f"Params: year=2025, team=Michigan")
    
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2025,
            'team': 'Michigan'
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            games = response.json()
            print(f"✅ Success! Found {len(games)} games")
            print(f"Response type: {type(games)}")
            
            if games:
                print(f"\nFirst game structure:")
                first_game = games[0]
                print(f"Game keys: {list(first_game.keys())}")
                for key, value in first_game.items():
                    print(f"  {key}: {value} (type: {type(value)})")
                
                print(f"\nAll games summary:")
                for i, game in enumerate(games):
                    print(f"  Game {i+1}: ID={game.get('id')}, Home={game.get('home_team')}, Away={game.get('away_team')}, Date={game.get('start_date')}")
                    
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    
    # Step 2: Try to get a specific game's plays
    if 'games' in locals() and games:
        game_id = games[0].get('id')
        print(f"2. Getting plays for game {game_id}...")
        print(f"URL: {base_url}/plays")
        print(f"Params: gameId={game_id}, year=2025")
        
        try:
            plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                'gameId': game_id,
                'year': 2025
            })
            
            print(f"Status Code: {plays_response.status_code}")
            
            if plays_response.status_code == 200:
                plays = plays_response.json()
                print(f"✅ Success! Found {len(plays)} plays")
                
                if plays:
                    print(f"\nFirst play structure:")
                    first_play = plays[0]
                    print(f"Play keys: {list(first_play.keys())}")
                    for key, value in first_play.items():
                        print(f"  {key}: {value} (type: {type(value)})")
                        
            else:
                print(f"❌ Failed: {plays_response.status_code}")
                print(f"Response: {plays_response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    
    # Step 3: Try different search approaches
    print("3. Trying different search approaches...")
    
    # Try searching for Washington games
    print("\n3a. Searching for Washington games in 2025...")
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2025,
            'team': 'Washington'
        })
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            washington_games = response.json()
            print(f"✅ Found {len(washington_games)} Washington games")
            
            for i, game in enumerate(washington_games):
                print(f"  Game {i+1}: ID={game.get('id')}, Home={game.get('home_team')}, Away={game.get('away_team')}, Date={game.get('start_date')}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Try searching for all games in 2025
    print("\n3b. Searching for all games in 2025...")
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2025
        })
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            all_games = response.json()
            print(f"✅ Found {len(all_games)} total games in 2025")
            
            # Look for games with both Michigan and Washington
            michigan_washington_games = []
            for game in all_games:
                home = game.get('home_team', '')
                away = game.get('away_team', '')
                if ('Michigan' in home or 'Michigan' in away) and ('Washington' in home or 'Washington' in away):
                    michigan_washington_games.append(game)
            
            print(f"Found {len(michigan_washington_games)} Michigan vs Washington games")
            for game in michigan_washington_games:
                print(f"  Game: {game.get('away_team')} @ {game.get('home_team')} (ID: {game.get('id')})")
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_cfbd_api_calls()
