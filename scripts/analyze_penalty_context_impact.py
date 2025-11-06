#!/usr/bin/env python3
"""
Analyze penalty context to understand impact - what happens before and after penalties
"""

import json
import os

def analyze_penalty_context_impact():
    """Analyze penalty context and impact"""
    
    # Load the sorted CFBD data
    cfbd_file = 'cfbd_plays_401752873_sorted.json'
    if not os.path.exists(cfbd_file):
        print("❌ SORTED CFBD data file not found")
        return
    
    with open(cfbd_file, 'r') as f:
        plays = json.load(f)
    
    print(f"📊 Analyzing penalty context and impact...")
    print("=" * 60)
    
    # Find penalty plays and their context
    penalty_analysis = []
    
    for i, play in enumerate(plays):
        play_text = play.get('playText', '').lower()
        
        if 'penalty' in play_text:
            # Get context (previous and next plays)
            prev_play = plays[i-1] if i > 0 else None
            next_play = plays[i+1] if i < len(plays)-1 else None
            
            penalty_info = {
                'penalty_play': play,
                'prev_play': prev_play,
                'next_play': next_play,
                'penalty_index': i
            }
            penalty_analysis.append(penalty_info)
    
    print(f"📊 Found {len(penalty_analysis)} penalty plays with context")
    
    # Analyze penalty impact
    for i, penalty_info in enumerate(penalty_analysis):
        penalty_play = penalty_info['penalty_play']
        prev_play = penalty_info['prev_play']
        next_play = penalty_info['next_play']
        
        print(f"\n📋 Penalty {i+1} Analysis:")
        print(f"  Penalty Play: {penalty_play.get('playText', '')[:80]}...")
        
        if prev_play:
            prev_ppa = prev_play.get('ppa', 'N/A')
            prev_text = prev_play.get('playText', '')[:60] + '...' if len(prev_play.get('playText', '')) > 60 else prev_play.get('playText', '')
            print(f"  Previous Play: PPA {prev_ppa} - {prev_text}")
        
        if next_play:
            next_ppa = next_play.get('ppa', 'N/A')
            next_text = next_play.get('playText', '')[:60] + '...' if len(next_play.get('playText', '')) > 60 else next_play.get('playText', '')
            print(f"  Next Play: PPA {next_ppa} - {next_text}")
        
        # Analyze penalty severity
        penalty_text = penalty_play.get('playText', '')
        penalty_yardage = 0
        
        # Extract yardage from penalty text
        import re
        yardage_match = re.search(r'(\d+)\s*yd', penalty_text)
        if yardage_match:
            penalty_yardage = int(yardage_match.group(1))
        
        # Categorize penalty severity
        if penalty_yardage >= 15:
            severity = "SEVERE"
        elif penalty_yardage >= 10:
            severity = "MODERATE"
        elif penalty_yardage >= 5:
            severity = "MINOR"
        else:
            severity = "UNKNOWN"
        
        print(f"  Penalty Yardage: {penalty_yardage} yards ({severity})")
        
        # Check if penalty resulted in automatic first down
        if 'automatic first down' in penalty_text.lower():
            print(f"  Impact: AUTOMATIC FIRST DOWN")
        elif 'loss of down' in penalty_text.lower():
            print(f"  Impact: LOSS OF DOWN")
        elif 'no play' in penalty_text.lower():
            print(f"  Impact: NO PLAY (replay down)")
        
        # Analyze down and distance impact
        penalty_down = penalty_play.get('down', '')
        penalty_distance = penalty_play.get('distance', '')
        
        if next_play:
            next_down = next_play.get('down', '')
            next_distance = next_play.get('distance', '')
            
            if penalty_down != next_down or penalty_distance != next_distance:
                print(f"  Down/Distance Change: {penalty_down}&{penalty_distance} → {next_down}&{next_distance}")
        
        print()
    
    # Analyze penalty patterns
    print(f"📊 Penalty Pattern Analysis:")
    
    # Group by penalty type
    penalty_types = {}
    penalty_yardages = []
    
    for penalty_info in penalty_analysis:
        penalty_play = penalty_info['penalty_play']
        penalty_text = penalty_play.get('playText', '').lower()
        
        # Categorize penalty type
        if 'false start' in penalty_text:
            penalty_types['False Start'] = penalty_types.get('False Start', 0) + 1
        elif 'holding' in penalty_text:
            penalty_types['Holding'] = penalty_types.get('Holding', 0) + 1
        elif 'pass interference' in penalty_text:
            penalty_types['Pass Interference'] = penalty_types.get('Pass Interference', 0) + 1
        elif 'offside' in penalty_text:
            penalty_types['Offside'] = penalty_types.get('Offside', 0) + 1
        elif 'personal foul' in penalty_text:
            penalty_types['Personal Foul'] = penalty_types.get('Personal Foul', 0) + 1
        elif 'delay of game' in penalty_text:
            penalty_types['Delay of Game'] = penalty_types.get('Delay of Game', 0) + 1
        elif 'ineligible downfield' in penalty_text:
            penalty_types['Ineligible Downfield'] = penalty_types.get('Ineligible Downfield', 0) + 1
        else:
            penalty_types['Other'] = penalty_types.get('Other', 0) + 1
        
        # Extract yardage
        import re
        yardage_match = re.search(r'(\d+)\s*yd', penalty_text)
        if yardage_match:
            penalty_yardages.append(int(yardage_match.group(1)))
    
    print(f"  Penalty Types:")
    for penalty_type, count in sorted(penalty_types.items(), key=lambda x: x[1], reverse=True):
        print(f"    {penalty_type}: {count}")
    
    if penalty_yardages:
        print(f"  Penalty Yardages:")
        print(f"    Range: {min(penalty_yardages)} to {max(penalty_yardages)} yards")
        print(f"    Average: {sum(penalty_yardages)/len(penalty_yardages):.1f} yards")
        print(f"    Distribution: {sorted(set(penalty_yardages))}")
    
    # Analyze penalty impact on drive success
    print(f"\n📊 Penalty Impact on Drive Success:")
    
    for penalty_info in penalty_analysis:
        penalty_play = penalty_info['penalty_play']
        next_play = penalty_info['next_play']
        
        if next_play:
            next_ppa = next_play.get('ppa')
            if next_ppa is not None:
                penalty_yardage = 0
                import re
                yardage_match = re.search(r'(\d+)\s*yd', penalty_play.get('playText', ''))
                if yardage_match:
                    penalty_yardage = int(yardage_match.group(1))
                
                print(f"  Penalty: {penalty_yardage} yards → Next Play PPA: {next_ppa:.3f}")
    
    return penalty_analysis

if __name__ == "__main__":
    analyze_penalty_context_impact()
