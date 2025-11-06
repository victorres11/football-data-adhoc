#!/usr/bin/env python3
"""
Find the longest 4th quarter touchdown drive given up by Purdue in ALL 2025 games
"""

import json
import cfbd

def find_longest_4th_q_td_drive_all_games():
    """Find the longest 4th quarter touchdown drive given up by Purdue in ALL 2025 games"""
    
    print("🔍 Finding the longest 4th quarter touchdown drive given up by Purdue in ALL 2025 games...")
    
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
            
            print(f"📊 Found {len(purdue_games)} Purdue games in 2025")
            
            all_4th_quarter_td_drives = []
            
            for game in purdue_games:
                print(f"\n📊 Analyzing: {game.away_team} @ {game.home_team} (Week {game.week})")
                
                try:
                    # Get all plays for this game
                    plays_api = cfbd.PlaysApi(api_client)
                    away_plays = plays_api.get_plays(year=2025, week=game.week, team=game.away_team)
                    home_plays = plays_api.get_plays(year=2025, week=game.week, team=game.home_team)
                    
                    # Combine and deduplicate
                    all_plays = away_plays + home_plays
                    unique_plays = {}
                    for play in all_plays:
                        key = f"{play.drive_number}_{play.play_number}"
                        if key not in unique_plays:
                            unique_plays[key] = play
                    
                    game_plays = list(unique_plays.values())
                    sorted_plays = sorted(game_plays, key=lambda x: (x.drive_number, x.play_number))
                    
                    print(f"  📊 Total plays: {len(sorted_plays)}")
                    
                    # Find quarter boundaries
                    quarter_boundaries = []
                    for i, play in enumerate(sorted_plays):
                        if 'End of' in play.play_text and 'Quarter' in play.play_text:
                            quarter_boundaries.append((i, play.play_text))
                    
                    # Find 4th quarter start
                    fourth_quarter_start = None
                    for i, (boundary_index, quarter_text) in enumerate(quarter_boundaries):
                        if '3rd' in quarter_text:
                            fourth_quarter_start = boundary_index + 1
                            break
                    
                    if fourth_quarter_start is None:
                        print(f"  ❌ Could not find 4th quarter start")
                        continue
                    
                    # Get 4th quarter plays
                    fourth_quarter_plays = sorted_plays[fourth_quarter_start:]
                    print(f"  📊 4th quarter plays: {len(fourth_quarter_plays)}")
                    
                    # Find touchdowns in 4th quarter against Purdue
                    fourth_quarter_tds = []
                    for play in fourth_quarter_plays:
                        is_td = ('touchdown' in play.play_text.lower() or 'TD' in play.play_text or play.scoring)
                        is_against_purdue = play.offense != 'Purdue'
                        
                        if is_td and is_against_purdue:
                            fourth_quarter_tds.append(play)
                            print(f"    🏈 4th Q TD: {play.play_text[:80]}...")
                    
                    print(f"  📊 Found {len(fourth_quarter_tds)} 4th quarter TDs against Purdue")
                    
                    # Analyze each 4th quarter touchdown drive
                    for td in fourth_quarter_tds:
                        drive_number = td.drive_number
                        drive_plays = [p for p in sorted_plays if p.drive_number == drive_number]
                        
                        # Count plays in 4th quarter for this drive
                        fourth_q_plays_in_drive = [p for p in drive_plays if p in fourth_quarter_plays]
                        fourth_q_length = len(fourth_q_plays_in_drive)
                        
                        drive_info = {
                            'game': f"{game.away_team} @ {game.home_team}",
                            'week': game.week,
                            'drive_number': drive_number,
                            'total_drive_length': len(drive_plays),
                            'fourth_q_length': fourth_q_length,
                            'offense': td.offense,
                            'defense': 'Purdue',
                            'touchdown_play': td.play_text,
                            'drive_plays': [{'play_number': p.play_number, 'text': p.play_text, 'offense': p.offense} for p in drive_plays]
                        }
                        
                        all_4th_quarter_td_drives.append(drive_info)
                        print(f"    📊 Drive {drive_number}: {fourth_q_length} plays in 4th quarter by {td.offense}")
                
                except Exception as e:
                    print(f"  ❌ Error analyzing game: {e}")
                    continue
            
            # Find the longest 4th quarter touchdown drive
            if all_4th_quarter_td_drives:
                longest_4th_q_drive = max(all_4th_quarter_td_drives, key=lambda x: x['fourth_q_length'])
                
                print(f"\n🏆 LONGEST 4TH QUARTER TOUCHDOWN DRIVE GIVEN UP BY PURDUE:")
                print(f"  Game: {longest_4th_q_drive['game']}")
                print(f"  Week: {longest_4th_q_drive['week']}")
                print(f"  Offense: {longest_4th_q_drive['offense']}")
                print(f"  Total Drive Length: {longest_4th_q_drive['total_drive_length']} plays")
                print(f"  4th Quarter Length: {longest_4th_q_drive['fourth_q_length']} plays")
                print(f"  Touchdown Play: {longest_4th_q_drive['touchdown_play']}")
                
                print(f"\n📊 Drive Details:")
                for i, play in enumerate(longest_4th_q_drive['drive_plays']):
                    print(f"  {i+1}. ({play['offense']}) {play['text']}")
                
                # Show all 4th quarter touchdown drives sorted by 4th quarter length
                print(f"\n📊 All 4th Quarter Touchdown Drives Against Purdue (sorted by 4th quarter length):")
                sorted_drives = sorted(all_4th_quarter_td_drives, key=lambda x: x['fourth_q_length'], reverse=True)
                for i, drive in enumerate(sorted_drives):
                    print(f"  {i+1}. {drive['game']} - {drive['fourth_q_length']} plays in 4th quarter by {drive['offense']}")
                
                # Save detailed analysis
                with open('purdue_longest_4th_q_td_drive_all_games_2025.json', 'w') as f:
                    json.dump(longest_4th_q_drive, f, indent=2, default=str)
                
                print(f"\n💾 Saved detailed analysis to purdue_longest_4th_q_td_drive_all_games_2025.json")
                
            else:
                print("❌ No 4th quarter touchdown drives found against Purdue")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_longest_4th_q_td_drive_all_games()
