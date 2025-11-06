#!/usr/bin/env python3
"""
Generate HTML table with play-by-play data and win probability
"""

import json
import requests
from datetime import datetime

def fetch_win_probability_data(game_id):
    """Fetch win probability data from ESPN API"""
    url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('winprobability', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching win probability data: {e}")
        return []

def load_game_data():
    """Load existing game data"""
    with open('data/game_401752873/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    
    with open('data/game_401752873/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return game_data, teams_data

def get_team_name(team_id, teams_data):
    """Get team name from team ID"""
    team_id_str = str(team_id)
    if team_id_str in teams_data:
        return teams_data[team_id_str].get('displayName', f'Team {team_id}')
    return f'Team {team_id}'

def create_win_probability_lookup(win_prob_data):
    """Create a lookup dictionary for win probability data"""
    lookup = {}
    for entry in win_prob_data:
        lookup[entry['playId']] = entry
    return lookup

def get_win_probability_change(current_win_prob, previous_win_prob):
    """Calculate win probability change"""
    if previous_win_prob is None:
        return 0
    return current_win_prob - previous_win_prob

def get_change_color_class(change):
    """Get CSS class for win probability change"""
    if change > 0.05:  # 5% or more increase
        return "win-prob-increase-high"
    elif change > 0.01:  # 1% or more increase
        return "win-prob-increase"
    elif change < -0.05:  # 5% or more decrease
        return "win-prob-decrease-high"
    elif change < -0.01:  # 1% or more decrease
        return "win-prob-decrease"
    else:
        return "win-prob-neutral"

def generate_html_table(game_data, teams_data, win_prob_lookup):
    """Generate HTML table with play-by-play data and win probability"""
    
    plays = game_data.get('plays', {}).get('items', [])
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Washington vs Michigan - Play by Play with Win Probability</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        
        .header {{
            background-color: #1e3a8a;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        
        .header p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        
        .table-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        th {{
            background-color: #374151;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        td {{
            padding: 8px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        
        tr:hover {{
            background-color: #f3f4f6;
        }}
        
        .play-number {{
            text-align: center;
            font-weight: bold;
            color: #6b7280;
        }}
        
        .quarter {{
            text-align: center;
            font-weight: bold;
            color: #1f2937;
        }}
        
        .time {{
            font-family: monospace;
            font-weight: bold;
            color: #374151;
        }}
        
        .win-prob {{
            text-align: center;
            font-weight: bold;
        }}
        
        .win-prob-increase-high {{
            background-color: #dcfce7;
            color: #166534;
        }}
        
        .win-prob-increase {{
            background-color: #f0fdf4;
            color: #15803d;
        }}
        
        .win-prob-decrease-high {{
            background-color: #fef2f2;
            color: #dc2626;
        }}
        
        .win-prob-decrease {{
            background-color: #fef7f7;
            color: #dc2626;
        }}
        
        .win-prob-neutral {{
            background-color: #f9fafb;
            color: #6b7280;
        }}
        
        .change {{
            text-align: center;
            font-weight: bold;
        }}
        
        .change.positive {{
            color: #166534;
        }}
        
        .change.negative {{
            color: #dc2626;
        }}
        
        .play-description {{
            max-width: 400px;
            word-wrap: break-word;
        }}
        
        .scoring-play {{
            background-color: #fef3c7;
            font-weight: bold;
        }}
        
        .penalty {{
            background-color: #fef2f2;
        }}
        
        .touchdown {{
            background-color: #dcfce7;
            font-weight: bold;
        }}
        
        .interception {{
            background-color: #fef2f2;
            font-weight: bold;
        }}
        
        .stats {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f3f4f6;
            border-radius: 8px;
        }}
        
        .stats h3 {{
            margin-top: 0;
            color: #374151;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            background-color: white;
            padding: 10px;
            border-radius: 6px;
            border-left: 4px solid #3b82f6;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: bold;
        }}
        
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #1f2937;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Washington Huskies vs Michigan Wolverines</h1>
        <p>Play-by-Play with Win Probability | October 18, 2025 | Game ID: 401752873</p>
    </div>
    
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th style="width: 50px;">#</th>
                    <th style="width: 50px;">Qtr</th>
                    <th style="width: 80px;">Time</th>
                    <th style="width: 100px;">Win Prob</th>
                    <th style="width: 80px;">Change</th>
                    <th style="width: 100px;">Down/Dist</th>
                    <th style="width: 120px;">Yard Line</th>
                    <th>Play Description</th>
                </tr>
            </thead>
            <tbody>
"""
    
    previous_win_prob = None
    scoring_plays = 0
    penalties = 0
    interceptions = 0
    touchdowns = 0
    
    for i, play in enumerate(plays):
        play_id = play.get('id', '')
        win_prob_data = win_prob_lookup.get(play_id, {})
        current_win_prob = win_prob_data.get('homeWinPercentage', 0)
        
        # Calculate change
        change = get_win_probability_change(current_win_prob, previous_win_prob)
        change_class = get_change_color_class(change)
        
        # Get play details
        quarter = play.get('period', {}).get('number', '')
        time = play.get('clock', {}).get('displayValue', '')
        down_distance = play.get('start', {}).get('downDistanceText', '')
        yard_line = play.get('start', {}).get('possessionText', '')
        play_text = play.get('shortText', '')
        play_type = play.get('type', {}).get('text', '')
        
        # Determine row classes
        row_classes = []
        if play.get('scoringPlay', False):
            row_classes.append('scoring-play')
            scoring_plays += 1
        if 'Penalty' in play_type:
            row_classes.append('penalty')
            penalties += 1
        if 'Touchdown' in play_type:
            row_classes.append('touchdown')
            touchdowns += 1
        if 'Interception' in play_type:
            row_classes.append('interception')
            interceptions += 1
        
        row_class = ' '.join(row_classes)
        
        # Format change
        if change > 0:
            change_str = f"+{change*100:.1f}%"
            change_class_css = "positive"
        elif change < 0:
            change_str = f"{change*100:.1f}%"
            change_class_css = "negative"
        else:
            change_str = "0.0%"
            change_class_css = ""
        
        # Format win probability
        win_prob_str = f"{current_win_prob*100:.1f}%"
        
        html += f"""
                <tr class="{row_class}">
                    <td class="play-number">{i+1}</td>
                    <td class="quarter">Q{quarter}</td>
                    <td class="time">{time}</td>
                    <td class="win-prob {change_class}">{win_prob_str}</td>
                    <td class="change {change_class_css}">{change_str}</td>
                    <td>{down_distance}</td>
                    <td>{yard_line}</td>
                    <td class="play-description">{play_text}</td>
                </tr>
"""
        
        previous_win_prob = current_win_prob
    
    # Add stats section
    html += f"""
            </tbody>
        </table>
    </div>
    
    <div class="stats">
        <h3>Game Statistics</h3>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-label">Total Plays</div>
                <div class="stat-value">{len(plays)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Scoring Plays</div>
                <div class="stat-value">{scoring_plays}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Penalties</div>
                <div class="stat-value">{penalties}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Touchdowns</div>
                <div class="stat-value">{touchdowns}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Interceptions</div>
                <div class="stat-value">{interceptions}</div>
            </div>
        </div>
    </div>
    
    <script>
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Highlight rows with significant win probability changes
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach(row => {{
                const changeCell = row.querySelector('.change');
                if (changeCell) {{
                    const changeText = changeCell.textContent;
                    if (changeText.includes('+') && parseFloat(changeText) > 5) {{
                        row.style.borderLeft = '4px solid #10b981';
                    }} else if (changeText.includes('-') && parseFloat(changeText) < -5) {{
                        row.style.borderLeft = '4px solid #ef4444';
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    
    return html

def main():
    print("Generating Play-by-Play HTML Table")
    print("Game ID: 401752873 | Date: October 18, 2025")
    print("=" * 50)
    
    game_id = 401752873
    
    # Fetch win probability data
    print("Fetching win probability data...")
    win_prob_data = fetch_win_probability_data(game_id)
    
    if not win_prob_data:
        print("No win probability data available")
        return
    
    # Load existing game data
    game_data, teams_data = load_game_data()
    
    # Create win probability lookup
    win_prob_lookup = create_win_probability_lookup(win_prob_data)
    
    # Generate HTML
    print("Generating HTML table...")
    html = generate_html_table(game_data, teams_data, win_prob_lookup)
    
    # Save HTML file
    import os
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/playbyplay_table.html', 'w') as f:
        f.write(html)
    
    print(f"HTML table saved to: data/game_401752873/playbyplay_table.html")
    print(f"Open the file in your browser to view the interactive table!")

if __name__ == "__main__":
    main()
