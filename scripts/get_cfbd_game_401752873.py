#!/usr/bin/env python3
"""
Get CFBD data for game 401752873 (Michigan vs Washington)
"""

import json
import requests

def get_cfbd_game_401752873():
    """Get CFBD data for the specific game"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("Getting CFBD data for game 401752873...")
    print("=" * 50)
    
    # First, get the game details
    print("1. Getting game details...")
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2025,
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
                print(f"✅ Found target game!")
                print(f"Game ID: {target_game.get('id')}")
                print(f"Home Team: {target_game.get('homeTeam')}")
                print(f"Away Team: {target_game.get('awayTeam')}")
                print(f"Date: {target_game.get('startDate')}")
                print(f"Home Points: {target_game.get('homePoints')}")
                print(f"Away Points: {target_game.get('awayPoints')}")
                print(f"Week: {target_game.get('week')}")
                print(f"Season Type: {target_game.get('seasonType')}")
                
                # Now get plays for this game
                print(f"\n2. Getting plays for game {target_game.get('id')}...")
                
                # Try with week parameter
                plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                    'gameId': target_game.get('id'),
                    'year': 2025,
                    'week': target_game.get('week')
                })
                
                print(f"Status Code: {plays_response.status_code}")
                
                if plays_response.status_code == 200:
                    plays = plays_response.json()
                    print(f"✅ Success! Found {len(plays)} plays")
                    
                    if plays:
                        print(f"\nFirst play details:")
                        first_play = plays[0]
                        print(f"Play ID: {first_play.get('id')}")
                        print(f"Play Text: {first_play.get('playText')}")
                        print(f"Offense: {first_play.get('offense')}")
                        print(f"Defense: {first_play.get('defense')}")
                        print(f"PPA: {first_play.get('ppa')}")
                        print(f"Period: {first_play.get('period')}")
                        print(f"Down: {first_play.get('down')}")
                        print(f"Distance: {first_play.get('distance')}")
                        print(f"Yards Gained: {first_play.get('yardsGained')}")
                        
                        # Save the data
                        game_data = {
                            'game': target_game,
                            'plays': plays
                        }
                        
                        with open('cfbd_game_401752873.json', 'w') as f:
                            json.dump(game_data, f, indent=2)
                        
                        print(f"\n📁 Data saved to: cfbd_game_401752873.json")
                        return target_game, plays
                        
                else:
                    print(f"❌ Failed to get plays: {plays_response.status_code}")
                    print(f"Response: {plays_response.text}")
                    
            else:
                print("❌ Game 401752873 not found in Michigan games")
                print("Available game IDs:")
                for game in games:
                    print(f"  {game.get('id')}: {game.get('awayTeam')} @ {game.get('homeTeam')}")
        else:
            print(f"❌ Failed to get games: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None, []

if __name__ == "__main__":
    game, plays = get_cfbd_game_401752873()
    if game and plays:
        print(f"\n✅ Successfully retrieved CFBD data!")
        print(f"Game: {game.get('awayTeam')} @ {game.get('homeTeam')}")
        print(f"Plays: {len(plays)}")
    else:
        print(f"\n❌ Failed to retrieve CFBD data")
