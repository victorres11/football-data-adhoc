#!/usr/bin/env python3
"""
Debug Purdue team identification in game data
"""

import json

def debug_team_ids():
    """Debug team IDs in Purdue games"""
    with open('data/purdue_games/game_401752864.json', 'r') as f:
        data = json.load(f)

    # Check competitors to find team IDs
    header = data['header']
    competitions = header.get('competitions', [])
    if competitions:
        competitors = competitions[0].get('competitors', [])
        print('Competitors:')
        for i, comp in enumerate(competitors):
            team_ref = comp.get('team', {}).get('$ref', '')
            team_id = team_ref.split('/')[-1] if 'teams' in team_ref else 'Unknown'
            home_away = comp.get('homeAway', 'Unknown')
            print(f'  {i+1}: Team ID {team_id} ({home_away})')

    # Check first drive to see team structure
    drives = data['drives']['items']
    if drives:
        first_drive = drives[0]
        print(f'\nFirst drive team ref: {first_drive.get("team", {})}')
        if 'plays' in first_drive and 'items' in first_drive['plays']:
            plays = first_drive['plays']['items']
            if plays:
                first_play = plays[0]
                print(f'First play team participants: {first_play.get("teamParticipants", [])}')

if __name__ == "__main__":
    debug_team_ids()
