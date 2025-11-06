#!/usr/bin/env python3
"""
Create enhanced play-by-play analysis for Rutgers vs Oregon (Game ID: 401752876)
"""

import json
import os
import re
from datetime import datetime

def load_game_data():
    """Load game data from files"""
    with open('data/game_401752876/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    
    with open('data/game_401752876/win_probability_data.json', 'r') as f:
        win_prob_data = json.load(f)
    
    with open('data/game_401752876/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return game_data, win_prob_data, teams_data

def extract_plays_from_game_data(game_data):
    """Extract plays from game data (public API structure) with drive information"""
    plays = []
    drives = game_data.get('drives', {})
    
    drive_counter = 1
    for drive_list in [drives.get('previous', []), drives.get('current', [])]:
        for drive in drive_list:
            drive_plays = drive.get('plays', [])
            # Add drive information to each play
            for play in drive_plays:
                play['drive_info'] = {
                    'drive_number': drive_counter,
                    'drive_description': drive.get('description', ''),
                    'drive_id': drive.get('id', '')
                }
                plays.append(play)
            drive_counter += 1
    
    return plays

def create_win_probability_lookup(win_prob_data):
    """Create lookup for win probability data by playId"""
    win_prob_lookup = {}
    
    for entry in win_prob_data:
        play_id = entry.get('playId')
        if play_id:
            win_prob_lookup[play_id] = entry
    
    return win_prob_lookup

def analyze_penalties(plays, win_prob_lookup):
    """Analyze penalties in the game"""
    penalties = []
    
    for i, play in enumerate(plays):
        play_text = play.get('text', '').lower()
        
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
            if 'rutgers' in play_text or 'scarlet' in play_text:
                team_committed = "Rutgers"
            elif 'oregon' in play_text or 'ducks' in play_text:
                team_committed = "Oregon"
            
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
                
                penalties.append({
                    'play': play,
                    'play_number': i + 1,
                    'team_committed': team_committed,
                    'description': play.get('text', ''),
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

def generate_enhanced_html_table(plays, teams_data, win_prob_lookup):
    """Generate enhanced HTML table"""
    print("Generating enhanced HTML table...")
    
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
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Play-by-Play Analysis - Rutgers vs Oregon</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Enhanced Play-by-Play Analysis</h1>
                <p>Rutgers vs Oregon | October 18, 2025 | Game ID: 401752876</p>
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
                                <th style="width: 80px;">Drive</th>
                                <th style="width: 100px;">Win Prob</th>
                                <th style="width: 80px;">Change</th>
                                <th style="width: 100px;">Down/Dist</th>
                                <th style="width: 120px;">Yard Line</th>
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
        
        # Extract drive information
        drive_info = play.get('drive_info', {})
        drive_number = drive_info.get('drive_number', '')
        drive_display = f"Drive {drive_number}" if drive_number else ''
        
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
                                <td class="drive" style="font-weight: bold; color: #666;">{drive_display}</td>
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
                
                <div class="win-probability-chart">
                    <h3>Win Probability Chart</h3>
                    <div class="chart-container" style="position: relative; width: 100%; height: 400px;">
                        <!-- Quarter background shading -->
                        <div class="quarter-background" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1;">
                            <div class="quarter-section" style="position: absolute; top: 0; left: 0%; width: 25%; height: 100%; background-color: rgba(240, 248, 255, 0.3); border-right: 2px solid rgba(0, 0, 0, 0.1);">
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q1</div>
                            </div>
                            <div class="quarter-section" style="position: absolute; top: 0; left: 25%; width: 25%; height: 100%; background-color: rgba(255, 248, 240, 0.3); border-right: 2px solid rgba(0, 0, 0, 0.1);">
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q2</div>
                            </div>
                            <div class="quarter-section" style="position: absolute; top: 0; left: 50%; width: 25%; height: 100%; background-color: rgba(240, 255, 240, 0.3); border-right: 2px solid rgba(0, 0, 0, 0.1);">
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q3</div>
                            </div>
                            <div class="quarter-section" style="position: absolute; top: 0; left: 75%; width: 25%; height: 100%; background-color: rgba(255, 240, 255, 0.3);">
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Q4</div>
                            </div>
                        </div>
                        <canvas id="winProbabilityChart" width="800" height="400" style="position: relative; z-index: 2;"></canvas>
                    </div>
                    <div class="chart-legend" style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px; justify-content: center;">
                        <div class="legend-item" style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                            <div class="legend-color" style="width: 16px; height: 16px; border-radius: 3px; background-color: rgb(75, 192, 192);"></div>
                            <span>Oregon Win %</span>
                        </div>
                        <div class="legend-item" style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                            <div class="legend-color" style="width: 16px; height: 16px; border-radius: 3px; background-color: rgb(255, 99, 132);"></div>
                            <span>Rutgers Win %</span>
                        </div>
                    </div>
                </div>
                
                <div class="penalty-analysis">
                    <h3>Penalty Impact Analysis</h3>
                    <p>Total penalties detected: {len(penalties)}</p>
                    <ul>
    """
    
    for penalty in penalties:
        impact_text = f"{penalty['change']:+.1f}%" if penalty['change'] != 0 else "0.0%"
        html += f"""
                        <li>
                            <strong>Play {penalty['play_number']}</strong>: {penalty['description']} 
                            <span class="change {'positive' if penalty['change'] > 0 else 'negative'}">({impact_text})</span>
                        </li>
        """
    
    html += f"""
                    </ul>
                </div>
                
                <div class="inflection-analysis">
                    <h3>Major Inflection Points Analysis</h3>
                    <p>Plays that caused significant win probability changes (5% or more): {len(inflection_points)}</p>
                    <ul>
    """
    
    for point in inflection_points:
        change_text = f"{point['change']:+.1f}%"
        change_class = "positive" if point['change'] > 0 else "negative"
        html += f"""
                        <li>
                            <strong>Play {point['play_number']}</strong>: {point['category']} 
                            <span class="change {change_class}">({change_text})</span>
                            <br><small>Oregon WP: {point['home_wp']:.1f}% → Rutgers WP: {point['away_wp']:.1f}%</small>
                            <br><em>"{point['play_text']}"</em>
                        </li>
        """
    
    html += """
                    </ul>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const ctx = document.getElementById('winProbabilityChart').getContext('2d');
            
            // Prepare data for chart
            const chartData = {json.dumps([item['wp_data'] for item in aligned_data])};
            const homeData = chartData.map(entry => entry.homeWinPercentage * 100);
            const awayData = chartData.map(entry => (1 - entry.homeWinPercentage) * 100);
            const labels = {json.dumps([f"Play {i+1}" for i in range(len(aligned_data))])};
            
            const winProbabilityChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Oregon Win %',
                        data: homeData,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 2,
                        tension: 0.1,
                        fill: false
                    }}, {{
                        label: 'Rutgers Win %',
                        data: awayData,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 2,
                        tension: 0.1,
                        fill: false
                    }}]
                }},
                options: {{
                    responsive: true,
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
    print("Creating enhanced play-by-play analysis for Rutgers vs Oregon")
    print("=" * 60)
    
    # Load data
    game_data, win_prob_data, teams_data = load_game_data()
    
    # Extract plays
    plays = extract_plays_from_game_data(game_data)
    print(f"Extracted {len(plays)} plays")
    
    # Create win probability lookup
    win_prob_lookup = create_win_probability_lookup(win_prob_data)
    print(f"Created win probability lookup with {len(win_prob_lookup)} entries")
    
    # Generate enhanced HTML
    html = generate_enhanced_html_table(plays, teams_data, win_prob_lookup)
    
    # Save to file
    output_file = "enhanced_analysis/enhanced_pbp_rutgers_oregon.html"
    os.makedirs('enhanced_analysis', exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Enhanced HTML table saved to: {output_file}")
    print("Features included:")
    print("  ✓ Play-by-play table with win probability")
    print("  ✓ Penalty impact analysis")
    print("  ✓ Major inflection points analysis")
    print("Open the file in your browser to view the enhanced analysis!")

if __name__ == "__main__":
    main()
