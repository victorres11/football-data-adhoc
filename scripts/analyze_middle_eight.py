#!/usr/bin/env python3
"""
Analyze Middle 8 (4 minutes before/after halftime) performance
"""

from typing import Dict, List, Any
from collections import defaultdict


def analyze_middle_eight(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze middle 8 performance
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Filter to middle 8 plays
    middle_eight_plays = [p for p in plays if p.get('middle_eight') == True]
    
    # Calculate points scored/allowed
    points_scored = 0
    points_allowed = 0
    
    # Group by game
    game_stats = defaultdict(lambda: {'points_scored': 0, 'points_allowed': 0, 'plays': []})
    
    scoring_drives = []
    
    for play in middle_eight_plays:
        game_id = play.get('game_id')
        is_offense = play.get('offense', '').lower() == team_name.lower()
        
        game_stats[game_id]['plays'].append(play)
        
        # Check for scoring plays
        if play.get('scoring') == True:
            if 'Touchdown' in play.get('play_type', ''):
                points = 7  # Assume TD (could be 6+2pt, but default to 7)
                if is_offense:
                    points_scored += points
                    game_stats[game_id]['points_scored'] += points
                else:
                    points_allowed += points
                    game_stats[game_id]['points_allowed'] += points
            elif 'Field Goal' in play.get('play_type', ''):
                points = 3
                if is_offense:
                    points_scored += points
                    game_stats[game_id]['points_scored'] += points
                else:
                    points_allowed += points
                    game_stats[game_id]['points_allowed'] += points
            
            # Add to scoring drives
            # Determine the actual opponent - if our team is on offense, opponent is defense, and vice versa
            scoring_team = play.get('offense', '')  # The team that scored
            actual_opponent = play.get('opponent', '')
            
            # If opponent is missing or incorrect, try to infer from offense/defense
            if not actual_opponent or actual_opponent.lower() == team_name.lower():
                # If opponent field is missing or shows our team, use defense field
                actual_opponent = play.get('defense', '')
            
            scoring_drives.append({
                'game_id': play.get('game_id'),
                'game_week': play.get('game_week'),
                'opponent': actual_opponent,  # Always the actual opponent team
                'scoring_team': scoring_team,  # The team that scored (offense)
                'drive_id': play.get('drive_id'),
                'drive_number': play.get('drive_number'),
                'period': play.get('period'),
                'clock': play.get('clock', ''),
                'play_type': play.get('play_type', ''),
                'points': points,  # Always positive
                'is_offense': is_offense,  # True if our team scored
                'play_text': play.get('play_text', '')[:100]
            })
    
    # Calculate per-game averages
    unique_games = len(game_stats)
    avg_points_scored = points_scored / unique_games if unique_games > 0 else 0
    avg_points_allowed = points_allowed / unique_games if unique_games > 0 else 0
    avg_net = (points_scored - points_allowed) / unique_games if unique_games > 0 else 0
    
    # Last 3 games
    sorted_games = sorted(game_stats.keys(), key=lambda gid: next(
        (p.get('game_week', 0) for p in plays if p.get('game_id') == gid), 0))
    last_3_games = sorted_games[-3:] if len(sorted_games) >= 3 else sorted_games
    
    last_3_points_scored = sum(game_stats[gid]['points_scored'] for gid in last_3_games)
    last_3_points_allowed = sum(game_stats[gid]['points_allowed'] for gid in last_3_games)
    last_3_net = last_3_points_scored - last_3_points_allowed
    last_3_avg_net = last_3_net / len(last_3_games) if len(last_3_games) > 0 else 0
    
    return {
        'total_points_scored': points_scored,
        'total_points_allowed': points_allowed,
        'total_net_points': points_scored - points_allowed,
        'avg_points_scored_per_game': avg_points_scored,
        'avg_points_allowed_per_game': avg_points_allowed,
        'avg_net_per_game': avg_net,
        'last_3_games': {
            'points_scored': last_3_points_scored,
            'points_allowed': last_3_points_allowed,
            'net_points': last_3_net,
            'avg_net_per_game': last_3_avg_net,
            'games': last_3_games
        },
        'scoring_drives': scoring_drives,
        'total_games': unique_games,
        'game_stats': dict(game_stats)
    }

