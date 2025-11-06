#!/usr/bin/env python3
"""
Analyze Washington Huskies at Michigan Wolverines game data
Game ID: 401752873
Date: October 18, 2025
"""

import json
import os
from datetime import datetime

def load_game_data():
    """Load the raw game data from ESPN API"""
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        return json.load(f)

def extract_game_info(data):
    """Extract basic game information"""
    print("=== GAME INFORMATION ===")
    
    header = data.get('header', {})
    print(f"Game: {header.get('name', 'Unknown')}")
    print(f"Date: {header.get('date', 'Unknown')}")
    print(f"Short Name: {header.get('shortName', 'Unknown')}")
    
    # Get competition details
    competitions = header.get('competitions', [])
    if competitions:
        comp = competitions[0]
        print(f"Attendance: {comp.get('attendance', 'Unknown'):,}")
        print(f"Neutral Site: {comp.get('neutralSite', False)}")
        print(f"Conference Game: {comp.get('conferenceCompetition', False)}")
    
    return header

def analyze_teams(data):
    """Analyze team information"""
    print("\n=== TEAM INFORMATION ===")
    
    header = data.get('header', {})
    competitions = header.get('competitions', [])
    
    if not competitions:
        print("No competition data available")
        return None
    
    comp = competitions[0]
    competitors = comp.get('competitors', [])
    
    teams = {}
    for competitor in competitors:
        team = competitor.get('team', {})
        team_name = team.get('displayName', 'Unknown')
        team_id = team.get('id', 'Unknown')
        
        print(f"\n{team_name} (ID: {team_id})")
        
        # Get team colors
        color = team.get('color', 'Unknown')
        alt_color = team.get('alternateColor', 'Unknown')
        print(f"  Primary Color: #{color}")
        print(f"  Alt Color: #{alt_color}")
        
        # Get home/away status
        home_away = competitor.get('homeAway', 'Unknown')
        print(f"  Status: {home_away}")
        
        teams[team_name] = {
            'id': team_id,
            'color': color,
            'alt_color': alt_color,
            'home_away': home_away
        }
    
    return teams

def analyze_plays(data):
    """Analyze play-by-play data"""
    print("\n=== PLAY-BY-PLAY ANALYSIS ===")
    
    plays_data = data.get('plays', {})
    
    if not plays_data or 'items' not in plays_data:
        print("No play-by-play data available")
        return None
    
    plays = plays_data['items']
    print(f"Total plays available: {len(plays)}")
    print(f"Total plays in game: {plays_data.get('count', 'Unknown')}")
    
    # Analyze play types
    play_types = {}
    quarters = {1: 0, 2: 0, 3: 0, 4: 0}
    
    for play in plays:
        # Count by quarter
        period = play.get('period', {})
        quarter = period.get('number', 1)
        if quarter in quarters:
            quarters[quarter] += 1
        
        # Count by play type
        play_type = play.get('type', {})
        type_text = play_type.get('text', 'Unknown')
        if type_text not in play_types:
            play_types[type_text] = 0
        play_types[type_text] += 1
    
    print(f"\nPlays by quarter:")
    for q, count in quarters.items():
        print(f"  Q{q}: {count} plays")
    
    print(f"\nTop play types:")
    for play_type, count in sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {play_type}: {count}")
    
    return {
        'total_plays': len(plays),
        'game_total': plays_data.get('count', 0),
        'quarters': quarters,
        'play_types': play_types
    }

def analyze_drives(data):
    """Analyze drive data"""
    print("\n=== DRIVE ANALYSIS ===")
    
    drives = data.get('drives', {})
    
    if not drives or 'items' not in drives:
        print("No drive data available")
        return None
    
    drive_items = drives['items']
    print(f"Total drives: {len(drive_items)}")
    
    # Analyze drives by team
    team_drives = {}
    scoring_drives = 0
    
    for drive in drive_items:
        team = drive.get('team', {})
        team_name = team.get('displayName', 'Unknown')
        
        if team_name not in team_drives:
            team_drives[team_name] = 0
        team_drives[team_name] += 1
        
        if drive.get('isScore', False):
            scoring_drives += 1
    
    print(f"Scoring drives: {scoring_drives}")
    print(f"Drives by team:")
    for team, count in team_drives.items():
        print(f"  {team}: {count}")
    
    return {
        'total_drives': len(drive_items),
        'scoring_drives': scoring_drives,
        'team_drives': team_drives
    }

def main():
    print("Washington Huskies at Michigan Wolverines Game Analysis")
    print("Game ID: 401752873")
    print("Date: October 18, 2025")
    print("=" * 60)
    
    # Load data
    data = load_game_data()
    
    # Extract game information
    game_info = extract_game_info(data)
    
    # Analyze teams
    teams = analyze_teams(data)
    
    # Analyze plays
    plays_analysis = analyze_plays(data)
    
    # Analyze drives
    drives_analysis = analyze_drives(data)
    
    # Create summary
    print(f"\n=== SUMMARY ===")
    print(f"Game: {game_info.get('name', 'Unknown')}")
    print(f"Date: {game_info.get('date', 'Unknown')}")
    
    if teams:
        print(f"Teams: {', '.join(teams.keys())}")
    
    if plays_analysis:
        print(f"Plays analyzed: {plays_analysis['total_plays']}")
        print(f"Total plays in game: {plays_analysis['game_total']}")
    
    if drives_analysis:
        print(f"Drives: {drives_analysis['total_drives']}")
        print(f"Scoring drives: {drives_analysis['scoring_drives']}")
    
    # Save analysis results
    analysis_results = {
        'game_info': game_info,
        'teams': teams,
        'plays_analysis': plays_analysis,
        'drives_analysis': drives_analysis,
        'analyzed_at': datetime.now().isoformat()
    }
    
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\nAnalysis saved to: data/game_401752873/analysis.json")

if __name__ == "__main__":
    main()
