#!/usr/bin/env python3
"""
Load and parse advanced play-by-play data from JSON files
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def load_team_data(team_name: str, data_dir: str = "advanced_reports_yogi") -> Dict[str, Any]:
    """
    Load all game data for a given team
    
    Args:
        team_name: 'Washington' or 'Wisconsin'
        data_dir: Base directory containing team folders
        
    Returns:
        Dictionary with game data and metadata
    """
    team_folder = f"{team_name.lower()}_play_by_play"
    # Handle both relative and absolute paths
    if Path(data_dir).is_absolute():
        team_path = Path(data_dir) / team_folder
    else:
        # Try from current directory, then from parent
        team_path = Path(data_dir) / team_folder
        if not team_path.exists():
            team_path = Path("..") / data_dir / team_folder
    
    if not team_path.exists():
        raise ValueError(f"Team folder not found: {team_path}")
    
    games = []
    all_plays = []
    
    # Load all JSON files
    json_files = sorted(team_path.glob("*.json"))
    
    for json_file in json_files:
        with open(json_file, 'r') as f:
            game_data = json.load(f)
            
        game_info = game_data.get('game_info', {})
        plays = game_data.get('plays', [])
        
        # Add game context to each play
        for play in plays:
            play['game_id'] = game_info.get('game_id')
            play['game_week'] = game_info.get('week')
            play['game_date'] = game_info.get('date')
            play['home_team'] = game_info.get('home_team')
            play['away_team'] = game_info.get('away_team')
            play['is_conference'] = game_info.get('conference', False)
            play['is_home'] = (play.get('offense', '').lower() == team_name.lower())
            
            # Determine opponent
            if play['is_home']:
                play['opponent'] = game_info.get('away_team', 'Unknown')
            else:
                play['opponent'] = game_info.get('home_team', 'Unknown')
        
        games.append({
            'game_info': game_info,
            'plays': plays,
            'file_name': json_file.name
        })
        all_plays.extend(plays)
    
    # Sort games by week
    games.sort(key=lambda x: x['game_info'].get('week', 0))
    
    return {
        'team_name': team_name,
        'games': games,
        'all_plays': all_plays,
        'total_games': len(games),
        'total_plays': len(all_plays)
    }


def filter_plays(plays: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """
    Filter plays based on criteria
    
    Args:
        plays: List of play dictionaries
        filters: Dictionary with filter criteria:
            - game_ids: List of game IDs to include
            - weeks: List of weeks to include
            - opponents: List of opponents to include
            - periods: List of periods to include
            - conference_only: Boolean for conference games only
            - non_conference_only: Boolean for non-conference games only
            - last_3_games: Boolean for last 3 games only
            
    Returns:
        Filtered list of plays
    """
    filtered = plays
    
    # Filter by game IDs
    if filters.get('game_ids'):
        filtered = [p for p in filtered if p.get('game_id') in filters['game_ids']]
    
    # Filter by weeks
    if filters.get('weeks'):
        filtered = [p for p in filtered if p.get('game_week') in filters['weeks']]
    
    # Filter by opponents
    if filters.get('opponents'):
        filtered = [p for p in filtered if p.get('opponent') in filters['opponents']]
    
    # Filter by periods
    if filters.get('periods'):
        filtered = [p for p in filtered if p.get('period') in filters['periods']]
    
    # Filter by conference/non-conference
    if filters.get('conference_only'):
        filtered = [p for p in filtered if p.get('is_conference') == True]
    elif filters.get('non_conference_only'):
        filtered = [p for p in filtered if p.get('is_conference') == False]
    
    # Filter by last 3 games
    if filters.get('last_3_games'):
        # Get unique games sorted by week
        games = sorted(set(p.get('game_id') for p in plays), 
                      key=lambda gid: next((p for p in plays if p.get('game_id') == gid), {}).get('game_week', 0))
        last_3_game_ids = games[-3:] if len(games) >= 3 else games
        filtered = [p for p in filtered if p.get('game_id') in last_3_game_ids]
    
    return filtered


def get_game_list(team_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get list of games with metadata for filtering
    
    Returns:
        List of game dictionaries with id, week, opponent, date, etc.
    """
    games = []
    for game in team_data['games']:
        game_info = game['game_info']
        games.append({
            'game_id': game_info.get('game_id'),
            'week': game_info.get('week'),
            'home_team': game_info.get('home_team'),
            'away_team': game_info.get('away_team'),
            'date': game_info.get('date'),
            'conference': game_info.get('conference', False),
            'opponent': game_info.get('away_team') if team_data['team_name'] == game_info.get('home_team') else game_info.get('home_team')
        })
    return games

