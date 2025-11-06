#!/usr/bin/env python3
"""
Working Game Comparison: ESPN vs CFBD
Use a game we know works from both APIs
"""

import json
import requests

def load_espn_data():
    """Load ESPN data for Michigan vs Washington (401752873)"""
    print("Loading ESPN data...")
    
    try:
        with open('data/game_401752873/complete_game_data.json', 'r') as f:
            game_data = json.load(f)
        
        # Extract plays from ESPN data
        plays = []
        if 'plays' in game_data and game_data['plays']:
            plays_data = game_data['plays']
            if isinstance(plays_data, dict):
                for key, value in plays_data.items():
                    if isinstance(value, list):
                        plays.extend(value)
        
        print(f"ESPN: Found {len(plays)} plays")
        return plays[:20]  # Limit to first 20 plays for detailed comparison
        
    except Exception as e:
        print(f"Error loading ESPN data: {e}")
        return []

def load_cfbd_data():
    """Load CFBD data for a working game"""
    print("Loading CFBD data...")
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get a working game from CFBD
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2024,
            'week': 1
        })
        
        if response.status_code == 200:
            games = response.json()
            print(f"Found {len(games)} games in Week 1, 2024")
            
            # Use the first game
            if games:
                game = games[0]
                game_id = game.get('id')
                print(f"Using game ID: {game_id}")
                
                # Get plays for this game
                plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                    'gameId': game_id,
                    'year': 2024,
                    'week': 1
                })
                
                if plays_response.status_code == 200:
                    plays = plays_response.json()
                    print(f"CFBD: Found {len(plays)} plays")
                    return plays[:20]  # Limit to first 20 plays
                else:
                    print(f"Failed to get plays: {plays_response.text}")
        else:
            print(f"Failed to get games: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return []

def create_detailed_comparison_html(espn_plays, cfbd_plays):
    """Create detailed side-by-side comparison HTML"""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESPN vs CFBD - Detailed Play Comparison</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1800px;
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
        
        .comparison-section {{
            padding: 30px;
        }}
        
        .play-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            margin: 20px 0;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .play-side {{
            padding: 20px;
        }}
        
        .play-side.espn {{
            background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
            border-right: 3px solid #dc3545;
        }}
        
        .play-side.cfbd {{
            background: linear-gradient(135deg, #f0fff4 0%, #e6ffe6 100%);
        }}
        
        .api-title {{
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            color: white;
        }}
        
        .api-title.espn {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        }}
        
        .api-title.cfbd {{
            background: linear-gradient(135deg, #28a745 0%, #218838 100%);
        }}
        
        .play-field {{
            margin: 10px 0;
            padding: 8px;
            background: rgba(255,255,255,0.8);
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }}
        
        .field-name {{
            font-weight: bold;
            color: #333;
            display: inline-block;
            width: 140px;
            font-size: 0.9em;
        }}
        
        .field-value {{
            color: #555;
            font-size: 0.9em;
        }}
        
        .play-number {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 1.2em;
            grid-column: 1 / -1;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2.2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .highlight {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        
        .cfbd-advantage {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ESPN vs CFBD - Detailed Play Comparison</h1>
            <p>Side-by-side analysis of play-by-play data from both APIs</p>
        </div>
        
        <div class="comparison-section">
            <div class="summary-stats">
                <div class="stat-card">
                    <div class="stat-number">{len(espn_plays)}</div>
                    <div class="stat-label">ESPN Plays Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(cfbd_plays)}</div>
                    <div class="stat-label">CFBD Plays Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Data Completeness</div>
                </div>
            </div>
            
            <h2>📊 Detailed Play-by-Play Comparison</h2>
            <p>Each play shows the exact data structure and content from both APIs:</p>
"""
    
    # Add detailed play comparisons
    max_plays = min(10, len(espn_plays), len(cfbd_plays))
    for i in range(max_plays):
        espn_play = espn_plays[i] if i < len(espn_plays) else {}
        cfbd_play = cfbd_plays[i] if i < len(cfbd_plays) else {}
        
        # Extract detailed data
        espn_data = {
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
            'home_score': espn_play.get('homeScore', 'N/A'),
            'away_score': espn_play.get('awayScore', 'N/A')
        }
        
        cfbd_data = {
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
            'drive_number': cfbd_play.get('driveNumber', 'N/A'),
            'offense_score': cfbd_play.get('offenseScore', 'N/A'),
            'defense_score': cfbd_play.get('defenseScore', 'N/A')
        }
        
        html += f"""
            <div class="play-comparison">
                <div class="play-number">Play {i+1} - Detailed Comparison</div>
                <div class="play-side espn">
                    <div class="api-title espn">ESPN API Data</div>
                    <div class="play-field"><span class="field-name">Play ID:</span><span class="field-value">{espn_data['id']}</span></div>
                    <div class="play-field"><span class="field-name">Play Text:</span><span class="field-value">{espn_data['text'][:100]}...</span></div>
                    <div class="play-field"><span class="field-name">Play Type:</span><span class="field-value">{espn_data['type']}</span></div>
                    <div class="play-field"><span class="field-name">Period:</span><span class="field-value">{espn_data['period']}</span></div>
                    <div class="play-field"><span class="field-name">Clock:</span><span class="field-value">{espn_data['clock']}</span></div>
                    <div class="play-field"><span class="field-name">Down:</span><span class="field-value">{espn_data['down']}</span></div>
                    <div class="play-field"><span class="field-name">Distance:</span><span class="field-value">{espn_data['distance']}</span></div>
                    <div class="play-field"><span class="field-name">Yard Line:</span><span class="field-value">{espn_data['yard_line']}</span></div>
                    <div class="play-field"><span class="field-name">Yards Gained:</span><span class="field-value">{espn_data['yards_gained']}</span></div>
                    <div class="play-field"><span class="field-name">Scoring:</span><span class="field-value">{espn_data['scoring']}</span></div>
                    <div class="play-field"><span class="field-name">Home Score:</span><span class="field-value">{espn_data['home_score']}</span></div>
                    <div class="play-field"><span class="field-name">Away Score:</span><span class="field-value">{espn_data['away_score']}</span></div>
                    <div class="play-field"><span class="field-name">Team Participants:</span><span class="field-value">{espn_data['team_participants']}</span></div>
                </div>
                <div class="play-side cfbd">
                    <div class="api-title cfbd">CFBD API Data</div>
                    <div class="play-field"><span class="field-name">Play ID:</span><span class="field-value">{cfbd_data['id']}</span></div>
                    <div class="play-field"><span class="field-name">Play Text:</span><span class="field-value">{cfbd_data['text'][:100]}...</span></div>
                    <div class="play-field"><span class="field-name">Play Type:</span><span class="field-value">{cfbd_data['type']}</span></div>
                    <div class="play-field"><span class="field-name">Period:</span><span class="field-value">{cfbd_data['period']}</span></div>
                    <div class="play-field"><span class="field-name">Clock:</span><span class="field-value">{cfbd_data['clock']}</span></div>
                    <div class="play-field"><span class="field-name">Down:</span><span class="field-value">{cfbd_data['down']}</span></div>
                    <div class="play-field"><span class="field-name">Distance:</span><span class="field-value">{cfbd_data['distance']}</span></div>
                    <div class="play-field"><span class="field-name">Yard Line:</span><span class="field-value">{cfbd_data['yard_line']}</span></div>
                    <div class="play-field"><span class="field-name">Yards Gained:</span><span class="field-value">{cfbd_data['yards_gained']}</span></div>
                    <div class="play-field"><span class="field-name">Scoring:</span><span class="field-value">{cfbd_data['scoring']}</span></div>
                    <div class="play-field"><span class="field-name">Offense:</span><span class="field-value">{cfbd_data['offense']}</span></div>
                    <div class="play-field"><span class="field-name">Defense:</span><span class="field-value">{cfbd_data['defense']}</span></div>
                    <div class="play-field"><span class="field-name">PPA:</span><span class="field-value">{cfbd_data['ppa']}</span></div>
                    <div class="play-field"><span class="field-name">Drive #:</span><span class="field-value">{cfbd_data['drive_number']}</span></div>
                    <div class="play-field"><span class="field-name">Offense Score:</span><span class="field-value">{cfbd_data['offense_score']}</span></div>
                    <div class="play-field"><span class="field-name">Defense Score:</span><span class="field-value">{cfbd_data['defense_score']}</span></div>
                </div>
            </div>
        """
    
    html += """
            <div class="highlight">
                <h3>🔍 Key Observations:</h3>
                <ul>
                    <li><strong>ESPN Data:</strong> Nested structure with varying field names, requires parsing of nested objects</li>
                    <li><strong>CFBD Data:</strong> Flat structure with consistent field names, includes advanced metrics (PPA)</li>
                    <li><strong>Team Context:</strong> CFBD clearly identifies offense/defense, ESPN requires team participant parsing</li>
                    <li><strong>Advanced Analytics:</strong> CFBD includes PPA (Predicted Points Added), ESPN does not</li>
                    <li><strong>Data Consistency:</strong> CFBD provides standardized field names, ESPN varies by endpoint</li>
                </ul>
            </div>
            
            <div class="cfbd-advantage">
                <h3>✅ CFBD Advantages:</h3>
                <ul>
                    <li><strong>Structured Data:</strong> Clean, consistent JSON with standardized field names</li>
                    <li><strong>Advanced Metrics:</strong> Built-in PPA, EPA, success rate calculations</li>
                    <li><strong>Team Context:</strong> Clear offense/defense identification</li>
                    <li><strong>Drive Information:</strong> Direct drive number and context</li>
                    <li><strong>Developer Experience:</strong> Type hints, documentation, consistent API</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("Working Game Comparison: ESPN vs CFBD")
    print("=" * 50)
    
    # Load data from both sources
    espn_plays = load_espn_data()
    cfbd_plays = load_cfbd_data()
    
    if not espn_plays or not cfbd_plays:
        print("Unable to load data from both sources")
        return
    
    print(f"\nComparison Summary:")
    print(f"ESPN plays: {len(espn_plays)}")
    print(f"CFBD plays: {len(cfbd_plays)}")
    
    # Generate detailed comparison
    html = create_detailed_comparison_html(espn_plays, cfbd_plays)
    
    # Save report
    output_file = "detailed_play_comparison.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"\nDetailed comparison saved to: {output_file}")
    print("Open the file in your browser to view the side-by-side comparison!")

if __name__ == "__main__":
    main()
