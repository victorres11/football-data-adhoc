#!/usr/bin/env python3
"""
Check ESPN data structure properly
"""

import json

def check_espn_data_structure():
    """Check ESPN data structure properly"""
    
    print("🔍 Checking ESPN data structure...")
    
    # Load ESPN game data
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    print(f"📊 ESPN data keys: {list(espn_data.keys())}")
    
    # Check plays structure
    if 'plays' in espn_data:
        plays = espn_data['plays']
        print(f"📊 Plays type: {type(plays)}")
        
        if isinstance(plays, dict):
            print(f"📊 Plays dict keys: {list(plays.keys())}")
            
            # Check if plays has items
            if 'items' in plays:
                play_items = plays['items']
                print(f"📊 Play items length: {len(play_items)}")
                
                if play_items:
                    first_play = play_items[0]
                    print(f"📊 First play keys: {list(first_play.keys())}")
                    
                    # Look for win probability in play
                    for key in first_play.keys():
                        if 'win' in key.lower() or 'prob' in key.lower():
                            print(f"📊 Found potential win probability in play: {key}")
        elif isinstance(plays, list):
            print(f"📊 Plays list length: {len(plays)}")
            if plays:
                first_play = plays[0]
                print(f"📊 First play keys: {list(first_play.keys())}")
    
    # Check drives structure
    if 'drives' in espn_data:
        drives = espn_data['drives']
        print(f"📊 Drives type: {type(drives)}")
        
        if isinstance(drives, dict):
            print(f"📊 Drives dict keys: {list(drives.keys())}")
            
            # Check if drives has items
            if 'items' in drives:
                drive_items = drives['items']
                print(f"📊 Drive items length: {len(drive_items)}")
                
                if drive_items:
                    first_drive = drive_items[0]
                    print(f"📊 First drive keys: {list(first_drive.keys())}")
                    
                    # Look for win probability in drive
                    for key in first_drive.keys():
                        if 'win' in key.lower() or 'prob' in key.lower():
                            print(f"📊 Found potential win probability in drive: {key}")
        elif isinstance(drives, list):
            print(f"📊 Drives list length: {len(drives)}")
            if drives:
                first_drive = drives[0]
                print(f"📊 First drive keys: {list(first_drive.keys())}")

if __name__ == "__main__":
    check_espn_data_structure()
