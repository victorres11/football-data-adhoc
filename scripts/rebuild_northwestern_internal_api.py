#!/usr/bin/env python3
"""
Rebuild Northwestern page using internal API data structure
This will make it consistent with Michigan page and much simpler
"""

import json
import os
import re
from datetime import datetime

def load_internal_api_data():
    """Load Northwestern data from internal API"""
    with open('data/game_401752866_internal/all_plays.json', 'r') as f:
        plays = json.load(f)
    
    # Load win probability data
    with open('data/game_401752866/win_probability_data.json', 'r') as f:
        win_prob_data = json.load(f)
    
    # Load teams data
    with open('data/game_401752866/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return plays, win_prob_data, teams_data

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

def analyze_penalties(plays, win_prob_lookup):
    """Analyze penalties in the game"""
    penalties = []
    
    for i, play in enumerate(plays):
        play_text = play.get('text', '').lower()
        short_text = play.get('shortText', play.get('text', '')).lower()
        
        is_penalty = False
        team_committed = "Unknown"
        
        # Check for penalty type
        play_type_id = play.get('type', {}).get('id', '')
        if play_type_id == '8':
            is_penalty = True
        elif 'penalty' in play_text:
            is_penalty = True
        
        if is_penalty:
            # Determine which team committed the penalty
            if 'northwestern' in play_text or 'nu' in play_text or 'wildcats' in play_text:
                team_committed = "Northwestern"
            elif 'penn state' in play_text or 'psu' in play_text or 'nittany' in play_text:
                team_committed = "Penn State"
            
            if team_committed != "Unknown":
                # Calculate win probability change
                play_id = play.get('id', '')
                wp_data = win_prob_lookup.get(play_id)
                
                wp_change = 0
                if wp_data and i > 0:
                    prev_play = plays[i-1]
                    prev_play_id = prev_play.get('id', '')
                    prev_wp_data = win_prob_lookup.get(prev_play_id)
                    
                    if prev_wp_data:
                        prev_home_wp = prev_wp_data.get('homeWinPercentage', 0) * 100
                        curr_home_wp = wp_data.get('homeWinPercentage', 0) * 100
                        wp_change = curr_home_wp - prev_home_wp
                
                # Extract penalty yards
                penalty_text = play.get('text', '')
                yards = 0
                yard_match = re.search(r'\((\d+)\s+yards?\)', penalty_text)
                if yard_match:
                    yards = int(yard_match.group(1))
                
                penalties.append({
                    'play': play,
                    'play_number': i + 1,
                    'team_committed': team_committed,
                    'description': penalty_text,
                    'yards': yards,
                    'change': wp_change
                })
    
    return penalties

def categorize_inflection_point(play_number, wp_change, plays):
    """Categorize what type of play caused the inflection point"""
    if play_number <= len(plays):
        play = plays[play_number - 1]
        play_type = play.get('type', {}).get('text', '').lower()
        play_text = play.get('text', '').lower()
        
        # Check for turnovers
        if 'interception' in play_text or 'fumble' in play_text or 'turnover' in play_text:
            return '🔄 Turnover'
        
        # Check for scores
        if 'touchdown' in play_text or 'field goal' in play_text or 'safety' in play_text:
            return '🏈 Score'
        
        # Check for explosive plays (long gains)
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

def generate_penalty_analysis_html(penalties):
    """Generate HTML for penalty analysis"""
    if not penalties:
        return "<p>No penalties detected in this game.</p>"
    
    # Group penalties by team
    northwestern_penalties = [p for p in penalties if p['team_committed'] == 'Northwestern']
    penn_state_penalties = [p for p in penalties if p['team_committed'] == 'Penn State']
    
    html = f"""
    <div class="penalty-analysis">
        <h3>Penalty Impact Analysis</h3>
        <div class="penalty-summary">
            <div class="penalty-stats">
                <h4>Northwestern Penalties: {len(northwestern_penalties)}</h4>
                <ul>
    """
    
    for penalty in northwestern_penalties:
        impact_text = f"{penalty['change']:+.1f}%" if penalty['change'] != 0 else "0.0%"
        html += f"""
                    <li>
                        <strong>Play {penalty['play_number']}</strong>: {penalty['description']} 
                        <span class="wp-impact">({impact_text})</span>
                    </li>
        """
    
    html += """
                </ul>
            </div>
            <div class="penalty-stats">
                <h4>Penn State Penalties: """ + str(len(penn_state_penalties)) + """</h4>
                <ul>
    """
    
    for penalty in penn_state_penalties:
        impact_text = f"{penalty['change']:+.1f}%" if penalty['change'] != 0 else "0.0%"
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

def generate_win_probability_chart(win_prob_data, penalties, plays):
    """Generate Chart.js chart for win probability with penalty markers and quarter shading"""
    if not win_prob_data:
        return "<p>No win probability data available for chart.</p>"
    
    # Create a lookup for win probability data by play ID
    win_prob_by_play_id = {}
    for i, entry in enumerate(win_prob_data):
        play_id = entry.get('playId')
        if play_id:
            win_prob_by_play_id[play_id] = entry
    
    # Create aligned data: match win probability to plays by playId
    aligned_data = []
    for i, play in enumerate(plays):
        play_id = play.get('id')
        wp_data = win_prob_by_play_id.get(play_id)
        
        if wp_data:
            aligned_data.append({
                'play_index': i,
                'play_number': i + 1,
                'play': play,
                'wp_data': wp_data
            })
    
    # Sort by play number to ensure chronological order
    aligned_data.sort(key=lambda x: x['play_number'])
    
    # Extract win probability data for chart
    chart_wp_data = [item['wp_data'] for item in aligned_data]
    
    if not chart_wp_data:
        return "<p>No aligned win probability data available for chart.</p>"
    
    # Create data arrays for chart
    home_data = [entry['homeWinPercentage'] * 100 for entry in chart_wp_data]
    away_data = [(1 - entry['homeWinPercentage']) * 100 for entry in chart_wp_data]
    
    # Calculate quarter boundaries for shading
    quarter_boundaries = []
    current_quarter = 1
    quarter_start = 0
    
    for i, item in enumerate(aligned_data):
        play = item['play']
        quarter = play.get('period', {}).get('number', 1)
        
        if quarter != current_quarter:
            # Quarter changed, record the boundary
            quarter_boundaries.append({
                'quarter': current_quarter,
                'start': quarter_start,
                'end': i - 1
            })
            current_quarter = quarter
            quarter_start = i
    
    # Add the final quarter
    quarter_boundaries.append({
        'quarter': current_quarter,
        'start': quarter_start,
        'end': len(aligned_data) - 1
    })
    
    # Create penalty delta data for tooltips
    washington_penalty_deltas = [None] * len(chart_wp_data)
    michigan_penalty_deltas = [None] * len(chart_wp_data)
    
    for penalty in penalties:
        play_id = penalty['play'].get('id', '')
        if play_id in win_prob_by_play_id:
            wp_data = win_prob_by_play_id[play_id]
            # Find the index in aligned data
            for i, item in enumerate(aligned_data):
                if item['play'].get('id') == play_id:
                    win_prob_change = penalty.get('change', 0)
                    
                    if penalty['team_committed'] == 'Northwestern':
                        washington_penalty_deltas[i] = win_prob_change
                    elif penalty['team_committed'] == 'Penn State':
                        michigan_penalty_deltas[i] = win_prob_change
                    break
    
    # Calculate inflection points
    inflection_points = []
    for i, item in enumerate(aligned_data):
        if i > 0:
            prev_home_wp = aligned_data[i-1]['wp_data']['homeWinPercentage'] * 100
            curr_home_wp = item['wp_data']['homeWinPercentage'] * 100
            wp_change = curr_home_wp - prev_home_wp
            
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
    
    # Create chart HTML with quarter shading
    chart_html = f"""
    <div class="win-probability-chart">
        <h3>Win Probability Chart</h3>
        <div class="chart-container" style="position: relative; width: 100%; height: 400px;">
            <!-- Quarter background shading -->
            <div class="quarter-background" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1;">
                <div class="quarter-section" style="position: absolute; top: 0; left: 0%; width: 22.4%; height: 100%; background-color: rgba(240, 248, 255, 0.3); border-right: 2px solid rgba(0, 0, 0, 0.1);">
                    <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q1</div>
                </div>
                <div class="quarter-section" style="position: absolute; top: 0; left: 22.4%; width: 30.0%; height: 100%; background-color: rgba(255, 248, 240, 0.3); border-right: 2px solid rgba(0, 0, 0, 0.1);">
                    <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q2</div>
                </div>
                <div class="quarter-section" style="position: absolute; top: 0; left: 52.4%; width: 22.4%; height: 100%; background-color: rgba(240, 255, 240, 0.3); border-right: 2px solid rgba(0, 0, 0, 0.1);">
                    <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q3</div>
                </div>
                <div class="quarter-section" style="position: absolute; top: 0; left: 74.8%; width: 25.2%; height: 100%; background-color: rgba(255, 240, 255, 0.3);">
                    <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q4</div>
                </div>
            </div>
            <canvas id="winProbabilityChart" width="800" height="400" style="position: relative; z-index: 2;"></canvas>
        </div>
        <div class="chart-legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: rgb(75, 192, 192);"></div>
                <span>Penn State Win %</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: rgb(255, 99, 132);"></div>
                <span>Northwestern Win %</span>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('winProbabilityChart').getContext('2d');
        
        const winProbabilityChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps([f"Play {i+1}" for i in range(len(chart_wp_data))])},
                datasets: [{{
                    label: 'Penn State Win %',
                    data: {json.dumps(home_data)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: false
                }}, {{
                    label: 'Northwestern Win %',
                    data: {json.dumps(away_data)},
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: false
                }}, {{
                    label: 'Northwestern Penalty Impact',
                    data: {json.dumps([None if i not in [j for j, item in enumerate(aligned_data) if item['play'].get('id') in [p['play'].get('id') for p in penalties if p['team_committed'] == 'Northwestern']] else away_data[i] for i in range(len(away_data))])},
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
                    data: {json.dumps([None if i not in [j for j, item in enumerate(aligned_data) if item['play'].get('id') in [p['play'].get('id') for p in penalties if p['team_committed'] == 'Penn State']] else home_data[i] for i in range(len(home_data))])},
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
                        text: 'Win Probability Throughout Game'
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
    """
    
    return chart_html

def generate_enhanced_html_table(plays, teams_data, win_prob_lookup):
    """Generate enhanced HTML table using internal API structure"""
    print("Generating enhanced HTML table with internal API structure...")
    
    # Create aligned data: match win probability to plays by playId
    aligned_data = []
    for i, play in enumerate(plays):
        play_id = play.get('id')
        wp_data = win_prob_lookup.get(play_id)
        
        if wp_data:
            aligned_data.append({
                'play_index': i,
                'play_number': i + 1,
                'play': play,
                'wp_data': wp_data
            })
    
    # Sort by play number to ensure chronological order
    aligned_data.sort(key=lambda x: x['play_number'])
    
    # Analyze penalties
    penalties = analyze_penalties(plays, win_prob_lookup)
    penalty_html = generate_penalty_analysis_html(penalties)
    
    # Calculate inflection points
    inflection_points = []
    for i, item in enumerate(aligned_data):
        if i > 0:
            prev_home_wp = aligned_data[i-1]['wp_data']['homeWinPercentage'] * 100
            curr_home_wp = item['wp_data']['homeWinPercentage'] * 100
            wp_change = curr_home_wp - prev_home_wp
            
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
    
    inflection_html = generate_inflection_points_analysis_html(inflection_points)
    
    # Generate win probability chart
    win_prob_data = [item['wp_data'] for item in aligned_data]
    chart_html = generate_win_probability_chart(win_prob_data, penalties, plays)
    
    # Generate HTML table
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Play-by-Play Analysis - Northwestern vs Penn State</title>
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
                background: #fff3cd;
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }}
            .inflection-summary {{
                margin-top: 20px;
            }}
            .inflection-stats {{
                background: white;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
            }}
            .inflection-stats ul {{
                list-style: none;
                padding: 0;
            }}
            .inflection-stats li {{
                padding: 10px;
                margin: 5px 0;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 3px solid #007bff;
            }}
            .wp-impact {{
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.9em;
            }}
            .wp-impact.positive {{
                background-color: #d4edda;
                color: #155724;
            }}
            .wp-impact.negative {{
                background-color: #f8d7da;
                color: #721c24;
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
                max-width: 300px;
                word-wrap: break-word;
            }}
            .down-dist {{
                font-weight: bold;
                color: #666;
            }}
            .yard-line {{
                font-weight: bold;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Enhanced Play-by-Play Analysis</h1>
                <p>Northwestern vs Penn State | October 11, 2025 | Game ID: 401752866</p>
            </div>
            
            <div class="content">
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
        
        # Extract quarter and time using clock.value for precision
        quarter = f"Q{play.get('period', {}).get('number', 1)}"
        clock = play.get('clock', {})
        
        # Use clock.value (raw seconds) for more precise timing
        # This gives us exact game clock time for each play (e.g., 900.0 = 15:00, 751.0 = 12:31)
        clock_seconds = clock.get('value', 900.0)  # Default to 15:00 if not available
        time = clock.get('displayValue', '15:00') if clock else '15:00'
        
        # Check for time gaps using clock.value for more accurate detection
        if i > 0:
            prev_play = aligned_data[i-1]['play']
            prev_clock = prev_play.get('clock', {})
            prev_seconds = prev_clock.get('value', 900.0)
            
            # Calculate time difference in game clock seconds
            time_diff = prev_seconds - clock_seconds
            
            # If there's a significant time jump (more than 30 seconds), it's likely a drive change
            if time_diff > 30:  # More than 30 seconds of game time
                time = f"{time} (Drive Change)"
            # Also check for wallclock changes as backup
            elif prev_play.get('wallclock') != play.get('wallclock'):
                time = f"{time} (Drive Change)"
        
        # Determine team
        team_name = "Unknown"
        if play.get('teamParticipants'):
            team_id = play['teamParticipants'][0].get('id', '')
            if team_id == '77':
                team_name = "Northwestern"
            elif team_id == '213':
                team_name = "Penn State"
        
        # Extract down and distance from start object
        down_dist = ""
        yard_line = ""
        
        start_info = play.get('start', {})
        if start_info:
            down = start_info.get('down', 0)
            distance = start_info.get('distance', 0)
            if down > 0 and distance > 0:
                down_dist = f"{down} & {distance}"
            yard_line = start_info.get('possessionText', '')
        
        # Fallback to parsing from play text if start object is not available
        if not down_dist or not yard_line:
            play_text = play.get('text', '')
            
            # Parse down and distance from play text
            down_match = re.search(r'(\d+)(?:st|nd|rd|th) & (\d+)', play_text)
            if down_match:
                down_dist = f"{down_match.group(1)} & {down_match.group(2)}"
            
            # Parse yard line from play text
            yard_match = re.search(r'at (?:NU|PSU) (\d+)', play_text)
            if yard_match:
                yard_line = f"{'NU' if 'NU' in play_text else 'PSU'} {yard_match.group(1)}"
        
        # Get play description
        play_text = play.get('text', '')
        
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
                                <td class="down-dist">{down_dist}</td>
                                <td class="yard-line">{yard_line}</td>
                                <td class="play-description">{play_text}</td>
                            </tr>
        """
    
    html += f"""
                        </tbody>
                    </table>
                </div>
                
                {chart_html}
                
                {penalty_html}
                
                {inflection_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    print("Rebuilding Northwestern page with internal API structure")
    print("=" * 60)
    
    # Load data
    plays, win_prob_data, teams_data = load_internal_api_data()
    print(f"Loaded {len(plays)} plays from internal API")
    
    # Create win probability lookup
    win_prob_lookup = create_win_probability_lookup(win_prob_data)
    print(f"Created win probability lookup with {len(win_prob_lookup)} entries")
    
    # Generate enhanced HTML
    html = generate_enhanced_html_table(plays, teams_data, win_prob_lookup)
    
    # Save to file
    output_file = "enhanced_pbp_northwestern_pennstate_internal.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Enhanced HTML table saved to: {output_file}")
    print("Features included:")
    print("  ✓ Play-by-play table with win probability")
    print("  ✓ Penalty impact analysis")
    print("  ✓ Interactive win probability chart")
    print("  ✓ Major inflection points analysis")
    print("  ✓ Internal API data structure (unified with Michigan)")
    print("Open the file in your browser to view the enhanced analysis!")

if __name__ == "__main__":
    main()
