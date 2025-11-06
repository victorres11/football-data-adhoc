#!/usr/bin/env python3
"""
Create comprehensive ESPN vs CFBD comparison for game 401752873 - FIXED VERSION
"""

import json
import os
from datetime import datetime

def load_espn_data():
    """Load ESPN data for game 401752873"""
    espn_file = 'data/game_401752873/complete_game_data.json'
    if os.path.exists(espn_file):
        with open(espn_file, 'r') as f:
            return json.load(f)
    return None

def load_cfbd_data():
    """Load CFBD data for game 401752873"""
    cfbd_file = 'cfbd_plays_401752873_filtered.json'
    if os.path.exists(cfbd_file):
        with open(cfbd_file, 'r') as f:
            return json.load(f)
    return None

def extract_espn_plays(espn_data):
    """Extract plays from ESPN data - FIXED to use plays.items (160 plays)"""
    plays = []
    
    # Use the direct plays.items array (160 plays) instead of drives structure (159 plays)
    if 'plays' in espn_data and 'items' in espn_data['plays']:
        for play in espn_data['plays']['items']:
            play_data = {
                'play_number': len(plays) + 1,
                'quarter': play.get('period', {}).get('displayValue', ''),
                'time': play.get('clock', {}).get('displayValue', ''),
                'down_distance': f"{play.get('down', '')} & {play.get('distance', '')}",
                'yard_line': play.get('start', {}).get('yardLine', ''),
                'play_text': play.get('text', ''),
                'offense': play.get('type', {}).get('text', ''),
                'defense': play.get('type', {}).get('text', ''),
                'yards_gained': play.get('statYardage', ''),
                'play_type': play.get('type', {}).get('text', ''),
                'score_home': play.get('homeScore', ''),
                'score_away': play.get('awayScore', ''),
                'win_prob_home': play.get('winprobability', {}).get('homeWinPercentage', ''),
                'win_prob_away': play.get('winprobability', {}).get('awayWinPercentage', ''),
                'play_id': play.get('id', ''),
                'drive_id': play.get('driveId', ''),
                'raw_data': play
            }
            plays.append(play_data)
    
    return plays

def extract_cfbd_plays(cfbd_data):
    """Extract plays from CFBD data"""
    plays = []
    
    for play in cfbd_data:
        play_data = {
            'play_number': len(plays) + 1,
            'quarter': f"Q{play.get('period', '')}",
            'time': f"{play.get('clock', {}).get('minutes', '')}:{play.get('clock', {}).get('seconds', '')}",
            'down_distance': f"{play.get('down', '')} & {play.get('distance', '')}",
            'yard_line': play.get('yardLine', ''),
            'play_text': play.get('playText', ''),
            'offense': play.get('offense', ''),
            'defense': play.get('defense', ''),
            'yards_gained': play.get('yardsGained', ''),
            'play_type': play.get('playType', ''),
            'score_home': play.get('homeScore', ''),
            'score_away': play.get('awayScore', ''),
            'win_prob_home': play.get('homeWinProbability', ''),
            'win_prob_away': play.get('awayWinProbability', ''),
            'play_id': play.get('id', ''),
            'game_id': play.get('gameId', ''),
            'ppa': play.get('ppa', ''),
            'raw_data': play
        }
        plays.append(play_data)
    
    return plays

def create_comparison_html(espn_plays, cfbd_plays):
    """Create comprehensive HTML comparison"""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESPN vs CFBD Data Comparison - Michigan vs Washington (401752873) - FIXED</title>
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
            .summary {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
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
            .comparison-table {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .table-header {{
                background: #2c3e50;
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 18px;
                font-weight: bold;
            }}
            .table-container {{
                overflow-x: auto;
                max-height: 80vh;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                vertical-align: top;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            .espn-column {{
                background-color: #e3f2fd;
            }}
            .cfbd-column {{
                background-color: #f3e5f5;
            }}
            .play-number {{
                text-align: center;
                font-weight: bold;
                background-color: #f0f0f0;
            }}
            .play-text {{
                max-width: 300px;
                word-wrap: break-word;
            }}
            .score {{
                text-align: center;
                font-weight: bold;
            }}
            .win-prob {{
                text-align: center;
                font-size: 11px;
            }}
            .raw-data {{
                max-width: 200px;
                word-wrap: break-word;
                font-size: 10px;
                color: #666;
            }}
            .fix-notice {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                color: #856404;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏈 ESPN vs CFBD Data Comparison - FIXED VERSION</h1>
            <h2>Michigan vs Washington - Game ID: 401752873</h2>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="fix-notice">
            <strong>🔧 FIXED:</strong> Now using ESPN's direct <code>plays.items</code> array (160 plays) instead of the drives structure (159 plays). 
            This gives us the correct play count comparison: ESPN 160 vs CFBD 159.
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>📺 ESPN Data (FIXED)</h3>
                <p><strong>Total Plays:</strong> {len(espn_plays)}</p>
                <p><strong>Data Source:</strong> ESPN API - plays.items</p>
                <p><strong>Data Structure:</strong> Direct plays array</p>
                <p><strong>Win Probability:</strong> Available</p>
                <p><strong>Play Details:</strong> Rich play descriptions</p>
            </div>
            <div class="summary-card">
                <h3>📊 CFBD Data</h3>
                <p><strong>Total Plays:</strong> {len(cfbd_plays)}</p>
                <p><strong>Data Source:</strong> CollegeFootballData.com API</p>
                <p><strong>Data Structure:</strong> Flat array</p>
                <p><strong>Win Probability:</strong> Available</p>
                <p><strong>Play Details:</strong> PPA, advanced metrics</p>
            </div>
        </div>
        
        <div class="comparison-table">
            <div class="table-header">
                📋 Side-by-Side Play Comparison (ESPN 160 vs CFBD 159)
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th rowspan="2">Play #</th>
                            <th colspan="2">Quarter</th>
                            <th colspan="2">Time</th>
                            <th colspan="2">Down & Distance</th>
                            <th colspan="2">Yard Line</th>
                            <th colspan="2">Play Description</th>
                            <th colspan="2">Offense</th>
                            <th colspan="2">Defense</th>
                            <th colspan="2">Yards Gained</th>
                            <th colspan="2">Score (H-A)</th>
                            <th colspan="2">Win Prob (H-A)</th>
                            <th colspan="2">Play ID</th>
                            <th colspan="2">Raw Data</th>
                        </tr>
                        <tr>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                            <th class="espn-column">ESPN</th>
                            <th class="cfbd-column">CFBD</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Add plays data
    max_plays = max(len(espn_plays), len(cfbd_plays))
    
    for i in range(max_plays):
        espn_play = espn_plays[i] if i < len(espn_plays) else {}
        cfbd_play = cfbd_plays[i] if i < len(cfbd_plays) else {}
        
        html += f"""
                        <tr>
                            <td class="play-number">{i + 1}</td>
                            <td class="espn-column">{espn_play.get('quarter', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('quarter', '')}</td>
                            <td class="espn-column">{espn_play.get('time', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('time', '')}</td>
                            <td class="espn-column">{espn_play.get('down_distance', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('down_distance', '')}</td>
                            <td class="espn-column">{espn_play.get('yard_line', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('yard_line', '')}</td>
                            <td class="espn-column play-text">{espn_play.get('play_text', '')}</td>
                            <td class="cfbd-column play-text">{cfbd_play.get('play_text', '')}</td>
                            <td class="espn-column">{espn_play.get('offense', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('offense', '')}</td>
                            <td class="espn-column">{espn_play.get('defense', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('defense', '')}</td>
                            <td class="espn-column">{espn_play.get('yards_gained', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('yards_gained', '')}</td>
                            <td class="espn-column score">{espn_play.get('score_home', '')}-{espn_play.get('score_away', '')}</td>
                            <td class="cfbd-column score">{cfbd_play.get('score_home', '')}-{cfbd_play.get('score_away', '')}</td>
                            <td class="espn-column win-prob">{espn_play.get('win_prob_home', '')}</td>
                            <td class="cfbd-column win-prob">{cfbd_play.get('win_prob_home', '')}</td>
                            <td class="espn-column">{espn_play.get('play_id', '')}</td>
                            <td class="cfbd-column">{cfbd_play.get('play_id', '')}</td>
                            <td class="espn-column raw-data">{str(espn_play.get('raw_data', {}))[:100]}...</td>
                            <td class="cfbd-column raw-data">{str(cfbd_play.get('raw_data', {}))[:100]}...</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    """Main function to create comparison"""
    print("Creating ESPN vs CFBD comparison for game 401752873 - FIXED VERSION...")
    
    # Load data
    espn_data = load_espn_data()
    cfbd_data = load_cfbd_data()
    
    if not espn_data:
        print("❌ ESPN data not found")
        return
    
    if not cfbd_data:
        print("❌ CFBD data not found")
        return
    
    print(f"✅ Loaded ESPN data")
    print(f"✅ Loaded CFBD data")
    
    # Extract plays
    espn_plays = extract_espn_plays(espn_data)
    cfbd_plays = extract_cfbd_plays(cfbd_data)
    
    print(f"📊 ESPN plays: {len(espn_plays)} (FIXED - using plays.items)")
    print(f"📊 CFBD plays: {len(cfbd_plays)}")
    
    # Create HTML
    html = create_comparison_html(espn_plays, cfbd_plays)
    
    # Save HTML
    output_file = 'espn_cfbd_comparison_401752873_FIXED.html'
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ FIXED comparison saved to: {output_file}")
    print(f"🌐 Open in browser to view the comparison")

if __name__ == "__main__":
    main()
