#!/usr/bin/env python3
"""
Add WPA data to the ESPN table side
"""

import json
import re

def add_wpa_to_espn_table():
    """Add WPA data to ESPN table"""
    
    print("🔍 Adding WPA data to ESPN table...")
    
    # Load ESPN game data to get win probability data
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    # Extract win probability data from ESPN
    win_prob_data = espn_data.get('winprobability', [])
    print(f"📊 Found {len(win_prob_data)} ESPN win probability entries")
    
    # Calculate WPA for each play
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
    
    print(f"📈 Calculated WPA for {len(wpa_data)} ESPN plays")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Add WPA column to ESPN table header
    # Look for ESPN table header
    espn_header_pattern = r'(<th>Team ID</th>\s*<th>Stat Type</th>\s*<th>Start Yard</th>\s*<th>End Yard</th>\s*<th>Raw Data</th>)'
    new_espn_header = r'\1<th>WPA</th>'
    html_content = re.sub(espn_header_pattern, new_espn_header, html_content)
    
    # Find ESPN table rows and add WPA data
    # Look for ESPN rows (they have different structure than CFBD)
    def add_wpa_to_espn_row(match):
        full_row = match.group(0)
        play_id = match.group(1)
        
        # Find matching WPA entry
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
    # Look for ESPN rows that have play IDs
    espn_row_pattern = r'<tr>\s*<td>(\d+)</td>.*?<td class="raw-data">.*?</td>\s*</tr>'
    html_content = re.sub(espn_row_pattern, add_wpa_to_espn_row, html_content, flags=re.DOTALL)
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Added WPA data to ESPN table")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
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
    
    # Show some examples of the WPA data
    print(f"\n📊 ESPN WPA Data Examples:")
    for play_id in list(wpa_data.keys())[:5]:
        wpa_entry = wpa_data[play_id]
        print(f"Play {play_id}: {wpa_entry['wpa_percentage']:+.1f}%")

if __name__ == "__main__":
    add_wpa_to_espn_table()
