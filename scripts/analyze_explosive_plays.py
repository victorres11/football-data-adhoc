#!/usr/bin/env python3
"""
Analyze explosive plays (plays marked as explosive_play: true)
"""

from typing import Dict, List, Any
from collections import defaultdict


def analyze_explosive_plays(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze explosive plays
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Filter to explosive plays by offense (excluding special teams)
    explosive_plays = [
        p for p in plays 
        if p.get('explosive_play') == True 
        and p.get('offense', '').lower() == team_name.lower()
        and p.get('play_classification') != 'special_teams'
    ]
    
    # Group by game
    game_stats = defaultdict(lambda: {'count': 0, 'plays': []})
    
    for play in explosive_plays:
        game_id = play.get('game_id')
        game_stats[game_id]['count'] += 1
        game_stats[game_id]['plays'].append({
            'game_id': play.get('game_id'),
            'game_week': play.get('game_week'),
            'opponent': play.get('opponent'),
            'period': play.get('period'),
            'clock': play.get('clock', ''),
            'down': play.get('down'),
            'distance': play.get('distance'),
            'play_type': play.get('play_type', ''),
            'yards_gained': play.get('yards_gained', 0),
            'ppa': play.get('ppa'),
            'play_text': play.get('play_text', '')[:150],
            'yard_line': play.get('yard_line'),
            'yards_to_goal': play.get('yards_to_goal')
        })
    
    total_explosive = len(explosive_plays)
    unique_games = len(game_stats)
    avg_per_game = total_explosive / unique_games if unique_games > 0 else 0
    
    # Last 3 games
    sorted_games = sorted(game_stats.keys(), key=lambda gid: next(
        (p.get('game_week', 0) for p in plays if p.get('game_id') == gid), 0))
    last_3_games = sorted_games[-3:] if len(sorted_games) >= 3 else sorted_games
    
    last_3_count = sum(game_stats[gid]['count'] for gid in last_3_games)
    last_3_avg = last_3_count / len(last_3_games) if len(last_3_games) > 0 else 0
    
    # Flatten all plays for table
    all_plays_flat = []
    for game_id, stats in game_stats.items():
        all_plays_flat.extend(stats['plays'])
    
    return {
        'total_explosive_plays': total_explosive,
        'avg_per_game': avg_per_game,
        'last_3_games': {
            'total': last_3_count,
            'avg_per_game': last_3_avg,
            'games': last_3_games
        },
        'plays': all_plays_flat,
        'total_games': unique_games,
        'game_stats': dict(game_stats)
    }

