#!/usr/bin/env python3
"""
Check ESPN win probability data structure
"""

import json

def check_espn_win_probability():
    """Check ESPN win probability data structure"""
    
    print("🔍 Checking ESPN win probability data structure...")
    
    # Load ESPN game data
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    print(f"📊 ESPN data keys: {list(espn_data.keys())}")
    
    # Check for win probability data
    if 'winprobability' in espn_data:
        wp_data = espn_data['winprobability']
        print(f"📈 Found winprobability with {len(wp_data)} entries")
        if wp_data:
            print(f"First entry: {wp_data[0]}")
    else:
        print("❌ No 'winprobability' key found")
    
    # Check for other possible win probability keys
    for key in espn_data.keys():
        if 'win' in key.lower() or 'prob' in key.lower():
            print(f"📊 Found potential win probability key: {key}")
            if isinstance(espn_data[key], list):
                print(f"  Length: {len(espn_data[key])}")
                if espn_data[key]:
                    print(f"  First entry: {espn_data[key][0]}")
            else:
                print(f"  Type: {type(espn_data[key])}")
    
    # Check if win probability is in drives
    if 'drives' in espn_data:
        drives = espn_data['drives']
        print(f"📊 Found drives with {len(drives)} entries")
        
        # Check first drive for win probability
        if drives:
            first_drive = drives[0]
            print(f"First drive keys: {list(first_drive.keys())}")
            
            # Look for win probability in drive
            for key in first_drive.keys():
                if 'win' in key.lower() or 'prob' in key.lower():
                    print(f"📊 Found potential win probability in drive: {key}")
    
    # Check if win probability is in plays
    if 'plays' in espn_data:
        plays = espn_data['plays']
        print(f"📊 Found plays with {len(plays)} entries")
        
        # Check first play for win probability
        if plays:
            first_play = plays[0]
            print(f"First play keys: {list(first_play.keys())}")
            
            # Look for win probability in play
            for key in first_play.keys():
                if 'win' in key.lower() or 'prob' in key.lower():
                    print(f"📊 Found potential win probability in play: {key}")

if __name__ == "__main__":
    check_espn_win_probability()
