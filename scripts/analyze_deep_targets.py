#!/usr/bin/env python3
"""
Analyze Deep Target (20+ Air Yards) Stats from SIS Data (Task 4)
"""

import json
from typing import Dict, List, Any
from pathlib import Path


def analyze_deep_targets(sis_data: Dict, team_name: str) -> Dict[str, Any]:
    """
    Analyze deep target (20+ air yards) stats from SIS Task 4 data
    
    Args:
        sis_data: SIS data dictionary
        team_name: 'Washington' or 'Wisconsin'
        
    Returns:
        Dictionary with analysis results for passing and receiving
    """
    # Get task 4 data for the team
    data = sis_data.get('data', {})
    task_4 = data.get('task_4', {})
    team_data = task_4.get(team_name.lower(), {})
    
    if not team_data:
        return {
            'passing': {
                'total': {'attempts': 0, 'completions': 0, 'yards': 0, 'touchdowns': 0, 'interceptions': 0},
                'by_game': {},
                'last_3_games': {'attempts': 0, 'completions': 0, 'yards': 0, 'touchdowns': 0, 'interceptions': 0},
                'big_ten_rank': None
            },
            'receiving': {
                'total': {'targets': 0, 'receptions': 0, 'yards': 0, 'touchdowns': 0},
                'by_game': {},
                'last_3_games': {'targets': 0, 'receptions': 0, 'yards': 0, 'touchdowns': 0},
                'players': []
            }
        }
    
    # Analyze passing data
    passing_data = team_data.get('passing', {})
    passing_by_game = passing_data.get('by_game', {})
    passing_total = passing_data.get('total', {})
    passing_rank = passing_data.get('big_ten_rank')
    
    # Calculate last 3 games for passing
    # Convert game keys to week numbers and sort
    game_weeks = []
    for game_key, game_stats in passing_by_game.items():
        # Extract week from key like "Week9_Illinois"
        if game_key.startswith('Week'):
            try:
                week = int(game_key.replace('Week', '').split('_')[0])
                game_weeks.append((week, game_key, game_stats))
            except ValueError:
                pass
    
    game_weeks.sort(key=lambda x: x[0])
    last_3_games = game_weeks[-3:] if len(game_weeks) >= 3 else game_weeks
    
    last_3_passing = {
        'attempts': sum(g[2].get('attempts', 0) for g in last_3_games),
        'completions': sum(g[2].get('completions', 0) for g in last_3_games),
        'yards': sum(g[2].get('yards', 0) for g in last_3_games),
        'touchdowns': sum(g[2].get('touchdowns', 0) for g in last_3_games),
        'interceptions': sum(g[2].get('interceptions', 0) for g in last_3_games)
    }
    
    # Format passing by_game with week numbers
    passing_by_game_formatted = {}
    for game_key, game_stats in passing_by_game.items():
        if game_key.startswith('Week'):
            try:
                week = int(game_key.replace('Week', '').split('_')[0])
                opponent = '_'.join(game_key.replace('Week', '').split('_')[1:])
                passing_by_game_formatted[game_key] = {
                    'week': week,
                    'opponent': opponent.replace('_', ' '),
                    'attempts': game_stats.get('attempts', 0),
                    'completions': game_stats.get('completions', 0),
                    'yards': game_stats.get('yards', 0),
                    'touchdowns': game_stats.get('touchdowns', 0),
                    'interceptions': game_stats.get('interceptions', 0)
                }
            except ValueError:
                passing_by_game_formatted[game_key] = game_stats
    
    # Analyze receiving data
    receiving_data = team_data.get('receiving', {})
    receiving_by_game = receiving_data.get('by_game', {})
    receiving_total = receiving_data.get('total', {})
    
    # Calculate last 3 games for receiving
    receiving_game_weeks = []
    for game_key, game_stats in receiving_by_game.items():
        if game_key.startswith('Week'):
            try:
                week = int(game_key.replace('Week', '').split('_')[0])
                receiving_game_weeks.append((week, game_key, game_stats))
            except ValueError:
                pass
    
    receiving_game_weeks.sort(key=lambda x: x[0])
    last_3_receiving_games = receiving_game_weeks[-3:] if len(receiving_game_weeks) >= 3 else receiving_game_weeks
    
    last_3_receiving = {
        'targets': sum(g[2].get('targets', 0) for g in last_3_receiving_games),
        'receptions': sum(g[2].get('receptions', 0) for g in last_3_receiving_games),
        'yards': sum(g[2].get('yards', 0) for g in last_3_receiving_games),
        'touchdowns': sum(
            sum(p.get('touchdowns', 0) for p in g[2].get('players', []))
            for g in last_3_receiving_games
        )
    }
    
    # Aggregate player stats across all games
    player_stats = {}
    for game_key, game_stats in receiving_by_game.items():
        players = game_stats.get('players', [])
        for player in players:
            player_name = player.get('player', 'Unknown')
            
            if player_name not in player_stats:
                player_stats[player_name] = {
                    'player': player_name,
                    'targets': 0,
                    'receptions': 0,
                    'yards': 0,
                    'touchdowns': 0,
                    'air_yards': 0
                }
            
            player_stats[player_name]['targets'] += player.get('targets', 0)
            player_stats[player_name]['receptions'] += player.get('receptions', 0)
            player_stats[player_name]['yards'] += player.get('yards', 0)
            player_stats[player_name]['touchdowns'] += player.get('touchdowns', 0)
            player_stats[player_name]['air_yards'] += player.get('air_yards', 0)
    
    # Sort players by targets (descending)
    players_list = sorted(player_stats.values(), key=lambda x: x['targets'], reverse=True)
    
    # Format receiving by_game with enrichment fields
    receiving_by_game_formatted = {}
    for game_key, game_stats in receiving_by_game.items():
        receiving_by_game_formatted[game_key] = {
            'week': game_stats.get('week') or (int(game_key.replace('Week', '').split('_')[0]) if game_key.startswith('Week') else None),
            'opponent': game_stats.get('opp') or '_'.join(game_key.replace('Week', '').split('_')[1:]).replace('_', ' ') if game_key.startswith('Week') else '',
            'game_id': game_stats.get('game_id'),
            'is_conference': game_stats.get('is_conference'),
            'is_power4_opponent': game_stats.get('is_power4_opponent'),
            'targets': game_stats.get('targets', 0),
            'receptions': game_stats.get('receptions', 0),
            'yards': game_stats.get('yards', 0),
            'touchdowns': game_stats.get('touchdowns', 0),
            'players': game_stats.get('players', [])
        }
    
    return {
        'passing': {
            'total': passing_total,
            'by_game': passing_by_game_formatted,
            'last_3_games': last_3_passing,
            'big_ten_rank': passing_rank
        },
        'receiving': {
            'total': receiving_total,
            'by_game': receiving_by_game_formatted,
            'last_3_games': last_3_receiving,
            'players': players_list
        }
    }

