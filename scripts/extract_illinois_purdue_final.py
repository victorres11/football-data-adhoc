#!/usr/bin/env python3
"""
Final extraction and analysis for Illinois vs Purdue game
Game ID: 401752861
Date: October 4, 2025
Final Score: Illinois 43, Purdue 27
"""

import json
import re

def load_game_data():
    """Load the raw game data from ESPN API"""
    with open('data/illinois_purdue/raw_game_data.json', 'r') as f:
        return json.load(f)

def extract_final_scores(data):
    """Extract final scores from the article section"""
    print("=== FINAL SCORES ===")
    
    # From the article section, we know: Illinois 43, Purdue 27
    final_scores = {
        'Illinois': 43,
        'Purdue': 27
    }
    
    print(f"Illinois: {final_scores['Illinois']}")
    print(f"Purdue: {final_scores['Purdue']}")
    
    return final_scores

def extract_team_info(data):
    """Extract team information and basic stats"""
    print("\n=== TEAM INFORMATION ===")
    teams = data['boxscore']['teams']
    
    team_info = {}
    for team in teams:
        team_data = team['team']
        team_name = team_data['displayName']
        team_id = team_data['id']
        
        print(f"\n{team_name} (ID: {team_id})")
        print(f"Color: #{team_data['color']}")
        print(f"Alt Color: #{team_data['alternateColor']}")
        
        # Extract key statistics
        stats = team['statistics']
        team_stats = {}
        
        for stat in stats:
            if stat['label'] in ['Total Yards', 'Rushing', 'Passing', '3rd down efficiency', '4th down efficiency', 'Turnovers', '1st Downs']:
                print(f"  {stat['label']}: {stat['displayValue']}")
                team_stats[stat['label']] = stat['displayValue']
        
        team_info[team_name] = {
            'id': team_id,
            'color': team_data['color'],
            'alt_color': team_data['alternateColor'],
            'stats': team_stats
        }
    
    return team_info

def extract_scoring_drives(data):
    """Extract scoring drives and quarter-by-quarter scores"""
    print("\n=== SCORING DRIVES ===")
    drives = data['drives']['previous']
    
    # Find scoring drives
    scoring_drives = [d for d in drives if d.get('isScore', False)]
    print(f"Total scoring drives: {len(scoring_drives)}")
    
    quarter_scores = {1: {'Illinois': 0, 'Purdue': 0}, 2: {'Illinois': 0, 'Purdue': 0}, 
                     3: {'Illinois': 0, 'Purdue': 0}, 4: {'Illinois': 0, 'Purdue': 0}}
    
    running_totals = {'Illinois': 0, 'Purdue': 0}
    
    for drive in scoring_drives:
        team_display = drive['team']['displayName']
        result = drive.get('result', '')
        
        # Map team names to our standard format
        if 'Illinois' in team_display:
            team = 'Illinois'
        elif 'Purdue' in team_display:
            team = 'Purdue'
        else:
            team = team_display
        
        # Get quarter from the drive's plays
        quarter = 1
        if 'plays' in drive and drive['plays']:
            quarter = drive['plays'][-1].get('period', {}).get('number', 1)
        
        points = 0
        if result == 'TD':
            points = 7
        elif result == 'FG':
            points = 3
        
        if points > 0:
            quarter_scores[quarter][team] += points
            running_totals[team] += points
            print(f"Q{quarter}: {team} scored {points} points ({result})")
    
    # Print quarter-by-quarter scores
    print("\n=== QUARTER-BY-QUARTER SCORES ===")
    for q in [1, 2, 3, 4]:
        print(f"\nQ{q}:")
        for team in ['Illinois', 'Purdue']:
            if team in quarter_scores[q]:
                print(f"  {team}: {quarter_scores[q][team]} (Running Total: {running_totals[team]})")
    
    return quarter_scores, running_totals

def extract_play_data(data):
    """Extract play-by-play data for 3rd/4th down analysis"""
    print("\n=== PLAY-BY-PLAY ANALYSIS ===")
    drives = data['drives']['previous']
    
    # Count plays by type
    play_counts = {}
    third_down_attempts = {'Illinois': 0, 'Purdue': 0}
    third_down_conversions = {'Illinois': 0, 'Purdue': 0}
    fourth_down_attempts = {'Illinois': 0, 'Purdue': 0}
    fourth_down_conversions = {'Illinois': 0, 'Purdue': 0}
    
    # Track explosive plays (20+ yards)
    explosive_plays = []
    fourth_down_plays = []
    
    for drive in drives:
        if 'plays' in drive:
            for play in drive['plays']:
                # Get play type
                play_type = play.get('type', {}).get('text', 'Unknown')
                if play_type not in play_counts:
                    play_counts[play_type] = 0
                play_counts[play_type] += 1
                
                # Check for explosive plays
                yards = play.get('statYardage', 0)
                if yards >= 20:
                    # Filter out special teams plays
                    if not any(st in play_type.lower() for st in ['punt', 'kickoff', 'field goal']):
                        # Determine team from teamParticipants
                        team = 'Unknown'
                        if 'teamParticipants' in play:
                            for participant in play['teamParticipants']:
                                if participant.get('type') == 'offense':
                                    team_id = participant.get('team', {}).get('id')
                                    if team_id == '356':  # Illinois
                                        team = 'Illinois'
                                    elif team_id == '2509':  # Purdue
                                        team = 'Purdue'
                                    break
                        
                        explosive_plays.append({
                            'quarter': play.get('period', {}).get('number'),
                            'time': play.get('clock', {}).get('displayValue'),
                            'yards': yards,
                            'description': play.get('text', ''),
                            'team': team
                        })
                
                # Check for 3rd/4th down
                start = play.get('start', {})
                down = start.get('down')
                
                # Determine team from teamParticipants
                team = None
                if 'teamParticipants' in play:
                    for participant in play['teamParticipants']:
                        if participant.get('type') == 'offense':
                            team_id = participant.get('team', {}).get('id')
                            if team_id == '356':  # Illinois
                                team = 'Illinois'
                            elif team_id == '2509':  # Purdue
                                team = 'Purdue'
                            break
                
                if team and down == 3:
                    third_down_attempts[team] += 1
                    # Check if it was a conversion
                    end = play.get('end', {})
                    if end.get('down') == 1:  # Next down is 1st
                        third_down_conversions[team] += 1
                
                elif team and down == 4:
                    fourth_down_attempts[team] += 1
                    # Check if it was a conversion
                    end = play.get('end', {})
                    if end.get('down') == 1:  # Next down is 1st
                        fourth_down_conversions[team] += 1
                    
                    # Add to 4th down plays list
                    fourth_down_plays.append({
                        'quarter': play.get('period', {}).get('number'),
                        'time': play.get('clock', {}).get('displayValue'),
                        'down_distance': f"4th & {start.get('distance')}",
                        'field_position': start.get('possessionText', ''),
                        'description': play.get('text', ''),
                        'yards': play.get('statYardage', 0),
                        'result': 'Conversion' if end.get('down') == 1 else 'Failed',
                        'team': team
                    })
    
    print(f"Total play types: {len(play_counts)}")
    print("Top play types:")
    for play_type, count in sorted(play_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {play_type}: {count}")
    
    print(f"\n3rd Down Analysis:")
    for team in ['Illinois', 'Purdue']:
        attempts = third_down_attempts[team]
        conversions = third_down_conversions[team]
        rate = (conversions / attempts * 100) if attempts > 0 else 0
        print(f"  {team}: {conversions}/{attempts} ({rate:.1f}%)")
    
    print(f"\n4th Down Analysis:")
    for team in ['Illinois', 'Purdue']:
        attempts = fourth_down_attempts[team]
        conversions = fourth_down_conversions[team]
        rate = (conversions / attempts * 100) if attempts > 0 else 0
        print(f"  {team}: {conversions}/{attempts} ({rate:.1f}%)")
    
    print(f"\nExplosive Plays: {len(explosive_plays)} total")
    print(f"4th Down Plays: {len(fourth_down_plays)} total")
    
    return play_counts, third_down_attempts, third_down_conversions, fourth_down_attempts, fourth_down_conversions, explosive_plays, fourth_down_plays

def extract_player_leaders(data):
    """Extract player leaders from the game"""
    print("\n=== PLAYER LEADERS ===")
    
    leaders = data.get('leaders', [])
    player_stats = {}
    
    for leader in leaders:
        category = leader.get('displayName', '')
        print(f"\n{category}:")
        
        for stat in leader.get('leaders', []):
            player = stat.get('athlete', {})
            player_name = player.get('displayName', 'Unknown')
            value = stat.get('displayValue', '0')
            print(f"  {player_name}: {value}")
            
            if category not in player_stats:
                player_stats[category] = []
            player_stats[category].append({
                'name': player_name,
                'value': value
            })
    
    return player_stats

def main():
    print("Illinois vs Purdue Game Analysis")
    print("Game ID: 401752861")
    print("Date: October 4, 2025")
    print("=" * 50)
    
    # Load data
    data = load_game_data()
    
    # Extract final scores
    final_scores = extract_final_scores(data)
    
    # Extract team information
    team_info = extract_team_info(data)
    
    # Extract scoring drives
    quarter_scores, running_totals = extract_scoring_drives(data)
    
    # Extract play data
    play_counts, third_down_attempts, third_down_conversions, fourth_down_attempts, fourth_down_conversions, explosive_plays, fourth_down_plays = extract_play_data(data)
    
    # Extract player leaders
    player_stats = extract_player_leaders(data)
    
    # Save extracted data
    extracted_data = {
        'game_info': {
            'game_id': '401752861',
            'date': 'October 4, 2025',
            'teams': team_info,
            'final_scores': final_scores
        },
        'quarter_data': {
            'scores': quarter_scores,
            'running_totals': running_totals
        },
        'play_data': {
            'play_counts': play_counts,
            'third_down': {
                'attempts': third_down_attempts,
                'conversions': third_down_conversions
            },
            'fourth_down': {
                'attempts': fourth_down_attempts,
                'conversions': fourth_down_conversions
            },
            'explosive_plays': explosive_plays,
            'fourth_down_plays': fourth_down_plays
        },
        'player_stats': player_stats
    }
    
    with open('data/illinois_purdue/extracted_data.json', 'w') as f:
        json.dump(extracted_data, f, indent=2)
    
    print(f"\nData saved to: data/illinois_purdue/extracted_data.json")

if __name__ == "__main__":
    main()
