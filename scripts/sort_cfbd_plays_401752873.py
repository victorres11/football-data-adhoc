#!/usr/bin/env python3
"""
Sort CFBD plays by drive and play number
"""

import json
import os

def sort_cfbd_plays():
    """Sort CFBD plays by drive and play number"""
    
    # Load the CFBD data
    cfbd_file = 'cfbd_plays_401752873_filtered.json'
    if not os.path.exists(cfbd_file):
        print("❌ CFBD data file not found")
        return
    
    with open(cfbd_file, 'r') as f:
        plays = json.load(f)
    
    print(f"📊 Loaded {len(plays)} CFBD plays")
    
    # Sort by drive and play number
    print("🔄 Sorting plays by drive and play number...")
    
    # First, let's see what fields are available for sorting
    if plays:
        sample_play = plays[0]
        print(f"Sample play fields: {list(sample_play.keys())}")
        
        # Check for drive and play number fields
        drive_field = None
        play_field = None
        
        # Look for drive-related fields
        for key in sample_play.keys():
            if 'drive' in key.lower():
                drive_field = key
                print(f"Found drive field: {key}")
            if 'play' in key.lower() and 'number' in key.lower():
                play_field = key
                print(f"Found play field: {key}")
        
        print(f"Drive field: {drive_field}")
        print(f"Play field: {play_field}")
        
        # Try to sort by available fields
        try:
            if drive_field and play_field:
                # Sort by drive, then by play number
                sorted_plays = sorted(plays, key=lambda x: (
                    x.get(drive_field, 0),
                    x.get(play_field, 0)
                ))
                print(f"✅ Sorted by {drive_field} and {play_field}")
            elif drive_field:
                # Sort by drive only
                sorted_plays = sorted(plays, key=lambda x: x.get(drive_field, 0))
                print(f"✅ Sorted by {drive_field}")
            else:
                # Try to sort by period and clock
                sorted_plays = sorted(plays, key=lambda x: (
                    x.get('period', 0),
                    x.get('clock', {}).get('minutes', 0) * 60 + x.get('clock', {}).get('seconds', 0)
                ))
                print(f"✅ Sorted by period and clock")
            
            # Save sorted plays
            output_file = 'cfbd_plays_401752873_sorted.json'
            with open(output_file, 'w') as f:
                json.dump(sorted_plays, f, indent=2)
            
            print(f"📁 Sorted plays saved to: {output_file}")
            
            # Show first few plays to verify sorting
            print(f"\n📋 First 10 plays after sorting:")
            for i, play in enumerate(sorted_plays[:10]):
                drive = play.get(drive_field, 'N/A') if drive_field else 'N/A'
                play_num = play.get(play_field, 'N/A') if play_field else 'N/A'
                period = play.get('period', 'N/A')
                clock = play.get('clock', {})
                time = f"{clock.get('minutes', 0)}:{clock.get('seconds', 0):02d}"
                text = play.get('playText', '')[:50] + '...' if len(play.get('playText', '')) > 50 else play.get('playText', '')
                
                print(f"  {i+1:2d}. Drive {drive}, Play {play_num}, Q{period} {time}: {text}")
            
            return sorted_plays
            
        except Exception as e:
            print(f"❌ Error sorting plays: {e}")
            return plays
    
    return plays

if __name__ == "__main__":
    sort_cfbd_plays()
