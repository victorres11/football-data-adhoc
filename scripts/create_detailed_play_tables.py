#!/usr/bin/env python3
"""
Create detailed play tables for ESPN and CFBD data
"""

import json

def create_detailed_play_tables():
    """Create detailed play tables for ESPN and CFBD data"""
    
    print("🔍 Creating detailed play tables...")
    
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
    
    # Create HTML with two detailed tables
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detailed Play Data: ESPN vs CFBD - Game 401752873</title>
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
        .tables-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .table-wrapper {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .table-header {{
            padding: 15px;
            font-weight: bold;
            font-size: 18px;
            text-align: center;
        }}
        .espn-header {{
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
        }}
        .cfbd-header {{
            background: linear-gradient(135deg, #4ecdc4, #44a08d);
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
            font-size: 12px;
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
            padding: 6px;
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
            max-width: 200px;
            word-wrap: break-word;
        }}
        .summary {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin-top: 0;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Detailed Play Data: ESPN vs CFBD</h1>
        <h2>Michigan vs Washington - Game ID: 401752873</h2>
        <p>Complete play-by-play data with WPA analysis for both data sources</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>📺 ESPN Data Summary</h3>
            <p><strong>Total Plays:</strong> {len(espn_data_aligned)}</p>
            <p><strong>Data Source:</strong> ESPN API (reconstructed from win probability)</p>
            <p><strong>WPA Range:</strong> -10.6% to +18.8%</p>
        </div>
        <div class="summary-card">
            <h3>📊 CFBD Data Summary</h3>
            <p><strong>Total Plays:</strong> {len(cfbd_data)}</p>
            <p><strong>Data Source:</strong> CollegeFootballData.com API</p>
            <p><strong>WPA Range:</strong> -4.7% to +3.7%</p>
        </div>
    </div>
    
    <div class="tables-container">
        <!-- ESPN Table -->
        <div class="table-wrapper">
            <div class="table-header espn-header">
                📺 ESPN Play Data (159 Plays)
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Play</th>
                            <th>ID</th>
                            <th>Text</th>
                            <th>Period</th>
                            <th>Clock</th>
                            <th>Team</th>
                            <th>Score</th>
                            <th>Win Prob</th>
                            <th>WPA</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add ESPN table rows
    for i, play in enumerate(espn_data_aligned):
        play_id = play.get('id', '')
        text = play.get('text', '')
        period = play.get('period', {})
        clock = play.get('clock', {})
        team = play.get('team', {})
        away_score = play.get('awayScore', 0)
        home_score = play.get('homeScore', 0)
        win_prob = play.get('winProbability', {})
        wpa = play.get('wpa', {})
        
        # Format WPA with color coding
        wpa_value = wpa.get('wpa_percentage', 0)
        if wpa_value > 5:
            wpa_class = 'wpa-positive'
        elif wpa_value < -5:
            wpa_class = 'wpa-negative'
        else:
            wpa_class = 'wpa-neutral'
        
        html_content += f"""
                        <tr>
                            <td class="play-number">{i+1}</td>
                            <td>{play_id}</td>
                            <td class="play-text">{text[:100]}{'...' if len(text) > 100 else ''}</td>
                            <td>{period.get('number', '')}</td>
                            <td>{clock.get('displayValue', '')}</td>
                            <td>{team.get('name', '')}</td>
                            <td>{away_score}-{home_score}</td>
                            <td>{win_prob.get('homeWinPercentage', 0):.1f}%</td>
                            <td class="{wpa_class}">{wpa_value:+.1f}%</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- CFBD Table -->
        <div class="table-wrapper">
            <div class="table-header cfbd-header">
                📊 CFBD Play Data (159 Plays)
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Play</th>
                            <th>Drive</th>
                            <th>Text</th>
                            <th>Qtr</th>
                            <th>Clock</th>
                            <th>Offense</th>
                            <th>Yards</th>
                            <th>Win Prob</th>
                            <th>WPA</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add CFBD table rows
    for i, play in enumerate(cfbd_data):
        play_number = play.get('play_number', i+1)
        drive_number = play.get('drive_number', '')
        text = play.get('play_text', '')
        quarter = play.get('quarter', '')
        clock = play.get('clock', '')
        offense = play.get('offense', '')
        yards = play.get('yards', '')
        cfbd_wpa = play.get('cfbd_wpa', {})
        
        # Format WPA with color coding
        wpa_value = cfbd_wpa.get('wpa_percentage', 0)
        if wpa_value > 5:
            wpa_class = 'wpa-positive'
        elif wpa_value < -5:
            wpa_class = 'wpa-negative'
        else:
            wpa_class = 'wpa-neutral'
        
        html_content += f"""
                        <tr>
                            <td class="play-number">{play_number}</td>
                            <td>{drive_number}</td>
                            <td class="play-text">{text[:100]}{'...' if len(text) > 100 else ''}</td>
                            <td>{quarter}</td>
                            <td>{clock}</td>
                            <td>{offense}</td>
                            <td>{yards}</td>
                            <td>{cfbd_wpa.get('home_win_probability', 0):.1f}%</td>
                            <td class="{wpa_class}">{wpa_value:+.1f}%</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background-color: #e9ecef; border-radius: 8px;">
        <h3>📈 WPA Color Coding</h3>
        <ul>
            <li><span style="background-color: #d4edda; color: #155724; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Green</span> - Positive WPA (+5% or more)</li>
            <li><span style="background-color: #f8d7da; color: #721c24; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Red</span> - Negative WPA (-5% or less)</li>
            <li><span style="background-color: #f8f9fa; color: #495057; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Gray</span> - Neutral WPA (-5% to +5%)</li>
        </ul>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    with open('detailed_play_tables_401752873.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created detailed play tables")
    print("📄 File: detailed_play_tables_401752873.html")
    
    # Show summary
    print(f"\n📊 Table Summary:")
    print(f"  ESPN plays: {len(espn_data_aligned)}")
    print(f"  CFBD plays: {len(cfbd_data)}")
    print(f"  Both tables show complete play-by-play data with WPA analysis")

if __name__ == "__main__":
    create_detailed_play_tables()
