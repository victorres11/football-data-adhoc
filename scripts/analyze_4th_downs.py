#!/usr/bin/env python3
"""
Analyze 4th down decisions (focus on "Go For It" decisions)
"""

from typing import Dict, List, Any
from collections import defaultdict


def is_go_for_it_4th_down(play: Dict) -> bool:
    """
    Determine if a 4th down play is a "go for it" attempt
    (not a punt or field goal)
    """
    if play.get('down') != 4:
        return False
    
    play_type = play.get('play_type', '').lower()
    
    # Exclude punts and field goals
    if 'punt' in play_type:
        return False
    if 'field goal' in play_type:
        return False
    if 'timeout' in play_type:
        return False
    
    # Exclude penalties that are no-play
    if play_type == 'penalty' and 'no play' in play.get('play_text', '').lower():
        return False
    
    return True


def analyze_4th_downs(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze 4th down decisions
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Filter to 4th down plays by offense
    fourth_down_plays = [
        p for p in plays 
        if p.get('down') == 4 
        and p.get('offense', '').lower() == team_name.lower()
    ]
    
    # Separate go-for-it vs other
    go_for_it_plays = [p for p in fourth_down_plays if is_go_for_it_4th_down(p)]
    
    # Determine conversions (1st down or scoring)
    conversions = []
    failures = []
    
    for play in go_for_it_plays:
        play_type = play.get('play_type', '').lower()
        play_text = play.get('play_text', '').lower()
        
        # Check if converted
        converted = False
        if '1st down' in play_text or 'first down' in play_text:
            converted = True
        elif 'touchdown' in play_type or 'touchdown' in play_text:
            converted = True
        elif play.get('yards_gained', 0) >= play.get('distance', 0):
            converted = True
        
        play_data = {
            'game_id': play.get('game_id'),
            'game_week': play.get('game_week'),
            'opponent': play.get('opponent'),
            'period': play.get('period'),
            'clock': play.get('clock', ''),
            'yard_line': play.get('yard_line'),
            'yards_to_goal': play.get('yards_to_goal'),
            'distance': play.get('distance'),
            'play_type': play.get('play_type', ''),
            'yards_gained': play.get('yards_gained', 0),
            'ppa': play.get('ppa'),
            'converted': converted,
            'play_text': play.get('play_text', '')[:200]
        }
        
        if converted:
            conversions.append(play_data)
        else:
            failures.append(play_data)
    
    total_attempts = len(go_for_it_plays)
    total_conversions = len(conversions)
    conversion_rate = (total_conversions / total_attempts * 100) if total_attempts > 0 else 0
    
    # Group by game
    game_stats = defaultdict(lambda: {'attempts': 0, 'conversions': 0, 'plays': []})
    for play in go_for_it_plays:
        game_id = play.get('game_id')
        game_stats[game_id]['attempts'] += 1
        game_stats[game_id]['plays'].append(play)
        
        # Check conversion
        play_text = play.get('play_text', '').lower()
        if '1st down' in play_text or 'first down' in play_text or 'touchdown' in play_text:
            game_stats[game_id]['conversions'] += 1
        elif play.get('yards_gained', 0) >= play.get('distance', 0):
            game_stats[game_id]['conversions'] += 1
    
    # Distance breakdowns
    distance_breakdown = defaultdict(lambda: {'attempts': 0, 'conversions': 0})
    for play in go_for_it_plays:
        distance = play.get('distance', 0)
        play_text = play.get('play_text', '').lower()
        converted = '1st down' in play_text or 'first down' in play_text or 'touchdown' in play_text or play.get('yards_gained', 0) >= distance
        
        if distance <= 1:
            dist_key = '1 yard or less'
        elif distance <= 3:
            dist_key = '2-3 yards'
        elif distance <= 5:
            dist_key = '4-5 yards'
        elif distance <= 10:
            dist_key = '6-10 yards'
        else:
            dist_key = '11+ yards'
        
        distance_breakdown[dist_key]['attempts'] += 1
        if converted:
            distance_breakdown[dist_key]['conversions'] += 1
    
    # Last 3 games
    sorted_games = sorted(game_stats.keys(), key=lambda gid: next(
        (p.get('game_week', 0) for p in plays if p.get('game_id') == gid), 0))
    last_3_games = sorted_games[-3:] if len(sorted_games) >= 3 else sorted_games
    
    last_3_attempts = sum(game_stats[gid]['attempts'] for gid in last_3_games)
    last_3_conversions = sum(game_stats[gid]['conversions'] for gid in last_3_games)
    last_3_rate = (last_3_conversions / last_3_attempts * 100) if last_3_attempts > 0 else 0
    
    # Combine all plays for table
    all_plays_flat = conversions + failures
    
    return {
        'total_attempts': total_attempts,
        'total_conversions': total_conversions,
        'conversion_rate': conversion_rate,
        'last_3_games': {
            'attempts': last_3_attempts,
            'conversions': last_3_conversions,
            'conversion_rate': last_3_rate,
            'games': last_3_games
        },
        'distance_breakdown': dict(distance_breakdown),
        'plays': all_plays_flat,
        'total_games': len(game_stats),
        'game_stats': dict(game_stats)
    }

