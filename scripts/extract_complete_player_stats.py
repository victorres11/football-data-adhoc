#!/usr/bin/env python3
"""
Extract complete top 3 rushers and receivers from Purdue vs Minnesota game data
"""

import json
import re
from collections import defaultdict

def extract_complete_player_stats(data):
    """Extract complete player stats from play-by-play data"""
    
    # Initialize player stats
    purdue_rushers = defaultdict(lambda: {'carries': 0, 'yards': 0, 'tds': 0})
    purdue_receivers = defaultdict(lambda: {'receptions': 0, 'yards': 0, 'tds': 0})
    minnesota_rushers = defaultdict(lambda: {'carries': 0, 'yards': 0, 'tds': 0})
    minnesota_receivers = defaultdict(lambda: {'receptions': 0, 'yards': 0, 'tds': 0})
    
    # Player name mappings
    purdue_players = {
        'Devin Mockobee': {'jersey': '45', 'position': 'RB'},
        'Malachi Singleton': {'jersey': '15', 'position': 'QB'},
        'Ryan Browne': {'jersey': '15', 'position': 'QB'},
        'Nitro Tuggle': {'jersey': '0', 'position': 'WR'},
        'Corey Smith': {'jersey': '8', 'position': 'WR'},
        'Michael Jackson III': {'jersey': '7', 'position': 'WR'},
        'Antonio Harris': {'jersey': '2', 'position': 'WR'},
        'Rico Walker': {'jersey': '9', 'position': 'WR'}
    }
    
    minnesota_players = {
        'Darius Taylor': {'jersey': '1', 'position': 'RB'},
        'Drake Lindsey': {'jersey': '5', 'position': 'QB'},
        'Meke Brockington': {'jersey': '3', 'position': 'WR'},
        'Javon Tracy': {'jersey': '2', 'position': 'WR'},
        'Logan Loya': {'jersey': '4', 'position': 'WR'},
        'Malachi Coleman': {'jersey': '6', 'position': 'WR'}
    }
    
    drives = data['drives']['previous']
    teams = {'2509': 'purdue', '135': 'minnesota'}
    
    for drive in drives:
        drive_team_id = drive.get('team', {}).get('id')
        if drive_team_id not in teams:
            continue
        
        team_name = teams[drive_team_id]
        
        if 'plays' in drive:
            for play in drive['plays']:
                text = play.get('text', '')
                yards = play.get('statYardage', 0)
                
                # Extract rushing plays
                if 'run' in text.lower() and 'yds' in text:
                    # Look for player name before 'run'
                    for player_name in purdue_players if team_name == 'purdue' else minnesota_players:
                        if player_name in text:
                            if team_name == 'purdue':
                                purdue_rushers[player_name]['carries'] += 1
                                purdue_rushers[player_name]['yards'] += yards
                                if 'TD' in text or 'touchdown' in text.lower():
                                    purdue_rushers[player_name]['tds'] += 1
                            else:
                                minnesota_rushers[player_name]['carries'] += 1
                                minnesota_rushers[player_name]['yards'] += yards
                                if 'TD' in text or 'touchdown' in text.lower():
                                    minnesota_rushers[player_name]['tds'] += 1
                            break
                
                # Extract receiving plays
                elif 'pass complete' in text.lower() and 'yds' in text:
                    # Look for player name after 'to'
                    for player_name in purdue_players if team_name == 'purdue' else minnesota_players:
                        if player_name in text:
                            if team_name == 'purdue':
                                purdue_receivers[player_name]['receptions'] += 1
                                purdue_receivers[player_name]['yards'] += yards
                                if 'TD' in text or 'touchdown' in text.lower():
                                    purdue_receivers[player_name]['tds'] += 1
                            else:
                                minnesota_receivers[player_name]['receptions'] += 1
                                minnesota_receivers[player_name]['yards'] += yards
                                if 'TD' in text or 'touchdown' in text.lower():
                                    minnesota_receivers[player_name]['tds'] += 1
                            break
    
    # Format the results
    def format_rushers(stats_dict, players_dict):
        formatted = []
        for player_name, stats in sorted(stats_dict.items(), key=lambda x: x[1]['yards'], reverse=True)[:3]:
            if player_name in players_dict:
                player_info = players_dict[player_name]
                td_text = f", {stats['tds']} TD" if stats['tds'] > 0 else ""
                formatted.append({
                    'name': player_name,
                    'jersey': player_info['jersey'],
                    'position': player_info['position'],
                    'stats': f"{stats['carries']} CAR, {stats['yards']} YDS{td_text}"
                })
        return formatted
    
    def format_receivers(stats_dict, players_dict):
        formatted = []
        for player_name, stats in sorted(stats_dict.items(), key=lambda x: x[1]['yards'], reverse=True)[:3]:
            if player_name in players_dict:
                player_info = players_dict[player_name]
                td_text = f", {stats['tds']} TD" if stats['tds'] > 0 else ""
                formatted.append({
                    'name': player_name,
                    'jersey': player_info['jersey'],
                    'position': player_info['position'],
                    'stats': f"{stats['receptions']} REC, {stats['yards']} YDS{td_text}"
                })
        return formatted
    
    return {
        'purdue': {
            'rushers': format_rushers(purdue_rushers, purdue_players),
            'receivers': format_receivers(purdue_receivers, purdue_players)
        },
        'minnesota': {
            'rushers': format_rushers(minnesota_rushers, minnesota_players),
            'receivers': format_receivers(minnesota_receivers, minnesota_players)
        }
    }

def main():
    """Main function to extract complete player stats"""
    print("Purdue vs Minnesota - Complete Top Player Stats Extraction")
    print("=" * 60)
    
    # Load Purdue game data
    with open('data/purdue/game_401752864/raw_game_data.json', 'r') as f:
        data = json.load(f)
    
    # Extract player stats
    player_stats = extract_complete_player_stats(data)
    
    # Print results
    print("\nPurdue Top Players:")
    print("Top 3 Rushers:")
    for i, rusher in enumerate(player_stats['purdue']['rushers'], 1):
        print(f"  {i}. #{rusher['jersey']} {rusher['name']} ({rusher['position']}) - {rusher['stats']}")
    
    print("\nTop 3 Receivers:")
    for i, receiver in enumerate(player_stats['purdue']['receivers'], 1):
        print(f"  {i}. #{receiver['jersey']} {receiver['name']} ({receiver['position']}) - {receiver['stats']}")
    
    print("\nMinnesota Top Players:")
    print("Top 3 Rushers:")
    for i, rusher in enumerate(player_stats['minnesota']['rushers'], 1):
        print(f"  {i}. #{rusher['jersey']} {rusher['name']} ({rusher['position']}) - {rusher['stats']}")
    
    print("\nTop 3 Receivers:")
    for i, receiver in enumerate(player_stats['minnesota']['receivers'], 1):
        print(f"  {i}. #{receiver['jersey']} {receiver['name']} ({receiver['position']}) - {receiver['stats']}")
    
    # Save to file
    with open('data/purdue/game_401752864/complete_player_stats.json', 'w') as f:
        json.dump(player_stats, f, indent=2)
    
    print(f"\n✓ Complete player stats saved to: data/purdue/game_401752864/complete_player_stats.json")

if __name__ == "__main__":
    main()
