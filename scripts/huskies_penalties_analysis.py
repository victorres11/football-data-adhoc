#!/usr/bin/env python3
"""
Extract and display all penalties for Washington Huskies in table format
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

def extract_huskies_penalties(data, teams_data):
    """Extract all penalties for Washington Huskies"""
    plays = data.get('plays', {}).get('items', [])
    
    huskies_penalties = []
    
    for play in plays:
        # Check if this is a penalty play
        play_type = play.get('type', {}).get('text', '')
        if 'Penalty' in play_type:
            # Check if Washington is the team that committed the penalty
            # Look for Washington in the play text or team participants
            play_text = play.get('text', '').lower()
            short_text = play.get('shortText', '').lower()
            
            # Check if Washington is mentioned as committing the penalty
            if 'washington penalty' in play_text or 'washington penalty' in short_text:
                # Extract penalty details
                penalty_info = {
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
                huskies_penalties.append(penalty_info)
    
    return huskies_penalties

def display_penalties_table(penalties):
    """Display penalties in a formatted table"""
    if not penalties:
        print("No penalties found for Washington Huskies.")
        return
    
    print("=" * 120)
    print("WASHINGTON HUSKIES PENALTIES")
    print("=" * 120)
    print(f"{'Qtr':<4} {'Time':<8} {'Yards':<6} {'Down/Distance':<20} {'Yard Line':<15} {'Penalty Description':<50}")
    print("-" * 120)
    
    for penalty in penalties:
        quarter = str(penalty['quarter'])
        time = penalty['time']
        yards = str(penalty['yards']) if penalty['yards'] != 0 else 'N/A'
        down_distance = penalty['down_distance'][:20] if len(penalty['down_distance']) > 20 else penalty['down_distance']
        yard_line = penalty['yard_line'][:15] if len(penalty['yard_line']) > 15 else penalty['yard_line']
        description = penalty['short_text'][:50] if len(penalty['short_text']) > 50 else penalty['short_text']
        
        print(f"{quarter:<4} {time:<8} {yards:<6} {down_distance:<20} {yard_line:<15} {description:<50}")
    
    print("-" * 120)
    print(f"Total Penalties: {len(penalties)}")
    
    # Calculate total penalty yards
    total_yards = sum(penalty['yards'] for penalty in penalties if penalty['yards'] != 0)
    print(f"Total Penalty Yards: {total_yards}")
    
    # Group by penalty type
    penalty_types = {}
    for penalty in penalties:
        penalty_type = penalty['penalty_type']
        if penalty_type not in penalty_types:
            penalty_types[penalty_type] = 0
        penalty_types[penalty_type] += 1
    
    print(f"\nPenalty Types:")
    for penalty_type, count in penalty_types.items():
        print(f"  {penalty_type}: {count}")

def main():
    print("Washington Huskies Penalties Analysis")
    print("Game ID: 401752873 | Date: October 18, 2025")
    print("=" * 70)
    
    # Load data
    game_data, teams_data = load_data()
    
    # Extract penalties
    penalties = extract_huskies_penalties(game_data, teams_data)
    
    # Display table
    display_penalties_table(penalties)
    
    # Save detailed data
    import os
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/huskies_penalties.json', 'w') as f:
        json.dump(penalties, f, indent=2)
    
    print(f"\nDetailed penalty data saved to: data/game_401752873/huskies_penalties.json")

if __name__ == "__main__":
    main()
