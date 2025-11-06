#!/usr/bin/env python3
"""
Debug Purdue touchdown detection
"""

import json
import cfbd

def debug_purdue_touchdown_detection():
    """Debug Purdue touchdown detection"""
    
    print("🔍 Debugging Purdue touchdown detection...")
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    # Configure CFBD
    configuration = cfbd.Configuration(access_token=api_key)
    
    with cfbd.ApiClient(configuration) as api_client:
        try:
            # Get Purdue's games for 2025 season
            games_api = cfbd.GamesApi(api_client)
            print("📊 Fetching Purdue's 2025 games...")
            
            purdue_games = games_api.get_games(year=2025, team='Purdue')
            print(f"📊 Found {len(purdue_games)} Purdue games in 2025")
            
            # Analyze first few games in detail
            for i, game in enumerate(purdue_games[:3]):  # Just first 3 games
                print(f"\n📊 Analyzing game {i+1}: {game.away_team} @ {game.home_team}")
                
                try:
                    # Get plays for this game
                    plays_api = cfbd.PlaysApi(api_client)
                    game_plays = plays_api.get_plays(
                        year=2025,
                        week=game.week,
                        team='Purdue'
                    )
                    
                    print(f"  📊 Found {len(game_plays)} plays")
                    
                    if len(game_plays) > 0:
                        # Show first few plays to understand structure
                        print(f"  📊 First 3 plays:")
                        for j, play in enumerate(game_plays[:3]):
                            print(f"    {j+1}. Offense: {play.offense}, Type: {play.play_type}, Text: {play.play_text[:50]}...")
                        
                        # Look for any scoring plays
                        scoring_plays = [p for p in game_plays if p.scoring]
                        print(f"  📊 Found {len(scoring_plays)} scoring plays")
                        
                        if scoring_plays:
                            print(f"  📊 First scoring play: {scoring_plays[0].play_text}")
                        
                        # Look for touchdown keywords
                        td_plays = [p for p in game_plays if 'touchdown' in p.play_text.lower()]
                        print(f"  📊 Found {len(td_plays)} plays with 'touchdown' in text")
                        
                        if td_plays:
                            print(f"  📊 First TD play: {td_plays[0].play_text}")
                            print(f"  📊 TD play offense: {td_plays[0].offense}")
                        
                        # Check if Purdue is home or away
                        print(f"  📊 Purdue is: {'Home' if game.home_team == 'Purdue' else 'Away'}")
                        print(f"  📊 Game teams: {game.away_team} @ {game.home_team}")
                    
                except Exception as e:
                    print(f"  ❌ Error analyzing game: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_purdue_touchdown_detection()
