#!/usr/bin/env python3
"""
Create ESPN play-by-play with ESPN-derived WPA
"""

import json

def create_espn_pbp_with_wpa():
    """Create ESPN play-by-play with ESPN-derived WPA"""
    
    print("🔍 Creating ESPN play-by-play with ESPN-derived WPA...")
    
    # Load ESPN game data
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    # Load ESPN win probability data
    with open('espn_win_probability_401752873.json', 'r') as f:
        espn_wp_data = json.load(f)
    
    print(f"📊 ESPN plays: {len(espn_data['plays']['items'])}")
    print(f"📊 ESPN win probability entries: {len(espn_wp_data)}")
    
    # Calculate ESPN WPA from ESPN data
    espn_wpa_data = {}
    for i, entry in enumerate(espn_wp_data):
        if i == 0:
            wpa = 0.0
        else:
            current_wp = entry.get('homeWinPercentage', 0)
            previous_wp = espn_wp_data[i-1].get('homeWinPercentage', 0)
            wpa = current_wp - previous_wp
        
        espn_wpa_data[entry.get('playId', i)] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100,
            'home_win_probability': entry.get('homeWinPercentage', 0),
            'tie_percentage': entry.get('tiePercentage', 0)
        }
    
    print(f"📈 Calculated ESPN WPA for {len(espn_wpa_data)} plays")
    
    # Create ESPN play-by-play with WPA
    espn_pbp_with_wpa = []
    
    for play in espn_data['plays']['items']:
        play_id = play.get('id')
        play_data = {
            'play_id': play_id,
            'sequence_number': play.get('sequenceNumber'),
            'type': play.get('type'),
            'text': play.get('text'),
            'short_text': play.get('shortText'),
            'away_score': play.get('awayScore'),
            'home_score': play.get('homeScore'),
            'period': play.get('period'),
            'clock': play.get('clock'),
            'scoring_play': play.get('scoringPlay'),
            'priority': play.get('priority'),
            'score_value': play.get('scoreValue'),
            'team': play.get('team'),
            'start': play.get('start'),
            'end': play.get('end'),
            'stat_yardage': play.get('statYardage')
        }
        
        # Add ESPN WPA data if available
        if play_id in espn_wpa_data:
            play_data['espn_wpa'] = espn_wpa_data[play_id]
        else:
            play_data['espn_wpa'] = {
                'wpa': 0.0,
                'wpa_percentage': 0.0,
                'home_win_probability': 0.0,
                'tie_percentage': 0.0
            }
        
        espn_pbp_with_wpa.append(play_data)
    
    # Save ESPN play-by-play with WPA
    with open('espn_pbp_with_wpa_401752873.json', 'w') as f:
        json.dump(espn_pbp_with_wpa, f, indent=2)
    
    print("✅ Created ESPN play-by-play with ESPN-derived WPA")
    print("📄 File: espn_pbp_with_wpa_401752873.json")
    
    # Show examples
    print(f"\n📊 ESPN WPA Examples:")
    for i, play in enumerate(espn_pbp_with_wpa[:5]):
        wpa_data = play['espn_wpa']
        print(f"  Play {i+1} ({play['play_id']}): {wpa_data['wpa_percentage']:+.1f}% (WP: {wpa_data['home_win_probability']:.1f}%)")

if __name__ == "__main__":
    create_espn_pbp_with_wpa()
