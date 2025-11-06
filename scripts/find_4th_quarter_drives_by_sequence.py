#!/usr/bin/env python3
"""
Find 4th quarter drives by analyzing play sequence and timing
"""

import json
import cfbd

def find_4th_quarter_drives_by_sequence():
    """Find 4th quarter drives by analyzing play sequence and timing"""
    
    print("🔍 Finding 4th quarter drives by analyzing play sequence...")
    
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
            
            print(f"📊 Analyzing: {minnesota_game.away_team} @ {minnesota_game.home_team}")
            
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
            
            print(f"📊 Total plays: {len(sorted_plays)}")
            
            # Find quarter boundaries
            quarter_boundaries = []
            for i, play in enumerate(sorted_plays):
                if 'End of' in play.play_text and 'Quarter' in play.play_text:
                    quarter_boundaries.append((i, play.play_text))
                    print(f"📊 Quarter boundary at play {i}: {play.play_text}")
            
            # Find the 4th quarter start
            fourth_quarter_start = None
            for i, (play_index, quarter_text) in enumerate(quarter_boundaries):
                if '3rd' in quarter_text or '3rd Quarter' in quarter_text:
                    if i + 1 < len(quarter_boundaries):
                        fourth_quarter_start = quarter_boundaries[i + 1][0]
                        print(f"📊 4th quarter starts at play index: {fourth_quarter_start}")
                    break
            
            if fourth_quarter_start is None:
                print("❌ Could not determine 4th quarter start")
                return
            
            # Get 4th quarter plays
            fourth_quarter_plays = sorted_plays[fourth_quarter_start:]
            print(f"📊 4th quarter plays: {len(fourth_quarter_plays)}")
            
            # Find touchdowns in 4th quarter
            fourth_quarter_tds = []
            for play in fourth_quarter_plays:
                is_td = ('touchdown' in play.play_text.lower() or 'TD' in play.play_text or play.scoring)
                is_against_purdue = play.offense != 'Purdue'
                
                if is_td and is_against_purdue:
                    fourth_quarter_tds.append(play)
                    print(f"🏈 4th Q TD: {play.play_text}")
            
            print(f"📊 Found {len(fourth_quarter_tds)} 4th quarter touchdowns against Purdue")
            
            # Analyze each 4th quarter touchdown drive
            for td in fourth_quarter_tds:
                drive_number = td.drive_number
                drive_plays = [p for p in game_plays if p.drive_number == drive_number]
                
                print(f"\n🏈 4th Quarter Touchdown Drive {drive_number}:")
                print(f"  Length: {len(drive_plays)} plays")
                print(f"  Touchdown: {td.play_text}")
                
                print(f"  📊 Drive plays:")
                for i, drive_play in enumerate(drive_plays):
                    print(f"    {i+1}. {drive_play.play_text[:80]}...")
            
            # Also check if any drives started in 3rd quarter but ended in 4th quarter
            print(f"\n🔍 Checking for drives that span quarters...")
            
            # Find drives that might have started before 4th quarter
            all_td_drives = []
            for play in game_plays:
                is_td = ('touchdown' in play.play_text.lower() or 'TD' in play.play_text or play.scoring)
                is_against_purdue = play.offense != 'Purdue'
                
                if is_td and is_against_purdue:
                    all_td_drives.append(play)
            
            for td in all_td_drives:
                drive_number = td.drive_number
                drive_plays = [p for p in game_plays if p.drive_number == drive_number]
                
                # Check if any play in this drive is in 4th quarter
                drive_in_4th = any(p in fourth_quarter_plays for p in drive_plays)
                
                if drive_in_4th:
                    print(f"\n🏈 Drive {drive_number} (spans quarters):")
                    print(f"  Length: {len(drive_plays)} plays")
                    print(f"  Touchdown: {td.play_text}")
                    
                    # Show which plays are in 4th quarter
                    fourth_q_plays_in_drive = [p for p in drive_plays if p in fourth_quarter_plays]
                    print(f"  📊 {len(fourth_q_plays_in_drive)} plays in 4th quarter")
                    
                    for play in fourth_q_plays_in_drive:
                        print(f"    - {play.play_text[:80]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_4th_quarter_drives_by_sequence()
