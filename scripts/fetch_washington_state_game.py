#!/usr/bin/env python3
"""
Fetch the missing Washington vs Washington State game (Week 4, 2025)
Game ID: 401752842
"""

import json
import requests
import sys
from pathlib import Path
from datetime import datetime

# Load config
config_path = Path(__file__).parent.parent / 'config.json'
with open(config_path, 'r') as f:
    config = json.load(f)

CFBD_API_KEY = config['api_key']
BASE_URL = config['base_url']

GAME_ID = 401752842
WEEK = 4
YEAR = 2025

def fetch_game_info():
    """Fetch game information from CFBD"""
    print(f"Fetching game info for game {GAME_ID}...")
    
    url = f"{BASE_URL}/games"
    params = {
        'year': YEAR,
        'week': WEEK,
        'seasonType': 'regular'
    }
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        games = response.json()
        
        # Find our specific game
        game = None
        for g in games:
            if g.get('id') == GAME_ID:
                game = g
                break
        
        if not game:
            print(f"❌ Game {GAME_ID} not found in week {WEEK} games")
            return None
        
        print(f"✅ Found game: {game.get('awayTeam')} @ {game.get('homeTeam')}")
        return game
        
    except Exception as e:
        print(f"❌ Error fetching game info: {e}")
        return None

def fetch_plays(game_id, week, year):
    """Fetch play-by-play data from CFBD"""
    print(f"Fetching plays for game {game_id} (Week {week})...")
    
    url = f"{BASE_URL}/plays"
    params = {
        'gameId': game_id,
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
        
        print(f"✅ Fetched {len(plays)} plays")
        return plays
        
    except Exception as e:
        print(f"❌ Error fetching plays: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text[:500]}")
        return []

def transform_cfbd_play(cfbd_play, game_info):
    """Transform CFBD play format to match existing file structure"""
    # Extract clock format - CFBD uses object with minutes/seconds
    clock_obj = cfbd_play.get('clock', {})
    if isinstance(clock_obj, dict):
        minutes = clock_obj.get('minutes', 0)
        seconds = clock_obj.get('seconds', 0)
        clock = f"seconds={seconds} minutes={minutes}"
    else:
        clock = str(clock_obj)
    
    # Build play ID similar to existing format
    play_id = str(cfbd_play.get('id', ''))
    
    # Extract drive ID
    drive_id = str(cfbd_play.get('driveId', ''))
    
    # Determine if explosive play (basic check - can be enhanced)
    yards_gained = cfbd_play.get('yardsGained', 0)
    play_type_cfbd = cfbd_play.get('playType', '').lower()
    explosive = False
    if play_type_cfbd:
        if 'rush' in play_type_cfbd and yards_gained >= 15:
            explosive = True
        elif 'pass' in play_type_cfbd and yards_gained >= 20:
            explosive = True
    
    # Classify play
    play_classification = 'normal'
    if 'punt' in play_type_cfbd:
        play_classification = 'special_teams'
    elif 'field goal' in play_type_cfbd or 'kick' in play_type_cfbd:
        play_classification = 'special_teams'
    elif 'penalty' in play_type_cfbd:
        play_classification = 'penalty'
    
    # Check for middle eight (final 4 min of 1st half, first 4 min of 2nd half)
    period = cfbd_play.get('period', 1)
    middle_eight = False
    if period == 2:
        # Final 4 minutes of first half
        if isinstance(clock_obj, dict):
            minutes = clock_obj.get('minutes', 15)
            if minutes <= 4:
                middle_eight = True
    elif period == 3:
        # First 4 minutes of second half
        if isinstance(clock_obj, dict):
            minutes = clock_obj.get('minutes', 15)
            if minutes >= 11:  # 15 - 11 = 4 minutes remaining
                middle_eight = True
    
    # Check for turnover
    turnover = cfbd_play.get('fumble', False) or cfbd_play.get('interception', False)
    
    # Extract penalty info
    penalty_type = None
    penalty_decision = None
    if cfbd_play.get('penalty', False):
        # Try to extract from play text
        play_text = cfbd_play.get('playText', '')
        if 'penalty' in play_text.lower():
            # Basic extraction - can be enhanced
            penalty_decision = 'accepted'  # Default assumption
    
    # Format wallclock
    wallclock = cfbd_play.get('wallclock', '')
    if not wallclock:
        # Try to construct from game date if available
        wallclock = datetime.now().isoformat() + 'Z'
    
    play = {
        'id': play_id,
        'drive_id': drive_id,
        'game_id': game_info.get('id'),
        'drive_number': cfbd_play.get('driveNumber', 0),
        'play_number': cfbd_play.get('playNumber', 0),
        'offense': cfbd_play.get('offense', ''),
        'defense': cfbd_play.get('defense', ''),
        'period': period,
        'clock': clock,
        'yard_line': cfbd_play.get('yardLine', 0),
        'yards_to_goal': cfbd_play.get('yardsToGoal', 0),
        'down': cfbd_play.get('down', ''),
        'distance': cfbd_play.get('distance', ''),
        'yards_gained': cfbd_play.get('yardsGained', 0),
        'scoring': cfbd_play.get('scoring', False),
        'play_type': cfbd_play.get('playType', ''),
        'play_text': cfbd_play.get('playText', ''),
        'ppa': cfbd_play.get('ppa', 0.0),
        'wallclock': wallclock,
        'explosive_play': explosive,
        'play_classification': play_classification,
        'middle_eight': middle_eight,
        'turnover': turnover,
        'no_play': False,  # Could be enhanced to detect timeouts, etc.
        'penalty_type': penalty_type,
        'penalty_decision': penalty_decision,
        'drive_started_after_turnover': False  # Would need to track this
    }
    
    return play

def main():
    print("=" * 70)
    print("Fetching Washington vs Washington State Game (Week 4, 2025)")
    print("=" * 70)
    print()
    
    # Fetch game info
    game_info = fetch_game_info()
    if not game_info:
        print("❌ Cannot proceed without game info")
        return
    
    # Fetch plays
    plays = fetch_plays(GAME_ID, WEEK, YEAR)
    if not plays:
        print("❌ Cannot proceed without plays")
        return
    
    # Transform plays
    print(f"\nTransforming {len(plays)} plays...")
    transformed_plays = []
    for cfbd_play in plays:
        transformed_play = transform_cfbd_play(cfbd_play, game_info)
        transformed_plays.append(transformed_play)
    
    # Build game_info structure
    game_info_formatted = {
        'game_id': game_info.get('id'),
        'home_team': game_info.get('homeTeam'),
        'away_team': game_info.get('awayTeam'),
        'week': game_info.get('week'),
        'date': game_info.get('startDate', ''),
        'total_plays': len(transformed_plays),
        'conference': game_info.get('conferenceGame', False)
    }
    
    # Create final structure
    game_data = {
        'game_info': game_info_formatted,
        'plays': transformed_plays
    }
    
    # Generate filename
    home = game_info.get('homeTeam', 'Unknown')
    away = game_info.get('awayTeam', 'Unknown')
    filename = f"game_{GAME_ID}_{away}_at_{home}_week_{WEEK}.json"
    
    # Save to Washington play-by-play directory
    output_dir = Path(__file__).parent.parent / 'advanced_reports_yogi' / 'washington_play_by_play'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        json.dump(game_data, f, indent=2)
    
    print(f"\n✅ Game data saved to: {output_path}")
    print(f"   Game: {away} @ {home}")
    print(f"   Week: {WEEK}")
    print(f"   Total Plays: {len(transformed_plays)}")
    print(f"   Date: {game_info.get('startDate', 'Unknown')}")

if __name__ == "__main__":
    main()

