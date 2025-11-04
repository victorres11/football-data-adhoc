#!/usr/bin/env python3
"""
Analyze penalties
"""

import re
from typing import Dict, List, Any
from collections import defaultdict, Counter


def analyze_penalties(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze penalties
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Filter to plays with penalties (offense or defense)
    penalty_plays = [
        p for p in plays 
        if p.get('penalty_type') is not None
        and (p.get('offense', '').lower() == team_name.lower() 
             or p.get('defense', '').lower() == team_name.lower())
    ]
    
    # Group by game
    game_stats = defaultdict(lambda: {'count': 0, 'accepted': 0, 'declined': 0, 'yards': 0, 'plays': []})
    
    # Count by type and decision
    penalty_types = Counter()
    penalty_decisions = Counter()
    total_penalty_yards = 0
    
    for play in penalty_plays:
        game_id = play.get('game_id')
        penalty_type = play.get('penalty_type', 'Unknown')
        decision = play.get('penalty_decision', 'Unknown')
        play_text = play.get('play_text', '')
        
        # Extract penalty yards (only for accepted penalties)
        # Use yards_gained field directly (should be negative or absolute value)
        penalty_yards = 0
        if decision == 'accepted':
            yards_gained = play.get('yards_gained', 0)
            # Use absolute value since yards_gained might be negative
            # Penalties are always negative yardage, so we want the absolute value
            penalty_yards = abs(yards_gained) if yards_gained is not None else 0
            total_penalty_yards += penalty_yards
            game_stats[game_id]['yards'] += penalty_yards
        
        game_stats[game_id]['count'] += 1
        if decision == 'accepted':
            game_stats[game_id]['accepted'] += 1
        elif decision == 'declined':
            game_stats[game_id]['declined'] += 1
        
        penalty_types[penalty_type] += 1
        penalty_decisions[decision] += 1
        
        game_stats[game_id]['plays'].append({
            'game_id': play.get('game_id'),
            'game_week': play.get('game_week'),
            'opponent': play.get('opponent'),
            'period': play.get('period'),
            'clock': play.get('clock', ''),
            'penalty_type': penalty_type,
            'penalty_decision': decision,
            'penalty_yards': penalty_yards,
            'is_offense': play.get('offense', '').lower() == team_name.lower(),
            'play_text': play.get('play_text', '')[:200]
        })
    
    total_penalties = len(penalty_plays)
    accepted = penalty_decisions.get('accepted', 0)
    declined = penalty_decisions.get('declined', 0)
    
    unique_games = len(game_stats)
    avg_per_game = total_penalties / unique_games if unique_games > 0 else 0
    
    # Last 3 games
    sorted_games = sorted(game_stats.keys(), key=lambda gid: next(
        (p.get('game_week', 0) for p in plays if p.get('game_id') == gid), 0))
    last_3_games = sorted_games[-3:] if len(sorted_games) >= 3 else sorted_games
    
    last_3_count = sum(game_stats[gid]['count'] for gid in last_3_games)
    last_3_accepted = sum(game_stats[gid]['accepted'] for gid in last_3_games)
    last_3_declined = sum(game_stats[gid]['declined'] for gid in last_3_games)
    last_3_yards = sum(game_stats[gid]['yards'] for gid in last_3_games)
    
    # Flatten all plays for table
    all_plays_flat = []
    for game_id, stats in game_stats.items():
        all_plays_flat.extend(stats['plays'])
    
    return {
        'total_penalties': total_penalties,
        'accepted': accepted,
        'declined': declined,
        'total_penalty_yards': total_penalty_yards,
        'avg_per_game': avg_per_game,
        'penalty_types': dict(penalty_types),
        'penalty_decisions': dict(penalty_decisions),
        'last_3_games': {
            'total': last_3_count,
            'accepted': last_3_accepted,
            'declined': last_3_declined,
            'yards': last_3_yards,
            'games': last_3_games
        },
        'plays': all_plays_flat,
        'total_games': unique_games,
        'game_stats': dict(game_stats)
    }

