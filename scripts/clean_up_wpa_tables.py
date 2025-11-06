#!/usr/bin/env python3
"""
Clean up WPA tables so each has its own WPA derived from its own data source
"""

import json
import re

def clean_up_wpa_tables():
    """Clean up WPA tables so each has its own WPA derived from its own data source"""
    
    print("🔍 Cleaning up WPA tables...")
    
    # Load ESPN win probability data
    with open('espn_win_probability_401752873.json', 'r') as f:
        espn_wp_data = json.load(f)
    
    # Load CFBD win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        cfbd_wp_data = json.load(f)
    
    print(f"📊 ESPN win probability entries: {len(espn_wp_data)}")
    print(f"📊 CFBD win probability entries: {len(cfbd_wp_data)}")
    
    # Calculate ESPN WPA from ESPN data
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
    
    # Calculate CFBD WPA from CFBD data
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
    
    print(f"📈 Calculated ESPN WPA for {len(espn_wpa_data)} plays")
    print(f"📈 Calculated CFBD WPA for {len(cfbd_wpa_data)} plays")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Update ESPN table header to "ESPN WPA"
    espn_header_pattern = r'<th>Raw Data</th><th>ESPN WPA</th>'
    new_espn_header = r'<th>Raw Data</th><th>ESPN WPA</th>'
    html_content = re.sub(espn_header_pattern, new_espn_header, html_content)
    
    # Update CFBD table header to "CFBD WPA"
    cfbd_header_pattern = r'<th>Raw Data</th><th>WPA</th>'
    new_cfbd_header = r'<th>Raw Data</th><th>CFBD WPA</th>'
    html_content = re.sub(cfbd_header_pattern, new_cfbd_header, html_content)
    
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
    
    # Update CFBD table rows with CFBD WPA data
    def add_cfbd_wpa_to_row(match):
        full_row = match.group(0)
        play_num = int(match.group(1))
        
        # Find matching CFBD WPA entry
        if play_num in cfbd_wpa_data:
            wpa_entry = cfbd_wpa_data[play_num]
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
    
    # Apply transformations
    # ESPN rows
    espn_row_pattern = r'<tr>\s*<td class="play-number">(\d+)</td>.*?<td class="raw-data">.*?</td>\s*</tr>'
    html_content = re.sub(espn_row_pattern, add_espn_wpa_to_row, html_content, flags=re.DOTALL)
    
    # CFBD rows
    cfbd_row_pattern = r'<tr>\s*<td class="play-number">(\d+)</td>.*?<td class="raw-data">.*?</td>\s*</tr>'
    html_content = re.sub(cfbd_row_pattern, add_cfbd_wpa_to_row, html_content, flags=re.DOTALL)
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Cleaned up WPA tables")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Show examples of both WPA calculations
    print(f"\n📊 ESPN WPA Examples:")
    for play_id in list(espn_wpa_data.keys())[:5]:
        wpa_entry = espn_wpa_data[play_id]
        print(f"  Play {play_id}: {wpa_entry['wpa_percentage']:+.1f}%")
    
    print(f"\n📊 CFBD WPA Examples:")
    for play_num in list(cfbd_wpa_data.keys())[:5]:
        wpa_entry = cfbd_wpa_data[play_num]
        print(f"  Play {play_num}: {wpa_entry['wpa_percentage']:+.1f}%")
    
    # Verify the fix
    print(f"\n📊 Verifying WPA data...")
    
    # Check for both WPA headers
    espn_wpa_headers = re.findall(r'<th>ESPN WPA</th>', html_content)
    cfbd_wpa_headers = re.findall(r'<th>CFBD WPA</th>', html_content)
    
    print(f"Found {len(espn_wpa_headers)} ESPN WPA headers")
    print(f"Found {len(cfbd_wpa_headers)} CFBD WPA headers")
    
    # Count total WPA values
    wpa_matches = re.findall(r'<td[^>]*>([+-]?\d+\.\d+%)</td>', html_content)
    print(f"Found {len(wpa_matches)} total WPA percentage values")

if __name__ == "__main__":
    clean_up_wpa_tables()
