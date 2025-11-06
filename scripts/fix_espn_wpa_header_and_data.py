#!/usr/bin/env python3
"""
Fix ESPN WPA header and use ESPN's own win probability data
"""

import json
import re

def fix_espn_wpa_header_and_data():
    """Fix ESPN WPA header and use ESPN's own win probability data"""
    
    print("🔍 Fixing ESPN WPA header and using ESPN's own win probability data...")
    
    # Load ESPN game data to get win probability data
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    # Check if ESPN has win probability data
    print(f"📊 ESPN data keys: {list(espn_data.keys())}")
    
    # Look for win probability in the data
    win_prob_data = None
    if 'winprobability' in espn_data:
        win_prob_data = espn_data['winprobability']
        print(f"📊 Found ESPN winprobability with {len(win_prob_data)} entries")
    else:
        print("❌ No ESPN winprobability data found")
        print("📊 Available keys:", list(espn_data.keys()))
        
        # Check if win probability is in a different location
        for key in espn_data.keys():
            if 'win' in key.lower() or 'prob' in key.lower():
                print(f"📊 Found potential win probability key: {key}")
                if isinstance(espn_data[key], list):
                    print(f"  Length: {len(espn_data[key])}")
                    if espn_data[key]:
                        print(f"  First entry: {espn_data[key][0]}")
                else:
                    print(f"  Type: {type(espn_data[key])}")
    
    # If no ESPN win probability data, we'll need to fetch it
    if not win_prob_data:
        print("📊 ESPN win probability data not available in current data")
        print("📊 Will need to fetch ESPN win probability data separately")
        
        # For now, let's just fix the header and leave the data as is
        # Load HTML
        with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
            html_content = f.read()
        
        # Change the WPA header to "ESPN WPA"
        espn_wpa_header_pattern = r'<th>Raw Data</th><th>WPA</th>'
        new_espn_header = r'<th>Raw Data</th><th>ESPN WPA</th>'
        html_content = re.sub(espn_wpa_header_pattern, new_espn_header, html_content)
        
        # Save updated HTML
        with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
            f.write(html_content)
        
        print("✅ Updated ESPN WPA header to 'ESPN WPA'")
        print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
        print("⚠️  Note: ESPN win probability data not available - will need to fetch separately")
        
        return
    
    # If we have ESPN win probability data, calculate WPA
    wpa_data = {}
    for i, entry in enumerate(win_prob_data):
        if i == 0:
            wpa = 0.0
        else:
            # ESPN win probability is for home team (Michigan)
            current_wp = entry.get('homeWinPercentage', 0) / 100
            previous_wp = win_prob_data[i-1].get('homeWinPercentage', 0) / 100
            wpa = current_wp - previous_wp
        
        wpa_data[entry.get('playId', i)] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100
        }
    
    print(f"📈 Calculated ESPN WPA for {len(wpa_data)} plays")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Change the WPA header to "ESPN WPA"
    espn_wpa_header_pattern = r'<th>Raw Data</th><th>WPA</th>'
    new_espn_header = r'<th>Raw Data</th><th>ESPN WPA</th>'
    html_content = re.sub(espn_wpa_header_pattern, new_espn_header, html_content)
    
    # Update ESPN table rows with ESPN WPA data
    def add_espn_wpa_to_row(match):
        full_row = match.group(0)
        play_id = match.group(1)
        
        # Find matching ESPN WPA entry
        if play_id in wpa_data:
            wpa_entry = wpa_data[play_id]
            wpa_value = f"{wpa_entry['wpa_percentage']:+.1f}%"
            
            # Color code based on WPA value
            if wpa_entry['wpa'] > 0.05:  # +5% or more
                wpa_cell = f'<td style="background-color: #d4edda; color: #155724; font-weight: bold;">{wpa_value}</td>'
            elif wpa_entry['wpa'] < -0.05:  # -5% or less
                wpa_cell = f'<td style="background-color: #f8d7da; color: #721c24; font-weight: bold;">{wpa_value}</td>'
            else:  # Small change
                wpa_cell = f'<td>{wpa_value}</td>'
            
            # Add WPA cell before the closing </tr>
            new_row = full_row.replace('</tr>', wpa_cell + '</tr>')
            return new_row
        else:
            # No matching entry found, add empty cell
            new_row = full_row.replace('</tr>', '<td>-</td></tr>')
            return new_row
    
    # Apply the transformation to ESPN rows
    espn_row_pattern = r'<tr>\s*<td class="play-number">(\d+)</td>.*?<td class="raw-data">.*?</td>\s*</tr>'
    html_content = re.sub(espn_row_pattern, add_espn_wpa_to_row, html_content, flags=re.DOTALL)
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Updated ESPN WPA header and data")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")

if __name__ == "__main__":
    fix_espn_wpa_header_and_data()
