#!/usr/bin/env python3
"""
Check ESPN probability data
"""

import json

def check_espn_probability():
    """Check ESPN probability data"""
    
    print("🔍 Checking ESPN probability data...")
    
    # Load ESPN game data
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    # Get plays
    plays = espn_data['plays']['items']
    print(f"📊 Found {len(plays)} plays")
    
    # Check probability data in first few plays
    for i, play in enumerate(plays[:5]):
        print(f"\n📊 Play {i+1}:")
        print(f"  ID: {play.get('id')}")
        print(f"  Text: {play.get('text', '')[:50]}...")
        print(f"  Probability: {play.get('probability')}")
        
        # Check if probability has win probability data
        prob = play.get('probability')
        if prob:
            print(f"  Probability keys: {list(prob.keys()) if isinstance(prob, dict) else 'Not a dict'}")
            if isinstance(prob, dict):
                for key, value in prob.items():
                    print(f"    {key}: {value}")
    
    # Check if there's a separate win probability endpoint
    print(f"\n📊 Checking for separate win probability data...")
    
    # Look for win probability in the main data
    for key in espn_data.keys():
        if 'win' in key.lower() or 'prob' in key.lower():
            print(f"📊 Found potential win probability key: {key}")
            if isinstance(espn_data[key], list):
                print(f"  Length: {len(espn_data[key])}")
                if espn_data[key]:
                    print(f"  First entry: {espn_data[key][0]}")
            else:
                print(f"  Type: {type(espn_data[key])}")

if __name__ == "__main__":
    check_espn_probability()
