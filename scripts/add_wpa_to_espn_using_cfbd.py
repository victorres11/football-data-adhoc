#!/usr/bin/env python3
"""
Add WPA data to ESPN table using CFBD win probability data
"""

import json
import re

def add_wpa_to_espn_using_cfbd():
    """Add WPA data to ESPN table using CFBD win probability data"""
    
    print("🔍 Adding WPA data to ESPN table using CFBD win probability data...")
    
    # Load CFBD win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        cfbd_wp_data = json.load(f)
    
    # Load ESPN game data to get play IDs
    with open('data/game_401752873/raw_game_data.json', 'r') as f:
        espn_data = json.load(f)
    
    # Get ESPN plays
    espn_plays = espn_data['plays']['items']
    print(f"📊 Found {len(espn_plays)} ESPN plays")
    
    # Create mapping from ESPN play IDs to CFBD play numbers
    espn_to_cfbd_mapping = {}
    for i, espn_play in enumerate(espn_plays):
        espn_play_id = espn_play.get('id')
        # Map ESPN play index to CFBD play number
        espn_to_cfbd_mapping[espn_play_id] = i
    
    print(f"📊 Created mapping for {len(espn_to_cfbd_mapping)} ESPN plays")
    
    # Calculate WPA using CFBD data
    wpa_data = {}
    for i, entry in enumerate(cfbd_wp_data):
        if i == 0:
            wpa = 0.0
        else:
            wpa = entry['home_win_probability'] - cfbd_wp_data[i-1]['home_win_probability']
        
        wpa_data[entry['play_number']] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100
        }
    
    print(f"📈 Calculated WPA for {len(wpa_data)} CFBD plays")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Add WPA column to ESPN table header
    # Look for ESPN table header
    espn_header_pattern = r'(<th>Team ID</th>\s*<th>Stat Type</th>\s*<th>Start Yard</th>\s*<th>End Yard</th>\s*<th>Raw Data</th>)'
    new_espn_header = r'\1<th>WPA</th>'
    html_content = re.sub(espn_header_pattern, new_espn_header, html_content)
    
    # Find ESPN table rows and add WPA data
    def add_wpa_to_espn_row(match):
        full_row = match.group(0)
        play_id = match.group(1)
        
        # Map ESPN play ID to CFBD play number
        cfbd_play_num = espn_to_cfbd_mapping.get(play_id)
        
        if cfbd_play_num is not None and cfbd_play_num in wpa_data:
            wpa_entry = wpa_data[cfbd_play_num]
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
    
    print("✅ Added WPA data to ESPN table using CFBD data")
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
    for play_id in list(espn_to_cfbd_mapping.keys())[:5]:
        cfbd_play_num = espn_to_cfbd_mapping[play_id]
        if cfbd_play_num in wpa_data:
            wpa_entry = wpa_data[cfbd_play_num]
            print(f"ESPN Play {play_id} (CFBD Play {cfbd_play_num}): {wpa_entry['wpa_percentage']:+.1f}%")

if __name__ == "__main__":
    add_wpa_to_espn_using_cfbd()
