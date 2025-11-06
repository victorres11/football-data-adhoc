#!/usr/bin/env python3
"""
Analyze complete Washington Huskies at Michigan Wolverines game data
Game ID: 401752873
Date: October 18, 2025
"""

import json
import os
from datetime import datetime

def load_complete_game_data():
    """Load the complete game data from ESPN API"""
    with open('data/game_401752873/complete_game_data.json', 'r') as f:
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
        
        # Get venue info
        venue = comp.get('venue', {})
        if venue:
            print(f"Venue: {venue.get('fullName', 'Unknown')}")
            address = venue.get('address', {})
            if address:
                print(f"Location: {address.get('city', '')}, {address.get('state', '')}")
    
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
        
        # Get winner status
        winner = competitor.get('winner', False)
        print(f"  Winner: {winner}")
        
        teams[team_name] = {
            'id': team_id,
            'color': color,
            'alt_color': alt_color,
            'home_away': home_away,
            'winner': winner
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
    print(f"Total plays: {len(plays)}")
    
    # Analyze play types
    play_types = {}
    quarters = {1: 0, 2: 0, 3: 0, 4: 0}
    team_plays = {}
    
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
        
        # Count by team
        team_participants = play.get('teamParticipants', [])
        for participant in team_participants:
            if participant.get('type') == 'offense':
                team = participant.get('team', {})
                team_name = team.get('displayName', 'Unknown')
                if team_name not in team_plays:
                    team_plays[team_name] = 0
                team_plays[team_name] += 1
                break
    
    print(f"\nPlays by quarter:")
    for q, count in quarters.items():
        print(f"  Q{q}: {count} plays")
    
    print(f"\nPlays by team:")
    for team, count in team_plays.items():
        print(f"  {team}: {count} plays")
    
    print(f"\nTop play types:")
    for play_type, count in sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {play_type}: {count}")
    
    return {
        'total_plays': len(plays),
        'quarters': quarters,
        'play_types': play_types,
        'team_plays': team_plays
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
    drive_lengths = []
    drive_results = {}
    
    for drive in drive_items:
        team = drive.get('team', {})
        team_name = team.get('displayName', 'Unknown')
        
        if team_name not in team_drives:
            team_drives[team_name] = 0
        team_drives[team_name] += 1
        
        # Check if scoring drive
        if drive.get('isScore', False):
            scoring_drives += 1
        
        # Get drive length
        plays = drive.get('plays', [])
        drive_lengths.append(len(plays))
        
        # Get drive result
        result = drive.get('result', 'Unknown')
        if result not in drive_results:
            drive_results[result] = 0
        drive_results[result] += 1
    
    print(f"Scoring drives: {scoring_drives}")
    print(f"Average drive length: {sum(drive_lengths) / len(drive_lengths):.1f} plays")
    
    print(f"\nDrives by team:")
    for team, count in team_drives.items():
        print(f"  {team}: {count}")
    
    print(f"\nDrive results:")
    for result, count in sorted(drive_results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {result}: {count}")
    
    return {
        'total_drives': len(drive_items),
        'scoring_drives': scoring_drives,
        'team_drives': team_drives,
        'drive_results': drive_results,
        'avg_drive_length': sum(drive_lengths) / len(drive_lengths) if drive_lengths else 0
    }

def analyze_scoring(data):
    """Analyze scoring plays"""
    print("\n=== SCORING ANALYSIS ===")
    
    plays = data.get('plays', {}).get('items', [])
    
    scoring_plays = []
    for play in plays:
        if play.get('scoringPlay', False):
            scoring_plays.append(play)
    
    print(f"Total scoring plays: {len(scoring_plays)}")
    
    # Analyze by team
    team_scores = {}
    for play in scoring_plays:
        team_participants = play.get('teamParticipants', [])
        for participant in team_participants:
            if participant.get('type') == 'offense':
                team = participant.get('team', {})
                team_name = team.get('displayName', 'Unknown')
                if team_name not in team_scores:
                    team_scores[team_name] = 0
                
                # Get points scored
                points = play.get('points', 0)
                team_scores[team_name] += points
                break
    
    print(f"\nPoints by team:")
    for team, points in team_scores.items():
        print(f"  {team}: {points} points")
    
    return {
        'total_scoring_plays': len(scoring_plays),
        'team_scores': team_scores
    }

def main():
    print("Complete Washington Huskies at Michigan Wolverines Game Analysis")
    print("Game ID: 401752873")
    print("Date: October 18, 2025")
    print("=" * 70)
    
    # Load complete data
    data = load_complete_game_data()
    
    # Extract game information
    game_info = extract_game_info(data)
    
    # Analyze teams
    teams = analyze_teams(data)
    
    # Analyze plays
    plays_analysis = analyze_plays(data)
    
    # Analyze drives
    drives_analysis = analyze_drives(data)
    
    # Analyze scoring
    scoring_analysis = analyze_scoring(data)
    
    # Create summary
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Game: {game_info.get('name', 'Unknown')}")
    print(f"Date: {game_info.get('date', 'Unknown')}")
    
    if teams:
        print(f"Teams: {', '.join(teams.keys())}")
        for team_name, team_data in teams.items():
            print(f"  {team_name}: {'Winner' if team_data.get('winner') else 'Loser'}")
    
    if plays_analysis:
        print(f"Total plays: {plays_analysis['total_plays']}")
        print(f"Plays by quarter: {plays_analysis['quarters']}")
    
    if drives_analysis:
        print(f"Total drives: {drives_analysis['total_drives']}")
        print(f"Scoring drives: {drives_analysis['scoring_drives']}")
        print(f"Average drive length: {drives_analysis['avg_drive_length']:.1f} plays")
    
    if scoring_analysis:
        print(f"Total scoring plays: {scoring_analysis['total_scoring_plays']}")
        print(f"Final scores: {scoring_analysis['team_scores']}")
    
    # Save analysis results
    analysis_results = {
        'game_info': game_info,
        'teams': teams,
        'plays_analysis': plays_analysis,
        'drives_analysis': drives_analysis,
        'scoring_analysis': scoring_analysis,
        'analyzed_at': datetime.now().isoformat()
    }
    
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/complete_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\nComplete analysis saved to: data/game_401752873/complete_analysis.json")

if __name__ == "__main__":
    main()
