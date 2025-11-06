#!/usr/bin/env python3
"""
Check ESPN full data structure to find all 160 plays
"""

import json

def check_espn_full_data():
    """Check ESPN full data structure"""
    
    print("🔍 Checking ESPN full data structure...")
    
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
                
                # Check if there are more plays in drives
                if 'drives' in espn_data:
                    drives = espn_data['drives']
                    print(f"📊 Drives type: {type(drives)}")
                    
                    if isinstance(drives, dict) and 'items' in drives:
                        drive_items = drives['items']
                        print(f"📊 Drive items length: {len(drive_items)}")
                        
                        # Check if drives have plays
                        total_plays = 0
                        for i, drive in enumerate(drive_items[:3]):  # Check first 3 drives
                            print(f"📊 Drive {i+1} keys: {list(drive.keys())}")
                            if 'plays' in drive:
                                drive_plays = drive['plays']
                                if isinstance(drive_plays, dict) and 'items' in drive_plays:
                                    drive_play_count = len(drive_plays['items'])
                                    total_plays += drive_play_count
                                    print(f"📊 Drive {i+1} plays: {drive_play_count}")
                                elif isinstance(drive_plays, list):
                                    drive_play_count = len(drive_plays)
                                    total_plays += drive_play_count
                                    print(f"📊 Drive {i+1} plays: {drive_play_count}")
                        
                        print(f"📊 Total plays in first 3 drives: {total_plays}")
    
    # Check if there's a different structure for all plays
    print(f"\n📊 Looking for all plays structure...")
    
    # Check if there's a plays array at the top level
    for key in espn_data.keys():
        if 'play' in key.lower():
            print(f"📊 Found potential plays key: {key}")
            if isinstance(espn_data[key], list):
                print(f"  Length: {len(espn_data[key])}")
            elif isinstance(espn_data[key], dict):
                print(f"  Dict keys: {list(espn_data[key].keys())}")
                if 'items' in espn_data[key]:
                    print(f"  Items length: {len(espn_data[key]['items'])}")

if __name__ == "__main__":
    check_espn_full_data()
