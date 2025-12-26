#!/usr/bin/env python3
"""
Load and parse advanced play-by-play data from JSON files
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def is_middle_eight(period: int, clock: str) -> bool:
    """
    Check if a play is in the "middle 8" (4 min before/after halftime).

    Args:
        period: Quarter number (1-4)
        clock: Clock string like "4:30" or "15:00"

    Returns:
        True if play is in middle 8
    """
    if not clock:
        return False

    # Parse clock string to get minutes and seconds
    match = re.match(r'^(\d+):(\d+)$', str(clock))
    if not match:
        return False

    minutes = int(match.group(1))
    seconds = int(match.group(2))

    # Period 2: Final 4 minutes of first half (clock <= 4:00)
    # 4:00 or less remaining means minutes < 4, or minutes == 4 and seconds == 0
    if period == 2 and (minutes < 4 or (minutes == 4 and seconds == 0)):
        return True

    # Period 3: First 4 minutes of second half (clock >= 11:00)
    # Clock starts at 15:00, so first 4 minutes = 15:00 down to 11:00
    if period == 3 and minutes >= 11:
        return True

    return False


def calculate_drive_started_after_turnover(plays: List[Dict]) -> List[Dict]:
    """
    Calculate drive_started_after_turnover field for PDF data.

    For PDF data that lacks this field, we calculate it by:
    1. Finding all turnovers (turnover == True, excluding turnover on downs)
    2. Marking all plays in the next drive as starting after a turnover

    Args:
        plays: List of play dictionaries

    Returns:
        List of plays with drive_started_after_turnover field added
    """
    from collections import defaultdict

    # Group plays by game (using game_week for PDF data)
    games = defaultdict(list)
    for play in plays:
        game_key = play.get('game_id') or f"week_{play.get('game_week', 0)}"
        games[game_key].append(play)

    # For each game, find turnovers and mark subsequent drives
    for game_key, game_plays in games.items():
        # Find all turnovers (excluding turnovers on downs)
        turnovers = []
        for p in game_plays:
            if p.get('turnover') == True:
                turnover_type = (p.get('turnover_type') or '').lower()
                if turnover_type != 'downs':
                    turnovers.append(p)

        # Get the drive numbers that started after turnovers
        drives_after_turnover = set()
        for turnover in turnovers:
            turnover_drive = turnover.get('drive_number')
            if turnover_drive is not None:
                # The next drive started after this turnover
                drives_after_turnover.add(turnover_drive + 1)

        # Mark plays in those drives
        for play in game_plays:
            play_drive = play.get('drive_number')
            if play_drive in drives_after_turnover:
                play['drive_started_after_turnover'] = True
            elif 'drive_started_after_turnover' not in play:
                play['drive_started_after_turnover'] = False

    return plays


def deduplicate_plays(plays: List[Dict]) -> List[Dict]:
    """
    Remove duplicate plays based on key identifying fields.

    Duplicates can occur in CFBD data where the same play is recorded twice
    with different IDs. We deduplicate by matching on:
    - game_id, period, clock, down, distance, drive_number, and play_text (first 100 chars)

    Args:
        plays: List of play dictionaries

    Returns:
        List of unique plays (first occurrence kept)
    """
    seen = set()
    unique_plays = []
    duplicates_removed = 0

    for play in plays:
        # Create a key from identifying fields
        # Include drive_number to differentiate kickoffs with same result (e.g., touchbacks)
        key = (
            play.get('game_id'),
            play.get('period'),
            str(play.get('clock', '')),
            play.get('down'),
            play.get('distance'),
            play.get('drive_number'),
            (play.get('play_text') or '')[:100]  # First 100 chars of play text
        )

        if key not in seen:
            seen.add(key)
            unique_plays.append(play)
        else:
            duplicates_removed += 1

    if duplicates_removed > 0:
        print(f"  Removed {duplicates_removed} duplicate play(s)")

    return unique_plays


def load_team_data(team_name: str, data_dir: str = "advanced_reports_yogi",
                   pdf_only: bool = False) -> Dict[str, Any]:
    """
    Load all game data for a given team

    Args:
        team_name: 'Washington' or 'Wisconsin'
        data_dir: Base directory containing team folders
        pdf_only: If True, only load files ending in '_PDF.json'

    Returns:
        Dictionary with game data and metadata
    """
    # Normalize team name for folder matching (lowercase, replace spaces/& with underscores)
    # Handle "William & Mary" -> "william_mary" (remove & and spaces, then replace with single underscore)
    normalized_name = team_name.lower().replace(" & ", "_").replace(" &", "_").replace("& ", "_").replace("&", "").replace(" ", "_").replace("-", "_")
    # Remove any double underscores
    while "__" in normalized_name:
        normalized_name = normalized_name.replace("__", "_")
    normalized_name = normalized_name.strip("_")
    team_folder = f"{normalized_name}_play_by_play"
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
    
    # Load JSON files (optionally filter for PDF-only sources)
    all_json_files = sorted(team_path.glob("*.json"))
    if pdf_only:
        # Only load files matching game_week*_PDF.json pattern (pure PDF without embedded game_ids)
        # This excludes files like game_401628333_*_PDF.json which have game_ids from filenames
        import re
        json_files = [f for f in all_json_files
                      if f.name.endswith('_PDF.json') and re.match(r'^game_week\d+_', f.name)]
    else:
        json_files = all_json_files
    
    for json_file in json_files:
        with open(json_file, 'r') as f:
            game_data = json.load(f)
            
        game_info = game_data.get('game_info', {})
        plays = game_data.get('plays', [])
        
        # Add game context to each play
        home_team = game_info.get('home_team', '')
        away_team = game_info.get('away_team', '')
        team_is_home = (team_name.lower() == home_team.lower())
        
        for play in plays:
            play['game_id'] = game_info.get('game_id')
            play['game_week'] = game_info.get('week')
            play['game_date'] = game_info.get('date')
            play['home_team'] = home_team
            play['away_team'] = away_team
            play['is_conference'] = game_info.get('conference', False)
            play['is_home'] = team_is_home
            
            # Determine opponent and Power 4 status
            # Opponent is always the other team, regardless of offense/defense
            if team_is_home:
                play['opponent'] = away_team if away_team else 'Unknown'
                # If team is home, opponent is away - check away_power4
                play['is_power4_opponent'] = game_info.get('away_power4', False)
            else:
                play['opponent'] = home_team if home_team else 'Unknown'
                # If team is away, opponent is home - check home_power4
                play['is_power4_opponent'] = game_info.get('home_power4', False)

            # Add middle_eight flag if not already present
            if 'middle_eight' not in play:
                play['middle_eight'] = is_middle_eight(
                    play.get('period', 0),
                    play.get('clock', '')
                )

        games.append({
            'game_info': game_info,
            'plays': plays,
            'file_name': json_file.name
        })
        all_plays.extend(plays)
    
    # Sort games by week
    games.sort(key=lambda x: x['game_info'].get('week', 0))

    # Deduplicate plays (CFBD data sometimes has duplicate entries)
    all_plays = deduplicate_plays(all_plays)

    # Calculate drive_started_after_turnover for PDF data that lacks this field
    all_plays = calculate_drive_started_after_turnover(all_plays)

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
    
    # Filter by conference/non-conference/power4
    if filters.get('conference_only'):
        filtered = [p for p in filtered if p.get('is_conference') == True]
    elif filters.get('non_conference_only'):
        filtered = [p for p in filtered if p.get('is_conference') == False]
    elif filters.get('power4_only'):
        filtered = [p for p in filtered if p.get('is_power4_opponent') == True]
    
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
        is_home = team_data['team_name'] == game_info.get('home_team')
        # Determine if opponent is Power 4
        if is_home:
            is_power4_opponent = game_info.get('away_power4', False)
        else:
            is_power4_opponent = game_info.get('home_power4', False)
        
        games.append({
            'game_id': game_info.get('game_id'),
            'week': game_info.get('week'),
            'home_team': game_info.get('home_team'),
            'away_team': game_info.get('away_team'),
            'date': game_info.get('date'),
            'conference': game_info.get('conference', False),
            'opponent': game_info.get('away_team') if is_home else game_info.get('home_team'),
            'is_power4_opponent': is_power4_opponent
        })
    return games

