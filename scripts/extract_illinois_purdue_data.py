#!/usr/bin/env python3
"""
Extract and analyze Illinois vs Purdue game data
Game ID: 401752861
Date: October 4, 2025
"""

import json

def load_game_data():
    """Load the raw game data from ESPN API"""
    with open('data/illinois_purdue/raw_game_data.json', 'r') as f:
        return json.load(f)

def extract_team_info(data):
    """Extract team information and basic stats"""
    print("=== TEAM INFORMATION ===")
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

def extract_drive_data(data):
    """Extract drive information for possession times and scoring"""
    print("\n=== DRIVE DATA ===")
    drives = data['drives']['previous']
    
    print(f"Total drives: {len(drives)}")
    
    # Analyze drives by quarter
    quarter_drives = {1: [], 2: [], 3: [], 4: []}
    quarter_scores = {1: {'Illinois': 0, 'Purdue': 0}, 2: {'Illinois': 0, 'Purdue': 0}, 
                     3: {'Illinois': 0, 'Purdue': 0}, 4: {'Illinois': 0, 'Purdue': 0}}
    
    for drive in drives:
        if 'plays' in drive and len(drive['plays']) > 0:
            # Get quarter from first play
            first_play = drive['plays'][0]
            quarter = first_play.get('period', {}).get('number', 1)
            
            if quarter in quarter_drives:
                quarter_drives[quarter].append(drive)
                
                # Check if this drive resulted in a score
                if drive.get('isScore', False):
                    team = drive.get('team', {}).get('displayName', '')
                    result = drive.get('result', '')
                    
                    points = 0
                    if result == 'TD':
                        points = 7
                    elif result == 'FG':
                        points = 3
                    
                    if points > 0 and team in quarter_scores[quarter]:
                        quarter_scores[quarter][team] += points
                        print(f"Q{quarter}: {team} scored {points} points ({result})")
    
    # Print quarter-by-quarter scores
    print("\n=== QUARTER-BY-QUARTER SCORES ===")
    running_totals = {'Illinois': 0, 'Purdue': 0}
    
    for q in [1, 2, 3, 4]:
        print(f"\nQ{q}:")
        for team in ['Illinois', 'Purdue']:
            if team in quarter_scores[q]:
                running_totals[team] += quarter_scores[q][team]
                print(f"  {team}: {quarter_scores[q][team]} (Total: {running_totals[team]})")
    
    return quarter_drives, quarter_scores, running_totals

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
    
    for drive in drives:
        if 'plays' in drive:
            for play in drive['plays']:
                # Get play type
                play_type = play.get('type', {}).get('text', 'Unknown')
                if play_type not in play_counts:
                    play_counts[play_type] = 0
                play_counts[play_type] += 1
                
                # Check for 3rd/4th down
                start = play.get('start', {})
                down = start.get('down')
                
                # Determine team (this is tricky, need to check teamParticipants)
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
                    # Check if it was a conversion (simplified - would need more logic)
                    if play.get('end', {}).get('down') == 1:  # Next down is 1st
                        third_down_conversions[team] += 1
                
                elif team and down == 4:
                    fourth_down_attempts[team] += 1
                    # Check if it was a conversion
                    if play.get('end', {}).get('down') == 1:  # Next down is 1st
                        fourth_down_conversions[team] += 1
    
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
    
    return play_counts, third_down_attempts, third_down_conversions, fourth_down_attempts, fourth_down_conversions

def main():
    print("Illinois vs Purdue Game Analysis")
    print("Game ID: 401752861")
    print("Date: October 4, 2025")
    print("=" * 50)
    
    # Load data
    data = load_game_data()
    
    # Extract team information
    team_info = extract_team_info(data)
    
    # Extract drive data
    quarter_drives, quarter_scores, final_scores = extract_drive_data(data)
    
    # Extract play data
    play_counts, third_down_attempts, third_down_conversions, fourth_down_attempts, fourth_down_conversions = extract_play_data(data)
    
    print(f"\n=== FINAL SCORES ===")
    for team, score in final_scores.items():
        print(f"{team}: {score}")
    
    # Save extracted data
    extracted_data = {
        'game_info': {
            'game_id': '401752861',
            'date': 'October 4, 2025',
            'teams': team_info,
            'final_scores': final_scores
        },
        'quarter_data': {
            'drives': quarter_drives,
            'scores': quarter_scores
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
            }
        }
    }
    
    with open('data/illinois_purdue/extracted_data.json', 'w') as f:
        json.dump(extracted_data, f, indent=2)
    
    print(f"\nData saved to: data/illinois_purdue/extracted_data.json")

if __name__ == "__main__":
    main()
