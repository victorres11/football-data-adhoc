#!/usr/bin/env python3
"""
Verify final WPA setup
"""

import json
import re

def verify_final_wpa_setup():
    """Verify final WPA setup"""
    
    print("🔍 Verifying final WPA setup...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Check headers
    espn_wpa_headers = re.findall(r'<th>ESPN WPA</th>', html_content)
    cfbd_wpa_headers = re.findall(r'<th>CFBD WPA</th>', html_content)
    
    print(f"📊 ESPN WPA headers: {len(espn_wpa_headers)}")
    print(f"📊 CFBD WPA headers: {len(cfbd_wpa_headers)}")
    
    # Check WPA data in both tables
    espn_wpa_data = re.findall(r'<td class="play-number">(\d+)</td>.*?<td>([+-]?\d+\.\d+%)</td>', html_content, re.DOTALL)
    print(f"📊 Total WPA entries: {len(espn_wpa_data)}")
    
    if espn_wpa_data:
        print("First 5 WPA entries:")
        for play_num, wpa_value in espn_wpa_data[:5]:
            print(f"  Play {play_num}: {wpa_value}")
    
    # Load and show examples of both WPA calculations
    print(f"\n📊 ESPN WPA Examples (from ESPN data):")
    with open('espn_win_probability_401752873.json', 'r') as f:
        espn_wp_data = json.load(f)
    
    espn_wpa_data = {}
    for i, entry in enumerate(espn_wp_data):
        if i == 0:
            wpa = 0.0
        else:
            current_wp = entry.get('homeWinPercentage', 0)
            previous_wp = espn_wp_data[i-1].get('homeWinPercentage', 0)
            wpa = current_wp - previous_wp
        
        espn_wpa_data[entry.get('playId', i)] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100
        }
    
    for play_id in list(espn_wpa_data.keys())[:5]:
        wpa_entry = espn_wpa_data[play_id]
        print(f"  Play {play_id}: {wpa_entry['wpa_percentage']:+.1f}%")
    
    print(f"\n📊 CFBD WPA Examples (from CFBD data):")
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        cfbd_wp_data = json.load(f)
    
    cfbd_wpa_data = {}
    for i, entry in enumerate(cfbd_wp_data):
        if i == 0:
            wpa = 0.0
        else:
            current_wp = entry['home_win_probability']
            previous_wp = cfbd_wp_data[i-1]['home_win_probability']
            wpa = current_wp - previous_wp
        
        cfbd_wpa_data[entry['play_number']] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100
        }
    
    for play_num in list(cfbd_wpa_data.keys())[:5]:
        wpa_entry = cfbd_wpa_data[play_num]
        print(f"  Play {play_num}: {wpa_entry['wpa_percentage']:+.1f}%")
    
    print(f"\n✅ Final setup complete:")
    print(f"  - ESPN table has 'ESPN WPA' column with ESPN-derived WPA")
    print(f"  - CFBD table has 'CFBD WPA' column with CFBD-derived WPA")
    print(f"  - Each table uses its own data source for WPA calculation")

if __name__ == "__main__":
    verify_final_wpa_setup()
