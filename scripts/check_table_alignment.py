#!/usr/bin/env python3
"""
Check table alignment and structure
"""

import re

def check_table_alignment():
    """Check table alignment and structure"""
    
    print("🔍 Checking table alignment and structure...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Check ESPN table structure
    print("📊 ESPN Table Structure:")
    espn_header_match = re.search(r'<thead>.*?</thead>', html_content, re.DOTALL)
    if espn_header_match:
        espn_header = espn_header_match.group(0)
        espn_headers = re.findall(r'<th>(.*?)</th>', espn_header)
        print(f"  Headers: {espn_headers}")
        print(f"  Header count: {len(espn_headers)}")
    
    # Check ESPN table rows
    espn_rows = re.findall(r'<tr>.*?<td class="play-number">1</td>.*?</tr>', html_content, re.DOTALL)
    if espn_rows:
        first_row = espn_rows[0]
        espn_cells = re.findall(r'<td[^>]*>(.*?)</td>', first_row)
        print(f"  First row cells: {len(espn_cells)}")
        print(f"  Last few cells: {espn_cells[-5:]}")
    
    # Check CFBD table structure
    print("\n📊 CFBD Table Structure:")
    cfbd_header_match = re.search(r'<th>#</th>.*?<th>WPA</th>', html_content, re.DOTALL)
    if cfbd_header_match:
        cfbd_header = cfbd_header_match.group(0)
        cfbd_headers = re.findall(r'<th>(.*?)</th>', cfbd_header)
        print(f"  Headers: {cfbd_headers}")
        print(f"  Header count: {len(cfbd_headers)}")
    
    # Check CFBD table rows
    cfbd_rows = re.findall(r'<tr>.*?<td class="play-number">1</td>.*?</tr>', html_content, re.DOTALL)
    if cfbd_rows:
        first_row = cfbd_rows[0]
        cfbd_cells = re.findall(r'<td[^>]*>(.*?)</td>', first_row)
        print(f"  First row cells: {len(cfbd_cells)}")
        print(f"  Last few cells: {cfbd_cells[-5:]}")
    
    # Check if WPA data is properly aligned
    print("\n📊 WPA Data Alignment:")
    wpa_matches = re.findall(r'<td class="play-number">(\d+)</td>.*?<td>([+-]?\d+\.\d+%)</td>', html_content, re.DOTALL)
    print(f"  Found {len(wpa_matches)} WPA entries")
    
    if wpa_matches:
        print("  First 5 WPA entries:")
        for play_num, wpa_value in wpa_matches[:5]:
            print(f"    Play {play_num}: {wpa_value}")

if __name__ == "__main__":
    check_table_alignment()
