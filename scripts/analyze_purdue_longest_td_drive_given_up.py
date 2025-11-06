#!/usr/bin/env python3
"""
Analyze Purdue's longest touchdown drive given up in 2025 season
"""

import json
import cfbd
import time

def analyze_purdue_longest_td_drive_given_up():
    """Analyze Purdue's longest touchdown drive given up in 2025 season"""
    
    print("🔍 Analyzing Purdue's longest touchdown drive given up in 2025 season...")
    
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
            
            if not purdue_games:
                print("❌ No Purdue games found for 2025 season")
                return
            
            # Show games
            print(f"\n📊 Purdue's 2025 Games:")
            for i, game in enumerate(purdue_games):
                print(f"  {i+1}. {game.away_team} @ {game.home_team} (Week {game.week})")
            
            # Get plays for each game
            plays_api = cfbd.PlaysApi(api_client)
            all_touchdown_drives = []
            
            for game in purdue_games:
                print(f"\n📊 Analyzing game: {game.away_team} @ {game.home_team}")
                
                try:
                    # Get plays for this game
                    game_plays = plays_api.get_plays(
                        year=2025,
                        week=game.week,
                        team='Purdue'
                    )
                    
                    print(f"  📊 Found {len(game_plays)} plays")
                    
                    # Filter for touchdown plays against Purdue
                    td_plays = []
                    for play in game_plays:
                        # Check if it's a touchdown and Purdue is on defense
                        if (play.scoring and 
                            play.play_type == 'Pass Touchdown' or 
                            play.play_type == 'Rush Touchdown' or
                            'touchdown' in play.play_text.lower()):
                            
                            # Check if Purdue is on defense (opposite of offense)
                            if play.offense != 'Purdue':
                                td_plays.append(play)
                    
                    print(f"  📊 Found {len(td_plays)} touchdown plays against Purdue")
                    
                    # Analyze each touchdown play
                    for td_play in td_plays:
                        drive_number = td_play.drive_number
                        
                        # Get all plays in this drive
                        drive_plays = [p for p in game_plays if p.drive_number == drive_number]
                        
                        # Calculate drive length
                        drive_length = len(drive_plays)
                        
                        # Get drive start and end
                        if drive_plays:
                            start_play = drive_plays[0]
                            end_play = drive_plays[-1]
                            
                            drive_info = {
                                'game': f"{game.away_team} @ {game.home_team}",
                                'week': game.week,
                                'drive_number': drive_number,
                                'drive_length': drive_length,
                                'offense': td_play.offense,
                                'defense': 'Purdue',
                                'touchdown_play': td_play.play_text,
                                'drive_plays': drive_plays
                            }
                            
                            all_touchdown_drives.append(drive_info)
                            print(f"    📊 Drive {drive_number}: {drive_length} plays by {td_play.offense}")
                    
                except Exception as e:
                    print(f"  ❌ Error analyzing game: {e}")
                    continue
            
            # Find the longest touchdown drive
            if all_touchdown_drives:
                longest_drive = max(all_touchdown_drives, key=lambda x: x['drive_length'])
                
                print(f"\n🏆 LONGEST TOUCHDOWN DRIVE GIVEN UP BY PURDUE:")
                print(f"  Game: {longest_drive['game']}")
                print(f"  Week: {longest_drive['week']}")
                print(f"  Offense: {longest_drive['offense']}")
                print(f"  Drive Length: {longest_drive['drive_length']} plays")
                print(f"  Touchdown Play: {longest_drive['touchdown_play']}")
                
                print(f"\n📊 Drive Details:")
                for i, play in enumerate(longest_drive['drive_plays']):
                    print(f"  {i+1}. {play.play_text}")
                
                # Save detailed analysis
                with open('purdue_longest_td_drive_given_up_2025.json', 'w') as f:
                    json.dump(longest_drive, f, indent=2, default=str)
                
                print(f"\n💾 Saved detailed analysis to purdue_longest_td_drive_given_up_2025.json")
                
            else:
                print("❌ No touchdown drives found against Purdue")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_purdue_longest_td_drive_given_up()
