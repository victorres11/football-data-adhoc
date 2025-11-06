#!/usr/bin/env python3
"""
Analyze Purdue's longest 4th quarter touchdown drive given up in 2025 season
"""

import json
import cfbd

def analyze_purdue_4th_quarter_td_drives():
    """Analyze Purdue's longest 4th quarter touchdown drive given up in 2025 season"""
    
    print("🔍 Analyzing Purdue's longest 4th quarter touchdown drive given up in 2025 season...")
    
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
            
            all_4th_quarter_td_drives = []
            
            for game in purdue_games:
                print(f"\n📊 Analyzing game: {game.away_team} @ {game.home_team}")
                
                try:
                    # Get ALL plays for this game
                    plays_api = cfbd.PlaysApi(api_client)
                    
                    # Try to get plays for both teams
                    away_plays = plays_api.get_plays(
                        year=2025,
                        week=game.week,
                        team=game.away_team
                    )
                    
                    home_plays = plays_api.get_plays(
                        year=2025,
                        week=game.week,
                        team=game.home_team
                    )
                    
                    # Combine and deduplicate plays
                    all_plays = away_plays + home_plays
                    unique_plays = {}
                    for play in all_plays:
                        key = f"{play.drive_number}_{play.play_number}"
                        if key not in unique_plays:
                            unique_plays[key] = play
                    
                    game_plays = list(unique_plays.values())
                    print(f"  📊 Found {len(game_plays)} total plays")
                    
                    # Find touchdown plays against Purdue in 4th quarter
                    td_plays_4th_quarter = []
                    
                    for play in game_plays:
                        # Check if it's a touchdown and Purdue is on defense
                        is_touchdown = (
                            play.scoring and 
                            ('touchdown' in play.play_text.lower() or 
                             'TD' in play.play_text or
                             play.play_type in ['Pass Touchdown', 'Rush Touchdown'])
                        )
                        
                        # Check if Purdue is on defense (opposite of offense)
                        is_against_purdue = play.offense != 'Purdue'
                        
                        # Check if it's 4th quarter - look for quarter indicators in play text
                        is_4th_quarter = (
                            '4th' in play.play_text or 
                            'fourth' in play.play_text.lower() or
                            'Q4' in play.play_text or
                            '4Q' in play.play_text
                        )
                        
                        if is_touchdown and is_against_purdue and is_4th_quarter:
                            td_plays_4th_quarter.append(play)
                            print(f"    🏈 4th Q TD against Purdue: {play.play_text[:80]}...")
                    
                    print(f"  📊 Found {len(td_plays_4th_quarter)} 4th quarter touchdown plays against Purdue")
                    
                    # Analyze each 4th quarter touchdown drive
                    for td_play in td_plays_4th_quarter:
                        drive_number = td_play.drive_number
                        
                        # Get all plays in this drive
                        drive_plays = [p for p in game_plays if p.drive_number == drive_number]
                        
                        # Calculate drive length
                        drive_length = len(drive_plays)
                        
                        if drive_plays:
                            drive_info = {
                                'game': f"{game.away_team} @ {game.home_team}",
                                'week': game.week,
                                'drive_number': drive_number,
                                'drive_length': drive_length,
                                'offense': td_play.offense,
                                'defense': 'Purdue',
                                'touchdown_play': td_play.play_text,
                                'drive_plays': [{'play_number': p.play_number, 'text': p.play_text, 'offense': p.offense} for p in drive_plays]
                            }
                            
                            all_4th_quarter_td_drives.append(drive_info)
                            print(f"    📊 4th Q Drive {drive_number}: {drive_length} plays by {td_play.offense}")
                    
                except Exception as e:
                    print(f"  ❌ Error analyzing game: {e}")
                    continue
            
            # Find the longest 4th quarter touchdown drive
            if all_4th_quarter_td_drives:
                longest_4th_q_drive = max(all_4th_quarter_td_drives, key=lambda x: x['drive_length'])
                
                print(f"\n🏆 LONGEST 4TH QUARTER TOUCHDOWN DRIVE GIVEN UP BY PURDUE:")
                print(f"  Game: {longest_4th_q_drive['game']}")
                print(f"  Week: {longest_4th_q_drive['week']}")
                print(f"  Offense: {longest_4th_q_drive['offense']}")
                print(f"  Drive Length: {longest_4th_q_drive['drive_length']} plays")
                print(f"  Touchdown Play: {longest_4th_q_drive['touchdown_play']}")
                
                print(f"\n📊 Drive Details:")
                for i, play in enumerate(longest_4th_q_drive['drive_plays']):
                    print(f"  {i+1}. ({play['offense']}) {play['text']}")
                
                # Show all 4th quarter touchdown drives sorted by length
                print(f"\n📊 All 4th Quarter Touchdown Drives Against Purdue (sorted by length):")
                sorted_drives = sorted(all_4th_quarter_td_drives, key=lambda x: x['drive_length'], reverse=True)
                for i, drive in enumerate(sorted_drives):
                    print(f"  {i+1}. {drive['game']} - {drive['drive_length']} plays by {drive['offense']}")
                
                # Save detailed analysis
                with open('purdue_longest_4th_q_td_drive_2025.json', 'w') as f:
                    json.dump(longest_4th_q_drive, f, indent=2, default=str)
                
                print(f"\n💾 Saved detailed analysis to purdue_longest_4th_q_td_drive_2025.json")
                
            else:
                print("❌ No 4th quarter touchdown drives found against Purdue")
                print("🔍 Let me check if there are any 4th quarter plays at all...")
                
                # Check for any 4th quarter plays
                for game in purdue_games[:3]:  # Check first 3 games
                    try:
                        away_plays = plays_api.get_plays(year=2025, week=game.week, team=game.away_team)
                        home_plays = plays_api.get_plays(year=2025, week=game.week, team=game.home_team)
                        all_plays = away_plays + home_plays
                        
                        q4_plays = [p for p in all_plays if '4th' in p.play_text or 'fourth' in p.play_text.lower() or 'Q4' in p.play_text]
                        print(f"  📊 {game.away_team} @ {game.home_team}: {len(q4_plays)} 4th quarter plays found")
                        
                        if q4_plays:
                            print(f"    Sample: {q4_plays[0].play_text[:80]}...")
                            
                    except Exception as e:
                        continue
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_purdue_4th_quarter_td_drives()
