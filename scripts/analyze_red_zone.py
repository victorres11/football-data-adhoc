#!/usr/bin/env python3
"""
Analyze Red Zone and Green Zone performance
"""

from typing import Dict, List, Any
from collections import defaultdict, Counter


def analyze_red_zone(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze Red Zone (20 yards to goal and in) and Green Zone (30 yards to goal and in) performance
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Filter to ONLY the primary team's offensive plays (but include field goals even though they're special teams)
    # This ensures we only analyze the primary team's performance, not opponent plays
    offensive_plays = [
        p for p in plays
        if p.get('offense', '').lower() == team_name.lower()
        and (p.get('play_classification') != 'special_teams' 
             or 'field goal' in p.get('play_type', '').lower())
    ]
    
    # Double-check: ensure no opponent plays slip through
    offensive_plays = [p for p in offensive_plays if p.get('offense', '').lower() == team_name.lower()]
    
    # Red Zone: 20 yards to goal and in
    red_zone_plays = [
        p for p in offensive_plays
        if p.get('yards_to_goal', 100) <= 20
    ]
    
    # Green Zone: 30 yards to goal and in
    green_zone_plays = [
        p for p in offensive_plays
        if p.get('yards_to_goal', 100) <= 30
    ]
    
    def analyze_zone(zone_plays, zone_name):
        """Analyze a specific zone"""
        if not zone_plays:
            return {
                'total_plays': 0,
                'touchdowns': 0,
                'td_scoring_rate': 0,
                'turnovers': 0,
                'avg_ppa': 0,
                'explosive_plays': 0,
                'explosive_rate': 0,
                'conversions_3rd': {'attempts': 0, 'conversions': 0, 'rate': 0},
                'conversions_4th': {'attempts': 0, 'conversions': 0, 'rate': 0},
                'plays': []
            }
        
        touchdowns = sum(1 for p in zone_plays if 'touchdown' in p.get('play_type', '').lower())
        td_scoring_rate = (touchdowns / len(zone_plays) * 100) if zone_plays else 0
        
        # Count turnovers in the zone
        turnovers = sum(1 for p in zone_plays if p.get('turnover') == True)
        
        # PPA
        ppas = [float(p.get('ppa')) for p in zone_plays if p.get('ppa') is not None]
        avg_ppa = sum(ppas) / len(ppas) if ppas else 0
        
        # Explosive plays
        explosive = sum(1 for p in zone_plays if p.get('explosive_play'))
        explosive_rate = (explosive / len(zone_plays) * 100) if zone_plays else 0
        
        # 3rd down conversions
        third_downs = [p for p in zone_plays if p.get('down') == 3]
        third_conversions = sum(1 for p in third_downs 
                               if '1st down' in p.get('play_text', '').lower() 
                               or 'first down' in p.get('play_text', '').lower()
                               or p.get('yards_gained', 0) >= p.get('distance', 0))
        
        # 4th down conversions (go for it only)
        fourth_downs = [
            p for p in zone_plays 
            if p.get('down') == 4 
            and 'punt' not in p.get('play_type', '').lower()
            and 'field goal' not in p.get('play_type', '').lower()
        ]
        fourth_conversions = sum(1 for p in fourth_downs
                                if '1st down' in p.get('play_text', '').lower()
                                or 'first down' in p.get('play_text', '').lower()
                                or p.get('yards_gained', 0) >= p.get('distance', 0))
        
        # Prepare plays for table
        zone_plays_list = []
        for play in zone_plays:
            zone_plays_list.append({
                'game_id': play.get('game_id'),
                'game_week': play.get('game_week'),
                'opponent': play.get('opponent'),
                'period': play.get('period'),
                'clock': play.get('clock', ''),
                'down': play.get('down'),
                'distance': play.get('distance'),
                'yards_to_goal': play.get('yards_to_goal'),
                'play_type': play.get('play_type', ''),
                'yards_gained': play.get('yards_gained', 0),
                'ppa': play.get('ppa'),
                'scoring': play.get('scoring', False),
                'explosive': play.get('explosive_play', False),
                'play_text': play.get('play_text', '')[:200]
            })
        
        return {
            'total_plays': len(zone_plays),
            'touchdowns': touchdowns,
            'td_scoring_rate': td_scoring_rate,
            'turnovers': turnovers,
            'avg_ppa': avg_ppa,
            'explosive_plays': explosive,
            'explosive_rate': explosive_rate,
            'conversions_3rd': {
                'attempts': len(third_downs),
                'conversions': third_conversions,
                'rate': (third_conversions / len(third_downs) * 100) if third_downs else 0
            },
            'conversions_4th': {
                'attempts': len(fourth_downs),
                'conversions': fourth_conversions,
                'rate': (fourth_conversions / len(fourth_downs) * 100) if fourth_downs else 0
            },
            'plays': zone_plays_list
        }
    
    red_zone_stats = analyze_zone(red_zone_plays, 'Red Zone')
    green_zone_stats = analyze_zone(green_zone_plays, 'Green Zone')
    
    # Group by game for trend analysis
    red_zone_by_game = defaultdict(lambda: {'plays': 0, 'scores': 0, 'touchdowns': 0})
    green_zone_by_game = defaultdict(lambda: {'plays': 0, 'scores': 0, 'touchdowns': 0})
    
    for play in red_zone_plays:
        game_id = play.get('game_id')
        red_zone_by_game[game_id]['plays'] += 1
        if play.get('scoring'):
            red_zone_by_game[game_id]['scores'] += 1
            if 'touchdown' in play.get('play_type', '').lower():
                red_zone_by_game[game_id]['touchdowns'] += 1
    
    for play in green_zone_plays:
        game_id = play.get('game_id')
        green_zone_by_game[game_id]['plays'] += 1
        if play.get('scoring'):
            green_zone_by_game[game_id]['scores'] += 1
            if 'touchdown' in play.get('play_type', '').lower():
                green_zone_by_game[game_id]['touchdowns'] += 1
    
    return {
        'red_zone': red_zone_stats,
        'green_zone': green_zone_stats,
        'red_zone_by_game': dict(red_zone_by_game),
        'green_zone_by_game': dict(green_zone_by_game),
        'total_games': len(set(p.get('game_id') for p in offensive_plays))
    }

