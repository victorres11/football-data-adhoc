#!/usr/bin/env python3
"""
Enhance HTML table with penalty analysis and win probability chart
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

def analyze_penalties(plays, win_prob_lookup):
    """Analyze how penalties affected the game"""
    penalties = []
    
    for i, play in enumerate(plays):
        play_type_id = play.get('type', {}).get('id', '')
        if play_type_id == '8':  # Penalty type ID
            play_id = play.get('id', '')
            win_prob_data = win_prob_lookup.get(play_id, {})
            current_win_prob = win_prob_data.get('homeWinPercentage', 0)
            
            # Get previous play's win probability
            prev_win_prob = None
            if i > 0:
                prev_play_id = plays[i-1].get('id', '')
                prev_win_prob_data = win_prob_lookup.get(prev_play_id, {})
                prev_win_prob = prev_win_prob_data.get('homeWinPercentage', 0)
            
            change = get_win_probability_change(current_win_prob, prev_win_prob)
            
            # Determine which team committed the penalty
            short_text = play.get('shortText', '').lower()
            team_committed = "Unknown"
            if 'washington penalty' in short_text:
                team_committed = "Washington"
            elif 'michigan penalty' in short_text:
                team_committed = "Michigan"
            
            penalties.append({
                'play': play,
                'play_number': i + 1,  # Add play number
                'win_prob': current_win_prob,
                'change': change,
                'team_committed': team_committed,
                'quarter': play.get('period', {}).get('number', ''),
                'time': play.get('clock', {}).get('displayValue', ''),
                'yards': play.get('statYardage', 0),
                'description': play.get('shortText', '')
            })
    
    return penalties

def generate_penalty_analysis_html(penalties):
    """Generate HTML for penalty analysis"""
    if not penalties:
        return "<p>No penalties found in this game.</p>"
    
    # Calculate statistics
    washington_penalties = [p for p in penalties if p['team_committed'] == 'Washington']
    michigan_penalties = [p for p in penalties if p['team_committed'] == 'Michigan']
    
    washington_yards = sum(p['yards'] for p in washington_penalties)
    michigan_yards = sum(p['yards'] for p in michigan_penalties)
    
    washington_win_prob_impact = sum(p['change'] for p in washington_penalties)
    michigan_win_prob_impact = sum(p['change'] for p in michigan_penalties)
    
    html = f"""
    <div class="penalty-analysis">
        <h3>Penalty Impact Analysis</h3>
        
        <div class="penalty-stats">
            <div class="stat-grid">
                <div class="stat-card">
                    <h4>Washington Penalties</h4>
                    <div class="stat-number">{len(washington_penalties)}</div>
                    <div class="stat-detail">{washington_yards} yards</div>
                    <div class="stat-detail">Win Prob Impact: {washington_win_prob_impact*100:+.1f}%</div>
                </div>
                <div class="stat-card">
                    <h4>Michigan Penalties</h4>
                    <div class="stat-number">{len(michigan_penalties)}</div>
                    <div class="stat-detail">{michigan_yards} yards</div>
                    <div class="stat-detail">Win Prob Impact: {michigan_win_prob_impact*100:+.1f}%</div>
                </div>
            </div>
        </div>
        
        <div class="penalty-table">
            <h4>Penalty Details</h4>
            <table class="penalty-details">
                <thead>
                    <tr>
                        <th>Qtr</th>
                        <th>Time</th>
                        <th>Team</th>
                        <th>Yards</th>
                        <th>Win Prob Change</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for penalty in penalties:
        change_str = f"{penalty['change']*100:+.1f}%"
        change_class = "positive" if penalty['change'] > 0 else "negative" if penalty['change'] < 0 else ""
        
        html += f"""
                    <tr>
                        <td>Q{penalty['quarter']}</td>
                        <td>{penalty['time']}</td>
                        <td>{penalty['team_committed']}</td>
                        <td>{penalty['yards']}</td>
                        <td class="{change_class}">{change_str}</td>
                        <td>{penalty['description']}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
"""
    
    return html

def generate_win_probability_chart(win_prob_data, penalties, plays):
    """Generate Chart.js chart for win probability with penalty markers"""
    if not win_prob_data:
        return "<p>No win probability data available for chart.</p>"
    
    # Create a lookup for win probability data by play ID
    win_prob_by_play_id = {}
    for i, entry in enumerate(win_prob_data):
        play_id = entry.get('playId', '')
        if play_id:
            win_prob_by_play_id[play_id] = {
                'index': i,
                'homeWinPercentage': entry['homeWinPercentage']
            }
    
    # Create penalty markers by finding their position in the win probability data
    washington_penalty_points = []
    michigan_penalty_points = []
    
    # Match penalties to their win probability data
    for penalty in penalties:
        play_id = penalty['play'].get('id', '')
        if play_id in win_prob_by_play_id:
            wp_data = win_prob_by_play_id[play_id]
            # Use play number directly as x-coordinate
            play_number = penalty['play_number']
            x_coord = play_number  # Play number directly (Play 13 = x=13)
            y_coord = wp_data['homeWinPercentage'] * 100
            
            # Get the win probability change from the penalty data
            win_prob_change = penalty.get('change', 0) * 100  # Convert to percentage
            
            if penalty['team_committed'] == 'Washington':
                # For Washington penalties, the change affects Washington's win probability
                washington_penalty_points.append({
                    'x': x_coord,
                    'y': 100 - y_coord,  # Invert for Washington's win probability
                    'y_end': 100 - y_coord + win_prob_change,  # End point after change
                    'yards': penalty['yards'],
                    'description': penalty['description'],
                    'change': win_prob_change
                })
            elif penalty['team_committed'] == 'Michigan':
                # For Michigan penalties, the change affects Michigan's win probability
                michigan_penalty_points.append({
                    'x': x_coord,
                    'y': y_coord,  # Keep Michigan's win probability
                    'y_end': y_coord + win_prob_change,  # End point after change
                    'yards': penalty['yards'],
                    'description': penalty['description'],
                    'change': win_prob_change
                })
    
    # Prepare data for chart
    labels = []
    home_data = []
    away_data = []
    
    # Create penalty markers for each data point
    washington_penalty_data = []
    michigan_penalty_data = []
    
    # Create penalty delta data for tooltips
    washington_penalty_deltas = [None] * len(win_prob_data)
    michigan_penalty_deltas = [None] * len(win_prob_data)
    
    for penalty in penalties:
        play_id = penalty['play'].get('id', '')
        if play_id in win_prob_by_play_id:
            wp_data = win_prob_by_play_id[play_id]
            index = wp_data['index']
            win_prob_change = penalty.get('change', 0) * 100  # Convert to percentage
            
            if penalty['team_committed'] == 'Washington':
                washington_penalty_deltas[index] = win_prob_change
            elif penalty['team_committed'] == 'Michigan':
                michigan_penalty_deltas[index] = win_prob_change
    
    # Analyze inflection points (major win probability changes)
    inflection_points = []
    
    for i, entry in enumerate(win_prob_data):
        labels.append(f"Play {i+1}")
        home_data.append(entry['homeWinPercentage'] * 100)
        away_data.append((1 - entry['homeWinPercentage']) * 100)
        
        # Calculate win probability change from previous play
        if i > 0:
            prev_home_wp = win_prob_data[i-1]['homeWinPercentage'] * 100
            curr_home_wp = entry['homeWinPercentage'] * 100
            wp_change = curr_home_wp - prev_home_wp
            
            # Check for significant inflection points (5%+ change)
            if abs(wp_change) >= 5.0:
                inflection_points.append({
                    'play_number': i + 1,
                    'change': wp_change,
                    'home_wp': curr_home_wp,
                    'away_wp': 100 - curr_home_wp
                })
        
        # Check if this data point has a penalty
        washington_penalty_data.append(None)
        michigan_penalty_data.append(None)
    
    # Categorize inflection points by play type
    def categorize_inflection_point(play_number, wp_change):
        """Categorize what type of play caused the inflection point"""
        # Find the corresponding play in the play-by-play data
        # The inflection point play_number is 1-based, so we need to find the play at index (play_number - 1)
        if play_number <= len(plays):
            play = plays[play_number - 1]  # Convert 1-based to 0-based index
            play_type = play.get('type', {}).get('text', '').lower()
            short_text = play.get('shortText', '').lower()
            text = play.get('text', '').lower()
            
            # Debug: print the play data for inflection points (commented out for production)
            # if play_number in [27, 38, 43, 74, 75]:  # Debug specific inflection points
            #     print(f"Play {play_number}: type='{play_type}', short='{short_text}', text='{text[:50]}...'")
            
            # Check for turnovers
            if any(keyword in play_type or keyword in short_text or keyword in text 
                   for keyword in ['interception', 'fumble', 'turnover', 'recovery']):
                return '🔄 Turnover'
            
            # Check for scores
            if any(keyword in play_type or keyword in short_text or keyword in text 
                   for keyword in ['touchdown', 'field goal', 'safety', 'conversion']):
                return '🏈 Score'
            
            # Check for explosive plays (long gains)
            if any(keyword in short_text or keyword in text 
                   for keyword in ['for 20', 'for 30', 'for 40', 'for 50', 'for 60', 'for 70', 'for 80', 'for 90']):
                return '💥 Explosive'
            
            # Check for first downs
            if 'first down' in short_text or 'first down' in text:
                return '📏 1st Down'
            
            # Check for fourth down conversions
            if '4th' in play_type and ('conversion' in short_text or 'conversion' in text):
                return '🎯 4th Down'
            
            # Check for penalties
            if play.get('type', {}).get('id') == '8':
                return '🚩 Penalty'
            
            # Default categorization
            return '⚡ Big Play'
        
        return '❓ Unknown'
    
    # Debug: print inflection points found (commented out for production)
    # print(f"Found {len(inflection_points)} inflection points:")
    # for point in inflection_points[:5]:  # Show first 5
    #     print(f"  Play {point['play_number']}: {point['change']:+.1f}% change")
    
    # Debug: print some sequenceNumbers from plays (commented out for production)
    # print("Sample sequenceNumbers from plays:")
    # for i, play in enumerate(plays[:10]):
    #     print(f"  Play {i}: sequenceNumber='{play.get('sequenceNumber')}', type='{play.get('type', {}).get('text', '')}'")
    
    # Add categorization to inflection points
    for point in inflection_points:
        point['category'] = categorize_inflection_point(point['play_number'], point['change'])
    
    html = f"""
    <div class="win-probability-chart">
        <h3>Win Probability Chart</h3>
        <canvas id="winProbabilityChart" width="800" height="400"></canvas>
        <div class="chart-legend">
            <div class="legend-item">
                <span class="legend-color" style="background-color: rgb(75, 192, 192);"></span>
                <span>Michigan Win %</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: rgb(255, 99, 132);"></span>
                <span>Washington Win %</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #ff6b6b; width: 8px; height: 8px; border-radius: 50%;"></span>
                <span>Washington Penalties</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #4ecdc4; width: 8px; height: 8px; border-radius: 50%;"></span>
                <span>Michigan Penalties</span>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        
        const ctx = document.getElementById('winProbabilityChart').getContext('2d');
        
        const winProbabilityChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)}, // Show all plays
                datasets: [{{
                    label: 'Michigan Win %',
                    data: {json.dumps(home_data)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }}, {{
                    label: 'Washington Win %',
                    data: {json.dumps(away_data)},
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.1,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }}, {{
                    label: 'Washington Penalty Impact',
                    data: {json.dumps([None if i not in [12, 45, 48, 103] else away_data[i] for i in range(len(away_data))])},
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.3)',
                    borderWidth: 4,
                    tension: 0.1,
                    fill: false,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: true,
                    spanGaps: false
                }}, {{
                    label: 'Michigan Penalty Impact',
                    data: {json.dumps([None if i not in [21, 59, 90, 145, 153] else home_data[i] for i in range(len(home_data))])},
                    borderColor: '#4ecdc4',
                    backgroundColor: 'rgba(78, 205, 196, 0.3)',
                    borderWidth: 4,
                    tension: 0.1,
                    fill: false,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: true,
                    spanGaps: false
                }}, {{
                    label: 'Major Inflection Points',
                    data: {json.dumps([None if i not in [p['play_number']-1 for p in inflection_points] else home_data[i] for i in range(len(home_data))])},
                    borderColor: '#ffa500',
                    backgroundColor: 'rgba(255, 165, 0, 0.3)',
                    borderWidth: 3,
                    tension: 0.1,
                    fill: false,
                    pointRadius: 8,
                    pointHoverRadius: 12,
                    showLine: true,
                    spanGaps: false,
                    pointStyle: 'triangle'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Win Probability Throughout the Game'
                    }},
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            afterLabel: function(context) {{
                                const datasetLabel = context.dataset.label;
                                const dataIndex = context.dataIndex;
                                
                                if (datasetLabel === 'Washington Penalty Impact') {{
                                    const delta = {json.dumps(washington_penalty_deltas)}[dataIndex];
                                    if (delta !== null && delta !== undefined) {{
                                        return `Delta: ${{delta > 0 ? '+' : ''}}${{delta.toFixed(1)}}%`;
                                    }}
                                }} else if (datasetLabel === 'Michigan Penalty Impact') {{
                                    const delta = {json.dumps(michigan_penalty_deltas)}[dataIndex];
                                    if (delta !== null && delta !== undefined) {{
                                        return `Delta: ${{delta > 0 ? '+' : ''}}${{delta.toFixed(1)}}%`;
                                    }}
                                }} else if (datasetLabel === 'Major Inflection Points') {{
                                    const inflectionPoints = {json.dumps(inflection_points)};
                                    const point = inflectionPoints.find(p => p.play_number - 1 === dataIndex);
                                    if (point) {{
                                        return `${{point.category}} - ${{point.change > 0 ? '+' : ''}}${{point.change.toFixed(1)}}%`;
                                    }}
                                }}
                                return '';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Play Number'
                        }}
                    }}
                }},
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }}
            }}
        }});
    </script>
"""
    
    return html

def generate_enhanced_html_table(game_data, teams_data, win_prob_lookup):
    """Generate enhanced HTML table with penalty analysis and win probability chart"""
    
    plays = game_data.get('plays', {}).get('items', [])
    
    # Get game info
    header = game_data.get('header', {})
    game_name = header.get('name', 'Washington vs Michigan')
    game_date = header.get('date', '2025-10-18')
    game_id = header.get('id', '401752873')
    
    # Analyze penalties
    penalties = analyze_penalties(plays, win_prob_lookup)
    
    # Generate penalty analysis HTML
    penalty_html = generate_penalty_analysis_html(penalties)
    
    # Generate win probability chart
    win_prob_data = list(win_prob_lookup.values())
    chart_html = generate_win_probability_chart(win_prob_data, penalties, plays)
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{game_name} - Enhanced Play by Play Analysis</title>
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
            margin-bottom: 30px;
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
        
        /* Penalty Analysis Styles */
        .penalty-analysis {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 30px;
        }}
        
        .penalty-analysis h3 {{
            margin-top: 0;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        
        .penalty-stats {{
            margin-bottom: 20px;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .stat-card {{
            background-color: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        
        .stat-card h4 {{
            margin: 0 0 10px 0;
            color: #374151;
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #1f2937;
        }}
        
        .stat-detail {{
            font-size: 14px;
            color: #6b7280;
            margin-top: 5px;
        }}
        
        .penalty-table {{
            margin-top: 20px;
        }}
        
        .penalty-details {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        .penalty-details th {{
            background-color: #374151;
            color: white;
            padding: 10px;
            text-align: left;
        }}
        
        .penalty-details td {{
            padding: 8px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .penalty-details tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        
        /* Win Probability Chart Styles */
        .win-probability-chart {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 30px;
        }}
        
        .win-probability-chart h3 {{
            margin-top: 0;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        
        #winProbabilityChart {{
            max-height: 400px;
        }}
        
        .chart-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 15px;
            justify-content: center;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{game_name}</h1>
        <p>Enhanced Play-by-Play Analysis with Penalty Impact & Win Probability Chart | {game_date} | Game ID: {game_id}</p>
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
    penalties_count = 0
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
        if play.get('type', {}).get('id') == '8':  # Penalty type ID
            row_classes.append('penalty')
            penalties_count += 1
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
                <div class="stat-value">{penalties_count}</div>
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
    
    {penalty_html}
    
    {chart_html}
    
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
    print("Generating Enhanced Play-by-Play HTML Table")
    print("Game ID: 401752873 | Date: October 18, 2025")
    print("=" * 60)
    
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
    
    # Generate enhanced HTML
    print("Generating enhanced HTML table with penalty analysis and win probability chart...")
    html = generate_enhanced_html_table(game_data, teams_data, win_prob_lookup)
    
    # Save HTML file
    import os
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/enhanced_playbyplay_table.html', 'w') as f:
        f.write(html)
    
    print(f"Enhanced HTML table saved to: data/game_401752873/enhanced_playbyplay_table.html")
    print(f"Features included:")
    print(f"  ✓ Play-by-play table with win probability")
    print(f"  ✓ Penalty impact analysis")
    print(f"  ✓ Interactive win probability chart")
    print(f"Open the file in your browser to view the enhanced analysis!")

if __name__ == "__main__":
    main()
