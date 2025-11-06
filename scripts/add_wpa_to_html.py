#!/usr/bin/env python3
"""
Add WPA (Win Probability Added) to the HTML page
"""

import json
import re

def add_wpa_to_html():
    """Add WPA data to the HTML page"""
    
    print("🔍 Adding WPA (Win Probability Added) to HTML page...")
    
    # Load win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        win_prob_data = json.load(f)
    
    print(f"📊 Loaded {len(win_prob_data)} win probability entries")
    
    # Calculate WPA for each play
    wpa_data = []
    for i, entry in enumerate(win_prob_data):
        if i == 0:
            # First play has no previous play to compare to
            wpa = 0.0
        else:
            # WPA = current win prob - previous win prob
            wpa = entry['home_win_probability'] - win_prob_data[i-1]['home_win_probability']
        
        wpa_data.append({
            'play_number': entry['play_number'],
            'play_id': entry['play_id'],
            'play_text': entry['play_text'],
            'home_win_probability': entry['home_win_probability'],
            'wpa': wpa,
            'wpa_percentage': wpa * 100  # Convert to percentage
        })
    
    print(f"📈 Calculated WPA for {len(wpa_data)} plays")
    
    # Load existing HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Add WPA column to CFBD table header
    cfbd_header_pattern = r'(<th>Play</th>\s*<th>Drive</th>\s*<th>Yard Line</th>\s*<th>Down</th>\s*<th>Distance</th>\s*<th>Play Text</th>\s*<th>Yards</th>\s*<th>PPA</th>\s*<th>Win Prob</th>)'
    new_cfbd_header = r'\1<th>WPA</th>'
    html_content = re.sub(cfbd_header_pattern, new_cfbd_header, html_content)
    
    # Find CFBD table rows and add WPA data
    cfbd_row_pattern = r'(<tr>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*</tr>)'
    
    def add_wpa_to_row(match):
        full_row = match.group(1)
        play_num = int(match.group(2))
        
        # Find matching WPA entry
        matching_wpa = None
        for wpa_entry in wpa_data:
            if wpa_entry['play_number'] == play_num:
                matching_wpa = wpa_entry
                break
        
        if matching_wpa:
            wpa_value = f"{matching_wpa['wpa_percentage']:+.1f}%"
            # Color code based on WPA value
            if matching_wpa['wpa'] > 0.05:  # +5% or more
                wpa_cell = f'<td style="background-color: #d4edda; color: #155724;">{wpa_value}</td>'
            elif matching_wpa['wpa'] < -0.05:  # -5% or less
                wpa_cell = f'<td style="background-color: #f8d7da; color: #721c24;">{wpa_value}</td>'
            else:  # Small change
                wpa_cell = f'<td>{wpa_value}</td>'
            
            new_row = full_row.replace('</tr>', wpa_cell + '</tr>')
            return new_row
        else:
            # No matching entry found, add empty cell
            new_row = full_row.replace('</tr>', '<td>-</td></tr>')
            return new_row
    
    # Apply the transformation
    html_content = re.sub(cfbd_row_pattern, add_wpa_to_row, html_content)
    
    # Add WPA analysis section
    wpa_analysis = """
    <div style="margin-top: 30px; padding: 20px; background-color: #e9ecef; border-radius: 8px;">
        <h3>📈 WPA (Win Probability Added) Analysis</h3>
        <p><strong>WPA</strong> measures how much each play changed the win probability. Positive values help Michigan, negative values help Washington.</p>
        
        <h4>Biggest WPA Plays:</h4>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <tr style="background-color: #f8f9fa;">
                <th style="border: 1px solid #dee2e6; padding: 8px;">Play</th>
                <th style="border: 1px solid #dee2e6; padding: 8px;">WPA</th>
                <th style="border: 1px solid #dee2e6; padding: 8px;">Play Text</th>
            </tr>
    """
    
    # Sort WPA data by absolute value to find biggest swings
    sorted_wpa = sorted(wpa_data, key=lambda x: abs(x['wpa']), reverse=True)
    
    # Add top 10 biggest WPA plays
    for i, entry in enumerate(sorted_wpa[:10]):
        if entry['wpa'] != 0:  # Skip plays with no WPA change
            wpa_color = "#d4edda" if entry['wpa'] > 0 else "#f8d7da"
            wpa_text_color = "#155724" if entry['wpa'] > 0 else "#721c24"
            wpa_analysis += f"""
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 8px;">{entry['play_number']}</td>
                <td style="border: 1px solid #dee2e6; padding: 8px; background-color: {wpa_color}; color: {wpa_text_color}; font-weight: bold;">{entry['wpa_percentage']:+.1f}%</td>
                <td style="border: 1px solid #dee2e6; padding: 8px;">{entry['play_text']}</td>
            </tr>
            """
    
    wpa_analysis += """
        </table>
        
        <h4>WPA Summary:</h4>
        <ul>
            <li><strong>Total WPA:</strong> {:.1f}% (Michigan's net win probability change)</li>
            <li><strong>Biggest Positive WPA:</strong> {:.1f}% (Play {})</li>
            <li><strong>Biggest Negative WPA:</strong> {:.1f}% (Play {})</li>
            <li><strong>Average WPA:</strong> {:.2f}% per play</li>
        </ul>
        
        <p><em>Note: WPA values are color-coded in the table above. Green indicates positive WPA for Michigan, red indicates negative WPA.</em></p>
    </div>
    """.format(
        sum(entry['wpa'] for entry in wpa_data) * 100,
        max(entry['wpa'] for entry in wpa_data) * 100,
        max(wpa_data, key=lambda x: x['wpa'])['play_number'],
        min(entry['wpa'] for entry in wpa_data) * 100,
        min(wpa_data, key=lambda x: x['wpa'])['play_number'],
        (sum(entry['wpa'] for entry in wpa_data) / len(wpa_data)) * 100
    )
    
    # Insert the WPA analysis section before the closing body tag
    html_content = html_content.replace('</body>', wpa_analysis + '</body>')
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Added WPA data to HTML page")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Also save WPA data to JSON for reference
    with open('cfbd_wpa_data_401752873.json', 'w') as f:
        json.dump(wpa_data, f, indent=2)
    
    print("💾 Saved WPA data to cfbd_wpa_data_401752873.json")

if __name__ == "__main__":
    add_wpa_to_html()
