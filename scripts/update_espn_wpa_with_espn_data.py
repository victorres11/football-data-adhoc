#!/usr/bin/env python3
"""
Update ESPN WPA with ESPN's own win probability data
"""

import json
import re

def update_espn_wpa_with_espn_data():
    """Update ESPN WPA with ESPN's own win probability data"""
    
    print("🔍 Updating ESPN WPA with ESPN's own win probability data...")
    
    # Load ESPN win probability data
    with open('espn_win_probability_401752873.json', 'r') as f:
        espn_wp_data = json.load(f)
    
    print(f"📊 Loaded {len(espn_wp_data)} ESPN win probability entries")
    
    # Calculate ESPN WPA for each play
    espn_wpa_data = {}
    for i, entry in enumerate(espn_wp_data):
        if i == 0:
            wpa = 0.0
        else:
            # ESPN win probability is for home team (Michigan)
            current_wp = entry.get('homeWinPercentage', 0)
            previous_wp = espn_wp_data[i-1].get('homeWinPercentage', 0)
            wpa = current_wp - previous_wp
        
        espn_wpa_data[entry.get('playId', i)] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100
        }
    
    print(f"📈 Calculated ESPN WPA for {len(espn_wpa_data)} plays")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Update ESPN table rows with ESPN WPA data
    def add_espn_wpa_to_row(match):
        full_row = match.group(0)
        play_id = match.group(1)
        
        # Find matching ESPN WPA entry
        if play_id in espn_wpa_data:
            wpa_entry = espn_wpa_data[play_id]
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
    
    print("✅ Updated ESPN WPA with ESPN's own win probability data")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Show some examples of the ESPN WPA data
    print(f"\n📊 ESPN WPA Data Examples:")
    for play_id in list(espn_wpa_data.keys())[:5]:
        wpa_entry = espn_wpa_data[play_id]
        print(f"Play {play_id}: {wpa_entry['wpa_percentage']:+.1f}%")
    
    # Verify the fix
    print(f"\n📊 Verifying ESPN WPA data...")
    
    # Count rows with WPA data
    wpa_count = html_content.count('+') + html_content.count('-')
    print(f"Found {wpa_count} potential WPA values in HTML")
    
    # Look for specific WPA patterns
    wpa_matches = re.findall(r'<td[^>]*>([+-]?\d+\.\d+%)</td>', html_content)
    print(f"Found {len(wpa_matches)} WPA percentage values")
    
    if wpa_matches:
        print("First 5 WPA values:")
        for wpa_value in wpa_matches[:5]:
            print(f"  {wpa_value}")

if __name__ == "__main__":
    update_espn_wpa_with_espn_data()
