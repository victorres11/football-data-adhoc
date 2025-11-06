#!/usr/bin/env python3
"""
Debug script to check penalty detection
"""

import json

def load_game_data():
    """Load existing game data"""
    with open('data/game_401752873/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    return game_data

def debug_penalties():
    """Debug penalty detection"""
    game_data = load_game_data()
    plays = game_data.get('plays', {}).get('items', [])
    
    print(f"Total plays: {len(plays)}")
    print("=" * 50)
    
    penalties = []
    for i, play in enumerate(plays):
        play_type_id = play.get('type', {}).get('id', '')
        if play_type_id == '8':  # Penalty type ID
            short_text = play.get('shortText', '')
            play_text = play.get('text', '')
            
            # Determine which team committed the penalty
            team_committed = "Unknown"
            if 'washington penalty' in short_text.lower():
                team_committed = "Washington"
            elif 'michigan penalty' in short_text.lower():
                team_committed = "Michigan"
            
            penalties.append({
                'play_number': i + 1,
                'team': team_committed,
                'short_text': short_text,
                'yards': play.get('statYardage', 0),
                'quarter': play.get('period', {}).get('number', ''),
                'time': play.get('clock', {}).get('displayValue', '')
            })
    
    print(f"Found {len(penalties)} penalties:")
    print("=" * 50)
    
    for penalty in penalties:
        print(f"Play #{penalty['play_number']} - Q{penalty['quarter']} {penalty['time']}")
        print(f"  Team: {penalty['team']}")
        print(f"  Yards: {penalty['yards']}")
        print(f"  Description: {penalty['short_text']}")
        print("-" * 30)
    
    # Count by team
    washington_penalties = [p for p in penalties if p['team'] == 'Washington']
    michigan_penalties = [p for p in penalties if p['team'] == 'Michigan']
    
    print(f"\nSummary:")
    print(f"Washington penalties: {len(washington_penalties)}")
    print(f"Michigan penalties: {len(michigan_penalties)}")
    print(f"Unknown penalties: {len(penalties) - len(washington_penalties) - len(michigan_penalties)}")

if __name__ == "__main__":
    debug_penalties()
