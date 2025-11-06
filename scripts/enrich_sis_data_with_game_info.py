#!/usr/bin/env python3
"""
Enrich SIS data JSON with game metadata for filtering support.

This script adds the following fields to each week entry in task_9 data:
- game_id: The game ID from play-by-play data
- is_conference: Whether the game was a conference game
- is_power4_opponent: Whether the opponent is a Power 4 team

This enables filtering of the Situational Receiving Analysis section.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import sys


def load_game_data(team_name: str, data_dir: str = "advanced_reports_yogi") -> List[Dict[str, Any]]:
    """
    Load game data from play-by-play JSON files to extract game metadata.
    
    Args:
        team_name: 'Washington' or 'Wisconsin'
        data_dir: Directory containing play-by-play data
        
    Returns:
        List of game dictionaries with metadata
    """
    games = []
    team_folder = data_dir / f"{team_name.lower()}_play_by_play"
    
    if not team_folder.exists():
        # Try parent directory
        team_folder = Path("..") / team_folder
        if not team_folder.exists():
            raise ValueError(f"Team folder not found: {team_folder}")
    
    for json_file in sorted(team_folder.glob("*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            game_info = data.get('game_info', {})
            if not game_info:
                continue
            
            # Determine if team is home
            home_team = game_info.get('home_team', '')
            away_team = game_info.get('away_team', '')
            team_is_home = (team_name.lower() == home_team.lower())
            
            # Determine opponent and Power 4 status
            if team_is_home:
                opponent = away_team if away_team else 'Unknown'
                is_power4_opponent = game_info.get('away_power4', False)
            else:
                opponent = home_team if home_team else 'Unknown'
                is_power4_opponent = game_info.get('home_power4', False)
            
            games.append({
                'game_id': game_info.get('game_id'),
                'week': game_info.get('week'),
                'opponent': opponent,
                'is_conference': game_info.get('conference', False),
                'is_power4_opponent': is_power4_opponent
            })
        except Exception as e:
            print(f"Warning: Could not load {json_file}: {e}")
            continue
    
    return games


def enrich_sis_data(sis_file_path: str, data_dir: str = "advanced_reports_yogi") -> None:
    """
    Enrich SIS data JSON with game metadata for filtering.
    
    Args:
        sis_file_path: Path to SIS data JSON file
        data_dir: Directory containing play-by-play data
    """
    data_dir = Path(data_dir)
    sis_path = Path(sis_file_path)
    
    if not sis_path.exists():
        # Try relative to current directory
        sis_path = data_dir / "sis-data" / sis_path.name
        if not sis_path.exists():
            raise ValueError(f"SIS data file not found: {sis_file_path}")
    
    # Load SIS data
    print(f"Loading SIS data from {sis_path}...")
    with open(sis_path, 'r') as f:
        sis_data = json.load(f)
    
    # Load game data for both teams
    print("Loading game data for Washington...")
    wash_games = load_game_data("Washington", data_dir)
    print(f"  Found {len(wash_games)} games")
    
    print("Loading game data for Wisconsin...")
    wisc_games = load_game_data("Wisconsin", data_dir)
    print(f"  Found {len(wisc_games)} games")
    
    # Create lookup dictionaries: (week, opponent_lower) -> game_info
    wash_lookup = {}
    for game in wash_games:
        key = (game['week'], game['opponent'].lower())
        wash_lookup[key] = game
    
    wisc_lookup = {}
    for game in wisc_games:
        key = (game['week'], game['opponent'].lower())
        wisc_lookup[key] = game
    
    # Get task_9 data
    task_9 = sis_data.get('data', {}).get('task_9', {})
    
    # Enrich Washington data
    if 'washington' in task_9:
        print("\nEnriching Washington data...")
        wash_data = task_9['washington']
        
        for situation in ['3rd_down', 'redzone']:
            if situation not in wash_data:
                continue
            
            by_week = wash_data[situation].get('by_week', {})
            enriched_count = 0
            
            for week_str, week_data in by_week.items():
                week = int(week_str)
                opponent = week_data.get('opponent', '')
                key = (week, opponent.lower())
                
                if key in wash_lookup:
                    game_info = wash_lookup[key]
                    week_data['game_id'] = game_info['game_id']
                    week_data['is_conference'] = game_info['is_conference']
                    week_data['is_power4_opponent'] = game_info['is_power4_opponent']
                    enriched_count += 1
                    print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                          f"conference={game_info['is_conference']}, power4={game_info['is_power4_opponent']}")
                else:
                    print(f"  Warning: Could not find game for Week {week} vs {opponent}")
            
            print(f"  {situation}: Enriched {enriched_count} of {len(by_week)} weeks")
    
    # Enrich Wisconsin data
    if 'wisconsin' in task_9:
        print("\nEnriching Wisconsin data...")
        wisc_data = task_9['wisconsin']
        
        for situation in ['3rd_down', 'redzone']:
            if situation not in wisc_data:
                continue
            
            by_week = wisc_data[situation].get('by_week', {})
            enriched_count = 0
            
            for week_str, week_data in by_week.items():
                week = int(week_str)
                opponent = week_data.get('opponent', '')
                key = (week, opponent.lower())
                
                if key in wisc_lookup:
                    game_info = wisc_lookup[key]
                    week_data['game_id'] = game_info['game_id']
                    week_data['is_conference'] = game_info['is_conference']
                    week_data['is_power4_opponent'] = game_info['is_power4_opponent']
                    enriched_count += 1
                    print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                          f"conference={game_info['is_conference']}, power4={game_info['is_power4_opponent']}")
                else:
                    print(f"  Warning: Could not find game for Week {week} vs {opponent}")
            
            print(f"  {situation}: Enriched {enriched_count} of {len(by_week)} weeks")
    
    # Save enriched data
    print(f"\nSaving enriched SIS data to {sis_path}...")
    with open(sis_path, 'w') as f:
        json.dump(sis_data, f, indent=2)
    
    print("✓ SIS data enrichment complete!")


if __name__ == "__main__":
    # Default path
    sis_file = "advanced_reports_yogi/sis-data/washington_wisconsin_analysis_2025.json"
    data_dir = "advanced_reports_yogi"
    
    # Allow override via command line
    if len(sys.argv) > 1:
        sis_file = sys.argv[1]
    if len(sys.argv) > 2:
        data_dir = sys.argv[2]
    
    try:
        enrich_sis_data(sis_file, data_dir)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

