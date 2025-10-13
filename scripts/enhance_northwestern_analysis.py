#!/usr/bin/env python3
"""
Enhanced Northwestern Analysis - Extract Player Stats and Group Play Selection

This script enhances the existing analysis by:
1. Grouping play selection into logical categories
2. Extracting detailed individual player statistics
3. Identifying key players and their performance
"""

import json
from collections import defaultdict, Counter

def group_play_selection(play_types):
    """Group play types into logical categories"""
    grouped = {
        'Rush Offense': 0,
        'Pass Offense': 0,
        'Special Teams': 0,
        'Other': 0
    }
    
    for play_type, count in play_types.items():
        if play_type in ['Rush', 'Rushing Touchdown']:
            grouped['Rush Offense'] += count
        elif play_type in ['Pass Reception', 'Pass Incompletion', 'Passing Touchdown', 'Sack']:
            grouped['Pass Offense'] += count
        elif play_type in ['Kickoff', 'Punt', 'Field Goal Good']:
            grouped['Special Teams'] += count
        else:
            grouped['Other'] += count
    
    return grouped

def extract_player_statistics(data, team_id):
    """Extract detailed player statistics from boxscore"""
    players = {
        'passing': [],
        'rushing': [],
        'receiving': [],
        'defensive': []
    }
    
    # Find Northwestern team in boxscore
    northwestern_team = None
    for team in data['boxscore']['teams']:
        if team['team']['id'] == team_id:
            northwestern_team = team
            break
    
    if not northwestern_team:
        return players
    
    # Extract team statistics
    team_stats = {}
    for stat in northwestern_team['statistics']:
        team_stats[stat['name']] = {
            'display_value': stat.get('displayValue', ''),
            'value': stat.get('value', 0),
            'label': stat.get('label', '')
        }
    
    # Extract player statistics from boxscore.players
    if 'players' in data['boxscore']:
        for team_data in data['boxscore']['players']:
            if team_data['team']['id'] == team_id:
                for stat_category in team_data['statistics']:
                    category_name = stat_category['name']
                    
                    if category_name in ['passing', 'rushing', 'receiving']:
                        for athlete_data in stat_category.get('athletes', []):
                            athlete = athlete_data['athlete']
                            stats = athlete_data['stats']
                            
                            player_info = {
                                'name': athlete['displayName'],
                                'position': athlete.get('position', {}).get('abbreviation', ''),
                                'jersey': athlete.get('jersey', ''),
                                'stats': stats,
                                'labels': stat_category.get('labels', []),
                                'descriptions': stat_category.get('descriptions', [])
                            }
                            
                            players[category_name].append(player_info)
    
    # Extract defensive leaders from leaders section
    for team_leaders in data['leaders']:
        if team_leaders['team']['id'] == team_id:
            for leader_category in team_leaders['leaders']:
                if leader_category['name'] in ['sacks', 'totalTackles', 'interceptions']:
                    for leader in leader_category.get('leaders', []):
                        athlete = leader['athlete']
                        player_info = {
                            'name': athlete['displayName'],
                            'position': athlete.get('position', {}).get('abbreviation', ''),
                            'jersey': athlete.get('jersey', ''),
                            'stat_value': leader['mainStat']['value'],
                            'stat_label': leader['mainStat']['label'],
                            'summary': leader.get('summary', ''),
                            'display_value': leader.get('displayValue', '')
                        }
                        players['defensive'].append(player_info)
    
    return players, team_stats

def identify_key_players(players):
    """Identify standout players based on performance"""
    key_players = {
        'qb': None,
        'top_rusher': None,
        'top_receiver': None,
        'defensive_standout': None
    }
    
    # Find QB
    if players['passing']:
        qb = players['passing'][0]  # Usually the starter is first
        key_players['qb'] = {
            'name': qb['name'],
            'position': qb['position'],
            'jersey': qb['jersey'],
            'completions': qb['stats'][0] if len(qb['stats']) > 0 else '0',
            'attempts': qb['stats'][0].split('/')[1] if '/' in qb['stats'][0] else '0',
            'yards': qb['stats'][1] if len(qb['stats']) > 1 else '0',
            'touchdowns': qb['stats'][3] if len(qb['stats']) > 3 else '0',
            'interceptions': qb['stats'][4] if len(qb['stats']) > 4 else '0'
        }
    
    # Find top rusher
    if players['rushing']:
        top_rusher = players['rushing'][0]  # Usually sorted by yards
        key_players['top_rusher'] = {
            'name': top_rusher['name'],
            'position': top_rusher['position'],
            'jersey': top_rusher['jersey'],
            'carries': top_rusher['stats'][0] if len(top_rusher['stats']) > 0 else '0',
            'yards': top_rusher['stats'][1] if len(top_rusher['stats']) > 1 else '0',
            'touchdowns': top_rusher['stats'][3] if len(top_rusher['stats']) > 3 else '0'
        }
    
    # Find top receiver
    if players['receiving']:
        top_receiver = players['receiving'][0]  # Usually sorted by yards
        key_players['top_receiver'] = {
            'name': top_receiver['name'],
            'position': top_receiver['position'],
            'jersey': top_receiver['jersey'],
            'receptions': top_receiver['stats'][0] if len(top_receiver['stats']) > 0 else '0',
            'yards': top_receiver['stats'][1] if len(top_receiver['stats']) > 1 else '0',
            'touchdowns': top_receiver['stats'][3] if len(top_receiver['stats']) > 3 else '0'
        }
    
    # Find defensive standout
    if players['defensive']:
        # Look for highest tackle count
        top_tackler = None
        for player in players['defensive']:
            if player['stat_label'] == 'TOT':
                if not top_tackler or int(player['stat_value']) > int(top_tackler['stat_value']):
                    top_tackler = player
        
        if top_tackler:
            key_players['defensive_standout'] = {
                'name': top_tackler['name'],
                'position': top_tackler['position'],
                'jersey': top_tackler['jersey'],
                'tackles': top_tackler['stat_value'],
                'summary': top_tackler['summary']
            }
    
    return key_players

def main():
    """Main analysis function"""
    print("Enhanced Northwestern Analysis")
    print("=" * 40)
    
    # Load existing analysis
    with open('../data/northwestern/scouting_report.json', 'r') as f:
        existing_analysis = json.load(f)
    
    # Load raw game data
    with open('../data/northwestern/game_401752866.json', 'r') as f:
        game_data = json.load(f)
    
    # Find Northwestern team ID
    northwestern_id = None
    for team_id, team in existing_analysis['game_info']['teams'].items():
        if 'Northwestern' in team['name']:
            northwestern_id = team_id
            break
    
    if not northwestern_id:
        print("Error: Could not find Northwestern team ID")
        return
    
    print(f"Analyzing: {existing_analysis['game_info']['northwestern_team']['name']}")
    
    # Group play selection
    print("\n1. Grouping Play Selection...")
    play_selection = existing_analysis['offensive_analysis']['play_selection']
    grouped_plays = group_play_selection(play_selection['by_type'])
    
    # Extract player statistics
    print("2. Extracting Player Statistics...")
    players, team_stats = extract_player_statistics(game_data, northwestern_id)
    
    # Identify key players
    print("3. Identifying Key Players...")
    key_players = identify_key_players(players)
    
    # Create enhanced analysis
    enhanced_analysis = {
        'game_info': existing_analysis['game_info'],
        'offensive_analysis': {
            'play_selection': {
                'by_type': play_selection['by_type'],
                'grouped': grouped_plays,
                'total_plays': play_selection['total_plays']
            },
            'scoring_drives': existing_analysis['offensive_analysis']['scoring_drives']
        },
        'player_analysis': {
            'key_players': key_players,
            'all_players': players,
            'team_stats': team_stats
        },
        'defensive_analysis': existing_analysis['defensive_analysis'],
        'turnovers': existing_analysis['turnovers'],
        'game_narrative': existing_analysis['game_narrative'],
        'summary': existing_analysis['summary']
    }
    
    # Save enhanced analysis
    print("\n4. Saving Enhanced Analysis...")
    with open('../data/northwestern/enhanced_scouting_report.json', 'w') as f:
        json.dump(enhanced_analysis, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 40)
    print("ENHANCED ANALYSIS SUMMARY")
    print("=" * 40)
    
    print(f"\nPlay Selection Groups:")
    for category, count in grouped_plays.items():
        percentage = (count / play_selection['total_plays']) * 100
        print(f"  {category}: {count} plays ({percentage:.1f}%)")
    
    print(f"\nKey Players:")
    if key_players['qb']:
        qb = key_players['qb']
        print(f"  QB: {qb['name']} - {qb['completions']}/{qb['attempts']} for {qb['yards']} yards, {qb['touchdowns']} TD, {qb['interceptions']} INT")
    
    if key_players['top_rusher']:
        rb = key_players['top_rusher']
        print(f"  Top Rusher: {rb['name']} - {rb['carries']} carries for {rb['yards']} yards, {rb['touchdowns']} TD")
    
    if key_players['top_receiver']:
        wr = key_players['top_receiver']
        print(f"  Top Receiver: {wr['name']} - {wr['receptions']} catches for {wr['yards']} yards, {wr['touchdowns']} TD")
    
    if key_players['defensive_standout']:
        def_player = key_players['defensive_standout']
        print(f"  Defensive Standout: {def_player['name']} - {def_player['tackles']} tackles")
    
    print(f"\nFiles saved:")
    print(f"- ../data/northwestern/enhanced_scouting_report.json")

if __name__ == "__main__":
    main()
