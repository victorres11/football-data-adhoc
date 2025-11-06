#!/usr/bin/env python3
"""
Analyze Drive 21 timing to determine if it was in the 4th quarter
"""

import json
import cfbd

def analyze_drive_21_timing():
    """Analyze Drive 21 timing to determine if it was in the 4th quarter"""
    
    print("🔍 Analyzing Drive 21 timing to determine quarter...")
    
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
            
            # Find Drive 21
            drive_21_plays = [p for p in sorted_plays if p.drive_number == 21]
            
            print(f"📊 Drive 21 has {len(drive_21_plays)} plays")
            
            # Find the position of Drive 21 in the overall game sequence
            drive_21_start_index = None
            for i, play in enumerate(sorted_plays):
                if play.drive_number == 21 and play.play_number == 1:
                    drive_21_start_index = i
                    break
            
            print(f"📊 Drive 21 starts at play index: {drive_21_start_index}")
            
            # Find quarter boundaries
            quarter_boundaries = []
            for i, play in enumerate(sorted_plays):
                if 'End of' in play.play_text and 'Quarter' in play.play_text:
                    quarter_boundaries.append((i, play.play_text))
                    print(f"📊 Quarter boundary at play {i}: {play.play_text}")
            
            # Determine which quarter Drive 21 is in
            drive_21_quarter = None
            for i, (boundary_index, quarter_text) in enumerate(quarter_boundaries):
                if drive_21_start_index > boundary_index:
                    if i + 1 < len(quarter_boundaries):
                        next_boundary = quarter_boundaries[i + 1][0]
                        if drive_21_start_index < next_boundary:
                            drive_21_quarter = i + 1
                            break
                    else:
                        drive_21_quarter = i + 1
                        break
            
            print(f"📊 Drive 21 is in Quarter: {drive_21_quarter}")
            
            # Show Drive 21 plays with timing
            print(f"\n📊 Drive 21 plays:")
            for i, play in enumerate(drive_21_plays):
                print(f"  {i+1}. {play.play_text}")
            
            # Check if this is the longest touchdown drive
            print(f"\n🏈 Drive 21 Analysis:")
            print(f"  Length: {len(drive_21_plays)} plays")
            print(f"  Quarter: {drive_21_quarter}")
            print(f"  Touchdown: Drake Lindsey pass complete to Jameson Geers for 4 yds for a TD")
            
            # Compare with other touchdown drives
            all_td_drives = []
            for play in sorted_plays:
                is_td = ('touchdown' in play.play_text.lower() or 'TD' in play.play_text or play.scoring)
                is_against_purdue = play.offense != 'Purdue'
                
                if is_td and is_against_purdue:
                    drive_num = play.drive_number
                    drive_plays = [p for p in sorted_plays if p.drive_number == drive_num]
                    all_td_drives.append((drive_num, len(drive_plays), play.play_text))
            
            print(f"\n📊 All touchdown drives against Purdue:")
            for drive_num, length, td_text in sorted(all_td_drives, key=lambda x: x[1], reverse=True):
                print(f"  Drive {drive_num}: {length} plays - {td_text[:60]}...")
            
            # Check if Drive 21 is the longest
            longest_drive = max(all_td_drives, key=lambda x: x[1])
            print(f"\n🏆 Longest touchdown drive: Drive {longest_drive[0]} with {longest_drive[1]} plays")
            
            if longest_drive[0] == 21:
                print(f"✅ Drive 21 is the longest touchdown drive!")
                if drive_21_quarter == 4:
                    print(f"🏆 This is the longest 4th quarter touchdown drive given up by Purdue!")
                else:
                    print(f"📊 This drive was in Quarter {drive_21_quarter}, not the 4th quarter")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_drive_21_timing()
