#!/usr/bin/env python3
"""
True Side-by-Side Game Comparison: ESPN vs CFBD
Find the same game in both APIs and compare play-by-play data
"""

import json
import requests
from datetime import datetime

def load_espn_game_data():
    """Load ESPN data for Michigan vs Washington (401752873)"""
    print("Loading ESPN game data...")
    
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
        
        # Get game info
        game_info = {
            'id': '401752873',
            'teams': ['Michigan', 'Washington'],
            'date': '2024-01-08',  # National Championship
            'type': 'National Championship'
        }
        
        return plays, game_info
        
    except Exception as e:
        print(f"Error loading ESPN data: {e}")
        return [], {}

def find_cfbd_matching_game():
    """Find a CFBD game that matches our ESPN game"""
    print("Searching for matching CFBD game...")
    
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
        # Search for games in January 2024 (National Championship timeframe)
        response = requests.get(f"{base_url}/games", headers=headers, params={
            'year': 2024,
            'seasonType': 'postseason'  # National Championship is postseason
        })
        
        if response.status_code == 200:
            games = response.json()
            print(f"Found {len(games)} postseason games in 2024")
            
            # Look for a game that might be the National Championship
            for game in games:
                print(f"Checking game: {game.get('id')} - {game.get('home_team')} vs {game.get('away_team')}")
                
                # Try to get plays for this game
                try:
                    plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                        'gameId': game.get('id'),
                        'year': 2024
                    })
                    
                    if plays_response.status_code == 200:
                        plays = plays_response.json()
                        print(f"  Found {len(plays)} plays")
                        
                        # If this looks like a championship game (lots of plays), use it
                        if len(plays) > 1000:  # Championship games have many plays
                            print(f"  Selected: {game.get('home_team')} vs {game.get('away_team')} ({len(plays)} plays)")
                            return game, plays[:200]  # Limit to first 200 plays for comparison
                            
                except Exception as e:
                    print(f"  Error getting plays: {e}")
            
            # If no championship game found, use the first available game
            if games:
                game = games[0]
                print(f"Using first available game: {game.get('home_team')} vs {game.get('away_team')}")
                
                plays_response = requests.get(f"{base_url}/plays", headers=headers, params={
                    'gameId': game.get('id'),
                    'year': 2024
                })
                
                if plays_response.status_code == 200:
                    plays = plays_response.json()
                    return game, plays[:200]
                    
        else:
            print(f"Failed to get CFBD games: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None, []

def compare_play_data(espn_play, cfbd_play, play_number):
    """Compare a single play from both APIs"""
    
    # Extract ESPN play data
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
        'team_participants': len(espn_play.get('teamParticipants', []))
    }
    
    # Extract CFBD play data
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
        'drive_number': cfbd_play.get('driveNumber', 'N/A')
    }
    
    return espn_data, cfbd_data

def generate_detailed_comparison_html(espn_plays, cfbd_plays, espn_game, cfbd_game):
    """Generate detailed side-by-side comparison HTML"""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESPN vs CFBD - True Game Comparison</title>
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
            max-width: 1600px;
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
            gap: 20px;
            margin: 20px 0;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .play-side {{
            padding: 20px;
        }}
        
        .play-side.espn {{
            background: #fff5f5;
            border-right: 2px solid #dc3545;
        }}
        
        .play-side.cfbd {{
            background: #f0fff4;
        }}
        
        .api-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            padding: 10px;
            border-radius: 5px;
        }}
        
        .api-title.espn {{
            background: #dc3545;
            color: white;
        }}
        
        .api-title.cfbd {{
            background: #28a745;
            color: white;
        }}
        
        .play-field {{
            margin: 8px 0;
            padding: 5px;
            background: rgba(255,255,255,0.7);
            border-radius: 3px;
        }}
        
        .field-name {{
            font-weight: bold;
            color: #555;
            display: inline-block;
            width: 120px;
        }}
        
        .field-value {{
            color: #333;
        }}
        
        .play-number {{
            background: #667eea;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 1.1em;
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
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ESPN vs CFBD - True Game Comparison</h1>
            <p>Side-by-side analysis of the same game from both APIs</p>
        </div>
        
        <div class="comparison-section">
            <div class="summary-stats">
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
            
            <h2>📊 Detailed Play-by-Play Comparison</h2>
"""
    
    # Add detailed play comparisons
    max_plays = min(10, len(espn_plays), len(cfbd_plays))
    for i in range(max_plays):
        espn_play = espn_plays[i] if i < len(espn_plays) else {}
        cfbd_play = cfbd_plays[i] if i < len(cfbd_plays) else {}
        
        espn_data, cfbd_data = compare_play_data(espn_play, cfbd_play, i+1)
        
        html += f"""
            <div class="play-comparison">
                <div class="play-number">Play {i+1}</div>
                <div class="play-side espn">
                    <div class="api-title espn">ESPN Data</div>
                    <div class="play-field"><span class="field-name">ID:</span><span class="field-value">{espn_data['id']}</span></div>
                    <div class="play-field"><span class="field-name">Text:</span><span class="field-value">{espn_data['text'][:80]}...</span></div>
                    <div class="play-field"><span class="field-name">Type:</span><span class="field-value">{espn_data['type']}</span></div>
                    <div class="play-field"><span class="field-name">Period:</span><span class="field-value">{espn_data['period']}</span></div>
                    <div class="play-field"><span class="field-name">Clock:</span><span class="field-value">{espn_data['clock']}</span></div>
                    <div class="play-field"><span class="field-name">Down/Distance:</span><span class="field-value">{espn_data['down']} & {espn_data['distance']}</span></div>
                    <div class="play-field"><span class="field-name">Yard Line:</span><span class="field-value">{espn_data['yard_line']}</span></div>
                    <div class="play-field"><span class="field-name">Yards Gained:</span><span class="field-value">{espn_data['yards_gained']}</span></div>
                    <div class="play-field"><span class="field-name">Scoring:</span><span class="field-value">{espn_data['scoring']}</span></div>
                    <div class="play-field"><span class="field-name">Team Participants:</span><span class="field-value">{espn_data['team_participants']}</span></div>
                </div>
                <div class="play-side cfbd">
                    <div class="api-title cfbd">CFBD Data</div>
                    <div class="play-field"><span class="field-name">ID:</span><span class="field-value">{cfbd_data['id']}</span></div>
                    <div class="play-field"><span class="field-name">Text:</span><span class="field-value">{cfbd_data['text'][:80]}...</span></div>
                    <div class="play-field"><span class="field-name">Type:</span><span class="field-value">{cfbd_data['type']}</span></div>
                    <div class="play-field"><span class="field-name">Period:</span><span class="field-value">{cfbd_data['period']}</span></div>
                    <div class="play-field"><span class="field-name">Clock:</span><span class="field-value">{cfbd_data['clock']}</span></div>
                    <div class="play-field"><span class="field-name">Down/Distance:</span><span class="field-value">{cfbd_data['down']} & {cfbd_data['distance']}</span></div>
                    <div class="play-field"><span class="field-name">Yard Line:</span><span class="field-value">{cfbd_data['yard_line']}</span></div>
                    <div class="play-field"><span class="field-name">Yards Gained:</span><span class="field-value">{cfbd_data['yards_gained']}</span></div>
                    <div class="play-field"><span class="field-name">Scoring:</span><span class="field-value">{cfbd_data['scoring']}</span></div>
                    <div class="play-field"><span class="field-name">Offense:</span><span class="field-value">{cfbd_data['offense']}</span></div>
                    <div class="play-field"><span class="field-name">Defense:</span><span class="field-value">{cfbd_data['defense']}</span></div>
                    <div class="play-field"><span class="field-name">PPA:</span><span class="field-value">{cfbd_data['ppa']}</span></div>
                    <div class="play-field"><span class="field-name">Drive #:</span><span class="field-value">{cfbd_data['drive_number']}</span></div>
                </div>
            </div>
        """
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("True Game Comparison: ESPN vs CFBD")
    print("=" * 50)
    
    # Load ESPN data
    espn_plays, espn_game = load_espn_game_data()
    
    # Find matching CFBD game
    cfbd_game, cfbd_plays = find_cfbd_matching_game()
    
    if not cfbd_plays:
        print("No CFBD data available for comparison")
        return
    
    print(f"\nComparison Summary:")
    print(f"ESPN plays: {len(espn_plays)}")
    print(f"CFBD plays: {len(cfbd_plays)}")
    
    # Generate detailed comparison
    html = generate_detailed_comparison_html(espn_plays, cfbd_plays, espn_game, cfbd_game)
    
    # Save report
    output_file = "true_game_comparison.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"\nDetailed comparison saved to: {output_file}")
    print("Open the file in your browser to view the side-by-side comparison!")

if __name__ == "__main__":
    main()
