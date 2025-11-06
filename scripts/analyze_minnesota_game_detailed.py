#!/usr/bin/env python3
"""
Analyze Minnesota game in detail to find 4th quarter touchdowns
"""

import json
import cfbd

def analyze_minnesota_game_detailed():
    """Analyze Minnesota game in detail to find 4th quarter touchdowns"""
    
    print("🔍 Analyzing Minnesota @ Purdue game in detail...")
    
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
            
            if not minnesota_game:
                print("❌ Minnesota game not found")
                return
            
            print(f"📊 Found Minnesota game: {minnesota_game.away_team} @ {minnesota_game.home_team} (Week {minnesota_game.week})")
            
            # Get all plays for this game
            plays_api = cfbd.PlaysApi(api_client)
            
            # Get plays for both teams
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
            print(f"📊 Found {len(game_plays)} total plays")
            
            # Find all touchdowns against Purdue
            tds_against_purdue = []
            for play in game_plays:
                is_td = ('touchdown' in play.play_text.lower() or 'TD' in play.play_text or play.scoring)
                is_against_purdue = play.offense != 'Purdue'
                
                if is_td and is_against_purdue:
                    tds_against_purdue.append(play)
            
            print(f"📊 Found {len(tds_against_purdue)} touchdowns against Purdue")
            
            # Show all touchdowns with drive info
            for i, td in enumerate(tds_against_purdue):
                drive_number = td.drive_number
                drive_plays = [p for p in game_plays if p.drive_number == drive_number]
                
                print(f"\n🏈 Touchdown {i+1}:")
                print(f"  Drive: {drive_number}")
                print(f"  Length: {len(drive_plays)} plays")
                print(f"  Play: {td.play_text}")
                
                # Show all plays in this drive
                print(f"  📊 Drive plays:")
                for j, drive_play in enumerate(drive_plays):
                    print(f"    {j+1}. {drive_play.play_text[:80]}...")
                
                # Look for quarter indicators in the drive
                quarter_indicators = []
                for drive_play in drive_plays:
                    if any(q in drive_play.play_text for q in ['1st', '2nd', '3rd', '4th', 'Q1', 'Q2', 'Q3', 'Q4']):
                        quarter_indicators.append(drive_play.play_text)
                
                if quarter_indicators:
                    print(f"  📊 Quarter indicators found:")
                    for indicator in quarter_indicators:
                        print(f"    - {indicator}")
                else:
                    print(f"  📊 No explicit quarter indicators found")
            
            # Also check for any plays that might indicate 4th quarter
            print(f"\n🔍 Looking for any 4th quarter indicators in all plays...")
            q4_indicators = [p for p in game_plays if any(q in p.play_text for q in ['4th', 'fourth', 'Q4', '4Q', '4th Quarter'])]
            print(f"📊 Found {len(q4_indicators)} plays with 4th quarter indicators")
            
            for indicator in q4_indicators:
                print(f"  - {indicator.play_text}")
            
            # Look for clock indicators that might suggest 4th quarter
            print(f"\n🔍 Looking for clock indicators...")
            clock_plays = [p for p in game_plays if any(clock in p.play_text for clock in ['15:00', '14:', '13:', '12:', '11:', '10:', '9:', '8:', '7:', '6:', '5:', '4:', '3:', '2:', '1:', '0:'])]
            print(f"📊 Found {len(clock_plays)} plays with clock indicators")
            
            # Show some clock plays
            for clock_play in clock_plays[:10]:  # First 10
                print(f"  - {clock_play.play_text[:80]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_minnesota_game_detailed()
