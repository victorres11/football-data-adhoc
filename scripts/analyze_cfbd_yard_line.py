#!/usr/bin/env python3
"""
Analyze CFBD data to understand yard line structure and find missing values
"""

import json
import os

def analyze_cfbd_yard_line():
    """Analyze CFBD yard line data structure"""
    
    # Load the sorted CFBD data
    cfbd_file = 'cfbd_plays_401752873_sorted.json'
    if not os.path.exists(cfbd_file):
        print("❌ SORTED CFBD data file not found")
        return
    
    with open(cfbd_file, 'r') as f:
        plays = json.load(f)
    
    print(f"📊 Analyzing {len(plays)} CFBD plays for yard line data...")
    print("=" * 60)
    
    # Analyze yard line fields
    yard_line_fields = {}
    yard_line_values = set()
    missing_yard_line = 0
    has_yard_line = 0
    
    print("🔍 Analyzing yard line fields...")
    
    for i, play in enumerate(plays):
        # Check for yard line related fields
        yard_line = play.get('yardline', '')
        yards_to_goal = play.get('yardsToGoal', '')
        
        if yard_line:
            has_yard_line += 1
            yard_line_values.add(yard_line)
        else:
            missing_yard_line += 1
        
        # Store field analysis
        for key, value in play.items():
            if 'yard' in key.lower() or 'line' in key.lower():
                if key not in yard_line_fields:
                    yard_line_fields[key] = {'count': 0, 'values': set(), 'missing': 0}
                
                if value and value != '':
                    yard_line_fields[key]['count'] += 1
                    yard_line_fields[key]['values'].add(str(value))
                else:
                    yard_line_fields[key]['missing'] += 1
    
    print(f"\n📊 Yard Line Analysis:")
    print(f"  Plays with yard line: {has_yard_line}")
    print(f"  Plays missing yard line: {missing_yard_line}")
    print(f"  Unique yard line values: {len(yard_line_values)}")
    
    print(f"\n🔍 Yard Line Fields Analysis:")
    for field, data in yard_line_fields.items():
        print(f"  {field}:")
        print(f"    Present: {data['count']}")
        print(f"    Missing: {data['missing']}")
        print(f"    Sample values: {list(data['values'])[:5]}")
        print()
    
    # Show sample plays with and without yard line
    print("📋 Sample plays WITH yard line:")
    count = 0
    for play in plays:
        if play.get('yardline') and count < 5:
            print(f"  Play {play.get('playNumber', 'N/A')}: {play.get('playText', '')[:50]}...")
            print(f"    Yard line: {play.get('yardline')}")
            print(f"    Yards to goal: {play.get('yardsToGoal')}")
            print(f"    Down: {play.get('down')}, Distance: {play.get('distance')}")
            print()
            count += 1
    
    print("📋 Sample plays MISSING yard line:")
    count = 0
    for play in plays:
        if not play.get('yardline') and count < 5:
            print(f"  Play {play.get('playNumber', 'N/A')}: {play.get('playText', '')[:50]}...")
            print(f"    Yard line: {play.get('yardline')}")
            print(f"    Yards to goal: {play.get('yardsToGoal')}")
            print(f"    Down: {play.get('down')}, Distance: {play.get('distance')}")
            print()
            count += 1
    
    # Analyze patterns in missing yard line
    print("🔍 Analyzing patterns in missing yard line...")
    
    missing_play_types = {}
    missing_quarters = {}
    missing_downs = {}
    
    for play in plays:
        if not play.get('yardline'):
            play_type = play.get('playType', 'Unknown')
            quarter = play.get('period', 'Unknown')
            down = play.get('down', 'Unknown')
            
            missing_play_types[play_type] = missing_play_types.get(play_type, 0) + 1
            missing_quarters[quarter] = missing_quarters.get(quarter, 0) + 1
            missing_downs[down] = missing_downs.get(down, 0) + 1
    
    print(f"\n📊 Missing yard line by play type:")
    for play_type, count in sorted(missing_play_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {play_type}: {count}")
    
    print(f"\n📊 Missing yard line by quarter:")
    for quarter, count in sorted(missing_quarters.items()):
        print(f"  Q{quarter}: {count}")
    
    print(f"\n📊 Missing yard line by down:")
    for down, count in sorted(missing_downs.items()):
        print(f"  {down}: {count}")
    
    # Check if we can derive yard line from other fields
    print(f"\n🔍 Checking for derivable yard line data...")
    
    # Look for plays with yardsToGoal but no yardline
    yards_to_goal_available = 0
    for play in plays:
        if play.get('yardsToGoal') and not play.get('yardline'):
            yards_to_goal_available += 1
    
    print(f"  Plays with yardsToGoal but no yardline: {yards_to_goal_available}")
    
    if yards_to_goal_available > 0:
        print(f"  ✅ We can derive yard line from yardsToGoal!")
        print(f"  Formula: Yard line = 100 - yardsToGoal")
        
        # Show examples
        print(f"\n📋 Examples of derivable yard lines:")
        count = 0
        for play in plays:
            if play.get('yardsToGoal') and not play.get('yardline') and count < 3:
                yards_to_goal = play.get('yardsToGoal')
                derived_yard_line = 100 - yards_to_goal
                print(f"  Play {play.get('playNumber', 'N/A')}: {play.get('playText', '')[:50]}...")
                print(f"    Yards to goal: {yards_to_goal}")
                print(f"    Derived yard line: {derived_yard_line}")
                print()
                count += 1
    
    # Check for other potential sources
    print(f"\n🔍 Checking for other yard line sources...")
    
    # Look for plays with start/end positions
    start_positions = set()
    end_positions = set()
    
    for play in plays:
        # Check if there are any position-related fields
        for key, value in play.items():
            if 'start' in key.lower() and value:
                start_positions.add(f"{key}: {value}")
            if 'end' in key.lower() and value:
                end_positions.add(f"{key}: {value}")
    
    if start_positions:
        print(f"  Start position fields found: {list(start_positions)[:5]}")
    if end_positions:
        print(f"  End position fields found: {list(end_positions)[:5]}")
    
    return plays

if __name__ == "__main__":
    analyze_cfbd_yard_line()
