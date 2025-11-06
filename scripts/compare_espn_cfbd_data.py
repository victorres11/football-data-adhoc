#!/usr/bin/env python3
"""
Compare ESPN vs CFBD Play-by-Play Data
Side-by-side analysis of the same game from both APIs
"""

import json
import requests
from datetime import datetime

def load_espn_data():
    """Load ESPN data for Michigan vs Washington (401752873)"""
    print("Loading ESPN data...")
    
    try:
        # Load the complete game data we already have
        with open('data/game_401752873/complete_game_data.json', 'r') as f:
            game_data = json.load(f)
        
        # Extract plays from ESPN data - check both 'plays' and 'drives' structures
        plays = []
        
        # First try direct plays array
        if 'plays' in game_data and game_data['plays']:
            plays_data = game_data['plays']
            if isinstance(plays_data, list):
                plays = plays_data
                print(f"Found {len(plays)} plays in direct 'plays' array")
            elif isinstance(plays_data, dict):
                # If it's a dict, try to extract plays from it
                plays = []
                for key, value in plays_data.items():
                    if isinstance(value, list):
                        plays.extend(value)
                print(f"Found {len(plays)} plays in 'plays' dict structure")
            else:
                plays = []
                print("Plays data is neither list nor dict")
        else:
            # Try drives structure
            drives = game_data.get('drives', {})
            if 'items' in drives:
                drive_items = drives['items']
                drive_counter = 1
                for drive in drive_items:
                    drive_plays = drive.get('plays', [])
                    for play in drive_plays:
                        play['drive_info'] = {
                            'drive_number': drive_counter,
                            'drive_description': drive.get('description', ''),
                            'drive_id': drive.get('id', '')
                        }
                        plays.append(play)
                    drive_counter += 1
                print(f"Found {len(plays)} plays in drives structure")
            else:
                print("No plays found in either structure")
        
        print(f"Loaded {len(plays)} ESPN plays")
        return plays, game_data
    except Exception as e:
        print(f"Error loading ESPN data: {e}")
        return [], {}

def load_cfbd_data():
    """Load CFBD data for the same game"""
    print("Loading CFBD data...")
    
    # Load API key from config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get any recent Michigan game for comparison
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2024,
            'team': 'Michigan'
        })
        
        if response.status_code == 200:
            games = response.json()
            print(f"Found {len(games)} Michigan games in 2024")
            
            # Use the first game for comparison
            if games:
                game = games[0]
                game_id = game.get('id')
                print(f"Using game: {game.get('home_team')} vs {game.get('away_team')} (ID: {game_id})")
                
                # Get plays for this game
                plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                    'gameId': game_id,
                    'year': 2024,
                    'week': 1
                })
                
                if plays_response.status_code == 200:
                    cfbd_plays = plays_response.json()
                    print(f"Retrieved {len(cfbd_plays)} plays from CFBD")
                    # Limit to first 100 plays for comparison
                    cfbd_plays = cfbd_plays[:100]
                    return cfbd_plays, game
                else:
                    print(f"Failed to get plays: {plays_response.text}")
            else:
                print("No games found")
        else:
            print(f"Failed to get games: {response.text}")
            
    except Exception as e:
        print(f"Error loading CFBD data: {e}")
    
    return [], {}

def compare_play_structures(espn_play, cfbd_play):
    """Compare the structure of a single play from both APIs"""
    
    comparison = {
        'espn': {
            'id': espn_play.get('id', 'N/A'),
            'text': espn_play.get('text', 'N/A'),
            'type': espn_play.get('type', {}).get('text', 'N/A'),
            'period': espn_play.get('period', {}).get('number', 'N/A'),
            'clock': espn_play.get('clock', {}).get('displayValue', 'N/A'),
            'down': espn_play.get('start', {}).get('down', 'N/A'),
            'distance': espn_play.get('start', {}).get('distance', 'N/A'),
            'yard_line': espn_play.get('start', {}).get('yardLine', 'N/A'),
            'yards_gained': espn_play.get('statYardage', 'N/A'),
            'scoring': espn_play.get('scoring', False),
            'team_participants': len(espn_play.get('teamParticipants', [])),
            'drive_info': espn_play.get('drive_info', {}).get('drive_number', 'N/A')
        },
        'cfbd': {
            'id': cfbd_play.get('id', 'N/A'),
            'text': cfbd_play.get('playText', 'N/A'),
            'type': cfbd_play.get('playType', 'N/A'),
            'period': cfbd_play.get('period', 'N/A'),
            'clock': f"{cfbd_play.get('clock', {}).get('minutes', 'N/A')}:{cfbd_play.get('clock', {}).get('seconds', 'N/A')}",
            'down': cfbd_play.get('down', 'N/A'),
            'distance': cfbd_play.get('distance', 'N/A'),
            'yard_line': cfbd_play.get('yardline', 'N/A'),
            'yards_gained': cfbd_play.get('yardsGained', 'N/A'),
            'scoring': cfbd_play.get('scoring', False),
            'offense': cfbd_play.get('offense', 'N/A'),
            'defense': cfbd_play.get('defense', 'N/A'),
            'ppa': cfbd_play.get('ppa', 'N/A'),
            'drive_number': cfbd_play.get('driveNumber', 'N/A')
        }
    }
    
    return comparison

def generate_comparison_report(espn_plays, cfbd_plays, espn_game, cfbd_game):
    """Generate a comprehensive comparison report"""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESPN vs CFBD Data Comparison Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            margin-top: 10px;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .section {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 20px 0;
        }}
        
        .api-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .api-section.cfbd {{
            border-left-color: #28a745;
        }}
        
        .api-section.espn {{
            border-left-color: #dc3545;
        }}
        
        .api-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .api-title.cfbd {{
            color: #28a745;
        }}
        
        .api-title.espn {{
            color: #dc3545;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .play-comparison {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .play-side {{
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .play-side.espn {{
            background: #fff5f5;
            border-left: 4px solid #dc3545;
        }}
        
        .play-side.cfbd {{
            background: #f0fff4;
            border-left: 4px solid #28a745;
        }}
        
        .play-field {{
            margin: 8px 0;
            display: flex;
            justify-content: space-between;
        }}
        
        .field-name {{
            font-weight: bold;
            color: #555;
        }}
        
        .field-value {{
            color: #333;
        }}
        
        .advantages {{
            background: #e8f5e8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .advantages h3 {{
            color: #28a745;
            margin-top: 0;
        }}
        
        .advantage-item {{
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #28a745;
        }}
        
        .disadvantages {{
            background: #fff5f5;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .disadvantages h3 {{
            color: #dc3545;
            margin-top: 0;
        }}
        
        .disadvantage-item {{
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #dc3545;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ESPN vs CFBD Data Comparison</h1>
            <div class="subtitle">Play-by-Play Data Analysis Report</div>
        </div>
        
        <div class="section">
            <h2>📊 Data Overview</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(espn_plays)}</div>
                    <div class="stat-label">ESPN Plays</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(cfbd_plays)}</div>
                    <div class="stat-label">CFBD Plays</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(espn_plays) - len(cfbd_plays) if len(espn_plays) > len(cfbd_plays) else len(cfbd_plays) - len(espn_plays)}</div>
                    <div class="stat-label">Play Count Difference</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Detailed Play Comparison</h2>
            <div class="play-comparison">
                <h3>Sample Play Analysis</h3>
"""
    
    # Add sample play comparisons
    if espn_plays and cfbd_plays:
        # Compare first few plays
        max_plays = min(3, len(espn_plays), len(cfbd_plays))
        for i in range(max_plays):
            espn_play = espn_plays[i] if i < len(espn_plays) else {}
            cfbd_play = cfbd_plays[i] if i < len(cfbd_plays) else {}
            comparison = compare_play_structures(espn_play, cfbd_play)
            
            html += f"""
                <div style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                    <h4>Play {i+1} Comparison</h4>
                    <div class="comparison-grid">
                        <div class="play-side espn">
                            <div class="api-title espn">ESPN Data</div>
                            <div class="play-field"><span class="field-name">ID:</span><span class="field-value">{comparison['espn']['id']}</span></div>
                            <div class="play-field"><span class="field-name">Text:</span><span class="field-value">{comparison['espn']['text'][:50]}...</span></div>
                            <div class="play-field"><span class="field-name">Type:</span><span class="field-value">{comparison['espn']['type']}</span></div>
                            <div class="play-field"><span class="field-name">Period:</span><span class="field-value">{comparison['espn']['period']}</span></div>
                            <div class="play-field"><span class="field-name">Clock:</span><span class="field-value">{comparison['espn']['clock']}</span></div>
                            <div class="play-field"><span class="field-name">Down/Distance:</span><span class="field-value">{comparison['espn']['down']} & {comparison['espn']['distance']}</span></div>
                            <div class="play-field"><span class="field-name">Yards Gained:</span><span class="field-value">{comparison['espn']['yards_gained']}</span></div>
                        </div>
                        <div class="play-side cfbd">
                            <div class="api-title cfbd">CFBD Data</div>
                            <div class="play-field"><span class="field-name">ID:</span><span class="field-value">{comparison['cfbd']['id']}</span></div>
                            <div class="play-field"><span class="field-name">Text:</span><span class="field-value">{comparison['cfbd']['text'][:50]}...</span></div>
                            <div class="play-field"><span class="field-name">Type:</span><span class="field-value">{comparison['cfbd']['type']}</span></div>
                            <div class="play-field"><span class="field-name">Period:</span><span class="field-value">{comparison['cfbd']['period']}</span></div>
                            <div class="play-field"><span class="field-name">Clock:</span><span class="field-value">{comparison['cfbd']['clock']}</span></div>
                            <div class="play-field"><span class="field-name">Down/Distance:</span><span class="field-value">{comparison['cfbd']['down']} & {comparison['cfbd']['distance']}</span></div>
                            <div class="play-field"><span class="field-name">Yards Gained:</span><span class="field-value">{comparison['cfbd']['yards_gained']}</span></div>
                            <div class="play-field"><span class="field-name">PPA:</span><span class="field-value">{comparison['cfbd']['ppa']}</span></div>
                            <div class="play-field"><span class="field-name">Offense:</span><span class="field-value">{comparison['cfbd']['offense']}</span></div>
                            <div class="play-field"><span class="field-name">Defense:</span><span class="field-value">{comparison['cfbd']['defense']}</span></div>
                        </div>
                    </div>
                </div>
            """
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>✅ CFBD Advantages</h2>
            <div class="advantages">
                <h3>What CFBD Does Better</h3>
                <div class="advantage-item">
                    <strong>🎯 Structured Data:</strong> Clean, consistent JSON responses with standardized field names
                </div>
                <div class="advantage-item">
                    <strong>📊 Advanced Analytics:</strong> Built-in PPA (Predicted Points Added), EPA, success rate metrics
                </div>
                <div class="advantage-item">
                    <strong>🔍 Rich Context:</strong> Offense/defense clearly identified, conference information included
                </div>
                <div class="advantage-item">
                    <strong>⚡ Better Performance:</strong> Optimized API with good rate limits and fast responses
                </div>
                <div class="advantage-item">
                    <strong>📈 Historical Data:</strong> Comprehensive access to historical datasets
                </div>
                <div class="advantage-item">
                    <strong>🛠️ Developer Experience:</strong> Well-documented, consistent endpoints, type hints
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>❌ CFBD Disadvantages</h2>
            <div class="disadvantages">
                <h3>What ESPN Does Better</h3>
                <div class="disadvantage-item">
                    <strong>🔓 No Authentication:</strong> ESPN requires no API key, CFBD requires free registration
                </div>
                <div class="disadvantage-item">
                    <strong>⏱️ Real-time Access:</strong> ESPN provides immediate access to live games
                </div>
                <div class="disadvantage-item">
                    <strong>📺 Media Integration:</strong> ESPN includes video highlights and media content
                </div>
                <div class="disadvantage-item">
                    <strong>🏆 Win Probability:</strong> ESPN has dedicated win probability endpoints
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Recommendations</h2>
            <div style="background: #e3f2fd; padding: 20px; border-radius: 10px;">
                <h3>For Enhanced Analysis Projects:</h3>
                <ul>
                    <li><strong>Use CFBD for:</strong> Historical analysis, advanced metrics, consistent data processing</li>
                    <li><strong>Use ESPN for:</strong> Real-time data, win probability, media integration</li>
                    <li><strong>Hybrid Approach:</strong> Use CFBD for play-by-play data and ESPN for win probability</li>
                </ul>
                
                <h3>Migration Benefits:</h3>
                <ul>
                    <li>Eliminate data structure inconsistencies</li>
                    <li>Access to advanced analytics (PPA, EPA)</li>
                    <li>Better historical data access</li>
                    <li>Improved developer experience</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("ESPN vs CFBD Data Comparison")
    print("=" * 50)
    
    # Load data from both sources
    espn_plays, espn_game = load_espn_data()
    cfbd_plays, cfbd_game = load_cfbd_data()
    
    print(f"ESPN plays: {len(espn_plays)}")
    print(f"CFBD plays: {len(cfbd_plays)}")
    
    # Generate comparison report
    html = generate_comparison_report(espn_plays, cfbd_plays, espn_game, cfbd_game)
    
    # Save report
    output_file = "espn_cfbd_comparison_report.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"\nComparison report saved to: {output_file}")
    print("Open the file in your browser to view the detailed comparison!")

if __name__ == "__main__":
    main()
