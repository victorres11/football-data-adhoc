#!/usr/bin/env python3
"""
Analyze performance after turnovers

Turnover filtering:
- Only counts fumbles lost and interceptions thrown
- Excludes turnovers on downs
- Filters out plays with "NO PLAY" in the text
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
    # Find turnovers - only fumbles lost and interceptions thrown
    # Exclude turnovers on downs and plays with "NO PLAY" in text
    turnovers = []
    for p in plays:
        if p.get('turnover') == True:
            # Filter out plays with "NO PLAY" in the text
            play_text = p.get('play_text', '').upper()
            if 'NO PLAY' in play_text:
                continue
            
            # Check turnover_type field first - if it's "downs", exclude it
            # Post turnover analysis only includes fumbles lost and interceptions
            turnover_type_field = p.get('turnover_type', '').lower() if p.get('turnover_type') else ''
            if turnover_type_field == 'downs':
                # This is a turnover on downs, exclude from post turnover analysis
                continue
            
            # Include penalty plays if they have a valid turnover_type (interception or fumble)
            # Penalties can mark turnovers that occurred (e.g., interception then penalty called)
            # But only if turnover_type is explicitly set to interception or fumble
            play_type = p.get('play_type', '').upper()
            if 'PENALTY' in play_type:
                # Only include penalty if it has a valid turnover_type
                if turnover_type_field not in ['interception', 'fumble']:
                    continue
                # If it has a valid turnover_type, we'll include it below
            
            # Only count fumbles lost and interceptions thrown
            # Exclude turnovers on downs
            
            # Check if it's an interception (check both play_type and turnover_type)
            is_interception = ('INTERCEPTION' in play_type or 
                             turnover_type_field == 'interception')
            
            # Check if it's a fumble lost (check both play_type and turnover_type)
            # A fumble is "lost" if the defense recovered it (turnover occurred)
            is_fumble = ('FUMBLE' in play_type or 
                        turnover_type_field == 'fumble')
            
            # For fumbles, check if the offense recovered their own fumble
            is_fumble_lost = False
            if is_fumble:
                # Check play_type for "(Own)" indicator - but also verify in play_text
                # If "(OWN)" is in play_type, check play_text to see who actually recovered
                play_text_upper = (p.get('play_text') or '').upper()
                offense_team = (p.get('offense') or '').upper()
                defense_team = (p.get('defense') or '').upper()
                
                # Check if play_text indicates the defense recovered (turnover)
                # Look for patterns like "recovered by [defense team]" or "recovered by [defense player]"
                defense_recovered = False
                if defense_team and defense_team in play_text_upper:
                    # Check if it says "recovered by [defense team]" or similar
                    recovered_patterns = [
                        f'RECOVERED BY {defense_team}',
                        f'RECOVERED BY {defense_team[:3]}',  # Abbreviation
                    ]
                    for pattern in recovered_patterns:
                        if pattern in play_text_upper:
                            defense_recovered = True
                            break
                
                # If play_type says "(Own)" but play_text shows defense recovered, it's a turnover
                if '(OWN)' in play_type and not defense_recovered:
                    # Offense recovered their own fumble - NOT a turnover, exclude it
                    continue
                else:
                    # If the play is marked as a turnover and has fumble, it's a fumble lost
                    is_fumble_lost = True
            
            # Exclude turnovers on downs (additional check in case turnover_type wasn't set)
            is_turnover_on_downs = (
                'TURNOVER ON DOWNS' in play_type or
                'DOWNS' in play_type.upper()
            )
            
            # Only include interceptions and fumbles lost, exclude turnovers on downs
            if (is_interception or is_fumble_lost) and not is_turnover_on_downs:
                turnovers.append(p)
    
    # Find drives that started after turnovers
    post_turnover_plays = [
        p for p in plays
        if p.get('drive_started_after_turnover') == True
    ]
    
    # Group by drive_id to get unique drives that started after turnovers
    post_turnover_drives = {}
    for play in post_turnover_plays:
        drive_id = play.get('drive_id')
        if drive_id not in post_turnover_drives:
            post_turnover_drives[drive_id] = {
                'game_id': play.get('game_id'),
                'drive_number': play.get('drive_number', 0),
                'plays': []
            }
        post_turnover_drives[drive_id]['plays'].append(play)
    
    # Group by turnover event
    turnover_analysis = []
    
    # For each drive that started after a turnover, find the turnover that caused it
    for drive_id, drive_info in post_turnover_drives.items():
        game_id = drive_info['game_id']
        drive_number = drive_info['drive_number']
        drive_plays = drive_info['plays']
        
        # Find the turnover in the previous drive (or same drive if turnover ended the drive)
        # Look for turnovers in drive_number - 1 first, then same drive_number
        # If a drive has drive_started_after_turnover == True, the turnover should be in the PREVIOUS drive
        matching_turnover = None
        
        # First, try to find turnover in previous drive
        for turnover in turnovers:
            if (turnover.get('game_id') == game_id and 
                turnover.get('drive_number', 0) == drive_number - 1):
                matching_turnover = turnover
                break
        
        # Only check same drive if no previous drive turnover found AND the drive doesn't have
        # drive_started_after_turnover == True (which would indicate a data inconsistency)
        # If drive_started_after_turnover is True, we should only match to previous drive turnovers
        if matching_turnover is None:
            # Check if this drive has drive_started_after_turnover flag
            # If it does, we should skip it if no previous drive turnover found (data inconsistency)
            drive_has_flag = any(p.get('drive_started_after_turnover') == True for p in drive_plays)
            
            if not drive_has_flag:
                # Drive doesn't have the flag, so it's safe to check same drive
                # This handles cases where turnover ended the previous drive and started the next
                for turnover in turnovers:
                    if (turnover.get('game_id') == game_id and 
                        turnover.get('drive_number', 0) == drive_number):
                        matching_turnover = turnover
                        break
        
        # Check if the turnover play itself resulted in points (e.g., pick-6, fumble return TD)
        drive_points = 0
        drive_result = 'No Score'
        scoring_play_text = ''
        
        if matching_turnover is not None and matching_turnover.get('scoring') == True:
            # Check play_type first
            play_type = matching_turnover.get('play_type', '')
            play_text = matching_turnover.get('play_text', '').upper()
            
            # Check for touchdown in play_type or play_text (for pick-6, fumble return TD)
            if 'Touchdown' in play_type or 'TOUCHDOWN' in play_text:
                drive_points = 7
                drive_result = 'Touchdown'
                scoring_play_text = matching_turnover.get('play_text', '')[:150]
            elif 'Field Goal' in play_type:
                drive_points = 3
                drive_result = 'Field Goal'
                scoring_play_text = matching_turnover.get('play_text', '')[:150]
        
        # If turnover didn't score (or no matching turnover found), check the drive for scoring plays
        if drive_points == 0:
            for play in drive_plays:
                if play.get('scoring') == True:
                    # If scoring is True, check play_text to determine if it's a TD or FG
                    # (play_type might be "Pass Reception" or "Rush" even for touchdowns)
                    play_type = play.get('play_type', '')
                    play_text = play.get('play_text', '').upper()
                    
                    # Check for touchdown in play_type or play_text
                    if 'Touchdown' in play_type or 'TOUCHDOWN' in play_text:
                        drive_points = 7
                        drive_result = 'Touchdown'
                        scoring_play_text = play.get('play_text', '')[:150]
                        break  # Touchdown is highest priority
                    elif 'Field Goal' in play_type or 'FIELD GOAL' in play_text:
                        if drive_result == 'No Score':  # Only set if we haven't found a TD
                            drive_points = 3
                            drive_result = 'Field Goal'
                            scoring_play_text = play.get('play_text', '')[:150]
        
        # Determine if it's our turnover or opponent's turnover
        # If we found a matching turnover, use it to determine ownership
        # If not, check if it's a turnover on downs and skip if so
        if matching_turnover is not None:
            is_our_turnover = matching_turnover.get('offense', '').lower() == team_name.lower()
            
            # For muffed punts (punts with fumbles), check who's on offense after the recovery
            # The receiving team (defense on the punt) loses the fumble if the punting team recovers
            play_type_check = matching_turnover.get('play_type', '').upper()
            play_text_check = (matching_turnover.get('play_text') or '').upper()
            if 'PUNT' in play_type_check and ('FUMBLE' in play_text_check or 'FUMBLED' in play_text_check):
                # Find the next play to see who's on offense after the recovery
                next_play = None
                turnover_drive = matching_turnover.get('drive_number', 0)
                turnover_play_num = matching_turnover.get('play_number', 0)
                
                # Look for next play in same drive or next drive
                for play in plays:
                    if play.get('game_id') == matching_turnover.get('game_id'):
                        play_drive = play.get('drive_number', 0)
                        play_num = play.get('play_number', 0)
                        # Next drive, or same drive with higher play number
                        if (play_drive == turnover_drive + 1) or \
                           (play_drive == turnover_drive and play_num > turnover_play_num):
                            next_play = play
                            break
                
                if next_play:
                    # Who's on offense after the recovery?
                    recovering_team = next_play.get('offense', '').lower()
                    receiving_team = matching_turnover.get('defense', '').lower()  # Receiving team is defense on punt
                    
                    # If the recovering team is on offense, the receiving team lost the fumble
                    if recovering_team != receiving_team:
                        # Recovering team got the ball - receiving team lost the fumble
                        is_our_turnover = receiving_team == team_name.lower()
                    else:
                        # Receiving team recovered their own fumble - not a turnover (shouldn't happen)
                        # But if it does, use default logic
                        is_our_turnover = matching_turnover.get('offense', '').lower() == team_name.lower()
                else:
                    # Can't find next play, use original logic: receiving team (defense) lost the fumble
                    is_our_turnover = matching_turnover.get('defense', '').lower() == team_name.lower()
        else:
            # No matching turnover found - check if it's a turnover on downs
            # Look for turnovers in the previous drive OR same drive that are turnovers on downs
            prev_drive_turnovers = [p for p in plays 
                                   if p.get('game_id') == game_id 
                                   and (p.get('drive_number', 0) == drive_number - 1 or
                                        p.get('drive_number', 0) == drive_number)
                                   and p.get('turnover') == True]
            
            # Check if any of these are turnovers on downs
            is_turnover_on_downs = False
            for t in prev_drive_turnovers:
                turnover_type_field = (t.get('turnover_type') or '').lower()
                if turnover_type_field == 'downs':
                    is_turnover_on_downs = True
                    break
            
            # If it's a turnover on downs, skip this drive (only track fumbles/interceptions)
            if is_turnover_on_downs:
                continue
            
            # Not a turnover on downs, but no matching turnover found
            # Check if there are any turnovers at all in the previous or same drive
            # If there are no turnovers found, this is likely a data inconsistency
            # (drive_started_after_turnover is True but no actual turnover exists)
            # Skip these drives to avoid creating "details not found" entries
            if len(prev_drive_turnovers) == 0:
                continue
            
            # There are turnovers in the previous/same drive, but none matched
            # This could be because they were filtered out for other reasons
            # For now, skip these to avoid "details not found" entries
            continue
        
        # Determine turnover type
        if matching_turnover is not None:
            # Only interceptions and fumbles lost should be in the turnovers list
            # (turnovers on downs are filtered out earlier)
            play_type = matching_turnover.get('play_type', 'Unknown')
            turnover_type_field = (matching_turnover.get('turnover_type') or '').lower()
            
            # Check both play_type and turnover_type field
            if ('Interception' in play_type or 'interception' in play_type.lower() or 
                turnover_type_field == 'interception'):
                turnover_type = 'Interception'
            elif ('Fumble' in play_type or 'fumble' in play_type.lower() or 
                  turnover_type_field == 'fumble'):
                turnover_type = 'Fumble'
            else:
                # This shouldn't happen if filtering is correct, but handle edge case
                turnover_type = 'Unknown'
            turnover_text = matching_turnover.get('play_text', '')[:150]
        else:
            # No matching turnover found - use unknown type
            turnover_type = 'Unknown'
            turnover_text = 'Turnover (details not found)'
        
        # Combine turnover play and scoring play text
        if scoring_play_text:
            play_description = f"TO: {turnover_text} | Score: {scoring_play_text}"
        else:
            play_description = f"TO: {turnover_text}"
        
        # Get game info from drive plays if matching_turnover is not available
        if matching_turnover is not None:
            game_week = matching_turnover.get('game_week')
            opponent = matching_turnover.get('opponent')
            period = matching_turnover.get('period')
            clock = matching_turnover.get('clock', '')
        else:
            # Use info from first play in drive
            if drive_plays:
                game_week = drive_plays[0].get('game_week', 0)
                opponent = drive_plays[0].get('opponent', 'Unknown')
                period = drive_plays[0].get('period', 0)
                clock = drive_plays[0].get('clock', '')
            else:
                # Skip if no plays available
                continue
        
        turnover_analysis.append({
            'game_id': game_id,
            'game_week': game_week,
            'opponent': opponent,
            'turnover_type': turnover_type,
            'is_our_turnover': is_our_turnover,
            'period': period,
            'clock': clock,
            'drive_result': drive_result,
            'points_scored': drive_points if not is_our_turnover else 0,
            'points_allowed': drive_points if is_our_turnover else 0,
            'play_text': play_description
        })
    
    # Handle turnovers that score directly (pick-6s, fumble return TDs) 
    # that don't have a subsequent drive
    processed_turnover_ids = set()
    for ta in turnover_analysis:
        # Get the game_id and drive_number from the turnover_analysis
        # We'll use this to identify which turnovers have already been processed
        if ta.get('game_id') and ta.get('play_text'):
            # Extract turnover info from play_text if possible
            # For now, we'll track by checking if turnover was in a processed drive
            pass
    
    # Find turnovers that score directly but weren't processed (no subsequent drive)
    for turnover in turnovers:
        if turnover.get('scoring') == True:
            # Check if this turnover was already processed
            # A turnover is processed if there's a drive that started after it
            game_id = turnover.get('game_id')
            drive_number = turnover.get('drive_number', 0)
            
            # Check if this turnover was already included in turnover_analysis
            # A turnover is already processed if there's a drive that started after it
            # Check if any drive started after this turnover
            already_processed = False
            for play in plays:
                if (play.get('game_id') == game_id and
                    play.get('drive_started_after_turnover') == True and
                    play.get('drive_number', 0) == drive_number + 1):
                    # There's a drive that started after this turnover, so it was already processed
                    already_processed = True
                    break
            
            # Also check turnover_analysis for matching entries
            if not already_processed:
                turnover_text = turnover.get('play_text', '')[:150]
                for ta in turnover_analysis:
                    if ta.get('game_id') == game_id:
                        ta_text = ta.get('play_text', '')
                        # Check if turnover text appears in the analysis entry
                        if turnover_text in ta_text or ta_text.startswith(f"TO: {turnover_text}"):
                            already_processed = True
                            break
                        # Also check by matching the first part of the play text
                        # (in case formatting is slightly different)
                        if ta_text.startswith('TO:'):
                            # Extract the turnover part from ta_text
                            ta_turnover_part = ta_text.split(' | Score:')[0].replace('TO: ', '')
                            if turnover_text[:100] in ta_turnover_part or ta_turnover_part[:100] in turnover_text:
                                already_processed = True
                                break
            
            if not already_processed:
                # This is a turnover that scored directly (pick-6, fumble return TD)
                # but doesn't have a subsequent drive
                play_type = turnover.get('play_type', '')
                play_text = turnover.get('play_text', '').upper()
                
                # Determine points and result
                drive_points = 0
                drive_result = 'No Score'
                if 'Touchdown' in play_type or 'TOUCHDOWN' in play_text:
                    drive_points = 7
                    drive_result = 'Touchdown'
                elif 'Field Goal' in play_type:
                    drive_points = 3
                    drive_result = 'Field Goal'
                
                # Determine if it's our turnover or opponent's
                is_our_turnover = turnover.get('offense', '').lower() == team_name.lower()
                
                # For fumble recoveries on punts, the offense field is the recovering team,
                # but the turnover actually belongs to the punting team (defense on the play)
                play_type_check = turnover.get('play_type', '').upper()
                if 'PUNT' in play_type_check and 'FUMBLE RECOVERY' in play_type_check:
                    is_our_turnover = turnover.get('defense', '').lower() == team_name.lower()
                
                # Determine turnover type
                turnover_type_field = (turnover.get('turnover_type') or '').lower()
                play_type_upper = play_type.upper()
                if 'INTERCEPTION' in play_type_upper or turnover_type_field == 'interception':
                    turnover_type = 'Interception'
                elif 'FUMBLE' in play_type_upper or turnover_type_field == 'fumble':
                    turnover_type = 'Fumble'
                else:
                    turnover_type = 'Unknown'
                
                turnover_text = turnover.get('play_text', '')[:150]
                play_description = f"TO: {turnover_text}"
                
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
                    'play_text': play_description
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

