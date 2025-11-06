#!/usr/bin/env python3
"""
Test CFBD Python library - get_plays function
Demonstrates what data we can extract from CollegeFootballData.com API
"""

import cfbd
from cfbd.rest import ApiException
import json

def test_cfbd_plays():
    """Test the CFBD get_plays function to see what data is available"""
    
    # Load API key from config
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Configure API key
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = config['api_key']
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    configuration.host = config['base_url']
    
    # Create API instance
    api_instance = cfbd.PlaysApi(cfbd.ApiClient(configuration))
    
    # Test parameters - let's try to get plays for a recent game
    # Using the Michigan vs Washington game we've been working with
    year = 2024
    week = 1  # First week of season
    
    try:
        print("Testing CFBD get_plays function...")
        print("=" * 50)
        
        # Try to get plays for a specific team (Michigan)
        print("Attempting to get plays for Michigan in 2024...")
        plays = api_instance.get_plays(
            year=year,
            team="Michigan",
            week=week
        )
        
        print(f"Successfully retrieved {len(plays)} plays")
        
        if plays:
            # Show structure of first play
            first_play = plays[0]
            print("\n=== FIRST PLAY STRUCTURE ===")
            print(f"Play ID: {first_play.id}")
            print(f"Game ID: {first_play.game_id}")
            print(f"Drive ID: {first_play.drive_id}")
            print(f"Drive Number: {first_play.drive_number}")
            print(f"Play Number: {first_play.play_number}")
            print(f"Offense: {first_play.offense}")
            print(f"Defense: {first_play.defense}")
            print(f"Offense Conference: {first_play.offense_conference}")
            print(f"Defense Conference: {first_play.defense_conference}")
            print(f"Offense Score: {first_play.offense_score}")
            print(f"Defense Score: {first_play.defense_score}")
            print(f"Period: {first_play.period}")
            print(f"Clock: {first_play.clock}")
            print(f"Yard Line: {first_play.yard_line}")
            print(f"Down: {first_play.down}")
            print(f"Distance: {first_play.distance}")
            print(f"Yards Gained: {first_play.yards_gained}")
            print(f"Scoring: {first_play.scoring}")
            print(f"Play Type: {first_play.play_type}")
            print(f"Play Text: {first_play.play_text}")
            
            # Show available attributes
            print("\n=== ALL AVAILABLE ATTRIBUTES ===")
            for attr in dir(first_play):
                if not attr.startswith('_'):
                    try:
                        value = getattr(first_play, attr)
                        if not callable(value):
                            print(f"{attr}: {value}")
                    except:
                        print(f"{attr}: <unable to access>")
            
            # Save sample data to file
            sample_data = {
                'total_plays': len(plays),
                'sample_play': {
                    'id': first_play.id,
                    'game_id': first_play.game_id,
                    'drive_id': first_play.drive_id,
                    'drive_number': first_play.drive_number,
                    'play_number': first_play.play_number,
                    'offense': first_play.offense,
                    'defense': first_play.defense,
                    'offense_conference': first_play.offense_conference,
                    'defense_conference': first_play.defense_conference,
                    'offense_score': first_play.offense_score,
                    'defense_score': first_play.defense_score,
                    'period': first_play.period,
                    'clock': first_play.clock,
                    'yard_line': first_play.yard_line,
                    'down': first_play.down,
                    'distance': first_play.distance,
                    'yards_gained': first_play.yards_gained,
                    'scoring': first_play.scoring,
                    'play_type': first_play.play_type,
                    'play_text': first_play.play_text
                }
            }
            
            with open('cfbd_sample_data.json', 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            print(f"\nSample data saved to: cfbd_sample_data.json")
            
        else:
            print("No plays found for the specified criteria")
            
    except ApiException as e:
        print(f"API Exception: {e}")
        print("This might be due to missing API key or rate limiting")
        
        # Try without authentication to see what's available
        print("\nTrying to get basic game information instead...")
        try:
            games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))
            games = games_api.get_games(year=2024, week=1)
            print(f"Found {len(games)} games in week 1 of 2024")
            if games:
                print(f"Sample game: {games[0].home_team} vs {games[0].away_team}")
        except Exception as e2:
            print(f"Games API also failed: {e2}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_cfbd_plays()
