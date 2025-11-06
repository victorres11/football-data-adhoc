#!/usr/bin/env python3
"""
Fix WPA data in CFBD table rows - final attempt
"""

import json
import re

def fix_wpa_final():
    """Fix WPA data in CFBD table rows"""
    
    print("🔍 Fixing WPA data in CFBD table rows - final attempt...")
    
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
    
    # Find CFBD table rows (skip header row)
    # Look for rows that have <td class="play-number"> followed by a number
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
            
            # Add WPA cell before the closing </tr>
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
    
    print("✅ Fixed WPA data in table rows")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Verify the fix by checking a few rows
    print(f"\n📊 Verifying WPA data in rows...")
    
    # Look for rows with WPA data
    wpa_matches = re.findall(r'<td class="play-number">(\d+)</td>.*?<td>([+-]?\d+\.\d+%)</td>', html_content)
    print(f"Found {len(wpa_matches)} rows with WPA data")
    
    if wpa_matches:
        print("First 5 WPA entries:")
        for play_num, wpa_value in wpa_matches[:5]:
            print(f"Play {play_num}: {wpa_value}")
    else:
        print("❌ No WPA data found in rows")
        
        # Let's check what the actual row structure looks like
        sample_rows = re.findall(r'<td class="play-number">1</td>.*?</tr>', html_content, re.DOTALL)
        if sample_rows:
            print(f"\n📋 Sample row structure:")
            print(f"Row content: {sample_rows[0][:300]}...")

if __name__ == "__main__":
    fix_wpa_final()
