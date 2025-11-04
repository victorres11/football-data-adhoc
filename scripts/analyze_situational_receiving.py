#!/usr/bin/env python3
"""
Analyze Situational Receiving Stats from SIS Data (Task 9)
"""

import json
from typing import Dict, List, Any
from pathlib import Path


def load_sis_data(sis_file_path: str = "advanced_reports_yogi/sis-data/washington_wisconsin_analysis_2025.json") -> Dict[str, Any]:
    """
    Load SIS data from JSON file
    
    Args:
        sis_file_path: Path to SIS data JSON file
        
    Returns:
        Dictionary containing SIS data
    """
    # Handle both relative and absolute paths
    if Path(sis_file_path).is_absolute():
        file_path = Path(sis_file_path)
    else:
        file_path = Path(sis_file_path)
        if not file_path.exists():
            file_path = Path("..") / sis_file_path
    
    if not file_path.exists():
        raise ValueError(f"SIS data file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return json.load(f)


def map_sis_to_games(sis_data: Dict, team_games: List[Dict], team_name: str) -> Dict[int, Dict]:
    """
    Map SIS game data to existing game IDs by week and opponent
    
    Args:
        sis_data: SIS data dictionary
        team_games: List of game dictionaries from existing data
        team_name: 'Washington' or 'Wisconsin'
        
    Returns:
        Dictionary mapping SIS week keys to existing game IDs
    """
    mapping = {}
    
    # Get task 9 data for the team (data is under 'data' key)
    data = sis_data.get('data', {})
    task_9 = data.get('task_9', {})
    team_data = task_9.get(team_name.lower(), {})
    
    # Create lookup by week and opponent from existing games
    game_lookup = {}
    for game in team_games:
        week = game.get('week')
        opponent = game.get('opponent', '')
        game_id = game.get('game_id')
        if week and opponent:
            key = (week, opponent.lower())
            game_lookup[key] = game_id
    
    # Map SIS weeks to game IDs
    for section in ['3rd_down', 'redzone']:
        if section in team_data:
            by_week = team_data[section].get('by_week', {})
            for week_str, week_data in by_week.items():
                week = int(week_str)
                opponent = week_data.get('opponent', '').lower()
                key = (week, opponent)
                if key in game_lookup:
                    mapping[week] = game_lookup[key]
    
    return mapping


def analyze_situational_receiving(sis_data: Dict, team_name: str, team_games: List[Dict]) -> Dict[str, Any]:
    """
    Analyze situational receiving stats from SIS Task 9 data
    
    Args:
        sis_data: SIS data dictionary
        team_name: 'Washington' or 'Wisconsin'
        team_games: List of game dictionaries for mapping
        
    Returns:
        Dictionary with analysis results
    """
    # Get task 9 data for the team (data is under 'data' key)
    data = sis_data.get('data', {})
    task_9 = data.get('task_9', {})
    team_data = task_9.get(team_name.lower(), {})
    
    if not team_data:
        return {
            '3rd_down': {
                'total': {'targets': 0, 'receptions': 0, 'first_downs': 0, 'touchdowns': 0, 'yards': 0},
                'by_week': {},
                'last_3_games': {'targets': 0, 'receptions': 0, 'first_downs': 0},
                'players': []
            },
            'redzone': {
                'total': {'targets': 0, 'receptions': 0, 'touchdowns': 0, 'yards': 0},
                'by_week': {},
                'last_3_games': {'targets': 0, 'receptions': 0, 'touchdowns': 0},
                'players': []
            },
            'game_mapping': {}
        }
    
    # Map SIS weeks to game IDs
    game_mapping = map_sis_to_games(sis_data, team_games, team_name)
    
    def analyze_situation(situation_data: Dict, situation_name: str) -> Dict[str, Any]:
        """Analyze a specific situation (3rd_down or redzone)"""
        by_week = situation_data.get('by_week', {})
        total = situation_data.get('total', {})
        
        # Calculate last 3 games
        sorted_weeks = sorted([int(w) for w in by_week.keys()])
        last_3_weeks = sorted_weeks[-3:] if len(sorted_weeks) >= 3 else sorted_weeks
        
        last_3_targets = sum(by_week.get(str(w), {}).get('stats', {}).get('targets', 0) for w in last_3_weeks)
        last_3_receptions = sum(by_week.get(str(w), {}).get('stats', {}).get('receptions', 0) for w in last_3_weeks)
        
        if situation_name == '3rd_down':
            last_3_first_downs = sum(by_week.get(str(w), {}).get('stats', {}).get('first_downs', 0) for w in last_3_weeks)
            # For 3rd down, also sum player-level TDs since stats might not have them
            last_3_touchdowns = sum(
                sum(p.get('touchdowns', 0) for p in by_week.get(str(w), {}).get('players', []))
                for w in last_3_weeks
            )
            last_3_extra = {'first_downs': last_3_first_downs, 'touchdowns': last_3_touchdowns}
        else:  # redzone
            # Sum player-level touchdowns since stats.touchdowns may be 0 but players have TDs
            last_3_touchdowns = sum(
                sum(p.get('touchdowns', 0) for p in by_week.get(str(w), {}).get('players', []))
                for w in last_3_weeks
            )
            last_3_extra = {'touchdowns': last_3_touchdowns}
        
        # Aggregate player stats across all games
        player_stats = {}
        for week_str, week_data in by_week.items():
            players = week_data.get('players', [])
            for player in players:
                player_id = player.get('playerId')
                player_name = player.get('player', 'Unknown')
                
                if player_id not in player_stats:
                    player_stats[player_id] = {
                        'playerId': player_id,
                        'player': player_name,
                        'targets': 0,
                        'receptions': 0,
                        'yards': 0
                    }
                    if situation_name == '3rd_down':
                        player_stats[player_id]['first_downs'] = 0
                        player_stats[player_id]['touchdowns'] = 0
                    else:
                        player_stats[player_id]['touchdowns'] = 0
                
                player_stats[player_id]['targets'] += player.get('targets', 0)
                player_stats[player_id]['receptions'] += player.get('receptions', 0)
                player_stats[player_id]['yards'] += player.get('yards', 0)
                
                if situation_name == '3rd_down':
                    player_stats[player_id]['first_downs'] += player.get('first_downs', 0)
                    player_stats[player_id]['touchdowns'] += player.get('touchdowns', 0)
                else:
                    player_stats[player_id]['touchdowns'] += player.get('touchdowns', 0)
        
        # Sort players by targets (descending)
        players_list = sorted(player_stats.values(), key=lambda x: x['targets'], reverse=True)
        
        # Format by_week data with game_id mapping
        by_week_formatted = {}
        for week_str, week_data in by_week.items():
            week = int(week_str)
            game_id = game_mapping.get(week)
            by_week_formatted[week_str] = {
                'week': week,
                'game_id': game_id,
                'opponent': week_data.get('opponent', ''),
                'stats': week_data.get('stats', {}),
                'players': week_data.get('players', [])
            }
        
        result = {
            'total': {
                'targets': total.get('targets', 0),
                'receptions': total.get('receptions', 0),
                'yards': sum(by_week.get(str(w), {}).get('stats', {}).get('yards', 0) for w in sorted_weeks)
            },
            'by_week': by_week_formatted,
            'last_3_games': {
                'targets': last_3_targets,
                'receptions': last_3_receptions,
                **last_3_extra
            },
            'players': players_list
        }
        
        if situation_name == '3rd_down':
            result['total']['first_downs'] = total.get('first_downs', 0)
            result['total']['touchdowns'] = total.get('touchdowns', 0)
        else:
            result['total']['touchdowns'] = total.get('touchdowns', 0)
        
        return result
    
    third_down = analyze_situation(team_data.get('3rd_down', {}), '3rd_down')
    redzone = analyze_situation(team_data.get('redzone', {}), 'redzone')
    
    # Get Big Ten rankings for players
    rankings = task_9.get('big_ten_rankings', {})
    player_rankings = rankings.get('player_rankings', {})
    
    # Map player rankings to player IDs for both situations
    third_down_rankings = {p.get('player_id'): p.get('rank') for p in player_rankings.get('third_down', []) if p.get('team') == team_name}
    redzone_rankings = {p.get('player_id'): p.get('rank') for p in player_rankings.get('redzone', []) if p.get('team') == team_name}
    
    # Add rankings to player data
    for player in third_down['players']:
        player_id = player.get('playerId')
        if player_id in third_down_rankings:
            player['big_ten_rank'] = third_down_rankings[player_id]
            player['is_top_25'] = third_down_rankings[player_id] <= 25
        else:
            player['big_ten_rank'] = None
            player['is_top_25'] = False
    
    for player in redzone['players']:
        player_id = player.get('playerId')
        if player_id in redzone_rankings:
            player['big_ten_rank'] = redzone_rankings[player_id]
            player['is_top_25'] = redzone_rankings[player_id] <= 25
        else:
            player['big_ten_rank'] = None
            player['is_top_25'] = False
    
    return {
        '3rd_down': third_down,
        'redzone': redzone,
        'game_mapping': game_mapping
    }

