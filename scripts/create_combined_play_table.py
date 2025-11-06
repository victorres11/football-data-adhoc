#!/usr/bin/env python3
"""
Create combined play table with ESPN and CFBD data side-by-side
"""

import json

def create_combined_play_table():
    """Create combined play table with ESPN and CFBD data side-by-side"""
    
    print("🔍 Creating combined play table with ESPN and CFBD data...")
    
    # Load aligned ESPN data (159 plays)
    with open('espn_reconstructed_plays_401752873.json', 'r') as f:
        espn_data = json.load(f)
    
    # Remove first play to align with CFBD
    espn_data_aligned = espn_data[1:]  # Skip first play
    
    # Load CFBD data
    with open('cfbd_pbp_with_wpa_401752873.json', 'r') as f:
        cfbd_data = json.load(f)
    
    print(f"📊 ESPN plays (aligned): {len(espn_data_aligned)}")
    print(f"📊 CFBD plays: {len(cfbd_data)}")
    
    # Create HTML with combined table
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Combined Play Data: ESPN vs CFBD - Game 401752873</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .table-wrapper {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 30px;
        }}
        .table-header {{
            padding: 15px;
            font-weight: bold;
            font-size: 18px;
            text-align: center;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }}
        .table-container {{
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        th {{
            background-color: #f8f9fa;
            padding: 8px;
            text-align: left;
            border: 1px solid #dee2e6;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        td {{
            padding: 4px;
            border: 1px solid #dee2e6;
            vertical-align: top;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e9ecef;
        }}
        .play-number {{
            font-weight: bold;
            text-align: center;
            background-color: #e3f2fd;
        }}
        .espn-section {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        .cfbd-section {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }}
        .wpa-positive {{
            background-color: #d4edda;
            color: #155724;
            font-weight: bold;
        }}
        .wpa-negative {{
            background-color: #f8d7da;
            color: #721c24;
            font-weight: bold;
        }}
        .wpa-neutral {{
            background-color: #f8f9fa;
            color: #495057;
        }}
        .play-text {{
            max-width: 150px;
            word-wrap: break-word;
        }}
        .legend {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            justify-content: center;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }}
        .espn-legend {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        .cfbd-legend {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Combined Play Data: ESPN vs CFBD</h1>
        <h2>Michigan vs Washington - Game ID: 401752873</h2>
        <p>All 159 plays with ESPN and CFBD data side-by-side</p>
    </div>
    
    <div class="legend">
        <div class="legend-item espn-legend">
            <span>📺 ESPN Data</span>
        </div>
        <div class="legend-item cfbd-legend">
            <span>📊 CFBD Data</span>
        </div>
    </div>
    
    <div class="table-wrapper">
        <div class="table-header">
            📊 Combined Play Data (159 Plays)
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Play</th>
                        <th colspan="4" class="espn-section">📺 ESPN Data</th>
                        <th colspan="4" class="cfbd-section">📊 CFBD Data</th>
                    </tr>
                    <tr>
                        <th>#</th>
                        <th class="espn-section">Text</th>
                        <th class="espn-section">Clock</th>
                        <th class="espn-section">Win Prob</th>
                        <th class="espn-section">WPA</th>
                        <th class="cfbd-section">Text</th>
                        <th class="cfbd-section">Clock</th>
                        <th class="cfbd-section">Win Prob</th>
                        <th class="cfbd-section">WPA</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add combined table rows
    for i in range(len(espn_data_aligned)):
        espn_play = espn_data_aligned[i]
        cfbd_play = cfbd_data[i]
        
        # ESPN data
        espn_text = espn_play.get('text', '')
        espn_clock = espn_play.get('clock', {})
        espn_win_prob = espn_play.get('winProbability', {})
        espn_wpa = espn_play.get('wpa', {})
        
        # CFBD data
        cfbd_text = cfbd_play.get('play_text', '')
        cfbd_clock = cfbd_play.get('clock', '')
        cfbd_wpa = cfbd_play.get('cfbd_wpa', {})
        
        # Format WPA with color coding for ESPN
        espn_wpa_value = espn_wpa.get('wpa_percentage', 0)
        if espn_wpa_value > 5:
            espn_wpa_class = 'wpa-positive'
        elif espn_wpa_value < -5:
            espn_wpa_class = 'wpa-negative'
        else:
            espn_wpa_class = 'wpa-neutral'
        
        # Format WPA with color coding for CFBD
        cfbd_wpa_value = cfbd_wpa.get('wpa_percentage', 0)
        if cfbd_wpa_value > 5:
            cfbd_wpa_class = 'wpa-positive'
        elif cfbd_wpa_value < -5:
            cfbd_wpa_class = 'wpa-negative'
        else:
            cfbd_wpa_class = 'wpa-neutral'
        
        html_content += f"""
                    <tr>
                        <td class="play-number">{i+1}</td>
                        <td class="espn-section play-text">{espn_text[:80]}{'...' if len(espn_text) > 80 else ''}</td>
                        <td class="espn-section">{espn_clock.get('displayValue', '')}</td>
                        <td class="espn-section">{espn_win_prob.get('homeWinPercentage', 0):.1f}%</td>
                        <td class="espn-section {espn_wpa_class}">{espn_wpa_value:+.1f}%</td>
                        <td class="cfbd-section play-text">{cfbd_text[:80]}{'...' if len(cfbd_text) > 80 else ''}</td>
                        <td class="cfbd-section">{cfbd_clock}</td>
                        <td class="cfbd-section">{cfbd_wpa.get('home_win_probability', 0):.1f}%</td>
                        <td class="cfbd-section {cfbd_wpa_class}">{cfbd_wpa_value:+.1f}%</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background-color: #e9ecef; border-radius: 8px;">
        <h3>📈 Data Legend</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h4>📺 ESPN Data (Yellow Highlight)</h4>
                <ul>
                    <li><strong>Text:</strong> Play description from ESPN</li>
                    <li><strong>Clock:</strong> Game clock from ESPN</li>
                    <li><strong>Win Prob:</strong> ESPN's win probability calculation</li>
                    <li><strong>WPA:</strong> ESPN's Win Probability Added</li>
                </ul>
            </div>
            <div>
                <h4>📊 CFBD Data (Blue Highlight)</h4>
                <ul>
                    <li><strong>Text:</strong> Play description from CFBD</li>
                    <li><strong>Clock:</strong> Game clock from CFBD</li>
                    <li><strong>Win Prob:</strong> CFBD's win probability calculation</li>
                    <li><strong>WPA:</strong> CFBD's Win Probability Added</li>
                </ul>
            </div>
        </div>
        <div style="margin-top: 15px;">
            <h4>🎨 WPA Color Coding</h4>
            <ul>
                <li><span style="background-color: #d4edda; color: #155724; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Green</span> - Positive WPA (+5% or more)</li>
                <li><span style="background-color: #f8d7da; color: #721c24; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Red</span> - Negative WPA (-5% or less)</li>
                <li><span style="background-color: #f8f9fa; color: #495057; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Gray</span> - Neutral WPA (-5% to +5%)</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    with open('combined_play_table_401752873.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created combined play table")
    print("📄 File: combined_play_table_401752873.html")
    
    # Show summary
    print(f"\n📊 Combined Table Summary:")
    print(f"  Total plays: 159")
    print(f"  ESPN data: Yellow highlighted columns")
    print(f"  CFBD data: Blue highlighted columns")
    print(f"  Side-by-side comparison of same game from both sources")

if __name__ == "__main__":
    create_combined_play_table()
