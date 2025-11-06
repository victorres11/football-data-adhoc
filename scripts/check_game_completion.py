#!/usr/bin/env python3
"""
Check if the Minnesota game was completed and analyze the final drives
"""

import json
import cfbd

def check_game_completion():
    """Check if the Minnesota game was completed and analyze the final drives"""
    
    print("🔍 Checking Minnesota game completion and final drives...")
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    # Configure CFBD
    configuration = cfbd.Configuration(access_token=api_key)
    
    with cfbd.ApiClient(configuration) as api_client:
        try:
            # Get Minnesota @ Purdue game (Week 7)
            games_api = cfbd.GamesApi(api_client)
            purdue_games = games_api.get_games(year=2025, team='Purdue')
            
            # Find Minnesota game
            minnesota_game = None
            for game in purdue_games:
                if 'Minnesota' in game.away_team or 'Minnesota' in game.home_team:
                    minnesota_game = game
                    break
            
            print(f"📊 Game: {minnesota_game.away_team} @ {minnesota_game.home_team}")
            print(f"📊 Week: {minnesota_game.week}")
            print(f"📊 Completed: {minnesota_game.completed}")
            print(f"📊 Home Score: {minnesota_game.home_points}")
            print(f"📊 Away Score: {minnesota_game.away_points}")
            
            # Get all plays for this game
            plays_api = cfbd.PlaysApi(api_client)
            away_plays = plays_api.get_plays(year=2025, week=minnesota_game.week, team=minnesota_game.away_team)
            home_plays = plays_api.get_plays(year=2025, week=minnesota_game.week, team=minnesota_game.home_team)
            
            # Combine and deduplicate
            all_plays = away_plays + home_plays
            unique_plays = {}
            for play in all_plays:
                key = f"{play.drive_number}_{play.play_number}"
                if key not in unique_plays:
                    unique_plays[key] = play
            
            game_plays = list(unique_plays.values())
            
            # Sort plays by drive and play number
            sorted_plays = sorted(game_plays, key=lambda x: (x.drive_number, x.play_number))
            
            print(f"\n📊 Total plays: {len(sorted_plays)}")
            
            # Find the last few drives
            last_drives = {}
            for play in sorted_plays:
                drive_num = play.drive_number
                if drive_num not in last_drives:
                    last_drives[drive_num] = []
                last_drives[drive_num].append(play)
            
            # Show the last few drives
            drive_numbers = sorted(last_drives.keys())
            print(f"\n📊 Last few drives:")
            
            for drive_num in drive_numbers[-5:]:  # Last 5 drives
                drive_plays = last_drives[drive_num]
                print(f"\n  Drive {drive_num} ({len(drive_plays)} plays):")
                
                for i, play in enumerate(drive_plays):
                    print(f"    {i+1}. {play.play_text[:80]}...")
                
                # Check if this drive has touchdowns against Purdue
                tds_in_drive = [p for p in drive_plays if 
                              ('touchdown' in p.play_text.lower() or 'TD' in p.play_text or p.scoring) and 
                              p.offense != 'Purdue']
                
                if tds_in_drive:
                    print(f"    🏈 TDs in this drive: {len(tds_in_drive)}")
                    for td in tds_in_drive:
                        print(f"      - {td.play_text}")
            
            # Check for any plays that might indicate the game ended early
            print(f"\n🔍 Looking for game-ending indicators...")
            end_indicators = [p for p in sorted_plays if any(word in p.play_text.lower() for word in ['end', 'final', 'game', 'over', 'time'])]
            
            for indicator in end_indicators[-10:]:  # Last 10 indicators
                print(f"  - {indicator.play_text}")
            
            # Check the final score and see if it matches the game data
            print(f"\n📊 Final Analysis:")
            print(f"  Game completed: {minnesota_game.completed}")
            print(f"  Final score: {minnesota_game.away_team} {minnesota_game.away_points}, {minnesota_game.home_team} {minnesota_game.home_points}")
            
            # Count total touchdowns by each team
            purdue_tds = [p for p in sorted_plays if ('touchdown' in p.play_text.lower() or 'TD' in p.play_text or p.scoring) and p.offense == 'Purdue']
            minnesota_tds = [p for p in sorted_plays if ('touchdown' in p.play_text.lower() or 'TD' in p.play_text or p.scoring) and p.offense == 'Minnesota']
            
            print(f"  Purdue TDs: {len(purdue_tds)}")
            print(f"  Minnesota TDs: {len(minnesota_tds)}")
            
            # Show Minnesota touchdowns
            print(f"\n🏈 Minnesota Touchdowns:")
            for i, td in enumerate(minnesota_tds):
                drive_num = td.drive_number
                drive_length = len([p for p in sorted_plays if p.drive_number == drive_num])
                print(f"  {i+1}. Drive {drive_num} ({drive_length} plays): {td.play_text}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_game_completion()
