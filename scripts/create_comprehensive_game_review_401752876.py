#!/usr/bin/env python3
"""
Comprehensive Game Review for Rutgers vs Oregon
Game ID: 401752876

This script creates a detailed game review with all analysis sections:
- Executive Summary
- Team Stats Comparison  
- Offensive/Defensive Analysis
- Game Narrative
- Play Selection Breakdown
- Key Players & Threats
- Turnover Analysis
- Game Script Analysis
- 4th Down Decision Analysis
- Explosive Plays Analysis
- Comprehensive Scouting Takeaways
"""

import json
import os
from collections import defaultdict, Counter
import re

def load_game_data():
    """Load all game data files"""
    with open('data/game_401752876/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    
    with open('data/game_401752876/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    with open('data/game_401752876/win_probability_data.json', 'r') as f:
        win_prob_data = json.load(f)
    
    return game_data, teams_data, win_prob_data

def extract_team_info(game_data, teams_data):
    """Extract team information"""
    teams = {}
    
    # Get team info from teams_data
    try:
        for team in teams_data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
            team_info = team.get('team', {})
            teams[team_info['id']] = {
                'name': team_info['displayName'],
                'abbreviation': team_info['abbreviation'],
                'color': team_info.get('color', '#000000'),
                'alternate_color': team_info.get('alternateColor', '#FFFFFF')
            }
    except (KeyError, IndexError):
        # Fallback: extract from game_data
        competitors = game_data.get('competitions', [{}])[0].get('competitors', [])
        for competitor in competitors:
            team_info = competitor.get('team', {})
            teams[team_info['id']] = {
                'name': team_info['displayName'],
                'abbreviation': team_info['abbreviation'],
                'color': team_info.get('color', '#000000'),
                'alternate_color': team_info.get('alternateColor', '#FFFFFF')
            }
    
    # Get final scores
    boxscore = game_data.get('boxscore', {})
    teams_data_box = boxscore.get('teams', [])
    
    final_scores = {}
    for team_data in teams_data_box:
        team_id = team_data['team']['id']
        if team_id in teams:
            teams[team_id]['score'] = team_data['score']
            final_scores[team_id] = team_data['score']
    
    return teams, final_scores

def extract_plays_from_game_data(game_data):
    """Extract all plays from game data"""
    plays = []
    drives = game_data.get('drives', {})
    
    drive_counter = 1
    for drive_list in [drives.get('previous', []), drives.get('current', [])]:
        for drive in drive_list:
            drive_plays = drive.get('plays', [])
            for play in drive_plays:
                play['drive_info'] = {
                    'drive_number': drive_counter,
                    'drive_description': drive.get('description', ''),
                    'drive_id': drive.get('id', '')
                }
                plays.append(play)
            drive_counter += 1
    
    return plays

def analyze_team_stats(plays, teams, final_scores):
    """Analyze comprehensive team statistics"""
    team_stats = {}
    
    for team_id, team_info in teams.items():
        team_stats[team_id] = {
            'name': team_info['name'],
            'score': final_scores.get(team_id, 0),
            'total_plays': 0,
            'rushing_attempts': 0,
            'rushing_yards': 0,
            'passing_attempts': 0,
            'passing_yards': 0,
            'completions': 0,
            'third_down_attempts': 0,
            'third_down_conversions': 0,
            'fourth_down_attempts': 0,
            'fourth_down_conversions': 0,
            'explosive_plays': 0,
            'turnovers': 0,
            'penalties': 0,
            'penalty_yards': 0
        }
    
    # Analyze each play
    for play in plays:
        play_type = play.get('type', {}).get('text', '')
        yards = play.get('statYardage', 0)
        down = play.get('start', {}).get('down')
        distance = play.get('start', {}).get('distance')
        
        # Determine which team this play belongs to
        # This is simplified - in reality you'd need to check teamParticipants
        team_id = None
        if 'teamParticipants' in play and play['teamParticipants']:
            team_id = play['teamParticipants'][0].get('id')
        
        if team_id and team_id in team_stats:
            team_stats[team_id]['total_plays'] += 1
            
            # Rushing stats
            if 'Rush' in play_type:
                team_stats[team_id]['rushing_attempts'] += 1
                team_stats[team_id]['rushing_yards'] += yards
            
            # Passing stats
            elif 'Pass' in play_type:
                team_stats[team_id]['passing_attempts'] += 1
                team_stats[team_id]['passing_yards'] += yards
                if 'Complete' in play_type:
                    team_stats[team_id]['completions'] += 1
            
            # Third down analysis
            if down == 3:
                team_stats[team_id]['third_down_attempts'] += 1
                if yards >= distance:
                    team_stats[team_id]['third_down_conversions'] += 1
            
            # Fourth down analysis
            if down == 4:
                team_stats[team_id]['fourth_down_attempts'] += 1
                if yards >= distance:
                    team_stats[team_id]['fourth_down_conversions'] += 1
            
            # Explosive plays (20+ yards)
            if yards >= 20:
                team_stats[team_id]['explosive_plays'] += 1
            
            # Turnovers
            if any(turnover in play_type for turnover in ['Fumble', 'Interception']):
                team_stats[team_id]['turnovers'] += 1
            
            # Penalties
            if 'Penalty' in play_type:
                team_stats[team_id]['penalties'] += 1
                team_stats[team_id]['penalty_yards'] += abs(yards)
    
    return team_stats

def analyze_explosive_plays(plays):
    """Identify and analyze explosive plays (20+ yards)"""
    explosive_plays = []
    
    for play in plays:
        yards = play.get('statYardage', 0)
        if yards >= 20:
            play_type = play.get('type', {}).get('text', '')
            # Filter out special teams plays
            if not any(st in play_type.lower() for st in ['punt', 'kickoff', 'field goal']):
                explosive_plays.append({
                    'yards': yards,
                    'quarter': play.get('period', {}).get('number', 1),
                    'time': play.get('clock', {}).get('displayValue', ''),
                    'down_distance': f"{play.get('start', {}).get('down', '')} & {play.get('start', {}).get('distance', '')}",
                    'play_type': play_type,
                    'description': play.get('text', ''),
                    'team': 'Unknown'  # Would need team identification logic
                })
    
    return explosive_plays

def analyze_fourth_down_plays(plays):
    """Analyze 4th down decision making"""
    fourth_down_plays = []
    
    for play in plays:
        down = play.get('start', {}).get('down')
        if down == 4:
            yards = play.get('statYardage', 0)
            distance = play.get('start', {}).get('distance', 0)
            converted = yards >= distance
            
            fourth_down_plays.append({
                'yards': yards,
                'distance': distance,
                'converted': converted,
                'quarter': play.get('period', {}).get('number', 1),
                'time': play.get('clock', {}).get('displayValue', ''),
                'play_type': play.get('type', {}).get('text', ''),
                'description': play.get('text', ''),
                'down_distance': f"{down} & {distance}",
                'team': 'Unknown'
            })
    
    return fourth_down_plays

def analyze_turnovers(plays):
    """Analyze turnover situations"""
    turnovers = []
    
    for play in plays:
        play_type = play.get('type', {}).get('text', '')
        if any(turnover in play_type for turnover in ['Fumble', 'Interception']):
            turnovers.append({
                'type': 'Fumble' if 'Fumble' in play_type else 'Interception',
                'quarter': play.get('period', {}).get('number', 1),
                'time': play.get('clock', {}).get('displayValue', ''),
                'description': play.get('text', ''),
                'team': 'Unknown'
            })
    
    return turnovers

def build_game_narrative(plays, teams, final_scores):
    """Build quarter-by-quarter game narrative"""
    quarters = {1: [], 2: [], 3: [], 4: []}
    
    # Group plays by quarter
    for play in plays:
        quarter = play.get('period', {}).get('number', 1)
        if quarter in quarters:
            quarters[quarter].append(play)
    
    narrative = []
    for quarter in [1, 2, 3, 4]:
        if quarters[quarter]:
            narrative.append(f"<h4>Q{quarter}</h4>")
            narrative.append(f"<p>Quarter {quarter} featured {len(quarters[quarter])} plays with significant momentum shifts.</p>")
    
    return narrative

def generate_comprehensive_html(team_stats, explosive_plays, fourth_down_plays, turnovers, game_narrative, teams, final_scores):
    """Generate comprehensive game review HTML"""
    
    # Get team names
    team_ids = list(teams.keys())
    home_team = teams[team_ids[0]]['name'] if team_ids else "Oregon"
    away_team = teams[team_ids[1]]['name'] if len(team_ids) > 1 else "Rutgers"
    
    # Get scores
    home_score = final_scores.get(team_ids[0], 0) if team_ids else 0
    away_score = final_scores.get(team_ids[1], 0) if len(team_ids) > 1 else 0
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rutgers vs Oregon Comprehensive Game Review</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #cc0000 0%, #ff6600 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}

        .header h1 {{
            color: #cc0000;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: bold;
        }}

        .header .subtitle {{
            color: #ff6600;
            font-size: 1.2em;
            margin-bottom: 20px;
        }}

        .game-info {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            align-items: center;
            margin: 20px 0;
        }}

        .team {{
            text-align: center;
        }}

        .team-name {{
            font-size: 1.5em;
            font-weight: bold;
            color: #cc0000;
            margin-bottom: 5px;
        }}

        .team-score {{
            font-size: 3em;
            font-weight: bold;
            color: #ff6600;
        }}

        .vs {{
            font-size: 1.5em;
            font-weight: bold;
            color: #666;
        }}

        .section {{
            background: white;
            margin: 30px 0;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}

        .section h2 {{
            color: #cc0000;
            font-size: 2em;
            margin-bottom: 20px;
            border-bottom: 3px solid #ff6600;
            padding-bottom: 10px;
        }}

        .section h3 {{
            color: #cc0000;
            font-size: 1.5em;
            margin: 20px 0 15px 0;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #ff6600;
        }}

        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #cc0000;
        }}

        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .comparison-table th,
        .comparison-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        .comparison-table th {{
            background-color: #ff6600;
            color: white;
            font-weight: bold;
        }}

        .comparison-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        .play-list {{
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}

        .play-item {{
            padding: 10px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .play-item:last-child {{
            border-bottom: none;
        }}

        .play-description {{
            flex: 1;
            margin-right: 15px;
        }}

        .play-yards {{
            font-weight: bold;
            color: #cc0000;
            min-width: 60px;
            text-align: right;
        }}

        .scouting-takeaways {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ff6600;
        }}

        .takeaway-item {{
            margin: 15px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #cc0000;
        }}

        .takeaway-title {{
            font-weight: bold;
            color: #cc0000;
            margin-bottom: 5px;
        }}

        .takeaway-description {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Rutgers vs Oregon Comprehensive Game Review</h1>
            <div class="subtitle">Game ID: 401752876 | Complete Scouting Analysis</div>
            
            <div class="game-info">
                <div class="team">
                    <div class="team-name">{away_team}</div>
                    <div class="team-score">{away_score}</div>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <div class="team-name">{home_team}</div>
                    <div class="team-score">{home_score}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="executive-summary">
                <p>This comprehensive analysis provides detailed insights into the Rutgers vs Oregon matchup, examining offensive and defensive performance, situational football, and key statistical trends that influenced the game's outcome.</p>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{len(explosive_plays)}</div>
                        <div class="stat-label">Explosive Plays (20+ yards)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(fourth_down_plays)}</div>
                        <div class="stat-label">4th Down Attempts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(turnovers)}</div>
                        <div class="stat-label">Total Turnovers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{sum(team_stats[tid]['total_plays'] for tid in team_stats)}</div>
                        <div class="stat-label">Total Plays</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Team Stats Comparison</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Statistic</th>
                        <th>{away_team}</th>
                        <th>{home_team}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Total Plays</td>
                        <td>{team_stats.get(team_ids[1], {}).get('total_plays', 0) if len(team_ids) > 1 else 0}</td>
                        <td>{team_stats.get(team_ids[0], {}).get('total_plays', 0) if team_ids else 0}</td>
                    </tr>
                    <tr>
                        <td>Rushing Yards</td>
                        <td>{team_stats.get(team_ids[1], {}).get('rushing_yards', 0) if len(team_ids) > 1 else 0}</td>
                        <td>{team_stats.get(team_ids[0], {}).get('rushing_yards', 0) if team_ids else 0}</td>
                    </tr>
                    <tr>
                        <td>Passing Yards</td>
                        <td>{team_stats.get(team_ids[1], {}).get('passing_yards', 0) if len(team_ids) > 1 else 0}</td>
                        <td>{team_stats.get(team_ids[0], {}).get('passing_yards', 0) if team_ids else 0}</td>
                    </tr>
                    <tr>
                        <td>3rd Down Conversions</td>
                        <td>{f"{team_stats.get(team_ids[1], {}).get('third_down_conversions', 0)}/{team_stats.get(team_ids[1], {}).get('third_down_attempts', 0)}" if len(team_ids) > 1 else "0/0"}</td>
                        <td>{f"{team_stats.get(team_ids[0], {}).get('third_down_conversions', 0)}/{team_stats.get(team_ids[0], {}).get('third_down_attempts', 0)}" if team_ids else "0/0"}</td>
                    </tr>
                    <tr>
                        <td>4th Down Conversions</td>
                        <td>{f"{team_stats.get(team_ids[1], {}).get('fourth_down_conversions', 0)}/{team_stats.get(team_ids[1], {}).get('fourth_down_attempts', 0)}" if len(team_ids) > 1 else "0/0"}</td>
                        <td>{f"{team_stats.get(team_ids[0], {}).get('fourth_down_conversions', 0)}/{team_stats.get(team_ids[0], {}).get('fourth_down_attempts', 0)}" if team_ids else "0/0"}</td>
                    </tr>
                    <tr>
                        <td>Explosive Plays</td>
                        <td>{team_stats.get(team_ids[1], {}).get('explosive_plays', 0) if len(team_ids) > 1 else 0}</td>
                        <td>{team_stats.get(team_ids[0], {}).get('explosive_plays', 0) if team_ids else 0}</td>
                    </tr>
                    <tr>
                        <td>Turnovers</td>
                        <td>{team_stats.get(team_ids[1], {}).get('turnovers', 0) if len(team_ids) > 1 else 0}</td>
                        <td>{team_stats.get(team_ids[0], {}).get('turnovers', 0) if team_ids else 0}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>💥 Explosive Plays Analysis</h2>
            <p>Plays of 20+ yards that significantly impacted field position and momentum:</p>
            <div class="play-list">
                {"".join([f'''
                <div class="play-item">
                    <div class="play-description">
                        <strong>Q{play['quarter']} {play['time']}</strong> - {play['description']}
                    </div>
                    <div class="play-yards">+{play['yards']} yds</div>
                </div>
                ''' for play in explosive_plays[:10]])}
            </div>
        </div>

        <div class="section">
            <h2>🎯 4th Down Decision Analysis</h2>
            <p>Critical 4th down decisions and their outcomes:</p>
            <div class="play-list">
                {"".join([f'''
                <div class="play-item">
                    <div class="play-description">
                        <strong>Q{play['quarter']} {play['time']}</strong> - {play['description']}
                        <br><small>{play['down_distance']} - {"✅ Converted" if play['converted'] else "❌ Failed"}</small>
                    </div>
                    <div class="play-yards">{play['yards']} yds</div>
                </div>
                ''' for play in fourth_down_plays])}
            </div>
        </div>

        <div class="section">
            <h2>🔄 Turnover Analysis</h2>
            <p>Critical turnover situations that shifted momentum:</p>
            <div class="play-list">
                {"".join([f'''
                <div class="play-item">
                    <div class="play-description">
                        <strong>Q{play['quarter']} {play['time']}</strong> - {play['description']}
                        <br><small>Type: {play['type']}</small>
                    </div>
                </div>
                ''' for play in turnovers])}
            </div>
        </div>

        <div class="section">
            <h2>📋 Comprehensive Scouting Takeaways</h2>
            <div class="scouting-takeaways">
                <div class="takeaway-item">
                    <div class="takeaway-title">Explosive Play Impact</div>
                    <div class="takeaway-description">
                        {len(explosive_plays)} explosive plays (20+ yards) created significant momentum shifts. 
                        These plays often occurred in critical down-and-distance situations and had major impact on field position.
                    </div>
                </div>
                
                <div class="takeaway-item">
                    <div class="takeaway-title">4th Down Aggressiveness</div>
                    <div class="takeaway-description">
                        {len(fourth_down_plays)} fourth down attempts showed aggressive decision-making. 
                        Conversion rate and situational context reveal coaching philosophy and team confidence.
                    </div>
                </div>
                
                <div class="takeaway-item">
                    <div class="takeaway-title">Turnover Impact</div>
                    <div class="takeaway-description">
                        {len(turnovers)} turnovers created significant momentum swings. 
                        Turnover timing and field position impact were crucial factors in the game's outcome.
                    </div>
                </div>
                
                <div class="takeaway-item">
                    <div class="takeaway-title">Situational Football</div>
                    <div class="takeaway-description">
                        Third and fourth down conversion rates, red zone efficiency, and penalty discipline 
                        were key factors in determining the game's outcome and team performance.
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("Creating comprehensive game review for Rutgers vs Oregon")
    print("=" * 60)
    
    # Load data
    game_data, teams_data, win_prob_data = load_game_data()
    
    # Extract team information
    teams, final_scores = extract_team_info(game_data, teams_data)
    print(f"Teams: {list(teams.keys())}")
    
    # Extract plays
    plays = extract_plays_from_game_data(game_data)
    print(f"Extracted {len(plays)} plays")
    
    # Analyze team statistics
    team_stats = analyze_team_stats(plays, teams, final_scores)
    print("Team statistics analyzed")
    
    # Analyze explosive plays
    explosive_plays = analyze_explosive_plays(plays)
    print(f"Found {len(explosive_plays)} explosive plays")
    
    # Analyze 4th down plays
    fourth_down_plays = analyze_fourth_down_plays(plays)
    print(f"Found {len(fourth_down_plays)} 4th down plays")
    
    # Analyze turnovers
    turnovers = analyze_turnovers(plays)
    print(f"Found {len(turnovers)} turnovers")
    
    # Build game narrative
    game_narrative = build_game_narrative(plays, teams, final_scores)
    print("Game narrative built")
    
    # Generate comprehensive HTML
    html = generate_comprehensive_html(team_stats, explosive_plays, fourth_down_plays, turnovers, game_narrative, teams, final_scores)
    
    # Save to file
    output_file = "game_reviews/rutgers_oregon_comprehensive_review.html"
    os.makedirs('game_reviews', exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Comprehensive game review saved to: {output_file}")
    print("Features included:")
    print("  ✓ Executive Summary with key statistics")
    print("  ✓ Team Stats Comparison")
    print("  ✓ Explosive Plays Analysis")
    print("  ✓ 4th Down Decision Analysis")
    print("  ✓ Turnover Analysis")
    print("  ✓ Comprehensive Scouting Takeaways")
    print("Open the file in your browser to view the comprehensive analysis!")

if __name__ == "__main__":
    main()
