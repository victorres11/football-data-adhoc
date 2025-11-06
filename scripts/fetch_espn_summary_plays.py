#!/usr/bin/env python3
"""
Fetch ESPN plays from summary endpoint
"""

import json
import requests

def fetch_espn_summary_plays():
    """Fetch ESPN plays from summary endpoint"""
    
    print("🔍 Fetching ESPN plays from summary endpoint...")
    
    # ESPN summary endpoint
    url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary"
    params = {
        'event': '401752873'
    }
    
    print(f"📊 Fetching from: {url}")
    print(f"📊 Params: {params}")
    
    try:
        response = requests.get(url, params=params)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for plays data
            if 'plays' in data:
                plays = data['plays']
                print(f"📊 Plays type: {type(plays)}")
                
                if isinstance(plays, list):
                    print(f"📊 Total plays found: {len(plays)}")
                    
                    # Save the complete plays data
                    with open('espn_summary_plays_401752873.json', 'w') as f:
                        json.dump(plays, f, indent=2)
                    
                    print(f"💾 Saved ESPN summary plays to espn_summary_plays_401752873.json")
                    
                    # Show first few plays
                    print(f"\n📊 First 3 plays:")
                    for i, play in enumerate(plays[:3]):
                        print(f"  Play {i+1}: {play.get('text', '')[:50]}...")
                    
                    return plays
                elif isinstance(plays, dict):
                    print(f"📊 Plays dict keys: {list(plays.keys())}")
                    if 'items' in plays:
                        play_items = plays['items']
                        print(f"📊 Play items length: {len(play_items)}")
                        
                        # Save the complete plays data
                        with open('espn_summary_plays_401752873.json', 'w') as f:
                            json.dump(play_items, f, indent=2)
                        
                        print(f"💾 Saved ESPN summary plays to espn_summary_plays_401752873.json")
                        
                        return play_items
            else:
                print("❌ No plays found in summary response")
                print(f"📊 Available keys: {list(data.keys())}")
                return None
        else:
            print(f"❌ Failed to fetch ESPN summary: {response.status_code}")
            print(f"📊 Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching ESPN summary: {e}")
        return None

if __name__ == "__main__":
    fetch_espn_summary_plays()
