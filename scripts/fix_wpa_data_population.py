#!/usr/bin/env python3
"""
Fix WPA data population in CFBD table
"""

import json
import re

def fix_wpa_data_population():
    """Fix WPA data population in CFBD table"""
    
    print("🔍 Fixing WPA data population in CFBD table...")
    
    # Load win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        win_prob_data = json.load(f)
    
    # Calculate WPA for each play
    wpa_data = {}
    for i, entry in enumerate(win_prob_data):
        if i == 0:
            wpa = 0.0
        else:
            wpa = entry['home_win_probability'] - win_prob_data[i-1]['home_win_probability']
        
        wpa_data[entry['play_number']] = {
            'wpa': wpa,
            'wpa_percentage': wpa * 100
        }
    
    print(f"📈 Calculated WPA for {len(wpa_data)} plays")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Find CFBD table rows with the correct pattern
    # Look for rows that start with <td class="play-number">
    cfbd_row_pattern = r'(<tr>\s*<td class="play-number">(\d+)</td>.*?</tr>)'
    
    def add_wpa_to_cfbd_row(match):
        full_row = match.group(1)
        play_num = int(match.group(2))
        
        # Find matching WPA entry
        if play_num in wpa_data:
            wpa_entry = wpa_data[play_num]
            wpa_value = f"{wpa_entry['wpa_percentage']:+.1f}%"
            
            # Color code based on WPA value
            if wpa_entry['wpa'] > 0.05:  # +5% or more
                wpa_cell = f'<td style="background-color: #d4edda; color: #155724; font-weight: bold;">{wpa_value}</td>'
            elif wpa_entry['wpa'] < -0.05:  # -5% or less
                wpa_cell = f'<td style="background-color: #f8d7da; color: #721c24; font-weight: bold;">{wpa_value}</td>'
            else:  # Small change
                wpa_cell = f'<td>{wpa_value}</td>'
            
            new_row = full_row.replace('</tr>', wpa_cell + '</tr>')
            return new_row
        else:
            # No matching entry found, add empty cell
            new_row = full_row.replace('</tr>', '<td>-</td></tr>')
            return new_row
    
    # Apply the transformation
    html_content = re.sub(cfbd_row_pattern, add_wpa_to_cfbd_row, html_content)
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Fixed WPA data population in CFBD table")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Show some examples of the WPA data
    print(f"\n📊 WPA Data Examples:")
    for play_num in sorted(wpa_data.keys())[:5]:
        wpa_entry = wpa_data[play_num]
        print(f"Play {play_num}: {wpa_entry['wpa_percentage']:+.1f}%")

if __name__ == "__main__":
    fix_wpa_data_population()
