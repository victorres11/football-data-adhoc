#!/usr/bin/env python3
"""
Minnesota 4th Down Analysis for 2025 Season
Retrieve all Minnesota offensive 4th down plays throughout the season
"""

import json
import requests
import os
import time
from datetime import datetime

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

CFBD_API_KEY = config['api_key']
BASE_URL = config['base_url']

def get_minnesota_games_2025():
    """Get all Minnesota games for 2025 season"""
    print("Fetching Minnesota's 2025 season games...")
    
    url = f"{BASE_URL}/games"
    params = {
        'year': 2025,
        'team': 'Minnesota',
        'seasonType': 'regular'
    }
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        games = response.json()
        
        print(f"Found {len(games)} games for Minnesota in 2025")
        for game in games:
            away_team = game.get('away_team', 'Unknown')
            home_team = game.get('home_team', 'Unknown')
            week = game.get('week', 'N/A')
            game_id = game.get('id', 'N/A')
            espn_id = game.get('espn_id', None)
            print(f"  Week {week}: {away_team} @ {home_team} (CFBD ID: {game_id}, ESPN ID: {espn_id})")
        
        return games
    except requests.exceptions.RequestException as e:
        print(f"Error fetching games: {e}")
        return []

def fetch_cfbd_game_plays(cfbd_game_id, week, year=2025):
    """Fetch play-by-play data from CFBD API - REQUIRES week parameter"""
    print(f"  Fetching CFBD plays for game {cfbd_game_id} (Week {week})...")
    
    url = f"{BASE_URL}/plays"
    params = {
        'gameId': cfbd_game_id,
        'year': year,
        'week': week
    }
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        plays = response.json()
        
        print(f"    ✓ Fetched {len(plays)} plays from CFBD")
        return plays
        
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Error fetching CFBD plays: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Error details: {e.response.text[:300]}")
        return []

def fetch_espn_game_plays(espn_game_id):
    """Fetch all plays from ESPN API using drives endpoint"""
    print(f"  Fetching ESPN plays for game {espn_game_id}...")
    
    all_plays = []
    
    # Fetch drives (which contain plays)
    drives_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{espn_game_id}/competitions/{espn_game_id}/drives"
    
    page = 1
    page_size = 100
    
    try:
        while True:
            params = {
                'limit': page_size,
                'page': page,
                'lang': 'en',
                'region': 'us'
            }
            
            response = requests.get(drives_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            drives = data.get('items', [])
            if not drives:
                break
            
            # Extract plays from drives
            for drive in drives:
                plays = drive.get('plays', [])
                all_plays.extend(plays)
            
            # Check if there are more pages
            page_count = data.get('pageCount', 1)
            if page >= page_count:
                break
            
            page += 1
            time.sleep(0.1)  # Rate limiting
        
        print(f"    ✓ Fetched {len(all_plays)} plays from {len(data.get('items', []))} drives")
        return all_plays, data.get('items', [])
        
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Error fetching ESPN plays: {e}")
        return [], []

def extract_minnesota_team_id(game_summary):
    """Extract Minnesota team ID from game summary"""
    try:
        competitors = game_summary.get('header', {}).get('competitions', [{}])[0].get('competitors', [])
        for comp in competitors:
            team_name = comp.get('team', {}).get('displayName', '')
            team_abbr = comp.get('team', {}).get('abbreviation', '')
            if 'Minnesota' in team_name or team_abbr == 'MINN':
                return comp.get('id', '')
    except:
        pass
    return None

def analyze_4th_down_plays(plays, drives, minnesota_team_id):
    """Extract all 4th down offensive plays for Minnesota from ESPN plays"""
    fourth_downs = []
    
    # Create a mapping of drive IDs to team IDs
    drive_team_map = {}
    for drive in drives:
        drive_id = drive.get('id', '')
        team_id = drive.get('team', {}).get('id', '')
        if drive_id and team_id:
            drive_team_map[drive_id] = team_id
    
    for play in plays:
        # Check if this is a Minnesota offensive play
        # First check teamParticipants
        is_minnesota_play = False
        drive_id = play.get('driveId', '')
        
        # Check drive team
        if drive_id in drive_team_map and drive_team_map[drive_id] == minnesota_team_id:
            is_minnesota_play = True
        else:
            # Fallback: check teamParticipants
            participants = play.get('teamParticipants', [])
            for participant in participants:
                if participant.get('id') == minnesota_team_id:
                    is_minnesota_play = True
                    break
        
        if not is_minnesota_play:
            continue
        
        # Get down from start object
        start = play.get('start', {})
        down = start.get('down', 0)
        
        # Only 4th down plays
        if down != 4:
            continue
        
        # Get play details
        play_text = play.get('text', '')
        quarter = play.get('period', {}).get('number', 1)
        clock = play.get('clock', {})
        clock_display = clock.get('displayValue', '15:00') if clock else '15:00'
        
        yards_to_endzone = start.get('yardsToEndzone', 0)
        yard_line = start.get('yardLine', 0)
        distance = start.get('distance', 0)
        
        # Determine if it's a "go for it" (not a punt, FG, or kneel)
        play_type_obj = play.get('type', {})
        play_type = play_type_obj.get('text', '').lower()
        is_go_for_it = True
        play_result = 'Unknown'
        
        if 'punt' in play_text.lower() or 'punts' in play_text.lower() or 'punt' in play_type:
            is_go_for_it = False
            play_result = 'Punt'
        elif 'field goal' in play_text.lower() or 'kicks' in play_text.lower() or 'field goal' in play_type:
            is_go_for_it = False
            play_result = 'Field Goal'
        elif 'kneel' in play_text.lower() or 'kneels' in play_text.lower():
            is_go_for_it = False
            play_result = 'Kneel'
        elif play.get('scoringPlay', False) or 'touchdown' in play_text.lower():
            play_result = 'Touchdown'
        elif 'incomplete' in play_text.lower():
            play_result = 'Incomplete Pass'
        elif 'interception' in play_text.lower() or 'int' in play_text.lower():
            play_result = 'Interception'
        elif 'fumble' in play_text.lower():
            play_result = 'Fumble'
        elif 'sacked' in play_text.lower():
            play_result = 'Sack'
        elif distance == 0 or 'first down' in play_text.lower():
            play_result = 'First Down'
        
        # Get yards gained
        yards_gained = play.get('statYardage', 0)
        
        # Determine conversion
        converted = False
        if is_go_for_it:
            if distance > 0:
                converted = yards_gained >= distance
            else:
                converted = 'touchdown' in play_text.lower() or 'first down' in play_text.lower() or play.get('firstDown', False)
        else:
            converted = None  # Not applicable for punts/FGs
        
        fourth_downs.append({
            'game_id': None,  # Will be filled in later
            'opponent': None,  # Will be filled in later
            'week': None,  # Will be filled in later
            'quarter': quarter,
            'time': clock_display,
            'down_distance': f"4 & {distance}",
            'yards_to_endzone': yards_to_endzone,
            'yard_line': yard_line,
            'is_go_for_it': is_go_for_it,
            'play_text': play_text,
            'play_type': play_type,
            'play_result': play_result,
            'yards_gained': yards_gained,
            'converted': converted,
            'scoring_play': play.get('scoringPlay', False)
        })
    
    return fourth_downs

def analyze_4th_down_plays_cfbd(plays, opponent_name):
    """Extract all 4th down offensive plays for Minnesota from CFBD plays"""
    fourth_downs = []
    
    for play in plays:
        # Check if this is a Minnesota offensive play
        offense = play.get('offense', '')
        if offense != 'Minnesota':
            continue
        
        # Only 4th down plays
        down = play.get('down', 0)
        if down != 4:
            continue
        
        # Get play details
        play_text = play.get('playText', '')
        quarter = play.get('period', 1)
        
        # Parse clock
        clock = play.get('clock', {})
        if isinstance(clock, dict):
            minutes = clock.get('minutes', 15)
            seconds = clock.get('seconds', 0)
            clock_display = f"{minutes}:{seconds:02d}"
        else:
            clock_display = str(clock)
        
        yards_to_goal = play.get('yardsToGoal', 0)
        yard_line = play.get('yardLine', 0)
        distance = play.get('distance', 0)
        
        # Determine if it's a "go for it" (not a punt, FG, or kneel)
        play_type = play.get('playType', '').lower()
        is_go_for_it = True
        play_result = 'Unknown'
        
        if 'punt' in play_text.lower() or 'punts' in play_text.lower() or play_type == 'punt':
            is_go_for_it = False
            play_result = 'Punt'
        elif 'field goal' in play_text.lower() or 'kicks' in play_text.lower() or play_type == 'field goal':
            is_go_for_it = False
            play_result = 'Field Goal'
        elif 'kneel' in play_text.lower() or 'kneels' in play_text.lower():
            is_go_for_it = False
            play_result = 'Kneel'
        elif play.get('scoringPlay', False) or 'touchdown' in play_text.lower():
            play_result = 'Touchdown'
        elif 'incomplete' in play_text.lower():
            play_result = 'Incomplete Pass'
        elif 'interception' in play_text.lower() or 'int' in play_text.lower():
            play_result = 'Interception'
        elif 'fumble' in play_text.lower():
            play_result = 'Fumble'
        elif 'sacked' in play_text.lower():
            play_result = 'Sack'
        elif distance == 0 or 'first down' in play_text.lower():
            play_result = 'First Down'
        
        # Get yards gained
        yards_gained = play.get('yardsGained', 0)
        
        # Determine conversion
        converted = False
        if is_go_for_it:
            if distance > 0:
                converted = yards_gained >= distance
            else:
                converted = 'touchdown' in play_text.lower() or 'first down' in play_text.lower() or play.get('firstDown', False)
        else:
            converted = None  # Not applicable for punts/FGs
        
        fourth_downs.append({
            'game_id': play.get('gameId'),
            'opponent': opponent_name,
            'week': play.get('week'),
            'quarter': quarter,
            'time': clock_display,
            'down_distance': f"4 & {distance}",
            'yards_to_goal': yards_to_goal,
            'yard_line': yard_line,
            'is_go_for_it': is_go_for_it,
            'play_text': play_text,
            'play_type': play_type,
            'play_result': play_result,
            'yards_gained': yards_gained,
            'converted': converted,
            'scoring_play': play.get('scoringPlay', False)
        })
    
    return fourth_downs

def main():
    print("=" * 70)
    print("Minnesota 2025 Season - All 4th Down Offensive Plays")
    print("=" * 70)
    
    # Get all Minnesota games
    games = get_minnesota_games_2025()
    
    if not games:
        print("No games found for Minnesota in 2025")
        return
    
    all_fourth_downs = []
    
    # Process each game
    for idx, game in enumerate(games, 1):
        cfbd_game_id = game.get('id')
        week = game.get('week', 'N/A')
        away_team = game.get('away_team', 'Unknown')
        home_team = game.get('home_team', 'Unknown')
        
        # Determine opponent - CFBD format
        opponent = away_team if away_team != 'Minnesota' else home_team
        if opponent == 'Unknown':
            # Try alternative fields
            opponent = game.get('opponent', 'Unknown')
        
        print(f"\n[{idx}/{len(games)}] Processing Week {week}: Minnesota vs {opponent}")
        
        if not cfbd_game_id:
            print(f"  ⚠ No CFBD game ID found, skipping...")
            continue
        
        # Try CFBD API first (requires week parameter)
        cfbd_plays = fetch_cfbd_game_plays(cfbd_game_id, week)
        
        if cfbd_plays:
            # Use CFBD plays
            print(f"  Using CFBD plays data...")
            fourth_downs = analyze_4th_down_plays_cfbd(cfbd_plays, opponent)
        else:
            # Fallback to ESPN API
            print(f"  Falling back to ESPN API...")
            plays, drives = fetch_espn_game_plays(cfbd_game_id)
            
            if not plays:
                print(f"  ⚠ Could not fetch plays from either API, skipping...")
                continue
            
            # Fetch game summary to get team IDs
            summary_url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={cfbd_game_id}"
            try:
                summary_response = requests.get(summary_url)
                summary_response.raise_for_status()
                game_summary = summary_response.json()
                
                # Extract Minnesota team ID
                minnesota_id = extract_minnesota_team_id(game_summary)
                if not minnesota_id:
                    print(f"  ⚠ Could not identify Minnesota team ID, skipping...")
                    continue
            except Exception as e:
                print(f"  ⚠ Could not fetch game summary: {e}, skipping...")
                continue
            
            # Analyze 4th downs
            fourth_downs = analyze_4th_down_plays(plays, drives, minnesota_id)
        
        # Add game context to each 4th down
        for fd in fourth_downs:
            fd['game_id'] = cfbd_game_id
            fd['opponent'] = opponent
            fd['week'] = week
            fd['date'] = game.get('start_date', '')
            fd['home_team'] = home_team
            fd['away_team'] = away_team
        
        all_fourth_downs.extend(fourth_downs)
        print(f"  ✓ Found {len(fourth_downs)} 4th down plays (Go for it: {sum(1 for fd in fourth_downs if fd['is_go_for_it'])})")
        
        time.sleep(0.2)  # Rate limiting
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("SEASON SUMMARY")
    print("=" * 70)
    total_4th_downs = len(all_fourth_downs)
    go_for_it = [fd for fd in all_fourth_downs if fd['is_go_for_it']]
    conversions = [fd for fd in go_for_it if fd['converted']]
    
    print(f"Total 4th Down Plays: {total_4th_downs}")
    print(f"  - Go For It Attempts: {len(go_for_it)}")
    print(f"  - Punts: {sum(1 for fd in all_fourth_downs if fd['play_result'] == 'Punt')}")
    print(f"  - Field Goals: {sum(1 for fd in all_fourth_downs if fd['play_result'] == 'Field Goal')}")
    print(f"  - Other: {total_4th_downs - len(go_for_it) - sum(1 for fd in all_fourth_downs if fd['play_result'] == 'Punt') - sum(1 for fd in all_fourth_downs if fd['play_result'] == 'Field Goal')}")
    
    if len(go_for_it) > 0:
        conversion_rate = (len(conversions) / len(go_for_it)) * 100
        print(f"\n4th Down Go For It Statistics:")
        print(f"  - Attempts: {len(go_for_it)}")
        print(f"  - Conversions: {len(conversions)}")
        print(f"  - Conversion Rate: {conversion_rate:.1f}%")
    
    # Save results
    output_file = 'minnesota_4th_downs_2025_season.json'
    output_data = {
        'team': 'Minnesota',
        'season': 2025,
        'total_games': len(games),
        'total_4th_downs': total_4th_downs,
        'go_for_it_attempts': len(go_for_it),
        'conversions': len(conversions),
        'conversion_rate': (len(conversions) / len(go_for_it) * 100) if len(go_for_it) > 0 else 0,
        'generated_at': datetime.now().isoformat(),
        'fourth_downs': all_fourth_downs
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")
    
    # Also create a summary CSV-friendly format
    summary_file = 'minnesota_4th_downs_2025_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("Minnesota 2025 Season - All 4th Down Offensive Plays\n")
        f.write("=" * 70 + "\n\n")
        
        for fd in all_fourth_downs:
            f.write(f"Week {fd['week']} vs {fd['opponent']}\n")
            f.write(f"  Q{fd['quarter']} {fd['time']} - {fd['down_distance']}\n")
            f.write(f"  {fd['play_text']}\n")
            if fd['is_go_for_it']:
                f.write(f"  Result: {'✓ CONVERTED' if fd['converted'] else '✗ FAILED'}\n")
            else:
                f.write(f"  Result: {fd['play_result']}\n")
            f.write(f"\n")
    
    print(f"✓ Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()

