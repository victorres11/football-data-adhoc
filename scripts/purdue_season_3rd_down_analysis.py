#!/usr/bin/env python3
"""
Purdue 3rd Down Analysis for 2025 Season
Extract all 3rd down plays and calculate conversion rates
"""

import json
import requests
import os
from datetime import datetime

# CFBD API configuration
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

CFBD_API_KEY = config['api_key']
BASE_URL = config['base_url']

def get_purdue_games_2025():
    """Get all Purdue games for 2025 season"""
    print("Fetching Purdue's 2025 season games...")
    
    url = f"{BASE_URL}/games"
    params = {
        'year': 2025,
        'team': 'Purdue',
        'seasonType': 'regular'
    }
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        games = response.json()
        
        print(f"Found {len(games)} games for Purdue in 2025")
        for game in games:
            away_team = game.get('away_team', 'Unknown')
            home_team = game.get('home_team', 'Unknown')
            print(f"  {game.get('season', 'N/A')} Week {game.get('week', 'N/A')}: {away_team} @ {home_team} (ID: {game.get('id', 'N/A')})")
        
        return games
    except requests.exceptions.RequestException as e:
        print(f"Error fetching games: {e}")
        return []

def get_game_plays(game_id):
    """Get play-by-play data for a specific game"""
    print(f"Fetching plays for game {game_id}...")
    
    url = f"{BASE_URL}/plays"
    params = {
        'gameId': game_id
    }
    headers = {
        'Authorization': f'Bearer {CFBD_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        plays = response.json()
        
        print(f"  Found {len(plays)} plays")
        return plays
    except requests.exceptions.RequestException as e:
        print(f"Error fetching plays for game {game_id}: {e}")
        return []

def analyze_third_down_plays(plays, team_name="Purdue"):
    """Analyze 3rd down plays for the specified team"""
    third_down_plays = []
    third_and_long_plays = []
    
    for play in plays:
        # Check if this is a 3rd down play for Purdue
        if (play.get('down') == 3 and 
            (play.get('offense') == team_name or 
             play.get('defense') == team_name)):
            
            # Extract play details
            play_info = {
                'game_id': play.get('gameId'),
                'week': play.get('week'),
                'quarter': play.get('period'),
                'down': play.get('down'),
                'distance': play.get('distance'),
                'yard_line': play.get('yardLine'),
                'yards_to_goal': play.get('yardsToGoal'),
                'play_type': play.get('playType'),
                'play_text': play.get('playText', ''),
                'yards_gained': play.get('yardsGained', 0),
                'is_conversion': False,
                'is_third_and_long': False
            }
            
            # Determine if it's a conversion
            if play.get('down') == 3:
                # Check if next play is 1st down (conversion) or 4th down (failed)
                # This is a simplified check - in reality, you'd need to look at the next play
                play_text = play.get('playText', '').lower()
                if any(word in play_text for word in ['first down', '1st down', 'touchdown']):
                    play_info['is_conversion'] = True
                elif any(word in play_text for word in ['fourth down', '4th down', 'punt', 'field goal']):
                    play_info['is_conversion'] = False
                else:
                    # If we can't determine from play text, we'll need to check the next play
                    play_info['is_conversion'] = None
            
            # Check if it's 3rd and 7+
            if play.get('distance', 0) >= 7:
                play_info['is_third_and_long'] = True
                third_and_long_plays.append(play_info)
            
            third_down_plays.append(play_info)
    
    return third_down_plays, third_and_long_plays

def calculate_conversion_rates(plays):
    """Calculate conversion rates for a list of plays"""
    total_attempts = len(plays)
    conversions = sum(1 for play in plays if play['is_conversion'] is True)
    failed = sum(1 for play in plays if play['is_conversion'] is False)
    unknown = sum(1 for play in plays if play['is_conversion'] is None)
    
    conversion_rate = (conversions / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        'total_attempts': total_attempts,
        'conversions': conversions,
        'failed': failed,
        'unknown': unknown,
        'conversion_rate': conversion_rate
    }

def create_html_table(plays, title, filename):
    """Create an HTML table of plays"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .conversion {{ background-color: #d4edda; }}
            .failed {{ background-color: #f8d7da; }}
            .unknown {{ background-color: #fff3cd; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <tr>
                <th>Week</th>
                <th>Quarter</th>
                <th>Down & Distance</th>
                <th>Yard Line</th>
                <th>Play Type</th>
                <th>Yards Gained</th>
                <th>Result</th>
                <th>Play Description</th>
            </tr>
    """
    
    for play in plays:
        result_class = ""
        result_text = ""
        
        if play['is_conversion'] is True:
            result_class = "conversion"
            result_text = "Conversion"
        elif play['is_conversion'] is False:
            result_class = "failed"
            result_text = "Failed"
        else:
            result_class = "unknown"
            result_text = "Unknown"
        
        html_content += f"""
            <tr class="{result_class}">
                <td>{play['week']}</td>
                <td>{play['quarter']}</td>
                <td>3rd & {play['distance']}</td>
                <td>{play['yard_line']}</td>
                <td>{play['play_type']}</td>
                <td>{play['yards_gained']}</td>
                <td>{result_text}</td>
                <td>{play['play_text']}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(filename, 'w') as f:
        f.write(html_content)
    
    print(f"HTML table saved to: {filename}")

def main():
    print("Purdue 3rd Down Analysis - 2025 Season")
    print("=" * 50)
    
    # Check if API key is provided
    if not CFBD_API_KEY:
        print("ERROR: No API key found in config.json")
        return
    
    # Get all Purdue games for 2025
    games = get_purdue_games_2025()
    if not games:
        print("No games found. Exiting.")
        return
    
    # Collect all 3rd down plays
    all_third_down_plays = []
    all_third_and_long_plays = []
    
    for game in games:
        game_id = game['id']
        plays = get_game_plays(game_id)
        
        if plays:
            third_down, third_and_long = analyze_third_down_plays(plays, "Purdue")
            all_third_down_plays.extend(third_down)
            all_third_and_long_plays.extend(third_and_long)
    
    # Calculate conversion rates
    print("\n" + "=" * 50)
    print("CONVERSION RATE ANALYSIS")
    print("=" * 50)
    
    # All 3rd downs
    all_third_stats = calculate_conversion_rates(all_third_down_plays)
    print(f"\nALL 3RD DOWNS:")
    print(f"  Total Attempts: {all_third_stats['total_attempts']}")
    print(f"  Conversions: {all_third_stats['conversions']}")
    print(f"  Failed: {all_third_stats['failed']}")
    print(f"  Unknown: {all_third_stats['unknown']}")
    print(f"  Conversion Rate: {all_third_stats['conversion_rate']:.1f}%")
    
    # 3rd and 7+
    third_and_long_stats = calculate_conversion_rates(all_third_and_long_plays)
    print(f"\n3RD AND 7+ (LONG):")
    print(f"  Total Attempts: {third_and_long_stats['total_attempts']}")
    print(f"  Conversions: {third_and_long_stats['conversions']}")
    print(f"  Failed: {third_and_long_stats['failed']}")
    print(f"  Unknown: {third_and_long_stats['unknown']}")
    print(f"  Conversion Rate: {third_and_long_stats['conversion_rate']:.1f}%")
    
    # Create HTML tables
    if all_third_down_plays:
        create_html_table(all_third_down_plays, "Purdue 3rd Down Plays - 2025 Season", "purdue_3rd_down_plays.html")
    
    if all_third_and_long_plays:
        create_html_table(all_third_and_long_plays, "Purdue 3rd and 7+ Plays - 2025 Season", "purdue_3rd_and_long_plays.html")
    
    # Save data as JSON
    data = {
        'season': 2025,
        'team': 'Purdue',
        'analysis_date': datetime.now().isoformat(),
        'all_third_down': {
            'stats': all_third_stats,
            'plays': all_third_down_plays
        },
        'third_and_long': {
            'stats': third_and_long_stats,
            'plays': all_third_and_long_plays
        }
    }
    
    with open('purdue_3rd_down_analysis.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nData saved to: purdue_3rd_down_analysis.json")

if __name__ == "__main__":
    main()
