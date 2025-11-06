#!/usr/bin/env python3
"""
Reconstruct ESPN plays from win probability data
"""

import json

def reconstruct_espn_plays_from_wp():
    """Reconstruct ESPN plays from win probability data"""
    
    print("🔍 Reconstructing ESPN plays from win probability data...")
    
    # Load ESPN win probability data
    with open('espn_win_probability_401752873.json', 'r') as f:
        espn_wp_data = json.load(f)
    
    print(f"📊 ESPN win probability entries: {len(espn_wp_data)}")
    
    # Load existing ESPN plays data
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    # Get existing plays
    existing_plays = espn_data['plays']['items']
    print(f"📊 Existing ESPN plays: {len(existing_plays)}")
    
    # Create a mapping of play IDs to plays
    play_id_to_play = {}
    for play in existing_plays:
        play_id = play.get('id')
        if play_id:
            play_id_to_play[play_id] = play
    
    print(f"📊 Mapped {len(play_id_to_play)} existing plays")
    
    # Reconstruct plays from win probability data
    reconstructed_plays = []
    
    for i, wp_entry in enumerate(espn_wp_data):
        play_id = wp_entry.get('playId')
        
        # Try to find existing play data
        if play_id in play_id_to_play:
            play_data = play_id_to_play[play_id].copy()
        else:
            # Create minimal play data from win probability
            play_data = {
                'id': play_id,
                'sequenceNumber': i + 1,
                'type': {'id': '1', 'text': 'Play'},
                'text': f"Play {i + 1}",
                'shortText': f"Play {i + 1}",
                'awayScore': 0,
                'homeScore': 0,
                'period': {'number': 1},
                'clock': {'displayValue': '15:00'},
                'scoringPlay': False,
                'priority': 0,
                'scoreValue': 0,
                'team': {'id': '130', 'name': 'Michigan'},
                'start': {'yardLine': 50},
                'end': {'yardLine': 50},
                'statYardage': 0
            }
        
        # Add win probability data
        play_data['winProbability'] = {
            'homeWinPercentage': wp_entry.get('homeWinPercentage', 0),
            'tiePercentage': wp_entry.get('tiePercentage', 0),
            'playId': play_id
        }
        
        # Calculate WPA
        if i == 0:
            wpa = 0.0
        else:
            current_wp = wp_entry.get('homeWinPercentage', 0)
            previous_wp = espn_wp_data[i-1].get('homeWinPercentage', 0)
            wpa = current_wp - previous_wp
        
        play_data['wpa'] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100
        }
        
        reconstructed_plays.append(play_data)
    
    print(f"📊 Reconstructed {len(reconstructed_plays)} plays")
    
    # Save reconstructed plays
    with open('espn_reconstructed_plays_401752873.json', 'w') as f:
        json.dump(reconstructed_plays, f, indent=2)
    
    print(f"💾 Saved reconstructed ESPN plays to espn_reconstructed_plays_401752873.json")
    
    # Show examples
    print(f"\n📊 First 5 reconstructed plays:")
    for i, play in enumerate(reconstructed_plays[:5]):
        wpa_data = play['wpa']
        wp_data = play['winProbability']
        print(f"  Play {i+1} ({play['id']}): {wpa_data['wpa_percentage']:+.1f}% (WP: {wp_data['homeWinPercentage']:.1f}%)")
    
    return reconstructed_plays

if __name__ == "__main__":
    reconstruct_espn_plays_from_wp()
