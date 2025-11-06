#!/usr/bin/env python3
"""
Add WPA data using a simpler approach
"""

import json
import re

def add_wpa_simple():
    """Add WPA data using a simpler approach"""
    
    print("🔍 Adding WPA data using simpler approach...")
    
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
    
    # Find all CFBD table rows and add WPA data
    # Look for the pattern: <td class="play-number">NUMBER</td> ... </tr>
    def add_wpa_to_row(match):
        full_row = match.group(0)
        play_num = int(match.group(1))
        
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
            
            # Add WPA cell before the closing </tr>
            new_row = full_row.replace('</tr>', wpa_cell + '</tr>')
            return new_row
        else:
            # No matching entry found, add empty cell
            new_row = full_row.replace('</tr>', '<td>-</td></tr>')
            return new_row
    
    # Apply the transformation to all CFBD rows
    # Look for rows that start with <td class="play-number"> and end with </tr>
    cfbd_row_pattern = r'<tr>\s*<td class="play-number">(\d+)</td>.*?</tr>'
    html_content = re.sub(cfbd_row_pattern, add_wpa_to_row, html_content, flags=re.DOTALL)
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Added WPA data to CFBD table rows")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Verify the fix
    print(f"\n📊 Verifying WPA data...")
    
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
    add_wpa_simple()
