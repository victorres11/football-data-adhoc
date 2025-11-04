#!/usr/bin/env python3
"""
Analyze special teams performance
"""

from typing import Dict, List, Any
from collections import defaultdict


def is_special_teams_explosive(play: Dict) -> bool:
    """
    Determine if a special teams play is explosive based on return type:
    - Kick return: 35+ yards
    - Punt return: 20+ yards
    """
    play_type = play.get('play_type', '').lower()
    play_text = play.get('play_text', '').lower()
    yards_gained = play.get('yards_gained', 0)
    
    # Kick return: 35+ yards
    if 'kickoff' in play_type or 'kickoff' in play_text:
        if 'return' in play_type or 'return' in play_text:
            return yards_gained >= 35
    
    # Punt return: 20+ yards
    if 'punt' in play_type or 'punt' in play_text:
        if 'return' in play_type or 'return' in play_text:
            return yards_gained >= 20
    
    return False


def is_bad_special_teams_result(play: Dict, is_our_play: bool, explosive_allowed: bool = False) -> bool:
    """
    Determine if a special teams play is a "bad result"
    - Turnover (play has turnover == True)
    - OR Explosive Allowed (opponent had an explosive return)
    """
    # Turnover
    if play.get('turnover', False):
        return True
    
    # Explosive allowed (only for our plays - when opponent has explosive return)
    if is_our_play and explosive_allowed:
        return True
    
    return False


def analyze_special_teams(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze special teams performance
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Filter to special teams plays
    special_teams_plays = [
        p for p in plays 
        if p.get('play_classification') == 'special_teams'
    ]
    
    # Separate by offense (our special teams) vs defense (opponent special teams)
    our_st_plays = [
        p for p in special_teams_plays
        if p.get('offense', '').lower() == team_name.lower()
    ]
    
    opponent_st_plays = [
        p for p in special_teams_plays
        if p.get('offense', '').lower() != team_name.lower()
    ]
    
    # Find explosive plays using special teams criteria (35+ kick return, 20+ punt return)
    explosive_plays = [p for p in our_st_plays if is_special_teams_explosive(p)]
    explosive_returns_allowed = [p for p in opponent_st_plays if is_special_teams_explosive(p)]
    
    # Count touchdowns on special teams
    tds_scored = [
        p for p in our_st_plays
        if p.get('scoring', False) and 
        ('touchdown' in p.get('play_type', '').lower() or 'touchdown' in p.get('play_text', '').lower())
    ]
    tds_allowed = [
        p for p in opponent_st_plays
        if p.get('scoring', False) and 
        ('touchdown' in p.get('play_type', '').lower() or 'touchdown' in p.get('play_text', '').lower())
    ]
    
    # Find bad results (Turnover OR Explosive Allowed)
    # For our plays: check if we had a turnover OR if opponent had explosive return
    bad_results = []
    for play in our_st_plays:
        is_turnover = play.get('turnover', False)
        # Check if opponent had explosive return on this play/drive
        game_id = play.get('game_id')
        drive_id = play.get('drive_id')
        explosive_allowed = any(
            p.get('game_id') == game_id and 
            p.get('drive_id') == drive_id and 
            is_special_teams_explosive(p)
            for p in opponent_st_plays
        )
        if is_bad_special_teams_result(play, is_our_play=True, explosive_allowed=explosive_allowed):
            bad_results.append(play)
    
    # Bad results allowed = opponent turnovers or our explosive returns
    bad_results_allowed = [
        p for p in opponent_st_plays 
        if p.get('turnover', False) or is_special_teams_explosive(p)
    ]
    
    # Group by game
    game_stats = defaultdict(lambda: {
        'total_plays': 0,
        'explosive': 0,
        'bad_results': 0,
        'plays': []
    })
    
    for play in special_teams_plays:
        game_id = play.get('game_id')
        is_our = play.get('offense', '').lower() == team_name.lower()
        
        game_stats[game_id]['total_plays'] += 1
        
        explosive = is_special_teams_explosive(play)
        if explosive:
            game_stats[game_id]['explosive'] += 1
        
        # Determine bad result for this play
        is_turnover = play.get('turnover', False)
        # Check if opponent had explosive return (for our plays)
        explosive_allowed = False
        if is_our:
            game_id_check = play.get('game_id')
            drive_id_check = play.get('drive_id')
            explosive_allowed = any(
                p.get('game_id') == game_id_check and 
                p.get('drive_id') == drive_id_check and 
                is_special_teams_explosive(p)
                for p in opponent_st_plays
            )
        bad_result = is_bad_special_teams_result(play, is_our_play=is_our, explosive_allowed=explosive_allowed)
        if bad_result:
            game_stats[game_id]['bad_results'] += 1
        
        game_stats[game_id]['plays'].append({
            'game_id': game_id,
            'game_week': play.get('game_week'),
            'opponent': play.get('opponent'),
            'period': play.get('period'),
            'clock': play.get('clock', ''),
            'play_type': play.get('play_type', ''),
            'is_our': is_our,
            'explosive': explosive,
            'bad_result': bad_result,
            'turnover': is_turnover,
            'yards_gained': play.get('yards_gained', 0),
            'play_text': play.get('play_text', '')[:200]
        })
    
    total_explosive = len(explosive_plays)
    total_bad_results = len(bad_results)
    
    unique_games = len(game_stats)
    
    # Flatten all plays for table
    all_plays_flat = []
    for game_id, stats in game_stats.items():
        all_plays_flat.extend(stats['plays'])
    
    return {
        'total_explosive_plays': total_explosive,
        'total_bad_results': total_bad_results,
        'explosive_returns_allowed': len(explosive_returns_allowed),
        'bad_results_allowed': len(bad_results_allowed),
        'tds_scored': len(tds_scored),
        'tds_allowed': len(tds_allowed),
        'plays': all_plays_flat,
        'total_games': unique_games,
        'game_stats': dict(game_stats)
    }

