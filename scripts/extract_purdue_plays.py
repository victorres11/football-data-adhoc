#!/usr/bin/env python3
"""
Extract 4th down and explosive plays from Purdue vs Minnesota game data
"""

import json
import os
from collections import defaultdict

def extract_team_from_play(play, teams, drive_team_id=None):
    """Extract the offensive team from a play"""
    # Check teamParticipants for offensive team
    if 'teamParticipants' in play:
        for participant in play['teamParticipants']:
            if participant.get('type') == 'offense':
                team_id = participant.get('team', {}).get('id')
                if team_id in teams:
                    return teams[team_id]
    
    # Check start team
    if 'start' in play and 'team' in play['start']:
        team_id = play['start'].get('team', {}).get('id')
        if team_id in teams:
            return teams[team_id]
    
    # Use drive team as fallback
    if drive_team_id and drive_team_id in teams:
        return teams[drive_team_id]
    
    return None

def determine_play_result(play):
    """Determine the result of a 4th down play"""
    play_type = play.get('type', {}).get('text', '').lower()
    
    if 'field goal' in play_type:
        if 'good' in play_type:
            return 'Field Goal'
        else:
            return 'Missed FG'
    elif 'punt' in play_type:
        return 'Punt'
    elif 'timeout' in play_type:
        return 'Timeout'
    elif 'penalty' in play_type:
        return 'Penalty'
    elif 'pass' in play_type or 'run' in play_type or 'rush' in play_type:
        # Check if it's a conversion
        if play.get('end', {}).get('down') == 1:
            return 'Conversion'
        else:
            return 'Failed'
    else:
        return 'Other'

def extract_fourth_down_plays(data, teams):
    """Extract all 4th down plays from the game"""
    print("Extracting 4th down plays...")
    
    fourth_down_plays = []
    
    # Get drives data
    drives = []
    if 'drives' in data:
        if 'previous' in data['drives']:
            drives = data['drives']['previous']
        elif 'items' in data['drives']:
            drives = data['drives']['items']
    
    for drive in drives:
        drive_team_id = drive.get('team', {}).get('id')
        if 'plays' in drive:
            for play in drive['plays']:
                start = play.get('start', {})
                if start.get('down') == 4:
                    team = extract_team_from_play(play, teams, drive_team_id)
                    if team:
                        play_info = {
                            'quarter': play.get('period', {}).get('number'),
                            'time': play.get('clock', {}).get('displayValue'),
                            'down_distance': f"4th & {start.get('distance')}",
                            'field_position': start.get('possessionText', ''),
                            'description': play.get('text', ''),
                            'yards': play.get('statYardage', 0),
                            'result': determine_play_result(play),
                            'team': team['name']
                        }
                        fourth_down_plays.append(play_info)
    
    return fourth_down_plays

def extract_explosive_plays(data, teams):
    """Extract all explosive plays (20+ yards) from the game"""
    print("Extracting explosive plays...")
    
    explosive_plays = []
    
    # Get drives data
    drives = []
    if 'drives' in data:
        if 'previous' in data['drives']:
            drives = data['drives']['previous']
        elif 'items' in data['drives']:
            drives = data['drives']['items']
    
    for drive in drives:
        drive_team_id = drive.get('team', {}).get('id')
        if 'plays' in drive:
            for play in drive['plays']:
                yards = play.get('statYardage', 0)
                if yards >= 20:
                    # Filter out special teams plays
                    play_type = play.get('type', {}).get('text', '').lower()
                    if not any(st in play_type for st in ['punt', 'kickoff', 'field goal']):
                        team = extract_team_from_play(play, teams, drive_team_id)
                        if team:
                            play_info = {
                                'quarter': play.get('period', {}).get('number'),
                                'time': play.get('clock', {}).get('displayValue'),
                                'yards': yards,
                                'description': play.get('text', ''),
                                'team': team['name']
                            }
                            explosive_plays.append(play_info)
    
    return explosive_plays

def main():
    """Main function to extract Purdue plays"""
    print("Purdue vs Minnesota - 4th Down and Explosive Plays Extraction")
    print("=" * 60)
    
    # Load Purdue game data
    with open('data/purdue/game_401752864/raw_game_data.json', 'r') as f:
        data = json.load(f)
    
    # Define teams
    teams = {
        '2509': {
            'id': '2509',
            'name': 'Purdue Boilermakers',
            'short_name': 'Purdue',
            'abbreviation': 'PUR'
        },
        '135': {
            'id': '135',
            'name': 'Minnesota Golden Gophers',
            'short_name': 'Minnesota',
            'abbreviation': 'MIN'
        }
    }
    
    # Extract 4th down plays
    fourth_down_plays = extract_fourth_down_plays(data, teams)
    
    # Extract explosive plays
    explosive_plays = extract_explosive_plays(data, teams)
    
    # Separate by team
    purdue_4th_down = [p for p in fourth_down_plays if 'Purdue' in p['team']]
    minnesota_4th_down = [p for p in fourth_down_plays if 'Minnesota' in p['team']]
    
    purdue_explosive = [p for p in explosive_plays if 'Purdue' in p['team']]
    minnesota_explosive = [p for p in explosive_plays if 'Minnesota' in p['team']]
    
    # Print results
    print(f"\n4th Down Plays:")
    print(f"Purdue: {len(purdue_4th_down)} attempts")
    for play in purdue_4th_down:
        print(f"  Q{play['quarter']} {play['time']} - {play['down_distance']} - {play['result']}")
    
    print(f"\nMinnesota: {len(minnesota_4th_down)} attempts")
    for play in minnesota_4th_down:
        print(f"  Q{play['quarter']} {play['time']} - {play['down_distance']} - {play['result']}")
    
    print(f"\nExplosive Plays (20+ yards):")
    print(f"Purdue: {len(purdue_explosive)} plays")
    for play in purdue_explosive:
        print(f"  Q{play['quarter']} {play['time']} - {play['yards']} yards")
    
    print(f"\nMinnesota: {len(minnesota_explosive)} plays")
    for play in minnesota_explosive:
        print(f"  Q{play['quarter']} {play['time']} - {play['yards']} yards")
    
    # Save to files
    output_data = {
        'fourth_down_plays': {
            'purdue': purdue_4th_down,
            'minnesota': minnesota_4th_down
        },
        'explosive_plays': {
            'purdue': purdue_explosive,
            'minnesota': minnesota_explosive
        }
    }
    
    with open('data/purdue/game_401752864/plays_analysis.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Plays analysis saved to: data/purdue/game_401752864/plays_analysis.json")

if __name__ == "__main__":
    main()
