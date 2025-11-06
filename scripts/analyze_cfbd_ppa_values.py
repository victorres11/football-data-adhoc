#!/usr/bin/env python3
"""
Analyze CFBD PPA values to understand the metric
"""

import json
import os

def analyze_cfbd_ppa_values():
    """Analyze CFBD PPA values"""
    
    # Load the sorted CFBD data
    cfbd_file = 'cfbd_plays_401752873_sorted.json'
    if not os.path.exists(cfbd_file):
        print("❌ SORTED CFBD data file not found")
        return
    
    with open(cfbd_file, 'r') as f:
        plays = json.load(f)
    
    print(f"📊 Analyzing PPA values in {len(plays)} CFBD plays...")
    print("=" * 60)
    
    # Analyze PPA values
    ppa_values = []
    ppa_by_play_type = {}
    ppa_by_down = {}
    ppa_by_yard_line = {}
    
    for play in plays:
        ppa = play.get('ppa')
        if ppa is not None and ppa != '':
            ppa_values.append(float(ppa))
            
            # Group by play type
            play_type = play.get('playType', 'Unknown')
            if play_type not in ppa_by_play_type:
                ppa_by_play_type[play_type] = []
            ppa_by_play_type[play_type].append(float(ppa))
            
            # Group by down
            down = play.get('down', 'Unknown')
            if down not in ppa_by_down:
                ppa_by_down[down] = []
            ppa_by_down[down].append(float(ppa))
            
            # Group by yard line
            yard_line = play.get('yardline', '')
            if yard_line:
                yard_line_int = int(yard_line)
                if yard_line_int not in ppa_by_yard_line:
                    ppa_by_yard_line[yard_line_int] = []
                ppa_by_yard_line[yard_line_int].append(float(ppa))
    
    print(f"📊 PPA Analysis:")
    print(f"  Total plays with PPA: {len(ppa_values)}")
    print(f"  Plays without PPA: {len(plays) - len(ppa_values)}")
    
    if ppa_values:
        print(f"  PPA Range: {min(ppa_values):.3f} to {max(ppa_values):.3f}")
        print(f"  PPA Average: {sum(ppa_values)/len(ppa_values):.3f}")
        print(f"  PPA Median: {sorted(ppa_values)[len(ppa_values)//2]:.3f}")
        
        # Show distribution
        positive_ppa = [p for p in ppa_values if p > 0]
        negative_ppa = [p for p in ppa_values if p < 0]
        zero_ppa = [p for p in ppa_values if p == 0]
        
        print(f"  Positive PPA: {len(positive_ppa)} plays")
        print(f"  Negative PPA: {len(negative_ppa)} plays")
        print(f"  Zero PPA: {len(zero_ppa)} plays")
        
        # Show top and bottom PPA plays
        print(f"\n📋 Top 5 PPA Plays:")
        sorted_plays = sorted(plays, key=lambda x: float(x.get('ppa', 0)) if x.get('ppa') is not None else 0, reverse=True)
        for i, play in enumerate(sorted_plays[:5]):
            ppa = play.get('ppa', 'N/A')
            play_text = play.get('playText', '')[:60] + '...' if len(play.get('playText', '')) > 60 else play.get('playText', '')
            print(f"  {i+1}. PPA: {ppa} - {play_text}")
        
        print(f"\n📋 Bottom 5 PPA Plays:")
        for i, play in enumerate(sorted_plays[-5:]):
            ppa = play.get('ppa', 'N/A')
            play_text = play.get('playText', '')[:60] + '...' if len(play.get('playText', '')) > 60 else play.get('playText', '')
            print(f"  {i+1}. PPA: {ppa} - {play_text}")
        
        # Analyze by play type
        print(f"\n📊 PPA by Play Type:")
        for play_type, ppas in ppa_by_play_type.items():
            if ppas:
                avg_ppa = sum(ppas) / len(ppas)
                print(f"  {play_type}: {len(ppas)} plays, Avg PPA: {avg_ppa:.3f}")
        
        # Analyze by down
        print(f"\n📊 PPA by Down:")
        for down, ppas in ppa_by_down.items():
            if ppas:
                avg_ppa = sum(ppas) / len(ppas)
                print(f"  {down} down: {len(ppas)} plays, Avg PPA: {avg_ppa:.3f}")
        
        # Show some examples with context
        print(f"\n📋 Sample PPA Plays with Context:")
        for i, play in enumerate(plays[:10]):
            ppa = play.get('ppa', 'N/A')
            if ppa is not None and ppa != '':
                play_text = play.get('playText', '')[:50] + '...' if len(play.get('playText', '')) > 50 else play.get('playText', '')
                down = play.get('down', '')
                distance = play.get('distance', '')
                yard_line = play.get('yardline', '')
                yards_gained = play.get('yardsGained', '')
                print(f"  Play {play.get('playNumber', 'N/A')}: PPA {ppa}")
                print(f"    {play_text}")
                print(f"    Down: {down}, Distance: {distance}, Yard Line: {yard_line}, Yards Gained: {yards_gained}")
                print()
    
    return ppa_values

if __name__ == "__main__":
    analyze_cfbd_ppa_values()
