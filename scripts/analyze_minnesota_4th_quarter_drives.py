#!/usr/bin/env python3
"""
Analyze all Minnesota drives in the 4th quarter of the Purdue game
"""

import json
import cfbd

def analyze_minnesota_4th_quarter_drives():
    """Analyze all Minnesota drives in the 4th quarter of the Purdue game"""
    
    print("🔍 Analyzing all Minnesota drives in the 4th quarter...")
    
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
            
            # Find quarter boundaries more carefully
            quarter_boundaries = []
            for i, play in enumerate(sorted_plays):
                if 'End of' in play.play_text and 'Quarter' in play.play_text:
                    quarter_boundaries.append((i, play.play_text))
                    print(f"📊 Quarter boundary at play {i}: {play.play_text}")
            
            # Find 4th quarter start (after "End of 3rd Quarter")
            fourth_quarter_start = None
            for i, (boundary_index, quarter_text) in enumerate(quarter_boundaries):
                if '3rd' in quarter_text:
                    fourth_quarter_start = boundary_index + 1
                    print(f"📊 4th quarter starts at play index: {fourth_quarter_start}")
                    break
            
            if fourth_quarter_start is None:
                print("❌ Could not find 4th quarter start")
                return
            
            # Get all plays from 4th quarter onwards
            fourth_quarter_plays = sorted_plays[fourth_quarter_start:]
            print(f"📊 4th quarter plays: {len(fourth_quarter_plays)}")
            
            # Find all drives that have plays in the 4th quarter
            fourth_quarter_drives = {}
            for play in fourth_quarter_plays:
                drive_num = play.drive_number
                if drive_num not in fourth_quarter_drives:
                    fourth_quarter_drives[drive_num] = []
                fourth_quarter_drives[drive_num].append(play)
            
            print(f"\n📊 Drives with plays in 4th quarter: {list(fourth_quarter_drives.keys())}")
            
            # Analyze each 4th quarter drive
            for drive_num in sorted(fourth_quarter_drives.keys()):
                drive_plays = fourth_quarter_drives[drive_num]
                print(f"\n🏈 Drive {drive_num} (4th quarter plays: {len(drive_plays)}):")
                
                for i, play in enumerate(drive_plays):
                    print(f"  {i+1}. {play.play_text}")
                
                # Check if this drive has touchdowns
                tds_in_drive = [p for p in drive_plays if 
                              ('touchdown' in p.play_text.lower() or 'TD' in p.play_text or p.scoring) and 
                              p.offense == 'Minnesota']
                
                if tds_in_drive:
                    print(f"  🏈 TDs in this drive: {len(tds_in_drive)}")
                    for td in tds_in_drive:
                        print(f"    - {td.play_text}")
                
                # Get the complete drive (including plays from earlier quarters)
                complete_drive = [p for p in sorted_plays if p.drive_number == drive_num]
                print(f"  📊 Complete drive length: {len(complete_drive)} plays")
                
                # Check if this drive started before 4th quarter
                drive_start_index = None
                for i, play in enumerate(sorted_plays):
                    if play.drive_number == drive_num and play.play_number == 1:
                        drive_start_index = i
                        break
                
                if drive_start_index is not None:
                    if drive_start_index < fourth_quarter_start:
                        print(f"  📊 This drive started before 4th quarter (play {drive_start_index})")
                    else:
                        print(f"  📊 This drive started in 4th quarter (play {drive_start_index})")
            
            # Also check for any drives that might have been missed
            print(f"\n🔍 Checking all drives for 4th quarter activity...")
            
            # Get all unique drives
            all_drives = set(p.drive_number for p in sorted_plays)
            print(f"📊 All drives in game: {sorted(all_drives)}")
            
            # Check each drive for 4th quarter plays
            for drive_num in sorted(all_drives):
                drive_plays = [p for p in sorted_plays if p.drive_number == drive_num]
                fourth_q_plays_in_drive = [p for p in drive_plays if p in fourth_quarter_plays]
                
                if fourth_q_plays_in_drive:
                    print(f"\n📊 Drive {drive_num} has {len(fourth_q_plays_in_drive)} plays in 4th quarter:")
                    for play in fourth_q_plays_in_drive:
                        print(f"  - {play.play_text}")
                    
                    # Check for touchdowns
                    tds = [p for p in fourth_q_plays_in_drive if 
                          ('touchdown' in p.play_text.lower() or 'TD' in p.play_text or p.scoring) and 
                          p.offense == 'Minnesota']
                    
                    if tds:
                        print(f"  🏈 Touchdowns in 4th quarter: {len(tds)}")
                        for td in tds:
                            print(f"    - {td.play_text}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_minnesota_4th_quarter_drives()
