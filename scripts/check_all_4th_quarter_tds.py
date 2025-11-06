#!/usr/bin/env python3
"""
Check for any 4th quarter touchdowns against Purdue
"""

import json
import cfbd

def check_all_4th_quarter_tds():
    """Check for any 4th quarter touchdowns against Purdue"""
    
    print("🔍 Checking for any 4th quarter touchdowns against Purdue...")
    
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
            purdue_games = games_api.get_games(year=2025, team='Purdue')
            
            all_4th_quarter_tds = []
            
            for game in purdue_games:
                print(f"\n📊 Checking: {game.away_team} @ {game.home_team}")
                
                try:
                    plays_api = cfbd.PlaysApi(api_client)
                    
                    # Get plays for both teams
                    away_plays = plays_api.get_plays(year=2025, week=game.week, team=game.away_team)
                    home_plays = plays_api.get_plays(year=2025, week=game.week, team=game.home_team)
                    all_plays = away_plays + home_plays
                    
                    # Remove duplicates
                    unique_plays = {}
                    for play in all_plays:
                        key = f"{play.drive_number}_{play.play_number}"
                        if key not in unique_plays:
                            unique_plays[key] = play
                    
                    game_plays = list(unique_plays.values())
                    
                    # Look for any 4th quarter plays
                    q4_plays = [p for p in game_plays if any(q in p.play_text for q in ['4th', 'fourth', 'Q4', '4Q', '4th Quarter'])]
                    print(f"  📊 Found {len(q4_plays)} 4th quarter plays")
                    
                    # Look for touchdowns in 4th quarter
                    q4_tds = []
                    for play in q4_plays:
                        is_td = ('touchdown' in play.play_text.lower() or 'TD' in play.play_text or play.scoring)
                        is_against_purdue = play.offense != 'Purdue'
                        
                        if is_td and is_against_purdue:
                            q4_tds.append(play)
                            print(f"    🏈 4th Q TD: {play.play_text[:80]}...")
                    
                    print(f"  📊 Found {len(q4_tds)} 4th quarter TDs against Purdue")
                    
                    # Also check for any scoring plays in 4th quarter
                    q4_scoring = [p for p in q4_plays if p.scoring and p.offense != 'Purdue']
                    print(f"  📊 Found {len(q4_scoring)} 4th quarter scoring plays against Purdue")
                    
                    if q4_scoring:
                        for score in q4_scoring:
                            print(f"    📊 4th Q Score: {score.play_text[:80]}...")
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    continue
            
            # Also check for any late-game touchdowns (not necessarily 4th quarter)
            print(f"\n🔍 Checking for any late-game touchdowns...")
            
            for game in purdue_games[:3]:  # Check first 3 games
                try:
                    away_plays = plays_api.get_plays(year=2025, week=game.week, team=game.away_team)
                    home_plays = plays_api.get_plays(year=2025, week=game.week, team=game.home_team)
                    all_plays = away_plays + home_plays
                    
                    # Remove duplicates
                    unique_plays = {}
                    for play in all_plays:
                        key = f"{play.drive_number}_{play.play_number}"
                        if key not in unique_plays:
                            unique_plays[key] = play
                    
                    game_plays = list(unique_plays.values())
                    
                    # Look for touchdowns against Purdue
                    tds_against_purdue = []
                    for play in game_plays:
                        is_td = ('touchdown' in play.play_text.lower() or 'TD' in play.play_text or play.scoring)
                        is_against_purdue = play.offense != 'Purdue'
                        
                        if is_td and is_against_purdue:
                            tds_against_purdue.append(play)
                    
                    print(f"  📊 {game.away_team} @ {game.home_team}: {len(tds_against_purdue)} total TDs against Purdue")
                    
                    # Show all touchdowns with their play text
                    for i, td in enumerate(tds_against_purdue):
                        print(f"    {i+1}. {td.play_text}")
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_all_4th_quarter_tds()
