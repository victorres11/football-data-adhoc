#!/usr/bin/env python3
"""
Verify ESPN WPA data is working
"""

import re

def verify_espn_wpa():
    """Verify ESPN WPA data is working"""
    
    print("🔍 Verifying ESPN WPA data...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Check for WPA headers
    wpa_headers = re.findall(r'<th>WPA</th>', html_content)
    print(f"📊 Found {len(wpa_headers)} WPA headers")
    
    # Check for WPA data in ESPN table
    espn_wpa_data = re.findall(r'<td class="play-number">(\d+)</td>.*?<td>([+-]?\d+\.\d+%)</td>', html_content, re.DOTALL)
    print(f"📊 Found {len(espn_wpa_data)} ESPN WPA entries")
    
    if espn_wpa_data:
        print("First 5 ESPN WPA entries:")
        for play_num, wpa_value in espn_wpa_data[:5]:
            print(f"  Play {play_num}: {wpa_value}")
    
    # Check for WPA data in CFBD table
    cfbd_wpa_data = re.findall(r'<td class="play-number">(\d+)</td>.*?<td>([+-]?\d+\.\d+%)</td>', html_content, re.DOTALL)
    print(f"📊 Found {len(cfbd_wpa_data)} CFBD WPA entries")
    
    if cfbd_wpa_data:
        print("First 5 CFBD WPA entries:")
        for play_num, wpa_value in cfbd_wpa_data[:5]:
            print(f"  Play {play_num}: {wpa_value}")
    
    # Check total WPA values
    all_wpa_values = re.findall(r'<td[^>]*>([+-]?\d+\.\d+%)</td>', html_content)
    print(f"📊 Total WPA values found: {len(all_wpa_values)}")
    
    if all_wpa_values:
        print("First 10 WPA values:")
        for wpa_value in all_wpa_values[:10]:
            print(f"  {wpa_value}")

if __name__ == "__main__":
    verify_espn_wpa()
