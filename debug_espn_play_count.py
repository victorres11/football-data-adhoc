#!/usr/bin/env python3
"""
Debug ESPN play count to understand the discrepancy
"""

import json
import os

def debug_espn_play_count():
    """Debug ESPN play count"""
    
    espn_file = 'data/game_401752873/complete_game_data.json'
    if not os.path.exists(espn_file):
        print("❌ ESPN data file not found")
        return
    
    with open(espn_file, 'r') as f:
        espn_data = json.load(f)
    
    print("🔍 Debugging ESPN play count...")
    print("=" * 50)
    
    # Check different ways to count plays
    print("1. Counting 'text' fields (play descriptions):")
    text_count = str(espn_data).count('"text":')
    print(f"   Found {text_count} 'text' fields")
    
    print("\n2. Counting 'id' fields (play IDs):")
    id_count = str(espn_data).count('"id":')
    print(f"   Found {id_count} 'id' fields")
    
    print("\n3. Looking for drives structure:")
    if 'drives' in espn_data:
        print(f"   ✅ Found 'drives' key")
        if 'items' in espn_data['drives']:
            print(f"   ✅ Found 'drives.items' with {len(espn_data['drives']['items'])} drives")
            
            total_plays = 0
            for i, drive in enumerate(espn_data['drives']['items']):
                if 'plays' in drive and 'items' in drive['plays']:
                    drive_plays = len(drive['plays']['items'])
                    total_plays += drive_plays
                    print(f"   Drive {i+1}: {drive_plays} plays")
            
            print(f"   Total plays from drives: {total_plays}")
        else:
            print("   ❌ No 'drives.items' found")
    else:
        print("   ❌ No 'drives' key found")
    
    print("\n4. Looking for direct plays structure:")
    if 'plays' in espn_data:
        print(f"   ✅ Found 'plays' key")
        if isinstance(espn_data['plays'], list):
            print(f"   ✅ 'plays' is a list with {len(espn_data['plays'])} items")
        elif isinstance(espn_data['plays'], dict):
            print(f"   ✅ 'plays' is a dict with keys: {list(espn_data['plays'].keys())}")
            if 'items' in espn_data['plays']:
                print(f"   ✅ 'plays.items' has {len(espn_data['plays']['items'])} items")
        else:
            print(f"   ❌ 'plays' is {type(espn_data['plays'])}")
    else:
        print("   ❌ No 'plays' key found")
    
    print("\n5. Looking for winprobability structure:")
    if 'winprobability' in espn_data:
        print(f"   ✅ Found 'winprobability' key")
        if 'items' in espn_data['winprobability']:
            print(f"   ✅ 'winprobability.items' has {len(espn_data['winprobability']['items'])} items")
        else:
            print(f"   ❌ No 'winprobability.items' found")
    else:
        print("   ❌ No 'winprobability' key found")
    
    print("\n6. Top-level keys in ESPN data:")
    print(f"   {list(espn_data.keys())}")

if __name__ == "__main__":
    debug_espn_play_count()
