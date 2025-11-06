#!/usr/bin/env python3
"""
Fetch ESPN win probability data for game 401752873
"""

import json
import requests

def fetch_espn_win_probability():
    """Fetch ESPN win probability data"""
    
    print("🔍 Fetching ESPN win probability data...")
    
    # ESPN win probability endpoint
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
            
            # Check for win probability data
            if 'winprobability' in data:
                wp_data = data['winprobability']
                print(f"✅ Found ESPN win probability data with {len(wp_data)} entries")
                
                # Save the data
                with open('espn_win_probability_401752873.json', 'w') as f:
                    json.dump(wp_data, f, indent=2)
                
                print(f"💾 Saved ESPN win probability data to espn_win_probability_401752873.json")
                
                # Show first few entries
                print(f"\n📊 First 3 entries:")
                for i, entry in enumerate(wp_data[:3]):
                    print(f"  Entry {i+1}: {entry}")
                
                return wp_data
            else:
                print("❌ No winprobability data found in ESPN response")
                print(f"📊 Available keys: {list(data.keys())}")
                return None
        else:
            print(f"❌ Failed to fetch ESPN data: {response.status_code}")
            print(f"📊 Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching ESPN data: {e}")
        return None

if __name__ == "__main__":
    fetch_espn_win_probability()
