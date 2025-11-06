#!/usr/bin/env python3
"""
Enhanced Play-by-Play Table Generator for Northwestern vs Penn State (Game ID: 401752866)
Includes win probability chart, penalty analysis, and inflection point analysis
"""

import json
import requests
import re
from datetime import datetime

def load_game_data():
    """Load existing game data"""
    with open('data/game_401752866/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    
    with open('data/game_401752866/teams_data.json', 'r') as f:
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

def analyze_penalties(plays, win_prob_lookup):
    """Analyze penalties in the game"""
    penalties = []
    
    for i, play in enumerate(plays):
        play_text = play.get('text', '').lower()
        short_text = play.get('shortText', play.get('text', '')).lower()
        
        # Check for penalties in both dedicated penalty plays and embedded penalties
        is_penalty = False
        team_committed = "Unknown"
        
        # Check if it's a dedicated penalty play
        play_type_id = play.get('type', {}).get('id', '')
        if play_type_id == '8':  # Penalty type ID
            is_penalty = True
            if 'northwestern penalty' in short_text:
                team_committed = "Northwestern"
            elif 'penn state penalty' in short_text:
                team_committed = "Penn State"
        
        # Check for embedded penalties in play text
        elif 'penalty' in play_text:
            is_penalty = True
            if 'northwestern penalty' in play_text:
                team_committed = "Northwestern"
            elif 'penn state penalty' in play_text:
                team_committed = "Penn State"
        
        if is_penalty and team_committed != "Unknown":
            
            # Calculate win probability change
            play_id = play.get('id', '')
            current_wp = None
            previous_wp = None
            
            if play_id in win_prob_lookup:
                current_wp = win_prob_lookup[play_id]['homeWinPercentage']
                if i > 0:
                    prev_play_id = plays[i-1].get('id', '')
                    if prev_play_id in win_prob_lookup:
                        previous_wp = win_prob_lookup[prev_play_id]['homeWinPercentage']
            
            wp_change = get_win_probability_change(current_wp, previous_wp)
            
            # Extract penalty details
            penalty_text = play.get('text', '')
            yards = 0
            description = penalty_text
            
            # Try to extract yards from penalty text
            import re
            yard_match = re.search(r'\((\d+)\s+yards?\)', penalty_text)
            if yard_match:
                yards = int(yard_match.group(1))
            
            penalties.append({
                'play': play,
                'play_number': i + 1,
                'team_committed': team_committed,
                'description': description,
                'yards': yards,
                'change': wp_change
            })
    
    return penalties

def generate_penalty_analysis_html(penalties):
    """Generate HTML for penalty analysis"""
    if not penalties:
        return "<p>No penalties found in this game.</p>"
    
    # Group penalties by team
    northwestern_penalties = [p for p in penalties if p['team_committed'] == 'Northwestern']
    penn_state_penalties = [p for p in penalties if p['team_committed'] == 'Penn State']
    
    html = f"""
    <div class="penalty-analysis">
        <h3>Penalty Impact Analysis</h3>
        <div class="penalty-summary">
            <div class="team-penalties">
                <h4>Northwestern Penalties: {len(northwestern_penalties)}</h4>
                <ul>
    """
    
    for penalty in northwestern_penalties:
        wp_impact = penalty['change'] * 100
        impact_text = f"{wp_impact:+.1f}%" if wp_impact != 0 else "No WP change"
        html += f"""
                    <li>
                        <strong>Play {penalty['play_number']}</strong>: {penalty['description']} 
                        <span class="wp-impact">({impact_text})</span>
                    </li>
        """
    
    html += """
                </ul>
            </div>
            <div class="team-penalties">
                <h4>Penn State Penalties: """ + str(len(penn_state_penalties)) + """</h4>
                <ul>
    """
    
    for penalty in penn_state_penalties:
        wp_impact = penalty['change'] * 100
        impact_text = f"{wp_impact:+.1f}%" if wp_impact != 0 else "No WP change"
        html += f"""
                    <li>
                        <strong>Play {penalty['play_number']}</strong>: {penalty['description']} 
                        <span class="wp-impact">({impact_text})</span>
                    </li>
        """
    
    html += """
                </ul>
            </div>
        </div>
    </div>
    """
    
    return html

def generate_inflection_points_analysis_html(inflection_points):
    """Generate HTML for major inflection points analysis"""
    if not inflection_points:
        return "<p>No major inflection points found in this game.</p>"
    
    # Sort by play number
    inflection_points.sort(key=lambda x: x['play_number'])
    
    html = f"""
    <div class="inflection-analysis">
        <h3>Major Inflection Points Analysis</h3>
        <p>Plays that caused significant win probability changes (5% or more)</p>
        <div class="inflection-summary">
            <div class="inflection-stats">
                <h4>Total Major Inflection Points: {len(inflection_points)}</h4>
                <ul>
    """
    
    for point in inflection_points:
        change_text = f"{point['change']:+.1f}%"
        change_class = "positive" if point['change'] > 0 else "negative"
        html += f"""
                    <li>
                        <strong>Play {point['play_number']}</strong>: {point['category']} 
                        <span class="wp-impact {change_class}">({change_text})</span>
                        <br><small>Penn State WP: {point['home_wp']:.1f}% → Northwestern WP: {point['away_wp']:.1f}%</small>
                        <br><em>"{point['play_text']}"</em>
                    </li>
        """
    
    html += """
                </ul>
            </div>
        </div>
    </div>
    """
    
    return html

def categorize_inflection_point(play_number, wp_change, plays):
    """Categorize what type of play caused the inflection point"""
    if play_number <= len(plays):
        play = plays[play_number - 1]  # Convert 1-based to 0-based index
        play_type = play.get('type', {}).get('text', '').lower()
        play_text = play.get('text', '').lower()
        
        # Check for turnovers
        if 'interception' in play_text or 'fumble' in play_text or 'turnover' in play_text:
            return '🔄 Turnover'
        
        # Check for scores
        if 'touchdown' in play_text or 'field goal' in play_text or 'safety' in play_text:
            return '🏈 Score'
        
        # Check for explosive plays (long gains) - improved detection
        import re
        yardage_match = re.search(r'(\d+)\s+yds?', play_text)
        if yardage_match:
            yards = int(yardage_match.group(1))
            if yards >= 20:
                return '💥 Explosive Play'
        
        # Check for first downs
        if '1st down' in play_text or 'first down' in play_text:
            return '📈 1st Down'
        
        # Check for 4th down plays
        if '4th' in play_text or 'fourth' in play_text:
            return '🎯 4th Down'
        
        # Check for penalties
        if 'penalty' in play_text:
            return '🚩 Penalty'
        
        # Check for big plays
        if 'big' in play_text or 'huge' in play_text:
            return '⭐ Big Play'
        
        # Check for significant yardage gains (10+ yards)
        if yardage_match:
            yards = int(yardage_match.group(1))
            if yards >= 10:
                return '📊 Significant Gain'
        
        # Check for play type and context
        if 'incomplete' in play_text:
            return '❌ Incomplete Pass'
        elif 'sack' in play_text:
            return '🏃 Sack'
        elif 'punt' in play_text:
            return '🏈 Punt'
        elif 'kickoff' in play_text:
            return '🏈 Kickoff'
        elif 'timeout' in play_text:
            return '⏰ Timeout'
        
        # Default categorization based on play type
        if play_type == 'rush':
            return '🏃 Rush'
        elif play_type == 'pass':
            return '🏈 Pass'
        elif play_type == 'kickoff':
            return '🏈 Kickoff'
        elif play_type == 'punt':
            return '🏈 Punt'
        else:
            return f'📋 {play_type.title()}'
    
    return '❓ Unknown'

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
    
    # Analyze penalties
    washington_penalty_points = []
    michigan_penalty_points = []
    
    # Match penalties to their win probability data
    for penalty in penalties:
        play_id = penalty['play'].get('id', '')
        if play_id in win_prob_by_play_id:
            wp_data = win_prob_by_play_id[play_id]
            play_number = penalty['play_number']
            x_coord = play_number
            y_coord = wp_data['homeWinPercentage'] * 100
            
            win_prob_change = penalty.get('change', 0) * 100
            
            if penalty['team_committed'] == 'Northwestern':
                washington_penalty_points.append({
                    'x': x_coord,
                    'y': 100 - y_coord,
                    'y_end': 100 - y_coord + win_prob_change,
                    'yards': penalty['yards'],
                    'description': penalty['description'],
                    'change': win_prob_change,
                    'play_number': penalty['play_number']
                })
            elif penalty['team_committed'] == 'Penn State':
                michigan_penalty_points.append({
                    'x': x_coord,
                    'y': y_coord,
                    'y_end': y_coord + win_prob_change,
                    'yards': penalty['yards'],
                    'description': penalty['description'],
                    'change': win_prob_change,
                    'play_number': penalty['play_number']
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
            win_prob_change = penalty.get('change', 0) * 100
            
            if penalty['team_committed'] == 'Northwestern':
                washington_penalty_deltas[index] = win_prob_change
            elif penalty['team_committed'] == 'Penn State':
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
                # Get the play text for this inflection point
                play_text = ""
                if i < len(plays):
                    play_text = plays[i].get('text', '')
                
                inflection_points.append({
                    'play_number': i + 1,
                    'change': wp_change,
                    'home_wp': curr_home_wp,
                    'away_wp': 100 - curr_home_wp,
                    'play_text': play_text
                })
        
        # Check if this data point has a penalty
        washington_penalty_data.append(None)
        michigan_penalty_data.append(None)
    
    # Categorize inflection points by play type
    def categorize_inflection_point(play_number, wp_change):
        """Categorize what type of play caused the inflection point"""
        if play_number <= len(plays):
            play = plays[play_number - 1]
            play_type = play.get('type', {}).get('text', '').lower()
            short_text = play.get('shortText', play.get('text', '')).lower()
            text = play.get('text', '').lower()
            
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
                <span>Penn State Win %</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: rgb(255, 99, 132);"></span>
                <span>Northwestern Win %</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #ff6b6b;"></span>
                <span>Northwestern Penalties</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #4ecdc4;"></span>
                <span>Penn State Penalties</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #ffa500;"></span>
                <span>Major Inflection Points</span>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('winProbabilityChart').getContext('2d');
        
        const winProbabilityChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Penn State Win %',
                    data: {json.dumps(home_data)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }}, {{
                    label: 'Northwestern Win %',
                    data: {json.dumps(away_data)},
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.1,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }}, {{
                    label: 'Northwestern Penalty Impact',
                    data: {json.dumps([None if i not in [p['play_number']-1 for p in washington_penalty_points] else away_data[i] for i in range(len(away_data))])},
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
                    label: 'Penn State Penalty Impact',
                    data: {json.dumps([None if i not in [p['play_number']-1 for p in michigan_penalty_points] else home_data[i] for i in range(len(home_data))])},
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
                                
                                if (datasetLabel === 'Northwestern Penalty Impact') {{
                                    const delta = {json.dumps(washington_penalty_deltas)}[dataIndex];
                                    if (delta !== null && delta !== undefined) {{
                                        return `Delta: ${{delta > 0 ? '+' : ''}}${{delta.toFixed(1)}}%`;
                                    }}
                                }} else if (datasetLabel === 'Penn State Penalty Impact') {{
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
    
    # Extract plays from drives (this game has plays nested in drives)
    plays = []
    drives_data = game_data.get('drives', {})
    
    # Check both previous and current drives
    for drive_list in [drives_data.get('previous', []), drives_data.get('current', [])]:
        for drive in drive_list:
            drive_plays = drive.get('plays', [])
            plays.extend(drive_plays)
    
    # If no plays found in drives, try the old structure
    if not plays:
        plays = game_data.get('plays', {}).get('items', [])
    
    print(f"Found {len(plays)} plays in the game data")
    
    # Get game info
    header = game_data.get('header', {})
    game_name = header.get('name', 'Northwestern vs Penn State')
    game_date = header.get('date', '2025-10-11')
    game_id = header.get('id', '401752866')
    
    # Analyze penalties
    penalties = analyze_penalties(plays, win_prob_lookup)
    
    # Generate penalty analysis HTML
    penalty_html = generate_penalty_analysis_html(penalties)
    
    # Use win probability data in its original order (chronological)
    # Match plays to win probability entries by position, not by ID
    win_prob_entries = list(win_prob_lookup.values())
    
    # Create aligned data by matching positionally
    aligned_data = []
    for i, wp_entry in enumerate(win_prob_entries):
        if i < len(plays):
            play = plays[i]
            aligned_data.append({
                'play_index': i,
                'play_number': i + 1,
                'play': play,
                'wp_data': wp_entry
            })
    
    # Generate win probability chart using aligned data
    win_prob_data = [item['wp_data'] for item in aligned_data]
    chart_html = generate_win_probability_chart(win_prob_data, penalties, plays)
    
    # Calculate inflection points for analysis using aligned data
    inflection_points = []
    for i, item in enumerate(aligned_data):
        if i > 0:
            prev_home_wp = aligned_data[i-1]['wp_data']['homeWinPercentage'] * 100
            curr_home_wp = item['wp_data']['homeWinPercentage'] * 100
            wp_change = curr_home_wp - prev_home_wp
            
            # Check for significant inflection points (5%+ change)
            if abs(wp_change) >= 5.0:
                play_number = item['play_number']
                play = item['play']
                category = categorize_inflection_point(play_number, wp_change, plays)
                play_text = play.get('text', '')
                
                inflection_points.append({
                    'play_number': play_number,
                    'change': wp_change,
                    'home_wp': curr_home_wp,
                    'away_wp': 100 - curr_home_wp,
                    'category': category,
                    'play_text': play_text
                })
    
    # Generate inflection points analysis HTML
    inflection_html = generate_inflection_points_analysis_html(inflection_points)
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{game_name} - Enhanced Play by Play Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .win-probability-chart {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
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
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}
        .penalty-analysis {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .penalty-summary {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }}
        .inflection-analysis {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .inflection-summary {{
            margin-top: 20px;
        }}
        .inflection-stats h4 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        .inflection-stats ul {{
            list-style: none;
            padding: 0;
        }}
        .inflection-stats li {{
            padding: 10px;
            margin-bottom: 8px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #28a745;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .team-penalties h4 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        .team-penalties ul {{
            list-style: none;
            padding: 0;
        }}
        .team-penalties li {{
            padding: 10px;
            margin: 8px 0;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #007bff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .wp-impact {{
            color: #28a745;
            font-weight: bold;
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
            background: #343a40;
            color: white;
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
        }}
        td {{
            padding: 12px 10px;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .play-number {{
            text-align: center;
            font-weight: bold;
            color: #6b7280;
        }}
        .quarter {{
            text-align: center;
            font-weight: bold;
            color: #374151;
        }}
        .time {{
            text-align: center;
            font-family: monospace;
            color: #6b7280;
        }}
        .win-prob {{
            font-weight: bold;
            text-align: center;
        }}
        .win-prob.high {{
            color: #28a745;
        }}
        .win-prob.low {{
            color: #dc3545;
        }}
        .win-prob-neutral {{
            color: #6b7280;
        }}
        .change {{
            text-align: center;
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
        @media (max-width: 768px) {{
            .penalty-summary {{
                grid-template-columns: 1fr;
            }}
            .chart-legend {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{game_name}</h1>
            <p>Enhanced Play-by-Play Analysis | {game_date} | Game ID: {game_id}</p>
        </div>
        
        <div class="content">
            {chart_html}
            
            {penalty_html}
            
            {inflection_html}
            
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
                            <th style="width: 100px;">Down/Dist</th>
                            <th style="width: 120px;">Yard Line</th>
                            <th>Play Description</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add play-by-play rows using aligned data
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
        
        # Check for time gaps using wallclock for more accurate detection
        if i > 0:
            prev_play = aligned_data[i-1]['play']
            prev_wallclock = prev_play.get('wallclock', '')
            curr_wallclock = play.get('wallclock', '')
            
            if prev_wallclock and curr_wallclock:
                try:
                    prev_dt = datetime.fromisoformat(prev_wallclock.replace('Z', '+00:00'))
                    curr_dt = datetime.fromisoformat(curr_wallclock.replace('Z', '+00:00'))
                    
                    # Calculate time difference in seconds
                    diff_seconds = (curr_dt - prev_dt).total_seconds()
                    
                    # If there's a gap of more than 2 minutes, it's likely a drive change
                    if diff_seconds > 120:  # More than 2 minutes
                        time = f"{time} (Drive Change)"
                except:
                    pass
        
        # Determine team
        team_name = "Unknown"
        if play.get('teamParticipants'):
            team_id = play['teamParticipants'][0].get('id', '')
            team_name = get_team_name(team_id, teams_data)
        
        # Style win probability based on value
        wp_class = "high" if home_wp > 60 else "low" if home_wp < 40 else "neutral"
        
        change_text = f"{wp_change:+.1f}%" if wp_change != 0 else "0.0%"
        change_class = "positive" if wp_change > 0 else "negative" if wp_change < 0 else ""
        
        # Extract play text first
        play_text = play.get('shortText', play.get('text', ''))
        
        # Extract down and distance from start object
        down_dist = ""
        yard_line = ""
        
        start_info = play.get('start', {})
        if start_info:
            # Get down and distance
            down = start_info.get('down', 0)
            distance = start_info.get('distance', 0)
            if down > 0 and distance > 0:
                down_dist = f"{down} & {distance}"
            
            # Get yard line from possessionText
            yard_line = start_info.get('possessionText', '')
        
        # Fallback to parsing from text if start object is not available
        if not down_dist:
            if '1st' in play_text or '2nd' in play_text or '3rd' in play_text or '4th' in play_text:
                down_match = re.search(r'(\d+)(?:st|nd|rd|th)', play_text)
                if down_match:
                    down = down_match.group(1)
                    dist_match = re.search(r'(\d+)\s+yds?', play_text)
                    if dist_match:
                        distance = dist_match.group(1)
                        down_dist = f"{down} & {distance}"
                    else:
                        down_dist = f"{down} & 10"
        
        # Fallback for yard line if not in start object
        if not yard_line:
            yard_match = re.search(r'at\s+([A-Z]+\s+\d+)', play_text)
            if yard_match:
                yard_line = yard_match.group(1)
        
        html += f"""
                        <tr>
                            <td class="play-number">{i + 1}</td>
                            <td class="quarter">{quarter}</td>
                            <td class="time">{time}</td>
                            <td class="win-prob {wp_class}">{home_wp:.1f}%</td>
                            <td class="change {change_class}">{change_text}</td>
                            <td>{down_dist}</td>
                            <td>{yard_line}</td>
                            <td class="play-description">{play_text}</td>
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
    print("Generating Enhanced Play-by-Play HTML Table")
    print("Game ID: 401752866 | Date: October 11, 2025")
    print("=" * 60)
    
    game_id = 401752866
    
    # Load win probability data
    print("Loading win probability data...")
    with open('data/game_401752866/win_probability_data.json', 'r') as f:
        win_prob_data = json.load(f)
    
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
    os.makedirs('data/game_401752866', exist_ok=True)
    with open('data/game_401752866/enhanced_playbyplay_table.html', 'w') as f:
        f.write(html)
    
    print("Enhanced HTML table saved to: data/game_401752866/enhanced_playbyplay_table.html")
    print("Features included:")
    print("  ✓ Play-by-play table with win probability")
    print("  ✓ Penalty impact analysis")
    print("  ✓ Interactive win probability chart")
    print("Open the file in your browser to view the enhanced analysis!")

if __name__ == "__main__":
    main()
