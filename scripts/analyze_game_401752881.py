#!/usr/bin/env python3
"""
Comprehensive analysis for game 401752881
Fetches ESPN data and generates complete analysis report
"""

import json
import requests
import os
import re
from datetime import datetime

def fetch_game_data(game_id):
    """Fetch basic game data from ESPN API"""
    print(f"Fetching game data for {game_id}...")
    
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Successfully fetched game data")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching game data: {e}")
        return None

def fetch_all_plays(game_id):
    """Fetch all pages of play-by-play data from ESPN API"""
    print(f"Fetching all play-by-play data for {game_id}...")
    
    all_plays = []
    page = 1
    
    while True:
        print(f"  Fetching page {page}...")
        url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays"
        params = {
            'page': page,
            'pageSize': 25
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data or not data['items']:
                print(f"  No more plays on page {page}")
                break
                
            all_plays.extend(data['items'])
            print(f"  ✓ Fetched {len(data['items'])} plays from page {page}")
            
            # Check if this is the last page
            if page >= data.get('pageCount', 1):
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error fetching page {page}: {e}")
            break
    
    print(f"  ✓ Total plays fetched: {len(all_plays)}")
    return all_plays

def fetch_win_probability_data(game_id):
    """Fetch win probability data from ESPN API"""
    print(f"Fetching win probability data for {game_id}...")
    
    url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        wp_data = data.get('winprobability', [])
        print(f"  ✓ Successfully fetched {len(wp_data)} win probability entries")
        return wp_data
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching win probability data: {e}")
        return []

def create_win_probability_lookup(win_prob_data):
    """Create lookup for win probability data by playId"""
    win_prob_lookup = {}
    
    if isinstance(win_prob_data, list):
        entries = win_prob_data
    else:
        entries = win_prob_data.get('winprobability', [])
    
    for entry in entries:
        play_id = entry.get('playId')
        if play_id:
            win_prob_lookup[play_id] = entry
    
    return win_prob_lookup

def save_data(game_id, game_data, all_plays, win_prob_data):
    """Save all fetched data to files"""
    print(f"Saving data for game {game_id}...")
    
    # Create directory if it doesn't exist
    os.makedirs(f'data/game_{game_id}', exist_ok=True)
    
    # Save complete game data
    complete_data = {
        "header": game_data,
        "plays": {
            "items": all_plays,
            "count": len(all_plays),
            "pageIndex": 1,
            "pageSize": len(all_plays),
            "pageCount": 1
        },
        "fetched_at": datetime.now().isoformat()
    }
    
    filename = f'data/game_{game_id}/complete_game_data.json'
    with open(filename, 'w') as f:
        json.dump(complete_data, f, indent=2)
    print(f"  ✓ Saved complete game data to {filename}")
    
    # Save win probability data
    wp_filename = f'data/game_{game_id}/win_probability_data.json'
    with open(wp_filename, 'w') as f:
        json.dump(win_prob_data, f, indent=2)
    print(f"  ✓ Saved win probability data to {wp_filename}")
    
    # Save ESPN play-by-play with WPA
    espn_pbp_with_wpa = []
    win_prob_lookup = create_win_probability_lookup(win_prob_data)
    
    for i, play in enumerate(all_plays):
        play_id = play.get('id')
        play_data = {
            'play_id': play_id,
            'sequence_number': play.get('sequenceNumber'),
            'type': play.get('type'),
            'text': play.get('text'),
            'short_text': play.get('shortText'),
            'away_score': play.get('awayScore'),
            'home_score': play.get('homeScore'),
            'period': play.get('period'),
            'clock': play.get('clock'),
            'scoring_play': play.get('scoringPlay'),
            'priority': play.get('priority'),
            'score_value': play.get('scoreValue'),
            'team': play.get('team'),
            'start': play.get('start'),
            'end': play.get('end'),
            'stat_yardage': play.get('statYardage')
        }
        
        # Add WPA data if available
        wp_entry = win_prob_lookup.get(play_id)
        if wp_entry:
            # Calculate WPA (Win Probability Added)
            home_wp = wp_entry.get('homeWinPercentage', 0)
            
            # Find previous play's win probability
            wpa = 0.0
            if i > 0:
                prev_play_id = all_plays[i-1].get('id')
                prev_wp_entry = win_prob_lookup.get(prev_play_id)
                if prev_wp_entry:
                    prev_home_wp = prev_wp_entry.get('homeWinPercentage', 0)
                    wpa = home_wp - prev_home_wp
            
            play_data['wpa'] = {
                'wpa': wpa,
                'wpa_percentage': wpa * 100,
                'home_win_probability': home_wp,
                'home_win_probability_percentage': home_wp * 100,
                'away_win_probability': 1 - home_wp,
                'away_win_probability_percentage': (1 - home_wp) * 100
            }
        else:
            play_data['wpa'] = {
                'wpa': 0.0,
                'wpa_percentage': 0.0,
                'home_win_probability': 0.0,
                'home_win_probability_percentage': 0.0,
                'away_win_probability': 0.0,
                'away_win_probability_percentage': 0.0
            }
        
        espn_pbp_with_wpa.append(play_data)
    
    pbp_filename = f'espn_pbp_with_wpa_{game_id}.json'
    with open(pbp_filename, 'w') as f:
        json.dump(espn_pbp_with_wpa, f, indent=2)
    print(f"  ✓ Saved play-by-play with WPA to {pbp_filename}")
    
    return complete_data

def get_team_names(game_data):
    """Extract team names from game data"""
    try:
        competitors = game_data.get('competitions', [{}])[0].get('competitors', [])
        if len(competitors) >= 2:
            away_team = competitors[0].get('team', {}).get('displayName', 'Away Team')
            home_team = competitors[1].get('team', {}).get('displayName', 'Home Team')
            return away_team, home_team
    except:
        pass
    return 'Away Team', 'Home Team'

def generate_html_analysis(game_id, complete_data, win_prob_data):
    """Generate comprehensive HTML analysis report"""
    print(f"Generating HTML analysis for game {game_id}...")
    
    all_plays = complete_data.get('plays', {}).get('items', [])
    game_data = complete_data.get('header', {})
    win_prob_lookup = create_win_probability_lookup(win_prob_data)
    
    # Get game info
    game_name = game_data.get('name', f'Game {game_id}')
    game_date = game_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    away_team, home_team = get_team_names(game_data)
    
    # Create aligned data: match win probability to plays by playId
    aligned_data = []
    for i, play in enumerate(all_plays):
        play_id = play.get('id')
        wp_data = win_prob_lookup.get(play_id)
        
        if wp_data:
            aligned_data.append({
                'play_index': i,
                'play_number': i + 1,
                'play': play,
                'wp_data': wp_data
            })
    
    # If alignment by ID fails, try positional alignment
    if len(aligned_data) < len(win_prob_data) * 0.5:
        print("  Warning: Low alignment rate, trying positional alignment")
        aligned_data = []
        win_prob_list = list(win_prob_lookup.values())
        min_len = min(len(all_plays), len(win_prob_list))
        for i in range(min_len):
            aligned_data.append({
                'play_index': i,
                'play_number': i + 1,
                'play': all_plays[i],
                'wp_data': win_prob_list[i]
            })
    
    # Sort by play number to ensure chronological order
    aligned_data.sort(key=lambda x: x['play_number'])
    
    print(f"  ✓ Aligned {len(aligned_data)} plays with win probability data")
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Play-by-Play Analysis - {game_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .win-probability-chart {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        .chart-container {{
            position: relative;
            width: 100%;
            height: 400px;
        }}
        .play-by-play-table {{
            margin: 30px 0;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }}
        td {{
            padding: 12px 10px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .play-number {{
            font-weight: bold;
            color: #667eea;
        }}
        .quarter {{
            font-weight: bold;
            color: #666;
        }}
        .time {{
            font-family: monospace;
            color: #666;
        }}
        .win-prob {{
            font-weight: bold;
        }}
        .win-prob.high {{
            color: #28a745;
        }}
        .win-prob.medium {{
            color: #ffc107;
        }}
        .win-prob.low {{
            color: #dc3545;
        }}
        .change {{
            font-weight: bold;
        }}
        .change.positive {{
            color: #28a745;
        }}
        .change.negative {{
            color: #dc3545;
        }}
        .play-description {{
            max-width: 400px;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enhanced Play-by-Play Analysis</h1>
            <p>{game_name} | {game_date} | Game ID: {game_id}</p>
        </div>
        
        <div class="content">
            <div class="stats-summary">
                <div class="stat-card">
                    <h3>Total Plays</h3>
                    <div class="value">{len(all_plays)}</div>
                </div>
                <div class="stat-card">
                    <h3>Aligned Plays</h3>
                    <div class="value">{len(aligned_data)}</div>
                </div>
                <div class="stat-card">
                    <h3>Win Prob Entries</h3>
                    <div class="value">{len(win_prob_data)}</div>
                </div>
            </div>
            
            <div class="win-probability-chart">
                <h3>Win Probability Chart</h3>
                <div class="chart-container">
                    <canvas id="winProbabilityChart"></canvas>
                </div>
            </div>
            
            <div class="play-by-play-table">
                <h3>Complete Play-by-Play with Win Probability</h3>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 50px;">#</th>
                            <th style="width: 50px;">Qtr</th>
                            <th style="width: 80px;">Time</th>
                            <th style="width: 100px;">Win Prob</th>
                            <th style="width: 80px;">Change</th>
                            <th>Play Description</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add play-by-play rows
    for i, item in enumerate(aligned_data):
        play = item['play']
        wp_data = item['wp_data']
        
        home_wp = wp_data.get('homeWinPercentage', 0) * 100
        away_wp = (1 - wp_data.get('homeWinPercentage', 0)) * 100
        
        # Calculate change from previous play
        wp_change = 0
        if i > 0:
            prev_wp_data = aligned_data[i-1]['wp_data']
            prev_home_wp = prev_wp_data.get('homeWinPercentage', 0) * 100
            wp_change = home_wp - prev_home_wp
        
        # Extract quarter and time
        quarter = f"Q{play.get('period', {}).get('number', 1)}"
        clock = play.get('clock', {})
        time = clock.get('displayValue', '15:00') if clock else '15:00'
        
        # Get play description
        play_text = play.get('text', 'N/A')
        
        # Determine win probability styling
        if home_wp >= 70:
            wp_class = "high"
        elif home_wp >= 30:
            wp_class = "medium"
        else:
            wp_class = "low"
        
        # Determine change styling
        if wp_change > 0:
            change_class = "positive"
            change_text = f"+{wp_change:.1f}%"
        elif wp_change < 0:
            change_class = "negative"
            change_text = f"{wp_change:.1f}%"
        else:
            change_class = ""
            change_text = "0.0%"
        
        html += f"""
                        <tr>
                            <td class="play-number">{item['play_number']}</td>
                            <td class="quarter">{quarter}</td>
                            <td class="time">{time}</td>
                            <td class="win-prob {wp_class}">{home_wp:.1f}%</td>
                            <td class="change {change_class}">{change_text}</td>
                            <td class="play-description">{play_text}</td>
                        </tr>
"""
    
    # Create chart data
    chart_labels = [f"Play {i+1}" for i in range(len(aligned_data))]
    home_data = [item['wp_data'].get('homeWinPercentage', 0) * 100 for item in aligned_data]
    away_data = [(1 - item['wp_data'].get('homeWinPercentage', 0)) * 100 for item in aligned_data]
    
    html += f"""
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('winProbabilityChart').getContext('2d');
        
        const winProbabilityChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [{{
                    label: '{home_team} Win %',
                    data: {json.dumps(home_data)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: false
                }}, {{
                    label: '{away_team} Win %',
                    data: {json.dumps(away_data)},
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Win Probability Throughout Game'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Win Probability (%)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Play Number'
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
    print("=" * 60)
    print("Comprehensive Game Analysis")
    print("=" * 60)
    
    game_id = 401752881
    
    # Fetch all data
    game_data = fetch_game_data(game_id)
    if not game_data:
        print("Error: Could not fetch game data")
        return
    
    all_plays = fetch_all_plays(game_id)
    if not all_plays:
        print("Error: Could not fetch plays")
        return
    
    win_prob_data = fetch_win_probability_data(game_id)
    
    # Save data
    complete_data = save_data(game_id, game_data, all_plays, win_prob_data)
    
    # Generate HTML analysis
    html = generate_html_analysis(game_id, complete_data, win_prob_data)
    
    # Save HTML
    html_filename = f'data/game_{game_id}/enhanced_analysis.html'
    with open(html_filename, 'w') as f:
        f.write(html)
    
    print(f"\n✓ Analysis complete!")
    print(f"✓ HTML report saved to: {html_filename}")
    print(f"\nSummary:")
    print(f"  - Total plays: {len(all_plays)}")
    print(f"  - Win probability entries: {len(win_prob_data)}")
    print(f"  - Data files saved in: data/game_{game_id}/")
    print(f"\nOpen {html_filename} in your browser to view the analysis!")

if __name__ == "__main__":
    main()

