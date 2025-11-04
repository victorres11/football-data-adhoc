#!/usr/bin/env python3
"""
Analyze performance after turnovers
"""

from typing import Dict, List, Any
from collections import defaultdict


def analyze_post_turnover(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze performance after turnovers
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Find turnovers
    turnovers = [
        p for p in plays 
        if p.get('turnover') == True
    ]
    
    # Find drives that started after turnovers
    post_turnover_plays = [
        p for p in plays
        if p.get('drive_started_after_turnover') == True
    ]
    
    # Group by turnover event
    turnover_analysis = []
    
    for turnover in turnovers:
        game_id = turnover.get('game_id')
        drive_id = turnover.get('drive_id')
        turnover_type = turnover.get('play_type', 'Unknown')
        
        # Find the drive that started after this turnover
        # (next drive by same offense or opposite defense)
        post_drive_plays = [
            p for p in post_turnover_plays
            if p.get('game_id') == game_id
            and p.get('drive_id') != drive_id
        ]
        
        # Check if this drive resulted in points
        drive_points = 0
        drive_result = 'No Score'
        
        for play in post_drive_plays:
            if play.get('scoring') == True:
                if 'Touchdown' in play.get('play_type', ''):
                    drive_points = 7
                    drive_result = 'Touchdown'
                elif 'Field Goal' in play.get('play_type', ''):
                    drive_points = 3
                    drive_result = 'Field Goal'
        
        # Check if it's our turnover (offense) or opponent's (defense)
        is_our_turnover = turnover.get('offense', '').lower() == team_name.lower()
        
        turnover_analysis.append({
            'game_id': game_id,
            'game_week': turnover.get('game_week'),
            'opponent': turnover.get('opponent'),
            'turnover_type': turnover_type,
            'is_our_turnover': is_our_turnover,
            'period': turnover.get('period'),
            'clock': turnover.get('clock', ''),
            'drive_result': drive_result,
            'points_scored': drive_points if not is_our_turnover else 0,
            'points_allowed': drive_points if is_our_turnover else 0,
            'play_text': turnover.get('play_text', '')[:150]
        })
    
    # Calculate totals
    our_turnovers = [t for t in turnover_analysis if t['is_our_turnover']]
    opponent_turnovers = [t for t in turnover_analysis if not t['is_our_turnover']]
    
    total_turnovers = len(turnovers)
    our_turnover_count = len(our_turnovers)
    opponent_turnover_count = len(opponent_turnovers)
    
    # Points after our turnovers (opponent scored)
    points_allowed_after_our_turnovers = sum(t['points_allowed'] for t in our_turnovers)
    
    # Points after opponent turnovers (we scored)
    points_scored_after_opponent_turnovers = sum(t['points_scored'] for t in opponent_turnovers)
    
    # Success rate (drives that resulted in scores)
    our_turnovers_with_scores = sum(1 for t in our_turnovers if t['points_allowed'] > 0)
    opponent_turnovers_with_scores = sum(1 for t in opponent_turnovers if t['points_scored'] > 0)
    
    our_turnover_score_rate = (our_turnovers_with_scores / our_turnover_count * 100) if our_turnover_count > 0 else 0
    opponent_turnover_score_rate = (opponent_turnovers_with_scores / opponent_turnover_count * 100) if opponent_turnover_count > 0 else 0
    
    # Calculate last 3 games stats
    sorted_games = sorted(set(t.get('game_week', 0) for t in turnover_analysis), key=lambda x: x)
    last_3_weeks = sorted_games[-3:] if len(sorted_games) >= 3 else sorted_games
    
    last_3_our_turnovers = [t for t in our_turnovers if t.get('game_week', 0) in last_3_weeks]
    last_3_opponent_turnovers = [t for t in opponent_turnovers if t.get('game_week', 0) in last_3_weeks]
    
    last_3_points_allowed = sum(t['points_allowed'] for t in last_3_our_turnovers)
    last_3_points_scored = sum(t['points_scored'] for t in last_3_opponent_turnovers)
    last_3_net_points = last_3_points_scored - last_3_points_allowed
    
    return {
        'total_turnovers': total_turnovers,
        'our_turnovers': our_turnover_count,
        'opponent_turnovers': opponent_turnover_count,
        'points_allowed_after_our_turnovers': points_allowed_after_our_turnovers,
        'points_scored_after_opponent_turnovers': points_scored_after_opponent_turnovers,
        'net_points_after_turnovers': points_scored_after_opponent_turnovers - points_allowed_after_our_turnovers,
        'last_3_games': {
            'points_allowed': last_3_points_allowed,
            'points_scored': last_3_points_scored,
            'net_points': last_3_net_points
        },
        'our_turnover_score_rate': our_turnover_score_rate,
        'opponent_turnover_score_rate': opponent_turnover_score_rate,
        'turnover_analysis': turnover_analysis
    }

