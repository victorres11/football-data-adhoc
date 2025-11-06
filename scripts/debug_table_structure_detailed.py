#!/usr/bin/env python3
"""
Debug table structure in detail
"""

import json
import re

def debug_table_structure_detailed():
    """Debug table structure in detail"""
    
    print("🔍 Debugging table structure in detail...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Find the CFBD table section
    cfbd_table_start = html_content.find('<!-- CFBD Table -->')
    if cfbd_table_start == -1:
        print("❌ CFBD Table section not found")
        return
    
    cfbd_table_end = html_content.find('</table>', cfbd_table_start)
    if cfbd_table_end == -1:
        print("❌ CFBD Table end not found")
        return
    
    cfbd_table_section = html_content[cfbd_table_start:cfbd_table_end + 8]
    
    print(f"📊 CFBD table section length: {len(cfbd_table_section)}")
    
    # Find the first few rows
    rows = re.findall(r'<tr>(.*?)</tr>', cfbd_table_section, re.DOTALL)
    print(f"📊 Found {len(rows)} rows in CFBD table")
    
    if rows:
        print(f"\n📋 First row structure:")
        first_row = rows[0]
        print(f"Row content: {first_row[:500]}...")
        
        # Count columns in first row
        columns = re.findall(r'<td[^>]*>.*?</td>', first_row)
        print(f"Number of columns: {len(columns)}")
        
        # Show column structure
        for i, col in enumerate(columns):
            print(f"Column {i+1}: {col[:100]}...")
    
    # Check if WPA column exists
    if '<th>WPA</th>' in cfbd_table_section:
        print("✅ WPA column header found")
    else:
        print("❌ WPA column header not found")
    
    # Check if any rows have WPA data
    wpa_rows = re.findall(r'<tr>.*?<td>([+-]?\d+\.\d+%)</td>.*?</tr>', cfbd_table_section, re.DOTALL)
    print(f"📊 Rows with WPA data: {len(wpa_rows)}")
    
    if wpa_rows:
        print("First WPA row:")
        print(wpa_rows[0][:200] + "...")

if __name__ == "__main__":
    debug_table_structure_detailed()
