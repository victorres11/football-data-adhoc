#!/usr/bin/env python3
"""
Update the HTML page with CFBD win probability data
"""

import json
import re

def update_html_with_win_probability():
    """Update the HTML page with CFBD win probability data"""
    
    print("🔍 Updating HTML page with CFBD win probability data...")
    
    # Load win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        win_prob_data = json.load(f)
    
    print(f"📊 Loaded {len(win_prob_data)} win probability entries")
    
    # Load existing HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Find the CFBD table section and add win probability column
    # Look for the CFBD table header
    cfbd_header_pattern = r'(<th>Play</th>\s*<th>Drive</th>\s*<th>Yard Line</th>\s*<th>Down</th>\s*<th>Distance</th>\s*<th>Play Text</th>\s*<th>Yards</th>\s*<th>PPA</th>)'
    
    # Add win probability column to header
    new_cfbd_header = r'\1<th>Win Prob</th>'
    html_content = re.sub(cfbd_header_pattern, new_cfbd_header, html_content)
    
    # Create a mapping of play_id to win probability
    win_prob_map = {}
    for entry in win_prob_data:
        win_prob_map[entry['play_id']] = entry
    
    print(f"📋 Created win probability mapping for {len(win_prob_map)} plays")
    
    # Find CFBD table rows and add win probability data
    # Look for CFBD table rows (they have specific structure)
    cfbd_row_pattern = r'(<tr>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*</tr>)'
    
    def add_win_prob_to_row(match):
        full_row = match.group(1)
        play_num = match.group(2)
        drive_num = match.group(3)
        
        # Try to find matching win probability entry
        # Look for entries with matching play_number
        matching_entry = None
        for entry in win_prob_data:
            if entry['play_number'] == int(play_num):
                matching_entry = entry
                break
        
        if matching_entry:
            win_prob = f"{matching_entry['home_win_probability']:.3f}"
            # Insert win probability column before closing </tr>
            new_row = full_row.replace('</tr>', f'<td>{win_prob}</td></tr>')
            return new_row
        else:
            # No matching entry found, add empty cell
            new_row = full_row.replace('</tr>', '<td>-</td></tr>')
            return new_row
    
    # Apply the transformation
    html_content = re.sub(cfbd_row_pattern, add_win_prob_to_row, html_content)
    
    # Add a section showing win probability analysis
    analysis_section = """
    <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
        <h3>📊 CFBD Win Probability Analysis</h3>
        <p><strong>Total Win Probability Entries:</strong> {}</p>
        <p><strong>Game:</strong> Michigan vs Washington (Game ID: 401752873)</p>
        <p><strong>Data Source:</strong> CollegeFootballData.com API</p>
        
        <h4>Win Probability Summary:</h4>
        <ul>
            <li><strong>Starting Win Probability:</strong> {:.1f}% (Michigan)</li>
            <li><strong>Final Win Probability:</strong> {:.1f}% (Michigan)</li>
            <li><strong>Biggest Swing:</strong> {:.1f}% change</li>
        </ul>
        
        <h4>Key Insights:</h4>
        <ul>
            <li>CFBD provides play-by-play win probability data</li>
            <li>Data includes play context (down, distance, yard line)</li>
            <li>Win probability updates after each play</li>
            <li>Can be used for momentum analysis and key play identification</li>
        </ul>
    </div>
    """.format(
        len(win_prob_data),
        win_prob_data[0]['home_win_probability'] * 100 if win_prob_data else 0,
        win_prob_data[-1]['home_win_probability'] * 100 if win_prob_data else 0,
        abs(win_prob_data[-1]['home_win_probability'] - win_prob_data[0]['home_win_probability']) * 100 if win_prob_data else 0
    )
    
    # Insert the analysis section before the closing body tag
    html_content = html_content.replace('</body>', analysis_section + '</body>')
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Updated HTML page with CFBD win probability data")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")

if __name__ == "__main__":
    update_html_with_win_probability()
