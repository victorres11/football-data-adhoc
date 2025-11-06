#!/usr/bin/env python3
"""
Create CFBD play-by-play with CFBD-derived WPA
"""

import json

def create_cfbd_pbp_with_wpa():
    """Create CFBD play-by-play with CFBD-derived WPA"""
    
    print("🔍 Creating CFBD play-by-play with CFBD-derived WPA...")
    
    # Load CFBD plays data
    with open('cfbd_plays_401752873_filtered.json', 'r') as f:
        cfbd_plays = json.load(f)
    
    # Load CFBD win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        cfbd_wp_data = json.load(f)
    
    print(f"📊 CFBD plays: {len(cfbd_plays)}")
    print(f"📊 CFBD win probability entries: {len(cfbd_wp_data)}")
    
    # Calculate CFBD WPA from CFBD data
    cfbd_wpa_data = {}
    for i, entry in enumerate(cfbd_wp_data):
        if i == 0:
            wpa = 0.0
        else:
            current_wp = entry['home_win_probability']
            previous_wp = cfbd_wp_data[i-1]['home_win_probability']
            wpa = current_wp - previous_wp
        
        cfbd_wpa_data[entry['play_number']] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100,
            'home_win_probability': entry['home_win_probability'],
            'play_text': entry['play_text'],
            'home_ball': entry['home_ball'],
            'home_score': entry['home_score'],
            'away_score': entry['away_score'],
            'yard_line': entry['yard_line'],
            'down': entry['down'],
            'distance': entry['distance']
        }
    
    print(f"📈 Calculated CFBD WPA for {len(cfbd_wpa_data)} plays")
    
    # Create CFBD play-by-play with WPA
    cfbd_pbp_with_wpa = []
    
    for play in cfbd_plays:
        play_number = play.get('playNumber')
        play_data = {
            'play_number': play_number,
            'drive_number': play.get('driveNumber'),
            'quarter': play.get('quarter'),
            'clock': play.get('clock'),
            'down': play.get('down'),
            'distance': play.get('distance'),
            'yard_line': play.get('yardline'),
            'yards_to_goal': play.get('yardsToGoal'),
            'play_text': play.get('playText'),
            'offense': play.get('offense'),
            'defense': play.get('defense'),
            'yards': play.get('yards'),
            'scoring': play.get('scoring'),
            'play_id': play.get('playId'),
            'game_id': play.get('gameId'),
            'ppa': play.get('ppa'),
            'success': play.get('success'),
            'rush': play.get('rush'),
            'pass': play.get('pass'),
            'sack': play.get('sack'),
            'fumble': play.get('fumble'),
            'penalty': play.get('penalty')
        }
        
        # Add CFBD WPA data if available
        if play_number in cfbd_wpa_data:
            play_data['cfbd_wpa'] = cfbd_wpa_data[play_number]
        else:
            play_data['cfbd_wpa'] = {
                'wpa': 0.0,
                'wpa_percentage': 0.0,
                'home_win_probability': 0.0,
                'play_text': '',
                'home_ball': False,
                'home_score': 0,
                'away_score': 0,
                'yard_line': 0,
                'down': 0,
                'distance': 0
            }
        
        cfbd_pbp_with_wpa.append(play_data)
    
    # Save CFBD play-by-play with WPA
    with open('cfbd_pbp_with_wpa_401752873.json', 'w') as f:
        json.dump(cfbd_pbp_with_wpa, f, indent=2)
    
    print("✅ Created CFBD play-by-play with CFBD-derived WPA")
    print("📄 File: cfbd_pbp_with_wpa_401752873.json")
    
    # Show examples
    print(f"\n📊 CFBD WPA Examples:")
    for i, play in enumerate(cfbd_pbp_with_wpa[:5]):
        wpa_data = play['cfbd_wpa']
        print(f"  Play {i+1} ({play['play_number']}): {wpa_data['wpa_percentage']:+.1f}% (WP: {wpa_data['home_win_probability']:.1f}%)")

if __name__ == "__main__":
    create_cfbd_pbp_with_wpa()
