#!/usr/bin/env python3
"""
Simple test chart to debug penalty positioning
"""

import json
import requests

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
    return game_data

def create_simple_test_chart():
    """Create a simple test chart with penalty markers"""
    
    # Get data
    game_data = load_game_data()
    plays = game_data.get('plays', {}).get('items', [])
    win_prob_data = fetch_win_probability_data(401752873)
    
    # Find penalties
    penalties = []
    for i, play in enumerate(plays):
        play_type_id = play.get('type', {}).get('id', '')
        if play_type_id == '8':  # Penalty type ID
            short_text = play.get('shortText', '')
            team_committed = "Unknown"
            if 'washington penalty' in short_text.lower():
                team_committed = "Washington"
            elif 'michigan penalty' in short_text.lower():
                team_committed = "Michigan"
            
            penalties.append({
                'play_number': i + 1,
                'play_id': play.get('id', ''),
                'team': team_committed,
                'short_text': short_text,
                'yards': play.get('statYardage', 0)
            })
    
    # Create win probability lookup
    win_prob_by_play_id = {}
    for i, entry in enumerate(win_prob_data):
        play_id = entry.get('playId', '')
        if play_id:
            win_prob_by_play_id[play_id] = {
                'index': i,
                'homeWinPercentage': entry['homeWinPercentage']
            }
    
    # Prepare chart data
    labels = []
    home_data = []
    away_data = []
    
    for i, entry in enumerate(win_prob_data):
        labels.append(f"Play {i+1}")
        home_data.append(entry['homeWinPercentage'] * 100)
        away_data.append((1 - entry['homeWinPercentage']) * 100)
    
    # Create penalty markers
    washington_penalty_points = []
    michigan_penalty_points = []
    
    for penalty in penalties:
        play_id = penalty['play_id']
        if play_id in win_prob_by_play_id:
            wp_data = win_prob_by_play_id[play_id]
            x_coord = wp_data['index']
            y_coord = wp_data['homeWinPercentage'] * 100
            
            if penalty['team'] == 'Washington':
                washington_penalty_points.append({
                    'x': x_coord,
                    'y': y_coord,
                    'yards': penalty['yards'],
                    'description': penalty['short_text']
                })
            elif penalty['team'] == 'Michigan':
                michigan_penalty_points.append({
                    'x': x_coord,
                    'y': y_coord,
                    'yards': penalty['yards'],
                    'description': penalty['short_text']
                })
    
    # Create simple HTML with test chart
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Penalty Chart Test</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Penalty Chart Test</h1>
    <p>Washington penalties: {len(washington_penalty_points)}</p>
    <p>Michigan penalties: {len(michigan_penalty_points)}</p>
    <p>Washington coords: {[(p['x'], p['y']) for p in washington_penalty_points]}</p>
    <p>Michigan coords: {[(p['x'], p['y']) for p in michigan_penalty_points]}</p>
    
    <canvas id="testChart" width="800" height="400"></canvas>
    
    <script>
        const ctx = document.getElementById('testChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels[::10])}, // Every 10th label
                datasets: [{{
                    label: 'Michigan Win %',
                    data: {json.dumps(home_data[::10])},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true
                }}, {{
                    label: 'Washington Win %',
                    data: {json.dumps(away_data[::10])},
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.1,
                    fill: true
                }}, {{
                    label: 'Washington Penalties',
                    data: {json.dumps([{'x': p['x'], 'y': p['y']} for p in washington_penalty_points])},
                    type: 'scatter',
                    backgroundColor: '#ff6b6b',
                    borderColor: '#ff6b6b',
                    pointRadius: 12,
                    pointHoverRadius: 15,
                    showLine: false
                }}, {{
                    label: 'Michigan Penalties',
                    data: {json.dumps([{'x': p['x'], 'y': p['y']} for p in michigan_penalty_points])},
                    type: 'scatter',
                    backgroundColor: '#4ecdc4',
                    borderColor: '#4ecdc4',
                    pointRadius: 12,
                    pointHoverRadius: 15,
                    showLine: false
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    x: {{
                        type: 'linear',
                        position: 'bottom'
                    }},
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    return html

def main():
    print("Creating simple test chart...")
    html = create_simple_test_chart()
    
    with open('data/game_401752873/test_chart.html', 'w') as f:
        f.write(html)
    
    print("Test chart saved to: data/game_401752873/test_chart.html")
    print("Open this file to see if the penalty markers appear correctly")

if __name__ == "__main__":
    main()
