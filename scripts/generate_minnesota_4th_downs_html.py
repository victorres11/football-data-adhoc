#!/usr/bin/env python3
"""
Generate HTML report for Minnesota 4th Down Plays
Creates detailed tables grouped by game with all available information
"""

import json
import requests
from datetime import datetime

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

BASE_URL = config['base_url']

def load_4th_downs_data():
    """Load the generated 4th downs data"""
    try:
        with open('minnesota_4th_downs_2025_season.json', 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def get_game_info(game_id, week):
    """Get additional game information from CFBD API"""
    try:
        url = f"{BASE_URL}/games"
        params = {
            'id': game_id,
            'year': 2025,
            'week': week
        }
        headers = {
            'Authorization': f'Bearer {config["api_key"]}'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            games = response.json()
            if games:
                return games[0]
    except:
        pass
    return None

def get_all_game_plays(game_id, week):
    """Fetch ALL plays for a game to calculate scores at time of play"""
    try:
        url = f"{BASE_URL}/plays"
        params = {
            'gameId': game_id,
            'year': 2025,
            'week': week
        }
        headers = {
            'Authorization': f'Bearer {config["api_key"]}'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            all_plays = response.json()
            # Sort plays chronologically
            sorted_plays = sorted(all_plays, key=lambda p: (
                p.get('period', 1),
                -p.get('clock', {}).get('minutes', 15) if isinstance(p.get('clock'), dict) else 15,
                -p.get('clock', {}).get('seconds', 0) if isinstance(p.get('clock'), dict) else 0
            ))
            return sorted_plays
    except Exception as e:
        print(f"      Error fetching all plays: {e}")
    return []

def calculate_scores_for_plays(all_plays):
    """Calculate score at the time of each play"""
    minnesota_score = 0
    opponent_score = 0
    score_map = {}  # Map play ID to score at that time
    
    for play in all_plays:
        play_id = play.get('id')
        
        # Store score before this play
        score_map[play_id] = {
            'minnesota': minnesota_score,
            'opponent': opponent_score
        }
        
        # Update score if this is a scoring play
        if play.get('scoringPlay'):
            offense = play.get('offense', '')
            play_type = play.get('playType', '').lower()
            play_text = play.get('playText', '').lower()
            
            # Determine points scored
            points = 0
            if 'touchdown' in play_text or 'touchdown' in play_type:
                points = 7  # TD + XP
            elif 'field goal' in play_type or 'field goal' in play_text or 'fg' in play_type:
                points = 3
            elif 'safety' in play_type:
                points = 2
            elif 'two point' in play_text or '2pt' in play_text:
                points = 2
            
            if offense == 'Minnesota':
                minnesota_score += points
            else:
                opponent_score += points
    
    return score_map

def get_enhanced_play_data(game_id, week):
    """Fetch enhanced play data with drive and score information from CFBD"""
    try:
        url = f"{BASE_URL}/plays"
        params = {
            'gameId': game_id,
            'year': 2025,
            'week': week
        }
        headers = {
            'Authorization': f'Bearer {config["api_key"]}'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            all_plays = response.json()
            # Filter to only 4th down Minnesota plays
            minnesota_4th_downs = []
            for play in all_plays:
                if play.get('offense') == 'Minnesota' and play.get('down') == 4:
                    minnesota_4th_downs.append(play)
            return minnesota_4th_downs
    except:
        pass
    return []

def calculate_score_at_play(plays, target_play_index):
    """Calculate score at the time of a specific play"""
    minnesota_score = 0
    opponent_score = 0
    
    # Track scoring plays up to this point
    for i, play in enumerate(plays[:target_play_index + 1]):
        if play.get('scoringPlay'):
            offense = play.get('offense', '')
            play_type = play.get('playType', '').lower()
            
            # Determine points scored
            points = 0
            if 'touchdown' in play.get('playText', '').lower() or 'touchdown' in play_type:
                points = 7  # Assume TD with XP (could be 6, but 7 is common)
            elif 'field goal' in play_type or 'field goal' in play.get('playText', '').lower():
                points = 3
            elif 'safety' in play_type:
                points = 2
            
            if offense == 'Minnesota':
                minnesota_score += points
            else:
                opponent_score += points
    
    return minnesota_score, opponent_score

def enhance_plays_with_game_context(plays_data):
    """Enhance plays with additional context from game data"""
    enhanced_plays = []
    
    # Group by game
    plays_by_game = {}
    for play in plays_data.get('fourth_downs', []):
        game_id = play.get('game_id')
        week = play.get('week')
        if game_id not in plays_by_game:
            plays_by_game[game_id] = {
                'week': week,
                'opponent': play.get('opponent', 'Unknown'),
                'plays': []
            }
        plays_by_game[game_id]['plays'].append(play)
    
    # Fetch game details and enhanced play data
    print("Enhancing plays with game context...")
    for game_id, game_data in plays_by_game.items():
        week = game_data['week']
        print(f"  Fetching enhanced data for {game_id} (Week {week})...")
        
        # Get game info
        game_info = get_game_info(game_id, week)
        if game_info:
            home_team = game_info.get('homeTeam', 'Unknown')
            away_team = game_info.get('awayTeam', 'Unknown')
            game_data['home_team'] = home_team
            game_data['away_team'] = away_team
            game_data['home_score'] = game_info.get('homePoints', 0)
            game_data['away_score'] = game_info.get('awayPoints', 0)
            game_data['final_score'] = f"{away_team} {game_data['away_score']} - {home_team} {game_data['home_score']}"
            
            # Determine opponent for Minnesota
            if 'Minnesota' in home_team:
                game_data['opponent'] = away_team
            else:
                game_data['opponent'] = home_team
        
        # Fetch ALL plays for potential fallback matching (if enhanced play match fails)
        print(f"      Fetching all plays for matching...")
        all_plays = get_all_game_plays(game_id, week)
        
        # Fetch enhanced play data with drive info (just 4th downs)
        enhanced_plays_cfbd = get_enhanced_play_data(game_id, week)
        
        # Create lookup map for enhanced data
        enhanced_play_map = {}
        for ep in enhanced_plays_cfbd:
            # Create a key based on quarter, time, and distance/yards to goal
            quarter = ep.get('period', 1)
            clock = ep.get('clock', {})
            if isinstance(clock, dict):
                minutes = clock.get('minutes', 15)
                seconds = clock.get('seconds', 0)
                time_key = f"{minutes}:{seconds:02d}"
            else:
                time_key = str(clock)
            
            distance = ep.get('distance', 0)
            yards_to_goal = ep.get('yardsToGoal', 0)
            
            # Create multiple keys for matching
            key1 = f"{quarter}_{time_key}_{distance}_{yards_to_goal}"
            key2 = f"{quarter}_{time_key}_{ep.get('playText', '')[:40]}"
            enhanced_play_map[key1] = ep
            enhanced_play_map[key2] = ep
        
        # Enhance each play with additional data
        for play in game_data['plays']:
            quarter = play.get('quarter', 1)
            time_str = play.get('time', '15:00')
            distance = play.get('down_distance', '4 & 0').split('&')[1].strip() if '&' in play.get('down_distance', '') else '0'
            yards_to_goal = play.get('yards_to_goal', play.get('yards_to_endzone', 0))
            play_text_short = play.get('play_text', '')[:40]
            
            # Try multiple matching keys
            key1 = f"{quarter}_{time_str}_{distance}_{yards_to_goal}"
            key2 = f"{quarter}_{time_str}_{play_text_short}"
            
            ep = enhanced_play_map.get(key1) or enhanced_play_map.get(key2)
            
            if ep:
                play['drive_id'] = ep.get('driveId', 'N/A')
                play['drive_number'] = ep.get('driveNumber', 'N/A')
                play['play_id'] = ep.get('id', 'N/A')
                
                # Get yard line from CFBD data
                yard_line = ep.get('yardline', 0)
                if yard_line and yard_line != 0:
                    play['yard_line'] = yard_line
                
                # Get clock details
                clock = ep.get('clock', {})
                if isinstance(clock, dict):
                    play['clock_minutes'] = clock.get('minutes', 15)
                    play['clock_seconds'] = clock.get('seconds', 0)
                
                # Get score at time of this play directly from CFBD play data
                # CFBD includes offenseScore and defenseScore in each play
                offense_score = ep.get('offenseScore', 0)
                defense_score = ep.get('defenseScore', 0)
                offense_team = ep.get('offense', '')
                
                # Determine Minnesota and opponent scores
                if offense_team == 'Minnesota':
                    play['score_minnesota'] = offense_score
                    play['score_opponent'] = defense_score
                    play['score_at_time'] = f"{offense_score}-{defense_score}"
                else:
                    # Opponent has the ball, so scores are reversed
                    play['score_minnesota'] = defense_score
                    play['score_opponent'] = offense_score
                    play['score_at_time'] = f"{defense_score}-{offense_score}"
            else:
                # No CFBD match found, try to find matching play in all_plays by quarter/time/yards
                play['drive_id'] = 'N/A'
                play['drive_number'] = 'N/A'
                play['play_id'] = 'N/A'
                
                # Try to find a matching play in all_plays
                quarter = play.get('quarter', 1)
                time_str = play.get('time', '15:00')
                ytg = play.get('yards_to_goal', 0)
                
                # Parse time
                try:
                    if ':' in time_str:
                        parts = time_str.split(':')
                        time_min = int(parts[0])
                        time_sec = int(parts[1]) if len(parts) > 1 else 0
                    else:
                        time_min = 15
                        time_sec = 0
                except:
                    time_min = 15
                    time_sec = 0
                
                # Find best matching play
                best_match = None
                best_diff = float('inf')
                
                for all_play in all_plays:
                    if (all_play.get('period') == quarter and
                        all_play.get('offense') == 'Minnesota' and
                        all_play.get('down') == 4):
                        # Check time
                        play_clock = all_play.get('clock', {})
                        if isinstance(play_clock, dict):
                            play_min = play_clock.get('minutes', 15)
                            play_sec = play_clock.get('seconds', 0)
                            time_diff = abs((time_min * 60 + time_sec) - (play_min * 60 + play_sec))
                            
                            # Check yards to goal
                            play_ytg = all_play.get('yardsToGoal', 0)
                            ytg_diff = abs(play_ytg - ytg)
                            
                            # Combined difference
                            total_diff = time_diff + (ytg_diff * 0.1)  # Weight time more
                            
                            if total_diff < best_diff:
                                best_diff = total_diff
                                best_match = all_play
                
                # If we found a match, use its score
                if best_match and best_diff < 120:  # Within 2 minutes
                    offense_score = best_match.get('offenseScore', 0)
                    defense_score = best_match.get('defenseScore', 0)
                    offense_team = best_match.get('offense', '')
                    
                    if offense_team == 'Minnesota':
                        play['score_minnesota'] = offense_score
                        play['score_opponent'] = defense_score
                        play['score_at_time'] = f"{offense_score}-{defense_score}"
                    else:
                        play['score_minnesota'] = defense_score
                        play['score_opponent'] = offense_score
                        play['score_at_time'] = f"{defense_score}-{offense_score}"
                else:
                    play['score_at_time'] = 'N/A'
                    play['score_minnesota'] = None
                    play['score_opponent'] = None
        
        # Sort plays by quarter and time (reverse time for proper sequence)
        def sort_key(p):
            quarter = p.get('quarter', 1)
            time_str = p.get('time', '15:00')
            # Parse time for sorting
            try:
                if ':' in time_str:
                    parts = time_str.split(':')
                    minutes = int(parts[0])
                    seconds = int(parts[1]) if len(parts) > 1 else 0
                    time_value = minutes * 60 + seconds
                else:
                    time_value = 0
            except:
                time_value = 0
            return (quarter, -time_value)  # Negative for reverse time order
        
        game_data['plays'].sort(key=sort_key)
    
    return plays_by_game

def generate_html_report(plays_data, enhanced_games):
    """Generate comprehensive HTML report with tables grouped by game"""
    
    summary = plays_data.get('season_summary', {})
    total_4th_downs = plays_data.get('total_4th_downs', 0)
    go_for_it = plays_data.get('go_for_it_attempts', 0)
    conversions = plays_data.get('conversions', 0)
    conversion_rate = plays_data.get('conversion_rate', 0)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minnesota 2025 Season - All 4th Down Offensive Plays</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #7E1416 0%, #000000 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #7E1416 0%, #000000 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #7E1416;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .game-section {{
            margin-bottom: 50px;
            border-top: 3px solid #7E1416;
            padding-top: 30px;
        }}
        
        .game-header {{
            background: #7E1416;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin-bottom: 0;
        }}
        
        .game-header h2 {{
            font-size: 1.8em;
            margin-bottom: 10px;
        }}
        
        .game-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 15px 20px;
            background: #f8f9fa;
            border-left: 4px solid #7E1416;
        }}
        
        .info-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .info-label {{
            font-size: 0.8em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .info-value {{
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
            margin-top: 5px;
        }}
        
        .plays-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-bottom: 30px;
        }}
        
        .plays-table th {{
            background: #7E1416;
            color: white;
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .plays-table td {{
            padding: 12px 10px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 0.9em;
        }}
        
        .plays-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .plays-table tr.go-for-it {{
            background-color: #fff3cd;
        }}
        
        .plays-table tr.go-for-it:hover {{
            background-color: #ffeaa7;
        }}
        
        .plays-table tr.converted {{
            border-left: 4px solid #28a745;
        }}
        
        .plays-table tr.failed {{
            border-left: 4px solid #dc3545;
        }}
        
        .plays-table tr.punt-fg {{
            border-left: 4px solid #6c757d;
        }}
        
        .quarter-badge {{
            display: inline-block;
            background: #7E1416;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .outcome-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .outcome-converted {{
            background: #d4edda;
            color: #155724;
        }}
        
        .outcome-failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .outcome-punt {{
            background: #e2e3e5;
            color: #383d41;
        }}
        
        .outcome-fg {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .outcome-td {{
            background: #cce5ff;
            color: #004085;
        }}
        
        .outcome-timeout {{
            background: #e9ecef;
            color: #495057;
        }}
        
        .plays-table tr.timeout {{
            background-color: #f8f9fa;
            border-left: 4px solid #adb5bd;
        }}
        
        .plays-table tr.timeout:hover {{
            background-color: #e9ecef;
        }}
        
        .yards {{
            font-weight: bold;
            color: #7E1416;
        }}
        
        .down-distance {{
            font-family: monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        
        .play-text {{
            max-width: 400px;
            word-wrap: break-word;
        }}
        
        .no-plays {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }}
        
        .toc {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .toc h3 {{
            margin-bottom: 15px;
            color: #7E1416;
        }}
        
        .toc ul {{
            list-style: none;
            columns: 2;
            column-gap: 30px;
        }}
        
        .toc li {{
            margin-bottom: 8px;
        }}
        
        .toc a {{
            color: #333;
            text-decoration: none;
            padding: 5px 10px;
            display: block;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .toc a:hover {{
            background: #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏈 Minnesota Golden Gophers</h1>
            <div class="subtitle">2025 Season - All 4th Down Offensive Plays</div>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value">{total_4th_downs}</div>
                <div class="stat-label">Total 4th Downs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{go_for_it}</div>
                <div class="stat-label">Go For It Attempts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{conversions}</div>
                <div class="stat-label">Conversions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{conversion_rate:.1f}%</div>
                <div class="stat-label">Conversion Rate</div>
            </div>
        </div>
        
        <div class="content">
            <div class="toc">
                <h3>📋 Table of Contents</h3>
                <ul>
"""
    
    # Add table of contents
    for game_id, game_data in sorted(enhanced_games.items(), key=lambda x: x[1]['week']):
        week = game_data['week']
        opponent = game_data.get('opponent', 'Unknown')
        play_count = len(game_data['plays'])
        html += f"""
                    <li><a href="#game-{game_id}">Week {week} vs {opponent} ({play_count} plays)</a></li>
"""
    
    html += """
                </ul>
            </div>
"""
    
    # Add game sections
    for game_id, game_data in sorted(enhanced_games.items(), key=lambda x: x[1]['week']):
        week = game_data['week']
        opponent = game_data.get('opponent', 'Unknown')
        home_team = game_data.get('home_team', 'Unknown')
        away_team = game_data.get('away_team', 'Unknown')
        final_score = game_data.get('final_score', f"{away_team} vs {home_team}")
        plays = game_data['plays']
        
        # Scores are already populated from CFBD play data (offenseScore/defenseScore)
        # No calculation needed - scores come directly from the API
        
        html += f"""
            <div id="game-{game_id}" class="game-section">
                <div class="game-header">
                    <h2>Week {week}: Minnesota vs {opponent}</h2>
                </div>
                <div class="game-info">
                    <div class="info-item">
                        <span class="info-label">Game ID</span>
                        <span class="info-value">{game_id}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Home Team</span>
                        <span class="info-value">{home_team}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Away Team</span>
                        <span class="info-value">{away_team}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Final Score</span>
                        <span class="info-value">{final_score}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Total 4th Downs</span>
                        <span class="info-value">{len(plays)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Go For It</span>
                        <span class="info-value">{sum(1 for p in plays if p.get('is_go_for_it'))}</span>
                    </div>
                </div>
"""
        
        if plays:
            html += """
                <table class="plays-table">
                    <thead>
                        <tr>
                            <th>Qtr</th>
                            <th>Time</th>
                            <th>Drive</th>
                            <th>Down & Distance</th>
                            <th>Yard Line</th>
                            <th>Yards to Goal</th>
                            <th>Type</th>
                            <th>Yards Gained</th>
                            <th>Score</th>
                            <th>Outcome</th>
                            <th>Play Description</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            
            for play in plays:
                quarter = play.get('quarter', 1)
                time_display = play.get('time', '15:00')
                drive_id = play.get('drive_id', 'N/A')
                drive_number = play.get('drive_number', 'N/A')
                drive_display = f"#{drive_number}" if drive_number != 'N/A' and drive_number != '' else f"ID: {drive_id}" if drive_id != 'N/A' and drive_id != '' else 'N/A'
                down_dist = play.get('down_distance', '4 & 0')
                yards_to_goal = play.get('yards_to_goal', play.get('yards_to_endzone', 0))
                
                # Calculate yard line from yards_to_goal:
                # yards_to_goal = 11 → yard_line = +11 (opponent's 11)
                # yards_to_goal = 90 → yard_line = -10 (our own 10)
                # yards_to_goal = 50 → yard_line = 50 (midfield)
                if yards_to_goal and yards_to_goal != 'N/A' and yards_to_goal != 0:
                    try:
                        ytg = int(yards_to_goal)
                        if ytg == 50:
                            yard_line = 50
                        elif ytg < 50:
                            yard_line = f"+{ytg}"
                        else:  # ytg > 50
                            yard_line = -(100 - ytg)
                    except (ValueError, TypeError):
                        yard_line = 'N/A'
                else:
                    yard_line = 'N/A'
                    
                if yards_to_goal == 0:
                    yards_to_goal = 'N/A'
                is_go_for_it = play.get('is_go_for_it', False)
                play_result = play.get('play_result', 'Unknown')
                
                # Apply field goal fix after getting the values
                play_type = play.get('play_type', '').lower()
                play_text = play.get('play_text', '').lower()
                play_type_cfbd = play.get('play_type_cfbd', '').lower()
                
                # Check for timeout - should be classified as non-play
                is_timeout = 'timeout' in play_type or 'timeout' in play_text or 'timeout' in play_type_cfbd
                
                if is_timeout:
                    is_go_for_it = False
                    play_result = 'Timeout'
                    converted = None  # Not applicable for timeout
                elif 'field goal' in play_type or 'field goal' in play_text or 'fg' in play_text or 'fg good' in play_text:
                    is_go_for_it = False
                    play_result = 'Field Goal'
                elif play_result == 'Unknown':
                    # Determine play_result from available data
                    if play_type_cfbd:
                        if 'punt' in play_type_cfbd:
                            play_result = 'Punt'
                        elif 'field goal' in play_type_cfbd:
                            if 'good' in play_type_cfbd or 'made' in play_type_cfbd:
                                play_result = 'Field Goal'
                            elif 'missed' in play_type_cfbd:
                                play_result = 'Missed FG'
                            else:
                                play_result = 'Field Goal'
                        elif ('rush' in play_type_cfbd or 'pass' in play_type_cfbd):
                            if converted is True:
                                play_result = 'Conversion'
                            elif converted is False:
                                play_result = 'Failed'
                    elif 'punt' in play_type:
                        play_result = 'Punt'
                    elif 'rush' in play_type or 'run' in play_text:
                        if converted is True:
                            play_result = 'Conversion'
                        elif converted is False:
                            play_result = 'Failed'
                        else:
                            play_result = 'Rush'
                    elif 'pass' in play_type:
                        if converted is True:
                            play_result = 'Conversion'
                        elif converted is False:
                            play_result = 'Failed'
                        else:
                            play_result = 'Pass'
                    elif 'first down' in play_text or '1st down' in play_text:
                        play_result = 'Conversion'
                    elif converted is True:
                        play_result = 'Conversion'
                    elif converted is False:
                        play_result = 'Failed'
                    elif is_go_for_it:
                        play_result = 'Attempt'
                yards_gained = play.get('yards_gained', 0)
                converted = play.get('converted')
                play_text = play.get('play_text', 'N/A')
                scoring_play = play.get('scoring_play', False)
                
                # Get score at time of play - prioritize CFBD data, then calculated
                score_at_time = play.get('score_at_time', 'N/A')
                minn_score = play.get('score_minnesota')
                opp_score = play.get('score_opponent')
                
                # If CFBD scores not available, use calculated scores
                if (minn_score is None or opp_score is None) and play.get('current_minn_score') is not None:
                    minn_score = play.get('current_minn_score')
                    opp_score = play.get('current_opp_score')
                
                # Format score display: always show Minnesota-Opponent format
                if score_at_time != 'N/A' and score_at_time != '0-0' and '-' in score_at_time:
                    # Use the pre-calculated score_at_time string if it's valid
                    pass
                elif minn_score is not None and opp_score is not None:
                    score_at_time = f"{int(minn_score)}-{int(opp_score)}"
                else:
                    # Default fallback - show 0-0
                    score_at_time = "0-0"
                
                # Determine row classes
                row_classes = []
                if is_timeout:
                    row_classes.append('timeout')
                elif is_go_for_it:
                    row_classes.append('go-for-it')
                    if converted is True:
                        row_classes.append('converted')
                    elif converted is False:
                        row_classes.append('failed')
                else:
                    row_classes.append('punt-fg')
                
                # Outcome badge
                if is_timeout:
                    outcome_class = 'outcome-timeout'
                    outcome_text = 'Timeout'
                elif play_result == 'Touchdown':
                    outcome_class = 'outcome-td'
                    outcome_text = 'TD'
                elif play_result == 'Punt':
                    outcome_class = 'outcome-punt'
                    outcome_text = 'Punt'
                elif play_result == 'Field Goal':
                    outcome_class = 'outcome-fg'
                    outcome_text = 'FG'
                elif converted is True:
                    outcome_class = 'outcome-converted'
                    outcome_text = '✓ Converted'
                elif converted is False:
                    outcome_class = 'outcome-failed'
                    outcome_text = '✗ Failed'
                else:
                    outcome_class = 'outcome-punt'
                    outcome_text = play_result
                
                html += f"""
                        <tr class="{' '.join(row_classes)}">
                            <td><span class="quarter-badge">Q{quarter}</span></td>
                            <td>{time_display}</td>
                            <td>{drive_display}</td>
                            <td><span class="down-distance">{down_dist}</span></td>
                            <td>{yard_line}</td>
                            <td>{yards_to_goal}</td>
                            <td>{'Go For It' if is_go_for_it else play_result}</td>
                            <td class="yards">{'+' if yards_gained > 0 else ''}{yards_gained}</td>
                            <td style="font-weight: bold;">{score_at_time}</td>
                            <td><span class="outcome-badge {outcome_class}">{outcome_text}</span></td>
                            <td class="play-text">{play_text}</td>
                        </tr>
"""
            
            html += """
                    </tbody>
                </table>
"""
        else:
            html += """
                <div class="no-plays">No 4th down plays recorded for this game</div>
"""
        
        html += """
            </div>
"""
    
    html += f"""
        </div>
        
        <div style="padding: 20px; text-align: center; color: #666; font-size: 0.9em;">
            Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("=" * 70)
    print("Generating HTML Report for Minnesota 4th Down Plays")
    print("=" * 70)
    
    # Load data
    plays_data = load_4th_downs_data()
    if not plays_data:
        print("Error: Could not load 4th downs data")
        return
    
    # Enhance with game context
    enhanced_games = enhance_plays_with_game_context(plays_data)
    
    # Generate HTML
    html = generate_html_report(plays_data, enhanced_games)
    
    # Save HTML
    output_file = 'minnesota_4th_downs_2025_season.html'
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"\n✓ HTML report generated: {output_file}")
    print(f"✓ Includes {len(enhanced_games)} games")
    print(f"✓ Total plays: {plays_data.get('total_4th_downs', 0)}")
    print(f"\nOpen {output_file} in your browser to view the report!")

if __name__ == "__main__":
    main()

