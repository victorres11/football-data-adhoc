#!/usr/bin/env python3
"""
Simple debug chart to understand the coordinate system
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

def create_debug_chart():
    """Create a simple debug chart"""
    
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
    
    # Prepare simple chart data
    labels = [f"Play {i+1}" for i in range(0, len(win_prob_data), 10)]  # Every 10th play
    home_data = [entry['homeWinPercentage'] * 100 for i, entry in enumerate(win_prob_data) if i % 10 == 0]
    away_data = [(1 - entry['homeWinPercentage']) * 100 for i, entry in enumerate(win_prob_data) if i % 10 == 0]
    
    # Create penalty markers with simple coordinates
    washington_penalties = []
    michigan_penalties = []
    
    for penalty in penalties:
        play_id = penalty['play_id']
        if play_id in win_prob_by_play_id:
            wp_data = win_prob_by_play_id[play_id]
            # Calculate exact position between chart data points
            play_number = penalty['play_number']
            chart_interval = 10  # Every 10th play
            x_coord = (play_number - 1) / chart_interval  # Exact position
            y_coord = wp_data['homeWinPercentage'] * 100
            
            if penalty['team'] == 'Washington':
                washington_penalties.append({
                    'x': x_coord,
                    'y': y_coord,
                    'play_number': penalty['play_number'],
                    'description': penalty['short_text']
                })
            elif penalty['team'] == 'Michigan':
                michigan_penalties.append({
                    'x': x_coord,
                    'y': y_coord,
                    'play_number': penalty['play_number'],
                    'description': penalty['short_text']
                })
    
    # Create HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Debug Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Debug Chart - Penalty Positioning</h1>
    
    <div style="margin: 20px; padding: 20px; background: #f0f0f0;">
        <h3>Debug Info:</h3>
        <p><strong>Total plays:</strong> {len(plays)}</p>
        <p><strong>Total win prob entries:</strong> {len(win_prob_data)}</p>
        <p><strong>Chart labels:</strong> {len(labels)} (every 10th)</p>
        <p><strong>Washington penalties:</strong> {len(washington_penalties)}</p>
        <p><strong>Michigan penalties:</strong> {len(michigan_penalties)}</p>
        
        <h4>Washington Penalty Coordinates:</h4>
        <ul>
"""
    
    for p in washington_penalties:
        html += f"<li>Play {p['play_number']}: x={p['x']}, y={p['y']:.1f}% - {p['description']}</li>"
    
    html += """
        </ul>
        
        <h4>Michigan Penalty Coordinates:</h4>
        <ul>
"""
    
    for p in michigan_penalties:
        html += f"<li>Play {p['play_number']}: x={p['x']}, y={p['y']:.1f}% - {p['description']}</li>"
    
    html += f"""
        </ul>
    </div>
    
    <canvas id="debugChart" width="800" height="400"></canvas>
    
    <script>
        const ctx = document.getElementById('debugChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Michigan Win %',
                    data: {json.dumps(home_data)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true
                }}, {{
                    label: 'Washington Win %',
                    data: {json.dumps(away_data)},
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.1,
                    fill: true
                }}, {{
                    label: 'Washington Penalties',
                    data: {json.dumps([{'x': p['x'], 'y': p['y']} for p in washington_penalties])},
                    type: 'scatter',
                    backgroundColor: '#ff6b6b',
                    borderColor: '#ff6b6b',
                    pointRadius: 15,
                    pointHoverRadius: 20,
                    showLine: false
                }}, {{
                    label: 'Michigan Penalties',
                    data: {json.dumps([{'x': p['x'], 'y': p['y']} for p in michigan_penalties])},
                    type: 'scatter',
                    backgroundColor: '#4ecdc4',
                    borderColor: '#4ecdc4',
                    pointRadius: 15,
                    pointHoverRadius: 20,
                    showLine: false
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    x: {{
                        type: 'linear',
                        position: 'bottom',
                        title: {{
                            display: true,
                            text: 'Chart Index (every 10th play)'
                        }}
                    }},
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Win Probability %'
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Debug Chart - Penalty Positioning'
                    }},
                    tooltip: {{
                        callbacks: {{
                            title: function(context) {{
                                return 'Play ' + (context[0].dataIndex * 10 + 1);
                            }},
                            label: function(context) {{
                                if (context.datasetIndex >= 2) {{
                                    const penaltyData = {json.dumps(washington_penalties + michigan_penalties)};
                                    const penalty = penaltyData[context.dataIndex];
                                    return [
                                        'Penalty: ' + penalty.description,
                                        'Play: ' + penalty.play_number,
                                        'Win Prob: ' + penalty.y.toFixed(1) + '%'
                                    ];
                                }}
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                            }}
                        }}
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
    print("Creating debug chart...")
    html = create_debug_chart()
    
    with open('data/game_401752873/debug_chart.html', 'w') as f:
        f.write(html)
    
    print("Debug chart saved to: data/game_401752873/debug_chart.html")
    print("This will show you exactly where the penalty markers are positioned")

if __name__ == "__main__":
    main()
