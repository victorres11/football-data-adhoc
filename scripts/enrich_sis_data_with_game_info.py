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
        team_name: 'Washington' or 'Wisconsin' or 'William & Mary'
        data_dir: Directory containing play-by-play data
        
    Returns:
        List of game dictionaries with metadata
    """
    games = []
    # Normalize team name for folder matching (same as load_advanced_pbp_data.py)
    normalized_name = team_name.lower().replace(" & ", "_").replace(" &", "_").replace("& ", "_").replace("&", "").replace(" ", "_").replace("-", "_")
    # Remove any double underscores
    while "__" in normalized_name:
        normalized_name = normalized_name.replace("__", "_")
    normalized_name = normalized_name.strip("_")
    team_folder = data_dir / f"{normalized_name}_play_by_play"
    
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


def enrich_sis_data(sis_file_path: str, data_dir: str = "advanced_reports_yogi", 
                    team1_name: str = None, team2_name: str = None) -> None:
    """
    Enrich SIS data JSON with game metadata for filtering.
    
    Args:
        sis_file_path: Path to SIS data JSON file
        data_dir: Directory containing play-by-play data
        team1_name: Name of first team (default: auto-detect from SIS data)
        team2_name: Name of second team (default: auto-detect from SIS data)
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
    
    # Auto-detect team names from SIS data if not provided
    task_9 = sis_data.get('data', {}).get('task_9', {})
    task_4 = sis_data.get('data', {}).get('task_4', {})
    
    if not team1_name or not team2_name:
        # Try to get from task_9
        team_keys = list(task_9.keys()) if task_9 else []
        if not team_keys and task_4:
            team_keys = list(task_4.keys())
        
        if len(team_keys) >= 2:
            team1_name = team1_name or team_keys[0].title()
            team2_name = team2_name or team_keys[1].title()
        else:
            # Fallback to Washington/Wisconsin
            team1_name = team1_name or "Washington"
            team2_name = team2_name or "Wisconsin"
    
    print(f"Detected teams: {team1_name} and {team2_name}")
    
    # Load game data for both teams
    print(f"Loading game data for {team1_name}...")
    team1_games = load_game_data(team1_name, data_dir)
    print(f"  Found {len(team1_games)} games")
    
    print(f"Loading game data for {team2_name}...")
    team2_games = load_game_data(team2_name, data_dir)
    print(f"  Found {len(team2_games)} games")
    
    # Create lookup dictionaries: (week, opponent_lower) -> game_info
    team1_lookup = {}
    for game in team1_games:
        key = (game['week'], game['opponent'].lower())
        team1_lookup[key] = game
    
    team2_lookup = {}
    for game in team2_games:
        key = (game['week'], game['opponent'].lower())
        team2_lookup[key] = game
    
    # Normalize team names for data keys (lowercase)
    team1_key = team1_name.lower()
    team2_key = team2_name.lower()
    
    # Enrich task_9 data (situational receiving)
    if task_9:
        # Enrich team1 data
        if team1_key in task_9:
            print(f"\nEnriching {team1_name} task_9 data...")
            team1_data = task_9[team1_key]
            
            for situation in ['3rd_down', 'redzone']:
                if situation not in team1_data:
                    continue
                
                # Check for by_week structure (old format)
                by_week = team1_data[situation].get('by_week', {})
                # Check for by_game structure (new format)
                by_game = team1_data[situation].get('by_game', {})
                
                enriched_count = 0
                
                # Handle by_week structure
                if by_week:
                    for week_str, week_data in by_week.items():
                        week = int(week_str)
                        opponent = week_data.get('opponent', '')
                        key = (week, opponent.lower())
                        
                        if key in team1_lookup:
                            game_info = team1_lookup[key]
                            week_data['game_id'] = game_info['game_id']
                            week_data['is_conference'] = game_info['is_conference']
                            # All Big Ten conference games are Power 4
                            week_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                            enriched_count += 1
                            print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                                  f"conference={game_info['is_conference']}, power4={week_data['is_power4_opponent']}")
                        else:
                            print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                
                # Handle by_game structure (similar to task_4)
                if by_game:
                    import re
                    for game_key, game_data in by_game.items():
                        # Try to get week and opponent from game_data first
                        week = game_data.get('week')
                        opponent = game_data.get('opponent', '')
                        
                        # If not found, try to extract from game_key (format: "Week{week}_{opponent}")
                        if not week or not opponent:
                            match = re.match(r'Week(\d+)_(.+)', game_key)
                            if match:
                                week = int(match.group(1))
                                opponent = match.group(2)
                        
                        # If still not found, try to get from first player in players array
                        if not week or not opponent:
                            players = game_data.get('players', [])
                            if players and len(players) > 0:
                                week = week or players[0].get('week')
                                opponent = opponent or players[0].get('opp', '') or players[0].get('opponent', '')
                        
                        if week and opponent:
                            key = (week, opponent.lower())
                            if key in team1_lookup:
                                game_info = team1_lookup[key]
                                game_data['week'] = week  # Ensure week is set
                                game_data['opponent'] = opponent  # Ensure opponent is set
                                game_data['game_id'] = game_info['game_id']
                                game_data['is_conference'] = game_info['is_conference']
                                # All Big Ten conference games are Power 4
                                game_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                                enriched_count += 1
                                print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                                      f"conference={game_info['is_conference']}, power4={game_info['is_power4_opponent']}")
                            else:
                                print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                        else:
                            print(f"  Warning: Could not extract week/opponent from game_key: {game_key}")
                
                total_entries = len(by_week) if by_week else len(by_game) if by_game else 0
                print(f"  {situation}: Enriched {enriched_count} of {total_entries} entries")
        
        # Enrich team2 data
        if team2_key in task_9:
            print(f"\nEnriching {team2_name} task_9 data...")
            team2_data = task_9[team2_key]
            
            for situation in ['3rd_down', 'redzone']:
                if situation not in team2_data:
                    continue
                
                # Check for by_week structure (old format)
                by_week = team2_data[situation].get('by_week', {})
                # Check for by_game structure (new format)
                by_game = team2_data[situation].get('by_game', {})
                
                enriched_count = 0
                
                # Handle by_week structure
                if by_week:
                    for week_str, week_data in by_week.items():
                        week = int(week_str)
                        opponent = week_data.get('opponent', '')
                        key = (week, opponent.lower())
                        
                        if key in team2_lookup:
                            game_info = team2_lookup[key]
                            week_data['game_id'] = game_info['game_id']
                            week_data['is_conference'] = game_info['is_conference']
                            # All Big Ten conference games are Power 4
                            week_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                            enriched_count += 1
                            print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                                  f"conference={game_info['is_conference']}, power4={week_data['is_power4_opponent']}")
                        else:
                            print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                
                # Handle by_game structure (similar to task_4)
                if by_game:
                    import re
                    for game_key, game_data in by_game.items():
                        # Try to get week and opponent from game_data first
                        week = game_data.get('week')
                        opponent = game_data.get('opponent', '')
                        
                        # If not found, try to extract from game_key (format: "Week{week}_{opponent}")
                        if not week or not opponent:
                            match = re.match(r'Week(\d+)_(.+)', game_key)
                            if match:
                                week = int(match.group(1))
                                opponent = match.group(2)
                        
                        # If still not found, try to get from first player in players array
                        if not week or not opponent:
                            players = game_data.get('players', [])
                            if players and len(players) > 0:
                                week = week or players[0].get('week')
                                opponent = opponent or players[0].get('opp', '') or players[0].get('opponent', '')
                        
                        if week and opponent:
                            key = (week, opponent.lower())
                            if key in team2_lookup:
                                game_info = team2_lookup[key]
                                game_data['week'] = week  # Ensure week is set
                                game_data['opponent'] = opponent  # Ensure opponent is set
                                game_data['game_id'] = game_info['game_id']
                                game_data['is_conference'] = game_info['is_conference']
                                # All Big Ten conference games are Power 4
                                game_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                                enriched_count += 1
                                print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                                      f"conference={game_info['is_conference']}, power4={game_info['is_power4_opponent']}")
                            else:
                                print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                        else:
                            print(f"  Warning: Could not extract week/opponent from game_key: {game_key}")
                
                total_entries = len(by_week) if by_week else len(by_game) if by_game else 0
                print(f"  {situation}: Enriched {enriched_count} of {total_entries} entries")
    
    # Enrich task_4 data (deep targets) - receiving.by_game
    if task_4:
        # Enrich team1 receiving data
        if team1_key in task_4 and 'receiving' in task_4[team1_key] and 'by_game' in task_4[team1_key]['receiving']:
            print(f"\nEnriching {team1_name} task_4 receiving data...")
            by_game = task_4[team1_key]['receiving']['by_game']
            enriched_count = 0
            
            for game_key, game_data in by_game.items():
                # Try to get week and opponent from game_data first
                week = game_data.get('week')
                opponent = game_data.get('opponent', '')
                
                # If not found, try to extract from game_key (format: "Week{week}_{opponent}")
                if not week or not opponent:
                    # Parse game_key like "Week10_Michigan State"
                    import re
                    match = re.match(r'Week(\d+)_(.+)', game_key)
                    if match:
                        week = int(match.group(1))
                        opponent = match.group(2)
                
                # If still not found, try to get from first player in players array
                if not week or not opponent:
                    players = game_data.get('players', [])
                    if players and len(players) > 0:
                        week = week or players[0].get('week')
                        opponent = opponent or players[0].get('opp', '') or players[0].get('opponent', '')
                
                if week and opponent:
                    key = (week, opponent.lower())
                    if key in team1_lookup:
                        game_info = team1_lookup[key]
                        game_data['week'] = week  # Ensure week is set
                        game_data['opponent'] = opponent  # Ensure opponent is set
                        game_data['game_id'] = game_info['game_id']
                        game_data['is_conference'] = game_info['is_conference']
                        # All Big Ten conference games are Power 4
                        game_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                        enriched_count += 1
                        print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                              f"conference={game_info['is_conference']}, power4={game_data['is_power4_opponent']}")
                    else:
                        print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                else:
                    print(f"  Warning: Could not extract week/opponent from game_key: {game_key}")
            
            print(f"  receiving: Enriched {enriched_count} of {len(by_game)} games")
        
        # Enrich team2 receiving data
        if team2_key in task_4 and 'receiving' in task_4[team2_key] and 'by_game' in task_4[team2_key]['receiving']:
            print(f"\nEnriching {team2_name} task_4 receiving data...")
            by_game = task_4[team2_key]['receiving']['by_game']
            enriched_count = 0
            
            for game_key, game_data in by_game.items():
                # Try to get week and opponent from game_data first
                week = game_data.get('week')
                opponent = game_data.get('opponent', '')
                
                # If not found, try to extract from game_key (format: "Week{week}_{opponent}")
                if not week or not opponent:
                    # Parse game_key like "Week10_Michigan State"
                    import re
                    match = re.match(r'Week(\d+)_(.+)', game_key)
                    if match:
                        week = int(match.group(1))
                        opponent = match.group(2)
                
                # If still not found, try to get from first player in players array
                if not week or not opponent:
                    players = game_data.get('players', [])
                    if players and len(players) > 0:
                        week = week or players[0].get('week')
                        opponent = opponent or players[0].get('opp', '') or players[0].get('opponent', '')
                
                if week and opponent:
                    key = (week, opponent.lower())
                    if key in team2_lookup:
                        game_info = team2_lookup[key]
                        game_data['week'] = week  # Ensure week is set
                        game_data['opponent'] = opponent  # Ensure opponent is set
                        game_data['game_id'] = game_info['game_id']
                        game_data['is_conference'] = game_info['is_conference']
                        # All Big Ten conference games are Power 4
                        game_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                        enriched_count += 1
                        print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                              f"conference={game_info['is_conference']}, power4={game_data['is_power4_opponent']}")
                    else:
                        print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                else:
                    print(f"  Warning: Could not extract week/opponent from game_key: {game_key}")
            
            print(f"  receiving: Enriched {enriched_count} of {len(by_game)} games")
        
        # Enrich team1 passing data
        if team1_key in task_4 and 'passing' in task_4[team1_key] and 'by_game' in task_4[team1_key]['passing']:
            print(f"\nEnriching {team1_name} task_4 passing data...")
            by_game = task_4[team1_key]['passing']['by_game']
            enriched_count = 0
            
            for game_key, game_data in by_game.items():
                # Try to get week and opponent from game_data first
                week = game_data.get('week')
                opponent = game_data.get('opponent', '')
                
                # If not found, try to extract from game_key (format: "Week{week}_{opponent}")
                if not week or not opponent:
                    import re
                    match = re.match(r'Week(\d+)_(.+)', game_key)
                    if match:
                        week = int(match.group(1))
                        opponent = match.group(2)
                
                # If still not found, try to get from first player in players array
                if not week or not opponent:
                    players = game_data.get('players', [])
                    if players and len(players) > 0:
                        week = week or players[0].get('week')
                        opponent = opponent or players[0].get('opp', '') or players[0].get('opponent', '')
                
                if week and opponent:
                    key = (week, opponent.lower())
                    if key in team1_lookup:
                        game_info = team1_lookup[key]
                        game_data['week'] = week  # Ensure week is set
                        game_data['opponent'] = opponent  # Ensure opponent is set
                        game_data['game_id'] = game_info['game_id']
                        game_data['is_conference'] = game_info['is_conference']
                        # All Big Ten conference games are Power 4
                        game_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                        enriched_count += 1
                        print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                              f"conference={game_info['is_conference']}, power4={game_data['is_power4_opponent']}")
                    else:
                        print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                else:
                    print(f"  Warning: Could not extract week/opponent from game_key: {game_key}")
            
            print(f"  passing: Enriched {enriched_count} of {len(by_game)} games")
        
        # Enrich team2 passing data
        if team2_key in task_4 and 'passing' in task_4[team2_key] and 'by_game' in task_4[team2_key]['passing']:
            print(f"\nEnriching {team2_name} task_4 passing data...")
            by_game = task_4[team2_key]['passing']['by_game']
            enriched_count = 0
            
            for game_key, game_data in by_game.items():
                # Try to get week and opponent from game_data first
                week = game_data.get('week')
                opponent = game_data.get('opponent', '')
                
                # If not found, try to extract from game_key (format: "Week{week}_{opponent}")
                if not week or not opponent:
                    import re
                    match = re.match(r'Week(\d+)_(.+)', game_key)
                    if match:
                        week = int(match.group(1))
                        opponent = match.group(2)
                
                # If still not found, try to get from first player in players array
                if not week or not opponent:
                    players = game_data.get('players', [])
                    if players and len(players) > 0:
                        week = week or players[0].get('week')
                        opponent = opponent or players[0].get('opp', '') or players[0].get('opponent', '')
                
                if week and opponent:
                    key = (week, opponent.lower())
                    if key in team2_lookup:
                        game_info = team2_lookup[key]
                        game_data['week'] = week  # Ensure week is set
                        game_data['opponent'] = opponent  # Ensure opponent is set
                        game_data['game_id'] = game_info['game_id']
                        game_data['is_conference'] = game_info['is_conference']
                        # All Big Ten conference games are Power 4
                        game_data['is_power4_opponent'] = True if game_info['is_conference'] else game_info['is_power4_opponent']
                        enriched_count += 1
                        print(f"  Week {week} vs {opponent}: game_id={game_info['game_id']}, "
                              f"conference={game_info['is_conference']}, power4={game_data['is_power4_opponent']}")
                    else:
                        print(f"  Warning: Could not find game for Week {week} vs {opponent}")
                else:
                    print(f"  Warning: Could not extract week/opponent from game_key: {game_key}")
            
            print(f"  passing: Enriched {enriched_count} of {len(by_game)} games")
    
    # Save enriched data
    print(f"\nSaving enriched SIS data to {sis_path}...")
    with open(sis_path, 'w') as f:
        json.dump(sis_data, f, indent=2)
    
    print("✓ SIS data enrichment complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich SIS data with game metadata')
    parser.add_argument('--sis-file', type=str, 
                       default="advanced_reports_yogi/sis-data/washington_wisconsin_analysis_2025.json",
                       help='Path to SIS data JSON file')
    parser.add_argument('--data-dir', type=str, default="advanced_reports_yogi",
                       help='Directory containing play-by-play data')
    parser.add_argument('--team1', type=str, default=None,
                       help='Name of first team (auto-detected if not provided)')
    parser.add_argument('--team2', type=str, default=None,
                       help='Name of second team (auto-detected if not provided)')
    
    args = parser.parse_args()
    
    try:
        enrich_sis_data(args.sis_file, args.data_dir, args.team1, args.team2)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

