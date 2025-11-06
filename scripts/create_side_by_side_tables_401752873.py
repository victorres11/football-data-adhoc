#!/usr/bin/env python3
"""
Create side-by-side tables for ESPN and CFBD data - completely separate
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
    """Extract ALL ESPN play data"""
    plays = []
    
    if 'plays' in espn_data and 'items' in espn_data['plays']:
        for play in espn_data['plays']['items']:
            play_data = {
                'play_number': len(plays) + 1,
                'quarter': play.get('period', {}).get('displayValue', ''),
                'time': play.get('clock', {}).get('displayValue', ''),
                'down': play.get('down', ''),
                'distance': play.get('distance', ''),
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
                'team_id': play.get('teamId', ''),
                'stat_type': play.get('statType', ''),
                'stat_yardage': play.get('statYardage', ''),
                'start_yard_line': play.get('start', {}).get('yardLine', ''),
                'end_yard_line': play.get('end', {}).get('yardLine', ''),
                'raw_data': play
            }
            plays.append(play_data)
    
    return plays

def extract_cfbd_plays(cfbd_data):
    """Extract ALL CFBD play data"""
    plays = []
    
    for play in cfbd_data:
        play_data = {
            'play_number': len(plays) + 1,
            'quarter': f"Q{play.get('period', '')}",
            'time': f"{play.get('clock', {}).get('minutes', '')}:{play.get('clock', {}).get('seconds', '')}",
            'down': play.get('down', ''),
            'distance': play.get('distance', ''),
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
            'success': play.get('success', ''),
            'rush': play.get('rush', ''),
            'pass': play.get('pass', ''),
            'sack': play.get('sack', ''),
            'fumble': play.get('fumble', ''),
            'penalty': play.get('penalty', ''),
            'raw_data': play
        }
        plays.append(play_data)
    
    return plays

def create_side_by_side_html(espn_plays, cfbd_plays):
    """Create side-by-side HTML with separate tables"""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESPN vs CFBD - Side-by-Side Data Comparison (401752873)</title>
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
            .tables-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .table-wrapper {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .table-header {{
                padding: 15px;
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                color: white;
            }}
            .espn-header {{
                background: #1976d2;
            }}
            .cfbd-header {{
                background: #7b1fa2;
            }}
            .table-container {{
                overflow-x: auto;
                max-height: 80vh;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 11px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 6px;
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
            .play-number {{
                text-align: center;
                font-weight: bold;
                background-color: #f0f0f0;
                width: 50px;
            }}
            .play-text {{
                max-width: 200px;
                word-wrap: break-word;
            }}
            .score {{
                text-align: center;
                font-weight: bold;
            }}
            .win-prob {{
                text-align: center;
                font-size: 10px;
            }}
            .raw-data {{
                max-width: 150px;
                word-wrap: break-word;
                font-size: 9px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏈 ESPN vs CFBD - Side-by-Side Data Comparison</h1>
            <h2>Michigan vs Washington - Game ID: 401752873</h2>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>📺 ESPN Data</h3>
                <p><strong>Total Plays:</strong> {len(espn_plays)}</p>
                <p><strong>Data Source:</strong> ESPN API</p>
                <p><strong>Structure:</strong> plays.items array</p>
                <p><strong>Win Probability:</strong> Available</p>
                <p><strong>Drive Info:</strong> Available</p>
            </div>
            <div class="summary-card">
                <h3>📊 CFBD Data</h3>
                <p><strong>Total Plays:</strong> {len(cfbd_plays)}</p>
                <p><strong>Data Source:</strong> CollegeFootballData.com API</p>
                <p><strong>Structure:</strong> Flat array</p>
                <p><strong>Win Probability:</strong> Available</p>
                <p><strong>PPA Metrics:</strong> Available</p>
            </div>
        </div>
        
        <div class="tables-container">
            <!-- ESPN Table -->
            <div class="table-wrapper">
                <div class="table-header espn-header">
                    📺 ESPN Data - All {len(espn_plays)} Plays
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Qtr</th>
                                <th>Time</th>
                                <th>Down</th>
                                <th>Dist</th>
                                <th>Yard Line</th>
                                <th>Play Description</th>
                                <th>Offense</th>
                                <th>Defense</th>
                                <th>Yards</th>
                                <th>Score</th>
                                <th>Win Prob</th>
                                <th>Play ID</th>
                                <th>Drive ID</th>
                                <th>Team ID</th>
                                <th>Stat Type</th>
                                <th>Start Yard</th>
                                <th>End Yard</th>
                                <th>Raw Data</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Add ESPN plays
    for play in espn_plays:
        html += f"""
                            <tr>
                                <td class="play-number">{play['play_number']}</td>
                                <td>{play['quarter']}</td>
                                <td>{play['time']}</td>
                                <td>{play['down']}</td>
                                <td>{play['distance']}</td>
                                <td>{play['yard_line']}</td>
                                <td class="play-text">{play['play_text']}</td>
                                <td>{play['offense']}</td>
                                <td>{play['defense']}</td>
                                <td>{play['yards_gained']}</td>
                                <td class="score">{play['score_home']}-{play['score_away']}</td>
                                <td class="win-prob">{play['win_prob_home']}</td>
                                <td>{play['play_id']}</td>
                                <td>{play['drive_id']}</td>
                                <td>{play['team_id']}</td>
                                <td>{play['stat_type']}</td>
                                <td>{play['start_yard_line']}</td>
                                <td>{play['end_yard_line']}</td>
                                <td class="raw-data">{str(play['raw_data'])[:100]}...</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- CFBD Table -->
            <div class="table-wrapper">
                <div class="table-header cfbd-header">
                    📊 CFBD Data - All """ + str(len(cfbd_plays)) + """ Plays
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Qtr</th>
                                <th>Time</th>
                                <th>Down</th>
                                <th>Dist</th>
                                <th>Yard Line</th>
                                <th>Play Description</th>
                                <th>Offense</th>
                                <th>Defense</th>
                                <th>Yards</th>
                                <th>Score</th>
                                <th>Win Prob</th>
                                <th>Play ID</th>
                                <th>Game ID</th>
                                <th>PPA</th>
                                <th>Success</th>
                                <th>Rush</th>
                                <th>Pass</th>
                                <th>Sack</th>
                                <th>Fumble</th>
                                <th>Penalty</th>
                                <th>Raw Data</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Add CFBD plays
    for play in cfbd_plays:
        html += f"""
                            <tr>
                                <td class="play-number">{play['play_number']}</td>
                                <td>{play['quarter']}</td>
                                <td>{play['time']}</td>
                                <td>{play['down']}</td>
                                <td>{play['distance']}</td>
                                <td>{play['yard_line']}</td>
                                <td class="play-text">{play['play_text']}</td>
                                <td>{play['offense']}</td>
                                <td>{play['defense']}</td>
                                <td>{play['yards_gained']}</td>
                                <td class="score">{play['score_home']}-{play['score_away']}</td>
                                <td class="win-prob">{play['win_prob_home']}</td>
                                <td>{play['play_id']}</td>
                                <td>{play['game_id']}</td>
                                <td>{play['ppa']}</td>
                                <td>{play['success']}</td>
                                <td>{play['rush']}</td>
                                <td>{play['pass']}</td>
                                <td>{play['sack']}</td>
                                <td>{play['fumble']}</td>
                                <td>{play['penalty']}</td>
                                <td class="raw-data">{str(play['raw_data'])[:100]}...</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    """Main function to create side-by-side comparison"""
    print("Creating side-by-side ESPN vs CFBD comparison for game 401752873...")
    
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
    
    print(f"📊 ESPN plays: {len(espn_plays)}")
    print(f"📊 CFBD plays: {len(cfbd_plays)}")
    
    # Create HTML
    html = create_side_by_side_html(espn_plays, cfbd_plays)
    
    # Save HTML
    output_file = 'espn_cfbd_side_by_side_401752873.html'
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Side-by-side comparison saved to: {output_file}")
    print(f"🌐 Open in browser to view the comparison")

if __name__ == "__main__":
    main()
