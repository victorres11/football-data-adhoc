#!/usr/bin/env python3
"""
Analyze penalties
"""

import re
from typing import Dict, List, Any
from collections import defaultdict, Counter


def analyze_penalties(plays: List[Dict], team_name: str) -> Dict[str, Any]:
    """
    Analyze penalties
    
    Args:
        plays: List of play dictionaries
        team_name: Name of the team
        
    Returns:
        Dictionary with analysis results
    """
    # Filter to plays with penalties committed by the team
    # Include penalties that are accepted OR have null decision but text indicates enforced
    penalty_plays = []
    team_upper = team_name.upper()
    for p in plays:
        if p.get('penalty_type') is not None:
            decision = p.get('penalty_decision')
            play_text = p.get('play_text', '')
            play_text_upper = play_text.upper()
            
            # Exclude offsetting penalties from the start
            is_offsetting = ('OFFSETTING' in play_text_upper or 
                           'OFFSETTING' in (p.get('penalty_type', '') or '').upper())
            if is_offsetting:
                continue
            
            # Include all penalties (accepted and declined) in the analysis
            # We'll filter by decision later when counting yards
            is_accepted = (decision == 'accepted' or 
                          (decision is None and 'ENFORCED' in play_text_upper))
            
            # Check if this team actually committed the penalty by looking at play text
            # Look for explicit team penalty markers
            team_committed = False
            
            # Check for explicit team penalty markers (full name and common abbreviations)
            team_abbrevs = {
                'WASHINGTON': ['WASH', 'WAS', 'UW'],
                'UCLA': ['UCLA'],
                'IOWA': ['IOWA', 'IA'],
                'USC': ['USC', 'TROJAN'],
                'WISCONSIN': ['WIS', 'WISC', 'UW'],
                'NORTHWESTERN': ['NU', 'NW'],
                'MICHIGAN': ['MICH', 'UM', 'UOM'],
                'MICHIGAN STATE': ['MSU', 'MICHIGAN STATE'],
                'ILLINOIS': ['ILL', 'ILLINOIS'],
                'PENN STATE': ['PSU', 'PENN STATE'],
                'OHIO STATE': ['OSU', 'OHIO STATE'],
                'INDIANA': ['IND', 'IU'],
                'PURDUE': ['PUR', 'PURDUE'],
                'RUTGERS': ['RUT', 'RUTGERS'],
                'MARYLAND': ['MD', 'MARYLAND'],
                'MINNESOTA': ['MINN', 'MINNESOTA'],
                'NEBRASKA': ['NEB', 'NEBRASKA'],
                'OREGON': ['ORE', 'OREGON'],
                'BALL STATE': ['BSU', 'BALL STATE']
            }
            
            # Check for full team name
            if (f'{team_upper} PENALTY' in play_text_upper or 
                f'PENALTY {team_upper}' in play_text_upper):
                team_committed = True
            # Check for team abbreviations
            elif team_upper in team_abbrevs:
                for abbrev in team_abbrevs[team_upper]:
                    if f'PENALTY {abbrev}' in play_text_upper or f'{abbrev} PENALTY' in play_text_upper:
                        team_committed = True
                        break
            # Special case for USC
            if team_name == 'USC' and ('TROJAN PENALTY' in play_text_upper or 'PENALTY TROJAN' in play_text_upper):
                team_committed = True
            
            # If we haven't found an explicit team marker, try to infer from penalty type and team position
            offense_team = (p.get('offense') or '').upper()
            defense_team = (p.get('defense') or '').upper()
            if not team_committed and (offense_team == team_upper or defense_team == team_upper):
                # Check if it's an offensive penalty and team is on offense, or defensive penalty and team is on defense
                penalty_type = p.get('penalty_type', '').upper()
                play_classification = p.get('play_classification', '').lower()
                offensive_penalties = ['FALSE START', 'DELAY OF GAME', 'ILLEGAL FORMATION', 'OFFENSIVE HOLDING', 'HOLDING', 'INTENTIONAL GROUNDING', 'ILLEGAL SNAP', 'INELIGIBLE DOWNFIELD']
                defensive_penalties = ['PASS INTERFERENCE', 'DEFENSIVE HOLDING', 'OFFSIDE', 'ROUGHING', 'UNNECESSARY ROUGHNESS', 'SIDELINE']
                special_teams_penalties = ['ILLEGAL BLOCK', 'ILLEGAL BLOCK IN BACK', 'ILLEGAL BLOCK ABOVE WAIST', 'KICK CATCHING INTERFERENCE', 'ROUGHING THE KICKER', 'ROUGHING THE PUNTER', 'RUNNING INTO THE KICKER']
                # Penalties that can be committed by either offense or defense
                either_side_penalties = ['UNSPORTSMANLIKE', 'PERSONAL FOUL']
                
                # Check for opponent penalty markers - check for explicit markers in full play text
                # This prevents false exclusions when opponent abbreviations appear in yard markers (e.g., "WASH37")
                is_opponent_penalty = False
                for opp_team, abbrevs in team_abbrevs.items():
                    if opp_team != team_upper:  # Skip the team we're analyzing
                        # Check full team name - must be explicit penalty marker
                        if f'{opp_team} PENALTY' in play_text_upper or f'PENALTY {opp_team}' in play_text_upper:
                            is_opponent_penalty = True
                            break
                        # Check abbreviations - must be explicit penalty marker
                        for abbrev in abbrevs:
                            if f'{abbrev} PENALTY' in play_text_upper or f'PENALTY {abbrev}' in play_text_upper:
                                is_opponent_penalty = True
                                break
                        if is_opponent_penalty:
                            break
                
                # Also check the hardcoded list for backwards compatibility
                # Only check for explicit penalty markers, not just team names in text
                if not is_opponent_penalty:
                    opponent_markers = ['MSU PENALTY', 'MISSOURI STATE PENALTY', 'GS PENALTY', 'GEORGIA SOUTHERN PENALTY', 
                                       'MICHIGAN STATE PENALTY', 'ILL PENALTY', 'ILLINOIS PENALTY',
                                       'UM PENALTY', 'UOM PENALTY', 'MICHIGAN PENALTY', 'IRISH PENALTY', 'NOTRE DAME PENALTY', 'ND PENALTY',
                                       'NEB PENALTY', 'NEBRASKA PENALTY', 'NU PENALTY', 'NORTHWESTERN PENALTY',
                                       'PENALTY WASH', 'WASH PENALTY', 'PENALTY WASHINGTON', 'WASHINGTON PENALTY',
                                       'PENALTY BALL', 'BALL PENALTY', 'PENALTY BSU', 'BSU PENALTY', 'BALL STATE PENALTY',
                                       'PENALTY USC', 'USC PENALTY',
                                       'PENALTY RUTGERS', 'RUTGERS PENALTY', 'PENALTY OSU', 'OSU PENALTY', 'OHIO STATE PENALTY',
                                       'PENALTY SIU', 'SIU PENALTY', 'SOUTHERN ILLINOIS PENALTY']
                    is_opponent_penalty = any(marker in play_text_upper for marker in opponent_markers)
                
                if not is_opponent_penalty:
                    # Check for special teams penalties (can be on either offense or defense depending on play type)
                    if any(st_penalty in penalty_type for st_penalty in special_teams_penalties):
                        # For special teams penalties, if team is on offense or defense, it's their penalty
                        # (e.g., illegal block on punt return = defense team's penalty)
                        if p.get('offense', '').upper() == team_upper or p.get('defense', '').upper() == team_upper:
                            team_committed = True
                    # Check for penalties that can be on either side (unsportsmanlike, personal foul)
                    elif any(either_penalty in penalty_type for either_penalty in either_side_penalties):
                        # For these penalties, if team is on offense or defense, it's their penalty
                        if p.get('offense', '').upper() == team_upper or p.get('defense', '').upper() == team_upper:
                            team_committed = True
                    # Infer based on penalty type and which side team is on
                    elif p.get('offense', '').upper() == team_upper and any(p in penalty_type for p in offensive_penalties):
                        team_committed = True
                    elif p.get('defense', '').upper() == team_upper and any(p in penalty_type for p in defensive_penalties):
                        team_committed = True
            
            if team_committed:
                penalty_plays.append(p)
    
    # Group by game
    game_stats = defaultdict(lambda: {'count': 0, 'accepted': 0, 'declined': 0, 'yards': 0, 'plays': []})
    
    # Count by type and decision
    penalty_types = Counter()
    penalty_decisions = Counter()
    total_penalty_yards = 0
    
    for play in penalty_plays:
        game_id = play.get('game_id')
        penalty_type = play.get('penalty_type', 'Unknown')
        penalty_category = play.get('penalty_category')  # For holding penalties
        decision = play.get('penalty_decision', 'Unknown')
        play_text = play.get('play_text', '')
        
        # Use penalty_category for holding penalties, otherwise use penalty_type
        # This breaks out holding into: offensive_holding, defensive_holding, special_teams_holding
        if penalty_category and penalty_category in ['offensive_holding', 'defensive_holding', 'special_teams_holding']:
            display_penalty_type = penalty_category.replace('_', ' ').title()  # "Offensive Holding", "Defensive Holding", "Special Teams Holding"
        else:
            display_penalty_type = penalty_type
        
        # Determine if penalty was accepted/enforced
        # Check decision field or if text says "enforced"
        # Exclude offsetting penalties
        # IMPORTANT: Also check play_text for "declined" even if decision field says "accepted"
        play_text_upper = play_text.upper()
        is_offsetting = ('OFFSETTING' in play_text_upper or 
                        'OFFSETTING' in (play.get('penalty_type', '') or '').upper())
        is_declined_in_text = 'DECLINED' in play_text_upper
        
        is_accepted_penalty = ((decision == 'accepted' or 
                               (decision is None and 'ENFORCED' in play_text_upper)) and
                               not is_offsetting and
                               not is_declined_in_text)
        
        # Extract penalty yards (only for accepted/enforced penalties)
        # Prefer penalty_yards field, fall back to yards_gained
        penalty_yards = 0
        if is_accepted_penalty:
            # First try penalty_yards field directly
            penalty_yards_field = play.get('penalty_yards')
            if penalty_yards_field is not None:
                penalty_yards = abs(penalty_yards_field)
            else:
                # Fall back to yards_gained field
                yards_gained = play.get('yards_gained', 0)
                # Use absolute value since yards_gained might be negative
                # Penalties are always negative yardage, so we want the absolute value
                penalty_yards = abs(yards_gained) if yards_gained is not None else 0
            total_penalty_yards += penalty_yards
            game_stats[game_id]['yards'] += penalty_yards
        
        game_stats[game_id]['count'] += 1
        if is_accepted_penalty:
            game_stats[game_id]['accepted'] += 1
            penalty_decisions['accepted'] = penalty_decisions.get('accepted', 0) + 1
        elif decision == 'declined' or is_declined_in_text:
            game_stats[game_id]['declined'] += 1
            penalty_decisions['declined'] = penalty_decisions.get('declined', 0) + 1
        else:
            # Other decision types (offsetting, etc.)
            decision_key = decision if decision else 'unknown'
            penalty_decisions[decision_key] = penalty_decisions.get(decision_key, 0) + 1
        
        penalty_types[display_penalty_type] += 1
        
        # Determine which team committed the penalty
        offense_team = play.get('offense', '')
        defense_team = play.get('defense', '')
        team_committed = offense_team if play.get('offense', '').lower() == team_name.lower() else defense_team
        
        # Extract yard line
        yard_line = play.get('yard_line', '')
        yards_to_goal = play.get('yards_to_goal', '')
        if yard_line and yard_line != 0:
            # Convert to signed format (+ for opponent territory, - for own territory)
            if yards_to_goal and yards_to_goal <= 50:
                yard_line_display = f"+{yards_to_goal}" if yards_to_goal <= 50 else f"-{100 - yards_to_goal}"
            else:
                yard_line_display = str(yard_line)
        else:
            yard_line_display = ''
        
        # Get down and distance
        down = play.get('down', '')
        distance = play.get('distance', '')
        down_distance = f"{down} & {distance}" if down and distance else ''
        
        # Get score if available
        offense_score = play.get('offenseScore', 0)
        defense_score = play.get('defenseScore', 0)
        score_display = f"{offense_score}-{defense_score}" if offense_score is not None and defense_score is not None else ''
        
        game_stats[game_id]['plays'].append({
            'game_id': play.get('game_id'),
            'game_week': play.get('game_week'),
            'opponent': play.get('opponent'),
            'period': play.get('period'),
            'clock': play.get('clock', ''),
            'penalty_type': display_penalty_type,  # Use the categorized type
            'penalty_decision': decision,
            'penalty_yards': penalty_yards,
            'yards_gained': play.get('yards_gained', 0),  # Include for extraction
            'is_offense': play.get('offense', '').lower() == team_name.lower(),
            'team_committed': team_committed,
            'down': play.get('down', ''),  # Include down field
            'distance': distance,
            'down_distance': down_distance,
            'yard_line': yard_line_display,
            'score': score_display,
            'offense': play.get('offense', ''),  # Include for table row highlighting
            'play_text': play.get('play_text', '')
        })
    
    total_penalties = len(penalty_plays)
    accepted = penalty_decisions.get('accepted', 0)
    declined = penalty_decisions.get('declined', 0)
    
    unique_games = len(game_stats)
    # Calculate avg_per_game based on accepted penalties instead of total
    avg_per_game = accepted / unique_games if unique_games > 0 else 0
    
    # Last 3 games
    sorted_games = sorted(game_stats.keys(), key=lambda gid: next(
        (p.get('game_week', 0) for p in plays if p.get('game_id') == gid), 0))
    last_3_games = sorted_games[-3:] if len(sorted_games) >= 3 else sorted_games
    
    last_3_count = sum(game_stats[gid]['count'] for gid in last_3_games)
    last_3_accepted = sum(game_stats[gid]['accepted'] for gid in last_3_games)
    last_3_declined = sum(game_stats[gid]['declined'] for gid in last_3_games)
    last_3_yards = sum(game_stats[gid]['yards'] for gid in last_3_games)
    
    # Flatten all plays for table
    all_plays_flat = []
    for game_id, stats in game_stats.items():
        all_plays_flat.extend(stats['plays'])
    
    return {
        'total_penalties': total_penalties,
        'accepted': accepted,
        'declined': declined,
        'total_penalty_yards': total_penalty_yards,
        'avg_per_game': avg_per_game,
        'penalty_types': dict(penalty_types),
        'penalty_decisions': dict(penalty_decisions),
        'last_3_games': {
            'total': last_3_count,
            'accepted': last_3_accepted,
            'declined': last_3_declined,
            'yards': last_3_yards,
            'games': last_3_games
        },
        'plays': all_plays_flat,
        'total_games': unique_games,
        'game_stats': dict(game_stats)
    }

