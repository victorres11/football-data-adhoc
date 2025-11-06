#!/usr/bin/env python3
"""
Fetch complete ESPN plays data
"""

import json
import requests

def fetch_complete_espn_plays():
    """Fetch complete ESPN plays data"""
    
    print("🔍 Fetching complete ESPN plays data...")
    
    # ESPN plays endpoint with pagination
    url = "http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/401752873/competitions/401752873/plays"
    
    print(f"📊 Fetching from: {url}")
    
    try:
        response = requests.get(url)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check the structure
            print(f"📊 Response keys: {list(data.keys())}")
            
            if 'items' in data:
                plays = data['items']
                print(f"📊 Total plays found: {len(plays)}")
                
                # Save the complete plays data
                with open('espn_complete_plays_401752873.json', 'w') as f:
                    json.dump(plays, f, indent=2)
                
                print(f"💾 Saved complete ESPN plays to espn_complete_plays_401752873.json")
                
                # Show first few plays
                print(f"\n📊 First 3 plays:")
                for i, play in enumerate(plays[:3]):
                    print(f"  Play {i+1}: {play.get('text', '')[:50]}...")
                
                return plays
            else:
                print("❌ No items found in response")
                return None
        else:
            print(f"❌ Failed to fetch ESPN plays: {response.status_code}")
            print(f"📊 Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching ESPN plays: {e}")
        return None

if __name__ == "__main__":
    fetch_complete_espn_plays()
