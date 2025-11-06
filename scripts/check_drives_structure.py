#!/usr/bin/env python3
"""
Check drives structure in detail
"""

import json
import requests

def check_drives_structure():
    """Check drives structure in detail"""
    
    print("🔍 Checking drives structure in detail...")
    
    # ESPN summary endpoint
    url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary"
    params = {
        'event': '401752873'
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check drives
            if 'drives' in data:
                drives = data['drives']
                print(f"📊 Drives type: {type(drives)}")
                print(f"📊 Drives keys: {list(drives.keys())}")
                
                if isinstance(drives, dict):
                    # Check if drives has items
                    if 'items' in drives:
                        drive_items = drives['items']
                        print(f"📊 Drive items length: {len(drive_items)}")
                        
                        # Check first drive structure
                        if drive_items:
                            first_drive = drive_items[0]
                            print(f"📊 First drive keys: {list(first_drive.keys())}")
                            
                            # Check if first drive has plays
                            if 'plays' in first_drive:
                                drive_plays = first_drive['plays']
                                print(f"📊 First drive plays type: {type(drive_plays)}")
                                
                                if isinstance(drive_plays, list):
                                    print(f"📊 First drive plays count: {len(drive_plays)}")
                                elif isinstance(drive_plays, dict):
                                    print(f"📊 First drive plays dict keys: {list(drive_plays.keys())}")
                                    if 'items' in drive_plays:
                                        print(f"📊 First drive plays items: {len(drive_plays['items'])}")
                            
                            # Check if first drive has playByPlay
                            if 'playByPlay' in first_drive:
                                play_by_play = first_drive['playByPlay']
                                print(f"📊 First drive playByPlay type: {type(play_by_play)}")
                                if isinstance(play_by_play, list):
                                    print(f"📊 First drive playByPlay count: {len(play_by_play)}")
                                elif isinstance(play_by_play, dict):
                                    print(f"📊 First drive playByPlay dict keys: {list(play_by_play.keys())}")
                                    if 'items' in play_by_play:
                                        print(f"📊 First drive playByPlay items: {len(play_by_play['items'])}")
                        
                        # Extract all plays from all drives
                        all_plays = []
                        for i, drive in enumerate(drive_items):
                            drive_plays = []
                            
                            # Check for plays
                            if 'plays' in drive:
                                plays = drive['plays']
                                if isinstance(plays, list):
                                    drive_plays.extend(plays)
                                elif isinstance(plays, dict) and 'items' in plays:
                                    drive_plays.extend(plays['items'])
                            
                            # Check for playByPlay
                            if 'playByPlay' in drive:
                                play_by_play = drive['playByPlay']
                                if isinstance(play_by_play, list):
                                    drive_plays.extend(play_by_play)
                                elif isinstance(play_by_play, dict) and 'items' in play_by_play:
                                    drive_plays.extend(play_by_play['items'])
                            
                            print(f"📊 Drive {i+1} plays: {len(drive_plays)}")
                            all_plays.extend(drive_plays)
                        
                        print(f"📊 Total plays extracted: {len(all_plays)}")
                        
                        # Save all plays
                        with open('espn_all_plays_from_drives_401752873.json', 'w') as f:
                            json.dump(all_plays, f, indent=2)
                        
                        print(f"💾 Saved all ESPN plays to espn_all_plays_from_drives_401752873.json")
                        
                        return all_plays
                    else:
                        print("❌ No items found in drives")
                        return None
                else:
                    print(f"📊 Drives is not a dict: {type(drives)}")
                    return None
            else:
                print("❌ No drives found in summary response")
                return None
        else:
            print(f"❌ Failed to fetch ESPN summary: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching ESPN summary: {e}")
        return None

if __name__ == "__main__":
    check_drives_structure()
