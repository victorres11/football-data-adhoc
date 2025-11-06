#!/usr/bin/env python3
"""
Final comprehensive analysis of Washington Huskies at Michigan Wolverines game
Game ID: 401752873
Date: October 18, 2025
"""

import json
import os
from datetime import datetime

def load_data():
    """Load all game data"""
    with open('data/game_401752873/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    
    with open('data/game_401752873/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return game_data, teams_data

def get_team_name(team_id, teams_data):
    """Get team name from team ID"""
    team_id_str = str(team_id)
    if team_id_str in teams_data:
        return teams_data[team_id_str].get('displayName', f'Team {team_id}')
    return f'Team {team_id}'

def analyze_game_summary(data, teams_data):
    """Analyze basic game information"""
    print("=== GAME SUMMARY ===")
    
    header = data.get('header', {})
    print(f"Game: {header.get('name', 'Unknown')}")
    print(f"Date: {header.get('date', 'Unknown')}")
    print(f"Venue: Michigan Stadium, Ann Arbor, MI")
    print(f"Attendance: {header.get('competitions', [{}])[0].get('attendance', 'Unknown'):,}")
    
    # Get team information
    competitions = header.get('competitions', [])
    if competitions:
        competitors = competitions[0].get('competitors', [])
        print(f"\nTeams:")
        for competitor in competitors:
            team_id = competitor.get('id')
            team_name = get_team_name(team_id, teams_data)
            home_away = competitor.get('homeAway', 'Unknown')
            winner = competitor.get('winner', False)
            print(f"  {team_name} ({home_away}) - {'Winner' if winner else 'Loser'}")
    
    return header

def analyze_plays_detailed(data, teams_data):
    """Detailed play-by-play analysis"""
    print("\n=== PLAY-BY-PLAY ANALYSIS ===")
    
    plays = data.get('plays', {}).get('items', [])
    print(f"Total plays: {len(plays)}")
    
    # Initialize counters
    play_types = {}
    quarters = {1: 0, 2: 0, 3: 0, 4: 0}
    team_plays = {}
    team_rushing = {}
    team_passing = {}
    team_penalties = {}
    
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
                team_id = participant.get('id')  # ID is directly in participant, not nested in team
                team_name = get_team_name(team_id, teams_data)
                
                if team_name not in team_plays:
                    team_plays[team_name] = 0
                team_plays[team_name] += 1
                
                # Count specific play types by team
                if type_text == 'Rush':
                    if team_name not in team_rushing:
                        team_rushing[team_name] = 0
                    team_rushing[team_name] += 1
                elif 'Pass' in type_text:
                    if team_name not in team_passing:
                        team_passing[team_name] = 0
                    team_passing[team_name] += 1
                elif type_text == 'Penalty':
                    if team_name not in team_penalties:
                        team_penalties[team_name] = 0
                    team_penalties[team_name] += 1
                break
    
    print(f"\nPlays by quarter:")
    for q, count in quarters.items():
        print(f"  Q{q}: {count} plays")
    
    print(f"\nPlays by team:")
    for team, count in team_plays.items():
        print(f"  {team}: {count} plays")
    
    print(f"\nRushing plays by team:")
    for team, count in team_rushing.items():
        print(f"  {team}: {count} rushes")
    
    print(f"\nPassing plays by team:")
    for team, count in team_passing.items():
        print(f"  {team}: {count} passes")
    
    print(f"\nPenalties by team:")
    for team, count in team_penalties.items():
        print(f"  {team}: {count} penalties")
    
    print(f"\nTop play types:")
    for play_type, count in sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {play_type}: {count}")
    
    return {
        'total_plays': len(plays),
        'quarters': quarters,
        'play_types': play_types,
        'team_plays': team_plays,
        'team_rushing': team_rushing,
        'team_passing': team_passing,
        'team_penalties': team_penalties
    }

def analyze_drives_detailed(data, teams_data):
    """Detailed drive analysis"""
    print("\n=== DRIVE ANALYSIS ===")
    
    drives = data.get('drives', {}).get('items', [])
    print(f"Total drives: {len(drives)}")
    
    team_drives = {}
    team_scoring_drives = {}
    drive_lengths = []
    drive_results = {}
    
    for drive in drives:
        team = drive.get('team', {})
        team_id = team.get('id') if team else None
        team_name = get_team_name(team_id, teams_data)
        
        if team_name not in team_drives:
            team_drives[team_name] = 0
        team_drives[team_name] += 1
        
        # Check if scoring drive
        if drive.get('isScore', False):
            if team_name not in team_scoring_drives:
                team_scoring_drives[team_name] = 0
            team_scoring_drives[team_name] += 1
        
        # Get drive length
        plays = drive.get('plays', [])
        drive_lengths.append(len(plays))
        
        # Get drive result
        result = drive.get('result', 'Unknown')
        if result not in drive_results:
            drive_results[result] = 0
        drive_results[result] += 1
    
    print(f"\nDrives by team:")
    for team, count in team_drives.items():
        print(f"  {team}: {count} drives")
    
    print(f"\nScoring drives by team:")
    for team, count in team_scoring_drives.items():
        print(f"  {team}: {count} scoring drives")
    
    print(f"\nDrive results:")
    for result, count in sorted(drive_results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {result}: {count}")
    
    print(f"\nAverage drive length: {sum(drive_lengths) / len(drive_lengths):.1f} plays")
    
    return {
        'total_drives': len(drives),
        'team_drives': team_drives,
        'team_scoring_drives': team_scoring_drives,
        'drive_results': drive_results,
        'avg_drive_length': sum(drive_lengths) / len(drive_lengths) if drive_lengths else 0
    }

def analyze_scoring_detailed(data, teams_data):
    """Detailed scoring analysis"""
    print("\n=== SCORING ANALYSIS ===")
    
    plays = data.get('plays', {}).get('items', [])
    
    scoring_plays = []
    team_scores = {}
    team_touchdowns = {}
    team_field_goals = {}
    
    for play in plays:
        if play.get('scoringPlay', False):
            scoring_plays.append(play)
            
            # Get team - for scoring plays, team info is directly in the play
            team = play.get('team', {})
            if team and '$ref' in team:
                # Extract team ID from the reference URL
                team_ref = team['$ref']
                team_id = team_ref.split('/')[-1].split('?')[0]  # Get the last part before query params
                team_name = get_team_name(team_id, teams_data)
                
                # Get points scored
                points = play.get('scoreValue', 0)
                if team_name not in team_scores:
                    team_scores[team_name] = 0
                team_scores[team_name] += points
                
                # Count touchdowns and field goals
                play_type = play.get('type', {}).get('text', '')
                if 'Touchdown' in play_type:
                    if team_name not in team_touchdowns:
                        team_touchdowns[team_name] = 0
                    team_touchdowns[team_name] += 1
                elif 'Field Goal' in play_type:
                    if team_name not in team_field_goals:
                        team_field_goals[team_name] = 0
                    team_field_goals[team_name] += 1
    
    print(f"Total scoring plays: {len(scoring_plays)}")
    
    print(f"\nFinal scores:")
    for team, points in team_scores.items():
        print(f"  {team}: {points} points")
    
    print(f"\nTouchdowns by team:")
    for team, count in team_touchdowns.items():
        print(f"  {team}: {count} touchdowns")
    
    print(f"\nField goals by team:")
    for team, count in team_field_goals.items():
        print(f"  {team}: {count} field goals")
    
    return {
        'total_scoring_plays': len(scoring_plays),
        'team_scores': team_scores,
        'team_touchdowns': team_touchdowns,
        'team_field_goals': team_field_goals
    }

def main():
    print("Final Comprehensive Analysis: Washington Huskies at Michigan Wolverines")
    print("Game ID: 401752873 | Date: October 18, 2025")
    print("=" * 80)
    
    # Load all data
    game_data, teams_data = load_data()
    
    # Run analyses
    game_summary = analyze_game_summary(game_data, teams_data)
    plays_analysis = analyze_plays_detailed(game_data, teams_data)
    drives_analysis = analyze_drives_detailed(game_data, teams_data)
    scoring_analysis = analyze_scoring_detailed(game_data, teams_data)
    
    # Final summary
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Game: {game_summary.get('name', 'Unknown')}")
    print(f"Date: {game_summary.get('date', 'Unknown')}")
    
    if scoring_analysis['team_scores']:
        print(f"Final Score:")
        for team, score in scoring_analysis['team_scores'].items():
            print(f"  {team}: {score}")
    
    print(f"\nGame Statistics:")
    print(f"  Total plays: {plays_analysis['total_plays']}")
    print(f"  Total drives: {drives_analysis['total_drives']}")
    print(f"  Average drive length: {drives_analysis['avg_drive_length']:.1f} plays")
    print(f"  Total scoring plays: {scoring_analysis['total_scoring_plays']}")
    
    # Save final analysis
    final_analysis = {
        'game_summary': game_summary,
        'plays_analysis': plays_analysis,
        'drives_analysis': drives_analysis,
        'scoring_analysis': scoring_analysis,
        'analyzed_at': datetime.now().isoformat()
    }
    
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/final_analysis.json', 'w') as f:
        json.dump(final_analysis, f, indent=2)
    
    print(f"\nFinal analysis saved to: data/game_401752873/final_analysis.json")

if __name__ == "__main__":
    main()
