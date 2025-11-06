#!/usr/bin/env python3
"""
Identify Purdue team IDs in game data
"""

import json

def identify_teams():
    """Identify which team is Purdue in the game data"""
    with open('data/purdue_games/game_401752864.json', 'r') as f:
        data = json.load(f)

    # Check the game name to identify teams
    header = data['header']
    game_name = header.get('name', '')
    print(f'Game: {game_name}')

    # Check competitors
    competitions = header.get('competitions', [])
    if competitions:
        competitors = competitions[0].get('competitors', [])
        print('\nCompetitors:')
        for i, comp in enumerate(competitors):
            team_ref = comp.get('team', {}).get('$ref', '')
            team_id = team_ref.split('/')[-1].split('?')[0]  # Remove query params
            home_away = comp.get('homeAway', 'Unknown')
            print(f'  {i+1}: Team ID {team_id} ({home_away})')

    # Check first few drives to see which team is which
    drives = data['drives']['items']
    print(f'\nFirst few drives:')
    for i, drive in enumerate(drives[:5]):
        team_ref = drive.get('team', {}).get('$ref', '')
        team_id = team_ref.split('/')[-1].split('?')[0]
        description = drive.get('description', '')
        print(f'  Drive {i+1}: Team {team_id} - {description}')

    # Based on the game name "Purdue Boilermakers at Minnesota Golden Gophers"
    # Purdue is the away team, Minnesota is home
    print(f'\nBased on game name "{game_name}":')
    print('  Purdue should be the away team')
    print('  Minnesota should be the home team')

if __name__ == "__main__":
    identify_teams()
