#!/usr/bin/env python3
"""
Extract all plays from ESPN drives
"""

import json
import requests

def extract_plays_from_drives():
    """Extract all plays from ESPN drives"""
    
    print("🔍 Extracting all plays from ESPN drives...")
    
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
                
                if isinstance(drives, list):
                    print(f"📊 Total drives: {len(drives)}")
                    
                    # Extract all plays from drives
                    all_plays = []
                    for i, drive in enumerate(drives):
                        if 'plays' in drive:
                            drive_plays = drive['plays']
                            if isinstance(drive_plays, list):
                                print(f"📊 Drive {i+1} plays: {len(drive_plays)}")
                                all_plays.extend(drive_plays)
                            elif isinstance(drive_plays, dict) and 'items' in drive_plays:
                                drive_play_items = drive_plays['items']
                                print(f"📊 Drive {i+1} plays: {len(drive_play_items)}")
                                all_plays.extend(drive_play_items)
                    
                    print(f"📊 Total plays extracted: {len(all_plays)}")
                    
                    # Save all plays
                    with open('espn_all_plays_from_drives_401752873.json', 'w') as f:
                        json.dump(all_plays, f, indent=2)
                    
                    print(f"💾 Saved all ESPN plays to espn_all_plays_from_drives_401752873.json")
                    
                    # Show first few plays
                    print(f"\n📊 First 3 plays:")
                    for i, play in enumerate(all_plays[:3]):
                        print(f"  Play {i+1}: {play.get('text', '')[:50]}...")
                    
                    return all_plays
                else:
                    print(f"📊 Drives is not a list: {type(drives)}")
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
    extract_plays_from_drives()
