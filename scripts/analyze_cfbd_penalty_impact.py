#!/usr/bin/env python3
"""
Analyze CFBD penalty data to understand penalty impact and severity
"""

import json
import os
import re

def analyze_cfbd_penalty_impact():
    """Analyze CFBD penalty data for impact metrics"""
    
    # Load the sorted CFBD data
    cfbd_file = 'cfbd_plays_401752873_sorted.json'
    if not os.path.exists(cfbd_file):
        print("❌ SORTED CFBD data file not found")
        return
    
    with open(cfbd_file, 'r') as f:
        plays = json.load(f)
    
    print(f"📊 Analyzing penalty data in {len(plays)} CFBD plays...")
    print("=" * 60)
    
    # Find penalty plays
    penalty_plays = []
    penalty_related_plays = []
    
    for play in plays:
        play_text = play.get('playText', '').lower()
        play_type = play.get('playType', '').lower()
        
        # Check if it's a penalty play
        if 'penalty' in play_text or 'penalty' in play_type:
            penalty_plays.append(play)
        
        # Check if penalty is mentioned in the play
        if 'penalty' in play_text:
            penalty_related_plays.append(play)
    
    print(f"📊 Penalty Analysis:")
    print(f"  Plays with penalty in text: {len(penalty_related_plays)}")
    print(f"  Penalty play type: {len(penalty_plays)}")
    
    # Analyze penalty plays
    if penalty_related_plays:
        print(f"\n📋 Sample Penalty Plays:")
        for i, play in enumerate(penalty_related_plays[:10]):
            ppa = play.get('ppa', 'N/A')
            play_text = play.get('playText', '')
            down = play.get('down', '')
            distance = play.get('distance', '')
            yard_line = play.get('yardline', '')
            yards_gained = play.get('yardsGained', '')
            
            print(f"  {i+1}. PPA: {ppa}")
            print(f"     {play_text}")
            print(f"     Down: {down}, Distance: {distance}, Yard Line: {yard_line}, Yards: {yards_gained}")
            print()
    
    # Analyze penalty impact using PPA
    penalty_ppa_values = []
    for play in penalty_related_plays:
        ppa = play.get('ppa')
        if ppa is not None and ppa != '':
            penalty_ppa_values.append(float(ppa))
    
    if penalty_ppa_values:
        print(f"📊 Penalty PPA Analysis:")
        print(f"  Penalty plays with PPA: {len(penalty_ppa_values)}")
        print(f"  Penalty PPA Range: {min(penalty_ppa_values):.3f} to {max(penalty_ppa_values):.3f}")
        print(f"  Penalty PPA Average: {sum(penalty_ppa_values)/len(penalty_ppa_values):.3f}")
        
        # Categorize penalty severity by PPA
        severe_penalties = [p for p in penalty_related_plays if p.get('ppa') and float(p.get('ppa')) < -1.0]
        moderate_penalties = [p for p in penalty_related_plays if p.get('ppa') and -1.0 <= float(p.get('ppa')) < 0]
        minor_penalties = [p for p in penalty_related_plays if p.get('ppa') and float(p.get('ppa')) >= 0]
        
        print(f"\n📊 Penalty Severity by PPA:")
        print(f"  Severe penalties (PPA < -1.0): {len(severe_penalties)}")
        print(f"  Moderate penalties (-1.0 ≤ PPA < 0): {len(moderate_penalties)}")
        print(f"  Minor penalties (PPA ≥ 0): {len(minor_penalties)}")
        
        # Show examples of each severity
        print(f"\n📋 Severe Penalties (PPA < -1.0):")
        for i, play in enumerate(severe_penalties[:5]):
            ppa = play.get('ppa', 'N/A')
            play_text = play.get('playText', '')[:80] + '...' if len(play.get('playText', '')) > 80 else play.get('playText', '')
            print(f"  {i+1}. PPA: {ppa} - {play_text}")
        
        print(f"\n📋 Moderate Penalties (-1.0 ≤ PPA < 0):")
        for i, play in enumerate(moderate_penalties[:5]):
            ppa = play.get('ppa', 'N/A')
            play_text = play.get('playText', '')[:80] + '...' if len(play.get('playText', '')) > 80 else play.get('playText', '')
            print(f"  {i+1}. PPA: {ppa} - {play_text}")
        
        print(f"\n📋 Minor Penalties (PPA ≥ 0):")
        for i, play in enumerate(minor_penalties[:5]):
            ppa = play.get('ppa', 'N/A')
            play_text = play.get('playText', '')[:80] + '...' if len(play.get('playText', '')) > 80 else play.get('playText', '')
            print(f"  {i+1}. PPA: {ppa} - {play_text}")
    
    # Analyze penalty types and yardage
    print(f"\n🔍 Analyzing Penalty Types and Yardage:")
    
    penalty_types = {}
    penalty_yardage = []
    
    for play in penalty_related_plays:
        play_text = play.get('playText', '')
        
        # Extract penalty type
        if 'false start' in play_text.lower():
            penalty_types['False Start'] = penalty_types.get('False Start', 0) + 1
        elif 'holding' in play_text.lower():
            penalty_types['Holding'] = penalty_types.get('Holding', 0) + 1
        elif 'pass interference' in play_text.lower():
            penalty_types['Pass Interference'] = penalty_types.get('Pass Interference', 0) + 1
        elif 'offside' in play_text.lower():
            penalty_types['Offside'] = penalty_types.get('Offside', 0) + 1
        elif 'personal foul' in play_text.lower():
            penalty_types['Personal Foul'] = penalty_types.get('Personal Foul', 0) + 1
        elif 'delay of game' in play_text.lower():
            penalty_types['Delay of Game'] = penalty_types.get('Delay of Game', 0) + 1
        else:
            penalty_types['Other'] = penalty_types.get('Other', 0) + 1
        
        # Extract penalty yardage
        yardage_match = re.search(r'(\d+)\s*yd', play_text)
        if yardage_match:
            penalty_yardage.append(int(yardage_match.group(1)))
    
    print(f"  Penalty Types:")
    for penalty_type, count in sorted(penalty_types.items(), key=lambda x: x[1], reverse=True):
        print(f"    {penalty_type}: {count}")
    
    if penalty_yardage:
        print(f"  Penalty Yardage:")
        print(f"    Range: {min(penalty_yardage)} to {max(penalty_yardage)} yards")
        print(f"    Average: {sum(penalty_yardage)/len(penalty_yardage):.1f} yards")
        print(f"    Common yardages: {sorted(set(penalty_yardage))}")
    
    # Check for penalty-specific metrics
    print(f"\n🔍 Checking for Penalty-Specific Metrics:")
    
    penalty_metrics = {}
    for play in penalty_related_plays:
        for key, value in play.items():
            if 'penalty' in key.lower() and value is not None:
                if key not in penalty_metrics:
                    penalty_metrics[key] = []
                penalty_metrics[key].append(value)
    
    if penalty_metrics:
        print(f"  Found penalty-specific fields:")
        for field, values in penalty_metrics.items():
            print(f"    {field}: {values[:5]}...")
    else:
        print(f"  No penalty-specific metrics found")
    
    # Analyze penalty impact on down and distance
    print(f"\n📊 Penalty Impact on Down and Distance:")
    
    for play in penalty_related_plays:
        down = play.get('down', '')
        distance = play.get('distance', '')
        play_text = play.get('playText', '')
        
        # Check if penalty resulted in automatic first down
        if 'automatic first down' in play_text.lower() or '1st & 10' in play_text:
            print(f"  Automatic First Down: {play_text[:60]}...")
        
        # Check if penalty resulted in loss of down
        if 'loss of down' in play_text.lower():
            print(f"  Loss of Down: {play_text[:60]}...")
    
    return penalty_related_plays

if __name__ == "__main__":
    analyze_cfbd_penalty_impact()
