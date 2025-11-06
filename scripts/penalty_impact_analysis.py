#!/usr/bin/env python3
"""
Penalty Impact Analysis - Grade how damaging penalties are
"""

import json
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

def calculate_penalty_impact_score(penalty):
    """Calculate impact score for a penalty (0-100, higher = more damaging)"""
    score = 0
    
    # Base score from yardage (0-40 points)
    yards = abs(penalty.get('yards', 0))
    score += min(yards * 2, 40)  # 2 points per yard, max 40
    
    # Down and distance impact (0-30 points)
    down_distance = penalty.get('down_distance', '')
    if '1st' in down_distance:
        score += 5  # Less damaging on 1st down
    elif '2nd' in down_distance:
        score += 15  # More damaging on 2nd down
    elif '3rd' in down_distance:
        score += 25  # Very damaging on 3rd down
    elif '4th' in down_distance:
        score += 30  # Extremely damaging on 4th down
    
    # Field position impact (0-20 points)
    yard_line = penalty.get('yard_line', '')
    if 'WASH' in yard_line:
        # In Washington territory - less damaging
        score += 5
    elif 'MICH' in yard_line:
        # In Michigan territory - more damaging
        score += 15
    else:
        # Neutral field
        score += 10
    
    # Penalty type impact (0-10 points)
    penalty_text = penalty.get('short_text', '').lower()
    if 'false start' in penalty_text:
        score += 8  # Very damaging - kills momentum
    elif 'holding' in penalty_text:
        score += 6  # Damaging - negates big plays
    elif 'pass interference' in penalty_text:
        score += 10  # Most damaging - automatic first down
    elif 'personal foul' in penalty_text:
        score += 7  # Damaging - 15 yards
    elif 'unsportsmanlike' in penalty_text:
        score += 5  # Moderately damaging
    else:
        score += 3  # Other penalties
    
    # Quarter impact (0-5 points)
    quarter = penalty.get('quarter', 1)
    if quarter == 4:
        score += 5  # Most damaging in 4th quarter
    elif quarter == 3:
        score += 3  # Moderately damaging in 3rd quarter
    elif quarter == 2:
        score += 2  # Somewhat damaging in 2nd quarter
    else:
        score += 1  # Least damaging in 1st quarter
    
    return min(score, 100)  # Cap at 100

def get_penalty_severity(score):
    """Get severity level based on impact score"""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MODERATE"
    elif score >= 20:
        return "LOW"
    else:
        return "MINIMAL"

def extract_all_penalties(data, teams_data):
    """Extract all penalties for both teams"""
    plays = data.get('plays', {}).get('items', [])
    
    all_penalties = []
    
    for play in plays:
        play_type = play.get('type', {}).get('text', '')
        if 'Penalty' in play_type:
            # Determine which team committed the penalty
            play_text = play.get('text', '').lower()
            short_text = play.get('shortText', '').lower()
            
            team_name = "Unknown"
            if 'washington penalty' in play_text or 'washington penalty' in short_text:
                team_name = "Washington Huskies"
            elif 'michigan penalty' in play_text or 'michigan penalty' in short_text:
                team_name = "Michigan Wolverines"
            
            if team_name != "Unknown":
                penalty_info = {
                    'team': team_name,
                    'quarter': play.get('period', {}).get('number', 'Unknown'),
                    'time': play.get('clock', {}).get('displayValue', 'Unknown'),
                    'play_text': play.get('text', ''),
                    'short_text': play.get('shortText', ''),
                    'penalty_type': play_type,
                    'yard_line': play.get('start', {}).get('possessionText', 'Unknown'),
                    'yards': play.get('statYardage', 0),
                    'down_distance': play.get('start', {}).get('downDistanceText', 'Unknown'),
                    'sequence': play.get('sequenceNumber', 'Unknown')
                }
                
                # Calculate impact score
                penalty_info['impact_score'] = calculate_penalty_impact_score(penalty_info)
                penalty_info['severity'] = get_penalty_severity(penalty_info['impact_score'])
                
                all_penalties.append(penalty_info)
    
    return all_penalties

def display_penalty_impact_table(penalties, team_name):
    """Display penalty impact analysis for a specific team"""
    team_penalties = [p for p in penalties if p['team'] == team_name]
    
    if not team_penalties:
        print(f"No penalties found for {team_name}.")
        return
    
    print(f"\n{'='*120}")
    print(f"{team_name.upper()} PENALTY IMPACT ANALYSIS")
    print(f"{'='*120}")
    print(f"{'Qtr':<4} {'Time':<8} {'Yards':<6} {'Impact':<8} {'Severity':<10} {'Down/Distance':<20} {'Penalty Description':<50}")
    print("-" * 120)
    
    total_impact = 0
    severity_counts = {}
    
    for penalty in team_penalties:
        quarter = str(penalty['quarter'])
        time = penalty['time']
        yards = str(penalty['yards']) if penalty['yards'] != 0 else 'N/A'
        impact = penalty['impact_score']
        severity = penalty['severity']
        down_distance = penalty['down_distance'][:20] if len(penalty['down_distance']) > 20 else penalty['down_distance']
        description = penalty['short_text'][:50] if len(penalty['short_text']) > 50 else penalty['short_text']
        
        print(f"{quarter:<4} {time:<8} {yards:<6} {impact:<8} {severity:<10} {down_distance:<20} {description:<50}")
        
        total_impact += impact
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print("-" * 120)
    print(f"Total Penalties: {len(team_penalties)}")
    print(f"Total Impact Score: {total_impact}")
    print(f"Average Impact Score: {total_impact / len(team_penalties):.1f}")
    
    print(f"\nSeverity Breakdown:")
    for severity, count in sorted(severity_counts.items(), key=lambda x: ['MINIMAL', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'].index(x[0])):
        print(f"  {severity}: {count}")

def compare_teams_penalty_impact(penalties):
    """Compare penalty impact between teams"""
    print(f"\n{'='*80}")
    print("PENALTY IMPACT COMPARISON")
    print(f"{'='*80}")
    
    teams = {}
    for penalty in penalties:
        team = penalty['team']
        if team not in teams:
            teams[team] = []
        teams[team].append(penalty)
    
    for team_name, team_penalties in teams.items():
        total_impact = sum(p['impact_score'] for p in team_penalties)
        avg_impact = total_impact / len(team_penalties) if team_penalties else 0
        
        print(f"\n{team_name}:")
        print(f"  Total Penalties: {len(team_penalties)}")
        print(f"  Total Impact Score: {total_impact}")
        print(f"  Average Impact Score: {avg_impact:.1f}")
        
        # Count by severity
        severity_counts = {}
        for penalty in team_penalties:
            severity = penalty['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print(f"  Severity Breakdown:")
        for severity, count in sorted(severity_counts.items(), key=lambda x: ['MINIMAL', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'].index(x[0])):
            print(f"    {severity}: {count}")

def main():
    print("Penalty Impact Analysis")
    print("Game ID: 401752873 | Date: October 18, 2025")
    print("=" * 70)
    
    # Load data
    game_data, teams_data = load_data()
    
    # Extract all penalties with impact scores
    penalties = extract_all_penalties(game_data, teams_data)
    
    # Display analysis for each team
    display_penalty_impact_table(penalties, "Washington Huskies")
    display_penalty_impact_table(penalties, "Michigan Wolverines")
    
    # Compare teams
    compare_teams_penalty_impact(penalties)
    
    # Save detailed data
    import os
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/penalty_impact_analysis.json', 'w') as f:
        json.dump(penalties, f, indent=2)
    
    print(f"\nDetailed penalty impact data saved to: data/game_401752873/penalty_impact_analysis.json")

if __name__ == "__main__":
    main()
