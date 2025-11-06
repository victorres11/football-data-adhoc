#!/usr/bin/env python3
"""
Find matching games between ESPN and CFBD APIs
"""

import json
import requests
from datetime import datetime

def find_matching_games():
    """Find games that exist in both ESPN and CFBD"""
    
    # Load API key from config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("Finding matching games between ESPN and CFBD...")
    print("=" * 60)
    
    # Get CFBD games for Michigan in 2024
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2024,
            'team': 'Michigan'
        })
        
        if response.status_code == 200:
            cfbd_games = response.json()
            print(f"Found {len(cfbd_games)} Michigan games in CFBD for 2024")
            
            # Show all CFBD games with details
            for i, game in enumerate(cfbd_games):
                print(f"\nCFBD Game {i+1}:")
                print(f"  ID: {game.get('id')}")
                print(f"  Home: {game.get('home_team')}")
                print(f"  Away: {game.get('away_team')}")
                print(f"  Date: {game.get('start_date')}")
                print(f"  Season: {game.get('season')}")
                print(f"  Week: {game.get('week')}")
                print(f"  Completed: {game.get('completed')}")
                print(f"  Home Score: {game.get('home_points')}")
                print(f"  Away Score: {game.get('away_points')}")
                
                # Try to get plays for this game
                try:
                    plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                        'gameId': game.get('id'),
                        'year': 2024,
                        'week': game.get('week', 1)
                    })
                    
                    if plays_response.status_code == 200:
                        plays = plays_response.json()
                        print(f"  Plays: {len(plays)}")
                        
                        # Show sample play
                        if plays:
                            sample_play = plays[0]
                            print(f"  Sample Play: {sample_play.get('playText', 'N/A')[:50]}...")
                            print(f"  Offense: {sample_play.get('offense')} vs Defense: {sample_play.get('defense')}")
                    else:
                        print(f"  Plays: Failed to retrieve ({plays_response.status_code})")
                        
                except Exception as e:
                    print(f"  Plays: Error - {e}")
                
                # If this looks like a good match, return it
                if i == 0:  # Use first game for now
                    return game, plays if 'plays' in locals() else []
        else:
            print(f"Failed to get CFBD games: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None, []

if __name__ == "__main__":
    game, plays = find_matching_games()
    if game:
        print(f"\nSelected game: {game.get('home_team')} vs {game.get('away_team')}")
        print(f"Game ID: {game.get('id')}")
        print(f"Plays: {len(plays)}")
    else:
        print("No matching game found")
