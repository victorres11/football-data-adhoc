#!/usr/bin/env python3
"""
Debug CFBD table structure to understand why WPA data isn't showing
"""

import json
import re

def debug_cfbd_table_structure():
    """Debug CFBD table structure"""
    
    print("🔍 Debugging CFBD table structure...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Find CFBD table rows
    cfbd_rows = re.findall(r'<tr>\s*<td>(\d+)</td>.*?</tr>', html_content, re.DOTALL)
    print(f"📊 Found {len(cfbd_rows)} CFBD table rows")
    
    # Show first few rows
    print("\n📋 First 3 CFBD rows:")
    for i, row in enumerate(cfbd_rows[:3]):
        print(f"Row {i+1}: {row}")
    
    # Find the actual table structure
    cfbd_table_pattern = r'<table>.*?<thead>.*?</thead>.*?<tbody>(.*?)</tbody>.*?</table>'
    table_match = re.search(cfbd_table_pattern, html_content, re.DOTALL)
    
    if table_match:
        tbody_content = table_match.group(1)
        print(f"\n📋 CFBD table tbody content length: {len(tbody_content)}")
        
        # Find first few rows in tbody
        rows = re.findall(r'<tr>(.*?)</tr>', tbody_content, re.DOTALL)
        print(f"📊 Found {len(rows)} rows in tbody")
        
        if rows:
            print(f"\n📋 First row structure:")
            first_row = rows[0]
            print(f"Row content: {first_row[:200]}...")
            
            # Count columns in first row
            columns = re.findall(r'<td[^>]*>.*?</td>', first_row)
            print(f"Number of columns: {len(columns)}")
            
            # Show column structure
            for i, col in enumerate(columns[:10]):  # Show first 10 columns
                print(f"Column {i+1}: {col[:50]}...")
    
    # Load win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        win_prob_data = json.load(f)
    
    print(f"\n📈 Win probability data: {len(win_prob_data)} entries")
    print(f"First entry: {win_prob_data[0]}")
    
    # Check if play numbers match
    cfbd_play_numbers = [int(row) for row in cfbd_rows]
    wp_play_numbers = [entry['play_number'] for entry in win_prob_data]
    
    print(f"\n📊 CFBD play numbers: {cfbd_play_numbers[:10]}")
    print(f"📊 WP play numbers: {wp_play_numbers[:10]}")
    
    # Find matching play numbers
    matches = set(cfbd_play_numbers) & set(wp_play_numbers)
    print(f"📊 Matching play numbers: {len(matches)}")
    print(f"📊 Match examples: {sorted(list(matches))[:10]}")

if __name__ == "__main__":
    debug_cfbd_table_structure()
