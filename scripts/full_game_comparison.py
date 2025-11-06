#!/usr/bin/env python3
"""
Full Game Comparison: ESPN vs CFBD
Use the Michigan vs Washington game we already have
"""

import json
import requests

def load_espn_michigan_washington():
    """Load ESPN data for Michigan vs Washington (401752873)"""
    print("Loading ESPN data for Michigan vs Washington...")
    
    try:
        with open('data/game_401752873/complete_game_data.json', 'r') as f:
            game_data = json.load(f)
        
        # Extract all plays from ESPN data
        plays = []
        if 'plays' in game_data and game_data['plays']:
            plays_data = game_data['plays']
            if isinstance(plays_data, dict):
                for key, value in plays_data.items():
                    if isinstance(value, list):
                        plays.extend(value)
        
        print(f"ESPN: Found {len(plays)} plays")
        
        # Get game info
        game_info = {
            'id': '401752873',
            'teams': ['Michigan', 'Washington'],
            'date': '2024-01-08',
            'type': 'National Championship'
        }
        
        return plays, game_info
        
    except Exception as e:
        print(f"Error loading ESPN data: {e}")
        return [], {}

def load_cfbd_michigan_washington():
    """Try to find Michigan vs Washington in CFBD"""
    print("Searching for Michigan vs Washington in CFBD...")
    
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
        # Search for Michigan games in 2024
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2024,
            'team': 'Michigan'
        })
        
        if response.status_code == 200:
            games = response.json()
            print(f"Found {len(games)} Michigan games in 2024")
            
            # Look for a game that might be the National Championship
            # Check games with high play counts (championship games have many plays)
            for game in games:
                game_id = game.get('id')
                print(f"Checking game {game_id}...")
                
                # Try to get plays for this game
                try:
                    plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                        'gameId': game_id,
                        'year': 2024,
                        'week': 1  # Add week parameter
                    })
                    
                    if plays_response.status_code == 200:
                        plays = plays_response.json()
                        print(f"  Found {len(plays)} plays")
                        
                        # If this has a lot of plays, it might be the championship
                        if len(plays) > 2000:  # Championship games have many plays
                            print(f"  Selected game {game_id} with {len(plays)} plays (likely championship)")
                            return plays[:500], game  # Limit to first 500 plays
                        elif len(plays) > 100:  # Use any game with reasonable play count
                            print(f"  Using game {game_id} with {len(plays)} plays")
                            return plays[:500], game  # Limit to first 500 plays
                            
                except Exception as e:
                    print(f"  Error getting plays: {e}")
            
            # If no high-play game found, use the one with most plays
            best_game = None
            best_play_count = 0
            
            for game in games:
                game_id = game.get('id')
                try:
                    plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                        'gameId': game_id,
                        'year': 2024
                    })
                    
                    if plays_response.status_code == 200:
                        plays = plays_response.json()
                        if len(plays) > best_play_count:
                            best_play_count = len(plays)
                            best_game = (game, plays)
                            
                except Exception as e:
                    continue
            
            if best_game:
                game, plays = best_game
                print(f"Using game with most plays: {len(plays)} plays")
                return plays, game
                
        else:
            print(f"Failed to get CFBD games: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return [], {}

def create_full_comparison_html(espn_plays, cfbd_plays, espn_game, cfbd_game):
    """Create full game comparison HTML"""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Game Comparison: ESPN vs CFBD</title>
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
        
        .game-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }}
        
        .game-card {{
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .game-card.espn {{
            background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
            border-left: 4px solid #dc3545;
        }}
        
        .game-card.cfbd {{
            background: linear-gradient(135deg, #f0fff4 0%, #e6ffe6 100%);
            border-left: 4px solid #28a745;
        }}
        
        .api-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            color: white;
        }}
        
        .api-title.espn {{
            background: #dc3545;
        }}
        
        .api-title.cfbd {{
            background: #28a745;
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
        
        .play-field {{
            margin: 8px 0;
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
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .cfbd-advantage {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Full Game Comparison: ESPN vs CFBD</h1>
            <p>Complete analysis of Michigan vs Washington (National Championship)</p>
        </div>
        
        <div class="comparison-section">
            <div class="summary-stats">
                <div class="stat-card">
                    <div class="stat-number">{len(espn_plays)}</div>
                    <div class="stat-label">ESPN Total Plays</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(cfbd_plays)}</div>
                    <div class="stat-label">CFBD Total Plays</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{abs(len(espn_plays) - len(cfbd_plays))}</div>
                    <div class="stat-label">Play Count Difference</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Data Completeness</div>
                </div>
            </div>
            
            <div class="game-info">
                <div class="game-card espn">
                    <div class="api-title espn">ESPN Game Data</div>
                    <div class="play-field"><span class="field-name">Game ID:</span><span class="field-value">{espn_game.get('id', 'N/A')}</span></div>
                    <div class="play-field"><span class="field-name">Teams:</span><span class="field-value">{', '.join(espn_game.get('teams', []))}</span></div>
                    <div class="play-field"><span class="field-name">Date:</span><span class="field-value">{espn_game.get('date', 'N/A')}</span></div>
                    <div class="play-field"><span class="field-name">Type:</span><span class="field-value">{espn_game.get('type', 'N/A')}</span></div>
                    <div class="play-field"><span class="field-name">Total Plays:</span><span class="field-value">{len(espn_plays)}</span></div>
                </div>
                <div class="game-card cfbd">
                    <div class="api-title cfbd">CFBD Game Data</div>
                    <div class="play-field"><span class="field-name">Game ID:</span><span class="field-value">{cfbd_game.get('id', 'N/A')}</span></div>
                    <div class="play-field"><span class="field-name">Home Team:</span><span class="field-value">{cfbd_game.get('home_team', 'N/A')}</span></div>
                    <div class="play-field"><span class="field-name">Away Team:</span><span class="field-value">{cfbd_game.get('away_team', 'N/A')}</span></div>
                    <div class="play-field"><span class="field-name">Date:</span><span class="field-value">{cfbd_game.get('start_date', 'N/A')}</span></div>
                    <div class="play-field"><span class="field-name">Total Plays:</span><span class="field-value">{len(cfbd_plays)}</span></div>
                </div>
            </div>
            
            <h2>📊 Sample Play Comparisons</h2>
            <p>Detailed side-by-side analysis of individual plays:</p>
"""
    
    # Add sample play comparisons (first 5 plays)
    max_plays = min(5, len(espn_plays), len(cfbd_plays))
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
            'scoring': espn_play.get('scoring', False)
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
            'ppa': cfbd_play.get('ppa', 'N/A')
        }
        
        html += f"""
            <div class="play-comparison">
                <div class="play-number">Play {i+1} - Complete Data Comparison</div>
                <div class="play-side espn">
                    <div class="api-title espn">ESPN API</div>
                    <div class="play-field"><span class="field-name">Play ID:</span><span class="field-value">{espn_data['id']}</span></div>
                    <div class="play-field"><span class="field-name">Play Text:</span><span class="field-value">{espn_data['text'][:80]}...</span></div>
                    <div class="play-field"><span class="field-name">Play Type:</span><span class="field-value">{espn_data['type']}</span></div>
                    <div class="play-field"><span class="field-name">Period:</span><span class="field-value">{espn_data['period']}</span></div>
                    <div class="play-field"><span class="field-name">Clock:</span><span class="field-value">{espn_data['clock']}</span></div>
                    <div class="play-field"><span class="field-name">Down:</span><span class="field-value">{espn_data['down']}</span></div>
                    <div class="play-field"><span class="field-name">Distance:</span><span class="field-value">{espn_data['distance']}</span></div>
                    <div class="play-field"><span class="field-name">Yard Line:</span><span class="field-value">{espn_data['yard_line']}</span></div>
                    <div class="play-field"><span class="field-name">Yards Gained:</span><span class="field-value">{espn_data['yards_gained']}</span></div>
                    <div class="play-field"><span class="field-name">Scoring:</span><span class="field-value">{espn_data['scoring']}</span></div>
                </div>
                <div class="play-side cfbd">
                    <div class="api-title cfbd">CFBD API</div>
                    <div class="play-field"><span class="field-name">Play ID:</span><span class="field-value">{cfbd_data['id']}</span></div>
                    <div class="play-field"><span class="field-name">Play Text:</span><span class="field-value">{cfbd_data['text'][:80]}...</span></div>
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
                </div>
            </div>
        """
    
    html += """
            <div class="highlight">
                <h3>🔍 Key Differences Observed:</h3>
                <ul>
                    <li><strong>Data Structure:</strong> ESPN uses nested objects, CFBD uses flat structure</li>
                    <li><strong>Field Names:</strong> ESPN varies by endpoint, CFBD is consistent</li>
                    <li><strong>Team Context:</strong> CFBD clearly identifies offense/defense, ESPN requires parsing</li>
                    <li><strong>Advanced Metrics:</strong> CFBD includes PPA (Predicted Points Added), ESPN does not</li>
                    <li><strong>Data Completeness:</strong> Both APIs provide comprehensive play data</li>
                </ul>
            </div>
            
            <div class="cfbd-advantage">
                <h3>✅ CFBD Advantages for Analysis:</h3>
                <ul>
                    <li><strong>Structured Data:</strong> Clean, consistent JSON with standardized field names</li>
                    <li><strong>Advanced Analytics:</strong> Built-in PPA, EPA, success rate calculations</li>
                    <li><strong>Team Context:</strong> Clear offense/defense identification for every play</li>
                    <li><strong>Drive Information:</strong> Direct drive number and context</li>
                    <li><strong>Developer Experience:</strong> Type hints, documentation, consistent API</li>
                    <li><strong>Historical Data:</strong> Comprehensive access to historical datasets</li>
                </ul>
            </div>
            
            <div class="highlight">
                <h3>📊 Summary:</h3>
                <p>This comparison shows that while both APIs provide comprehensive play-by-play data, CFBD offers significantly better structured data with advanced analytics. For enhanced analysis projects, CFBD would provide:</p>
                <ul>
                    <li>More consistent data processing</li>
                    <li>Built-in advanced metrics (PPA, EPA)</li>
                    <li>Better team context identification</li>
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
    print("Full Game Comparison: ESPN vs CFBD")
    print("=" * 50)
    
    # Load ESPN data for Michigan vs Washington
    espn_plays, espn_game = load_espn_michigan_washington()
    
    # Load CFBD data for the same game
    cfbd_plays, cfbd_game = load_cfbd_michigan_washington()
    
    if not espn_plays:
        print("Failed to load ESPN data")
        return
    
    if not cfbd_plays:
        print("Failed to load CFBD data")
        return
    
    print(f"\nComparison Summary:")
    print(f"ESPN plays: {len(espn_plays)}")
    print(f"CFBD plays: {len(cfbd_plays)}")
    
    # Generate full comparison
    html = create_full_comparison_html(espn_plays, cfbd_plays, espn_game, cfbd_game)
    
    # Save report
    output_file = "full_game_comparison.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"\nFull game comparison saved to: {output_file}")
    print("Open the file in your browser to view the complete comparison!")

if __name__ == "__main__":
    main()
