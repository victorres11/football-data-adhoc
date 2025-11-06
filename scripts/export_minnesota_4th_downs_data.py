#!/usr/bin/env python3
"""
Export Minnesota 4th Down Plays data to JSON and CSV formats
Includes all enhanced data: scores, drives, yard lines, etc.
"""

import json
import csv
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
    """Get game information from CFBD API"""
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
    """Fetch ALL plays for a game"""
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
            return response.json()
    except Exception as e:
        print(f"      Error fetching plays: {e}")
    return []

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

def enhance_plays_with_cfbd_data(plays_data):
    """Enhance plays with CFBD data including scores, drives, yard lines"""
    
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
    
    print("Enhancing plays with CFBD data...")
    enhanced_plays = []
    
    for game_id, game_data in plays_by_game.items():
        week = game_data['week']
        print(f"  Processing game {game_id} (Week {week})...")
        
        # Get game info
        game_info = get_game_info(game_id, week)
        if game_info:
            home_team = game_info.get('homeTeam', 'Unknown')
            away_team = game_info.get('awayTeam', 'Unknown')
            game_data['home_team'] = home_team
            game_data['away_team'] = away_team
            
            # Determine opponent for Minnesota
            if 'Minnesota' in home_team:
                game_data['opponent'] = away_team
            else:
                game_data['opponent'] = home_team
        
        # Fetch all plays for matching
        all_plays = get_all_game_plays(game_id, week)
        
        # Fetch enhanced 4th down plays
        enhanced_plays_cfbd = get_enhanced_play_data(game_id, week)
        
        # Create lookup map
        enhanced_play_map = {}
        for ep in enhanced_plays_cfbd:
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
        
        # Enhance each play
        for play in game_data['plays']:
            enhanced_play = play.copy()
            
            # Add game context
            enhanced_play['game_week'] = week
            enhanced_play['home_team'] = game_data.get('home_team', 'Unknown')
            enhanced_play['away_team'] = game_data.get('away_team', 'Unknown')
            enhanced_play['opponent'] = game_data.get('opponent', 'Unknown')
            
            quarter = play.get('quarter', 1)
            time_str = play.get('time', '15:00')
            distance = play.get('down_distance', '4 & 0').split('&')[1].strip() if '&' in play.get('down_distance', '') else '0'
            yards_to_goal = play.get('yards_to_goal', play.get('yards_to_endzone', 0))
            play_text_short = play.get('play_text', '')[:40]
            
            # Try to match with CFBD data
            key1 = f"{quarter}_{time_str}_{distance}_{yards_to_goal}"
            key2 = f"{quarter}_{time_str}_{play_text_short}"
            
            ep = enhanced_play_map.get(key1) or enhanced_play_map.get(key2)
            
            if ep:
                # Extract all CFBD data
                enhanced_play['drive_id'] = ep.get('driveId', '')
                enhanced_play['drive_number'] = ep.get('driveNumber', '')
                enhanced_play['play_id'] = ep.get('id', '')
                enhanced_play['play_number'] = ep.get('playNumber', '')
                enhanced_play['offense'] = ep.get('offense', '')
                enhanced_play['defense'] = ep.get('defense', '')
                
                # Scores from CFBD
                offense_score = ep.get('offenseScore', 0)
                defense_score = ep.get('defenseScore', 0)
                offense_team = ep.get('offense', '')
                
                if offense_team == 'Minnesota':
                    enhanced_play['score_minnesota'] = offense_score
                    enhanced_play['score_opponent'] = defense_score
                else:
                    enhanced_play['score_minnesota'] = defense_score
                    enhanced_play['score_opponent'] = offense_score
                
                # Yard line from CFBD
                yard_line = ep.get('yardline', 0)
                if yard_line and yard_line != 0:
                    enhanced_play['yard_line_cfbd'] = yard_line
                
                # Other CFBD fields
                enhanced_play['yards_gained_cfbd'] = ep.get('yardsGained', 0)
                enhanced_play['ppa'] = ep.get('ppa')
                enhanced_play['scoring'] = ep.get('scoring', False)
                enhanced_play['play_type_cfbd'] = ep.get('playType', '')
                enhanced_play['play_text_cfbd'] = ep.get('playText', '')
                
                # Clock details
                clock = ep.get('clock', {})
                if isinstance(clock, dict):
                    enhanced_play['clock_minutes'] = clock.get('minutes', 15)
                    enhanced_play['clock_seconds'] = clock.get('seconds', 0)
            
            else:
                # No CFBD match - try to find in all_plays
                enhanced_play['drive_id'] = ''
                enhanced_play['drive_number'] = ''
                enhanced_play['play_id'] = ''
                
                # Try to find matching play
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
                
                best_match = None
                best_diff = float('inf')
                
                for all_play in all_plays:
                    if (all_play.get('period') == quarter and
                        all_play.get('offense') == 'Minnesota' and
                        all_play.get('down') == 4):
                        play_clock = all_play.get('clock', {})
                        if isinstance(play_clock, dict):
                            play_min = play_clock.get('minutes', 15)
                            play_sec = play_clock.get('seconds', 0)
                            time_diff = abs((time_min * 60 + time_sec) - (play_min * 60 + play_sec))
                            play_ytg = all_play.get('yardsToGoal', 0)
                            ytg_diff = abs(play_ytg - yards_to_goal)
                            total_diff = time_diff + (ytg_diff * 0.1)
                            
                            if total_diff < best_diff and total_diff < 120:
                                best_diff = total_diff
                                best_match = all_play
                
                if best_match:
                    offense_score = best_match.get('offenseScore', 0)
                    defense_score = best_match.get('defenseScore', 0)
                    offense_team = best_match.get('offense', '')
                    
                    enhanced_play['drive_id'] = best_match.get('driveId', '')
                    enhanced_play['drive_number'] = best_match.get('driveNumber', '')
                    enhanced_play['play_id'] = best_match.get('id', '')
                    enhanced_play['play_number'] = best_match.get('playNumber', '')
                    
                    if offense_team == 'Minnesota':
                        enhanced_play['score_minnesota'] = offense_score
                        enhanced_play['score_opponent'] = defense_score
                    else:
                        enhanced_play['score_minnesota'] = defense_score
                        enhanced_play['score_opponent'] = offense_score
                    
                    yard_line = best_match.get('yardline', 0)
                    if yard_line and yard_line != 0:
                        enhanced_play['yard_line_cfbd'] = yard_line
                    
                    enhanced_play['yards_gained_cfbd'] = best_match.get('yardsGained', 0)
                    enhanced_play['ppa'] = best_match.get('ppa')
                    enhanced_play['scoring'] = best_match.get('scoring', False)
                else:
                    enhanced_play['score_minnesota'] = None
                    enhanced_play['score_opponent'] = None
                    enhanced_play['yard_line_cfbd'] = None
            
            # Calculate yard line display format
            yards_to_goal = enhanced_play.get('yards_to_goal', enhanced_play.get('yards_to_endzone', 0))
            if yards_to_goal and yards_to_goal != 'N/A' and yards_to_goal != 0:
                try:
                    ytg = int(yards_to_goal)
                    if ytg == 50:
                        enhanced_play['yard_line_display'] = 50
                    elif ytg < 50:
                        enhanced_play['yard_line_display'] = f"+{ytg}"
                    else:
                        enhanced_play['yard_line_display'] = -(100 - ytg)
                except:
                    enhanced_play['yard_line_display'] = None
            else:
                enhanced_play['yard_line_display'] = None
            
            # Determine play_result properly based on available data
            play_text_lower = enhanced_play.get('play_text', '').lower()
            play_type_lower = enhanced_play.get('play_type', '').lower()
            play_type_cfbd_lower = enhanced_play.get('play_type_cfbd', '').lower()
            
            # Check if this is a timeout - should be classified as non-play
            is_timeout = 'timeout' in play_text_lower or 'timeout' in play_type_lower or 'timeout' in play_type_cfbd_lower
            
            if is_timeout:
                enhanced_play['is_timeout'] = True
                enhanced_play['is_go_for_it'] = False
                enhanced_play['play_result'] = 'Timeout'
                enhanced_play['converted'] = None  # Not applicable for timeout
            else:
                enhanced_play['is_timeout'] = False
                
                # Determine play_result from available data
                play_result = enhanced_play.get('play_result', 'Unknown')
                
                # If play_result is Unknown, try to determine it
                if play_result == 'Unknown':
                    # Check CFBD play type first
                    if play_type_cfbd_lower:
                        if 'punt' in play_type_cfbd_lower:
                            play_result = 'Punt'
                        elif 'field goal' in play_type_cfbd_lower:
                            if 'good' in play_type_cfbd_lower or 'made' in play_type_cfbd_lower:
                                play_result = 'Field Goal'
                            elif 'missed' in play_type_cfbd_lower or 'no good' in play_type_cfbd_lower:
                                play_result = 'Missed FG'
                            else:
                                play_result = 'Field Goal'
                        elif 'rush' in play_type_cfbd_lower:
                            if enhanced_play.get('converted') is True:
                                play_result = 'Conversion'
                            elif enhanced_play.get('converted') is False:
                                play_result = 'Failed'
                            else:
                                play_result = 'Rush'
                        elif 'pass' in play_type_cfbd_lower:
                            if enhanced_play.get('converted') is True:
                                play_result = 'Conversion'
                            elif enhanced_play.get('converted') is False:
                                play_result = 'Failed'
                            else:
                                play_result = 'Pass'
                    
                    # If still Unknown, check original play_type
                    if play_result == 'Unknown':
                        if 'punt' in play_type_lower:
                            play_result = 'Punt'
                        elif 'field goal' in play_type_lower or 'fg' in play_text_lower:
                            if 'good' in play_text_lower or 'made' in play_text_lower:
                                play_result = 'Field Goal'
                            elif 'missed' in play_text_lower or 'no good' in play_text_lower:
                                play_result = 'Missed FG'
                            else:
                                play_result = 'Field Goal'
                        elif 'rush' in play_type_lower or 'run' in play_text_lower:
                            if enhanced_play.get('converted') is True:
                                play_result = 'Conversion'
                            elif enhanced_play.get('converted') is False:
                                play_result = 'Failed'
                            else:
                                play_result = 'Rush'
                        elif 'pass' in play_type_lower:
                            if enhanced_play.get('converted') is True:
                                play_result = 'Conversion'
                            elif enhanced_play.get('converted') is False:
                                play_result = 'Failed'
                            else:
                                play_result = 'Pass'
                    
                    # If still Unknown, check play_text for clues
                    if play_result == 'Unknown':
                        if 'first down' in play_text_lower or '1st down' in play_text_lower:
                            play_result = 'Conversion'
                        elif enhanced_play.get('converted') is True:
                            play_result = 'Conversion'
                        elif enhanced_play.get('converted') is False:
                            play_result = 'Failed'
                        elif enhanced_play.get('is_go_for_it'):
                            # Go for it but conversion status unclear - default to attempt
                            play_result = 'Attempt'
                
                enhanced_play['play_result'] = play_result
            
            enhanced_plays.append(enhanced_play)
    
    return enhanced_plays

def export_to_json(enhanced_plays, filename='minnesota_4th_downs_complete.json'):
    """Export to JSON format"""
    output_data = {
        'team': 'Minnesota',
        'season': 2025,
        'total_plays': len(enhanced_plays),
        'generated_at': datetime.now().isoformat(),
        'plays': enhanced_plays
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    return filename

def export_to_csv(enhanced_plays, filename='minnesota_4th_downs_complete.csv'):
    """Export to CSV format"""
    if not enhanced_plays:
        print("No plays to export")
        return None
    
    # Get all unique keys from all plays
    all_keys = set()
    for play in enhanced_plays:
        all_keys.update(play.keys())
    
    # Sort keys for consistent column order
    fieldnames = sorted(all_keys)
    
    # Reorder to put important fields first
    priority_fields = [
        'game_id', 'game_week', 'opponent', 'quarter', 'time', 'clock_minutes', 'clock_seconds',
        'drive_number', 'drive_id', 'play_number', 'play_id',
        'down_distance', 'yards_to_goal', 'yard_line_cfbd', 'yard_line_display',
        'score_minnesota', 'score_opponent', 'is_go_for_it', 'play_type', 'play_result',
        'yards_gained', 'yards_gained_cfbd', 'converted', 'scoring', 'scoring_play',
        'play_text', 'play_text_cfbd', 'home_team', 'away_team', 'ppa'
    ]
    
    # Build fieldnames with priority fields first
    ordered_fieldnames = []
    for field in priority_fields:
        if field in fieldnames:
            ordered_fieldnames.append(field)
            fieldnames.remove(field)
    
    # Add remaining fields
    ordered_fieldnames.extend(sorted(fieldnames))
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
        writer.writeheader()
        
        for play in enhanced_plays:
            # Convert None to empty string for CSV
            row = {}
            for field in ordered_fieldnames:
                value = play.get(field, '')
                if value is None:
                    value = ''
                elif isinstance(value, bool):
                    value = 'TRUE' if value else 'FALSE'
                row[field] = value
            writer.writerow(row)
    
    return filename

def main():
    print("=" * 70)
    print("Exporting Minnesota 4th Down Plays to JSON and CSV")
    print("=" * 70)
    
    # Load data
    plays_data = load_4th_downs_data()
    if not plays_data:
        print("Error: Could not load 4th downs data")
        return
    
    # Enhance with CFBD data
    enhanced_plays = enhance_plays_with_cfbd_data(plays_data)
    
    print(f"\n✓ Enhanced {len(enhanced_plays)} plays with CFBD data")
    
    # Export to JSON
    json_file = export_to_json(enhanced_plays)
    print(f"✓ Exported JSON: {json_file}")
    
    # Export to CSV
    csv_file = export_to_csv(enhanced_plays)
    print(f"✓ Exported CSV: {csv_file}")
    
    print(f"\n✓ Export complete!")
    print(f"  - JSON file: {json_file}")
    print(f"  - CSV file: {csv_file}")
    print(f"  - Total plays: {len(enhanced_plays)}")

if __name__ == "__main__":
    main()

