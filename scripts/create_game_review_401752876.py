#!/usr/bin/env python3
"""
Create traditional game review analysis for Rutgers vs Oregon (Game ID: 401752876)
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
    
    return game_data, win_prob_data

def extract_plays_from_game_data(game_data):
    """Extract plays from game data (public API structure)"""
    plays = []
    drives = game_data.get('drives', {})
    
    for drive_list in [drives.get('previous', []), drives.get('current', [])]:
        for drive in drive_list:
            plays.extend(drive.get('plays', []))
    
    return plays

def identify_key_moments(plays, win_prob_data):
    """Identify key moments in the game"""
    key_moments = []
    
    # Create win probability lookup
    wp_lookup = {}
    for entry in win_prob_data:
        play_id = entry.get('playId')
        if play_id:
            wp_lookup[play_id] = entry
    
    # Find significant win probability changes
    for i, play in enumerate(plays):
        play_id = play.get('id')
        wp_data = wp_lookup.get(play_id)
        
        if wp_data and i > 0:
            prev_play = plays[i-1]
            prev_play_id = prev_play.get('id')
            prev_wp_data = wp_lookup.get(prev_play_id)
            
            if prev_wp_data:
                prev_home_wp = prev_wp_data.get('homeWinPercentage', 0) * 100
                curr_home_wp = wp_data.get('homeWinPercentage', 0) * 100
                wp_change = curr_home_wp - prev_home_wp
                
                # Significant moments (3%+ change)
                if abs(wp_change) >= 3.0:
                    key_moments.append({
                        'play_number': i + 1,
                        'play': play,
                        'wp_change': wp_change,
                        'home_wp': curr_home_wp,
                        'away_wp': 100 - curr_home_wp
                    })
    
    return key_moments

def analyze_team_performance(plays):
    """Analyze team performance"""
    rutgers_plays = []
    oregon_plays = []
    
    for play in plays:
        play_text = play.get('text', '').lower()
        if 'rutgers' in play_text or 'scarlet' in play_text:
            rutgers_plays.append(play)
        elif 'oregon' in play_text or 'ducks' in play_text:
            oregon_plays.append(play)
    
    return {
        'rutgers_plays': len(rutgers_plays),
        'oregon_plays': len(oregon_plays),
        'total_plays': len(plays)
    }

def generate_game_review_html(plays, key_moments, team_performance, game_data, win_prob_data):
    """Generate traditional game review HTML from Rutgers perspective"""
    
    # Get game information
    competitors = game_data.get('header', {}).get('competitions', [{}])[0].get('competitors', [])
    home_team = competitors[0].get('team', {}).get('displayName', 'Home Team')
    away_team = competitors[1].get('team', {}).get('displayName', 'Away Team')
    game_date = game_data.get('header', {}).get('competitions', [{}])[0].get('date', 'Unknown')
    
    # Rutgers is the away team in this game
    rutgers_team = away_team
    opponent_team = home_team
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rutgers Game Review - vs {opponent_team}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #cc0000 0%, #ff6600 100%);
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
            .section {{
                margin: 30px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }}
            .section h3 {{
                margin-top: 0;
                color: #2c3e50;
            }}
            .key-moment {{
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 3px solid #e74c3c;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .key-moment h4 {{
                margin: 0 0 10px 0;
                color: #e74c3c;
            }}
            .wp-change {{
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.9em;
            }}
            .wp-change.positive {{
                background-color: #d4edda;
                color: #155724;
            }}
            .wp-change.negative {{
                background-color: #f8d7da;
                color: #721c24;
            }}
            .play-description {{
                font-style: italic;
                color: #666;
                margin: 5px 0;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
            }}
            .stat-label {{
                color: #666;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Rutgers Scarlet Knights Game Review</h1>
                <p>Rutgers vs {opponent_team} | {game_date} | Game ID: 401752876</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <h3>Game Overview</h3>
                    <p>This analysis provides a strategic breakdown of the key moments and turning points from Rutgers' perspective in the game against {opponent_team}. The review focuses on significant plays that impacted the game's outcome and win probability, with particular attention to Rutgers' performance and opportunities.</p>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{team_performance['total_plays']}</div>
                            <div class="stat-label">Total Plays</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{len(key_moments)}</div>
                            <div class="stat-label">Key Moments</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{team_performance['rutgers_plays']}</div>
                            <div class="stat-label">Rutgers Plays</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{team_performance['oregon_plays']}</div>
                            <div class="stat-label">{opponent_team} Plays</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>Key Moments Analysis</h3>
                    <p>The following plays had the most significant impact on the game's win probability (3% or greater change):</p>
    """
    
    # Add key moments
    for moment in key_moments[:10]:  # Show top 10 key moments
        play = moment['play']
        wp_change = moment['wp_change']
        change_text = f"{wp_change:+.1f}%"
        change_class = "positive" if wp_change > 0 else "negative"
        
        html += f"""
                    <div class="key-moment">
                        <h4>Play {moment['play_number']} - <span class="wp-change {change_class}">{change_text}</span></h4>
                        <div class="play-description">"{play.get('text', '')}"</div>
                        <p><strong>Win Probability:</strong> {moment['home_wp']:.1f}% → {moment['away_wp']:.1f}%</p>
                    </div>
        """
    
    html += f"""
                </div>
                
                <div class="section">
                    <h3>Strategic Observations</h3>
                    <h4>Game Flow Analysis</h4>
                    <p>This game featured {len(key_moments)} significant momentum shifts, indicating a competitive contest with multiple turning points.</p>
                    
                    <h4>Rutgers Performance</h4>
                    <p>Rutgers was involved in {team_performance['rutgers_plays']} plays, while {opponent_team} was involved in {team_performance['oregon_plays']} plays. This shows Rutgers' offensive involvement and opportunities throughout the game.</p>
                    
                    <h4>Key Takeaways for Rutgers</h4>
                    <ul>
                        <li>Total of {len(key_moments)} significant momentum shifts in the game</li>
                        <li>Rutgers had {team_performance['rutgers_plays']} offensive opportunities</li>
                        <li>Multiple chances for Rutgers to gain momentum and control</li>
                        <li>Win probability changes show Rutgers' impact on the game flow</li>
                        <li>Competitive game with opportunities for Rutgers to capitalize</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h3>Analysis Notes</h3>
                    <p><strong>Methodology:</strong> This analysis identifies plays with win probability changes of 3% or greater, indicating significant momentum shifts in the game.</p>
                    <p><strong>Data Source:</strong> ESPN API with win probability data from {len(win_prob_data)} data points.</p>
                    <p><strong>Focus:</strong> Strategic analysis of key moments rather than comprehensive play-by-play coverage.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    print("Creating game review analysis for Rutgers vs Oregon")
    print("=" * 60)
    
    # Load data
    game_data, win_prob_data = load_game_data()
    
    # Extract plays
    plays = extract_plays_from_game_data(game_data)
    print(f"Extracted {len(plays)} plays")
    
    # Identify key moments
    key_moments = identify_key_moments(plays, win_prob_data)
    print(f"Identified {len(key_moments)} key moments")
    
    # Analyze team performance
    team_performance = analyze_team_performance(plays)
    print(f"Team performance: {team_performance}")
    
    # Generate game review HTML
    html = generate_game_review_html(plays, key_moments, team_performance, game_data, win_prob_data)
    
    # Save to file
    output_file = "game_reviews/rutgers_oregon_game_review.html"
    os.makedirs('game_reviews', exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Game review saved to: {output_file}")
    print("Features included:")
    print("  ✓ Strategic analysis of key moments")
    print("  ✓ Win probability impact analysis")
    print("  ✓ Team performance overview")
    print("  ✓ Game flow observations")
    print("Open the file in your browser to view the game review!")

if __name__ == "__main__":
    main()
