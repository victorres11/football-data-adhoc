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
    
    For returns, we parse the return yards from the play text because
    yards_gained might include the kick/punt distance, not just the return.
    """
    import re
    
    play_type = play.get('play_type', '').lower()
    play_text = play.get('play_text', '').lower()
    play_text_full = play.get('play_text', '')  # Keep original case for regex
    
    def parse_return_yards(text: str) -> int:
        """Parse return yards from play text"""
        if not text:
            return 0
        
        # Look for patterns like "returns for X yds" or "returns for no gain"
        # Examples:
        # "returns for 56 yds" -> 56
        # "returns for no gain" -> 0
        # "return for 20 yds" -> 20
        match = re.search(r'return[s]? for (?:no gain|(\d+) (?:yd|yard))', text, re.IGNORECASE)
        if match:
            if match.group(1):
                return int(match.group(1))
            else:
                return 0  # "no gain"
        
        # Fallback: if we can't parse, return 0 to be safe
        return 0
    
    # Kick return: 35+ yards
    if 'kickoff' in play_type or 'kickoff' in play_text:
        if 'return' in play_type or 'return' in play_text:
            return_yards = parse_return_yards(play_text_full)
            return return_yards >= 35
    
    # Punt return: 20+ yards
    if 'punt' in play_type or 'punt' in play_text:
        if 'return' in play_type or 'return' in play_text:
            return_yards = parse_return_yards(play_text_full)
            return return_yards >= 20
    
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
    # For returns, the returning team is on "defense", not "offense"
    our_st_plays = []
    opponent_st_plays = []
    
    for p in special_teams_plays:
        play_type = p.get('play_type', '').lower()
        play_text = p.get('play_text', '').lower()
        
        # Check if it's a return play (kickoff return or punt return)
        is_return = (
            ('return' in play_type or 'return' in play_text) and
            ('kickoff' in play_type or 'kickoff' in play_text or
             'punt' in play_type or 'punt' in play_text)
        )
        
        if is_return:
            # For returns, check defense field (returning team)
            defense = p.get('defense', '') or ''
            if defense.lower() == team_name.lower():
                our_st_plays.append(p)
            else:
                opponent_st_plays.append(p)
        else:
            # For other ST plays (kicks, punts), check offense field
            offense = p.get('offense', '') or ''
            if offense.lower() == team_name.lower():
                our_st_plays.append(p)
            else:
                opponent_st_plays.append(p)
    
    # Find explosive plays using special teams criteria (35+ kick return, 20+ punt return)
    explosive_plays = [p for p in our_st_plays if is_special_teams_explosive(p)]
    explosive_returns_allowed = [p for p in opponent_st_plays if is_special_teams_explosive(p)]
    
    # Count touchdowns on special teams
    # Important: For return TDs, the "offense" field is the team that punted/kicked,
    # not the team that scored. We need to check all ST plays and determine who scored.
    tds_scored = []
    for p in special_teams_plays:
        if not p.get('scoring', False):
            continue
        play_type = p.get('play_type', '').lower()
        play_text = p.get('play_text', '').lower()
        has_td = 'touchdown' in play_type or 'touchdown' in play_text or ' for a td' in play_text
        
        if not has_td:
            continue
        
        # Check if this is a return TD (punt return or kickoff return)
        is_return_td = (('return' in play_type or 'return' in play_text) and
                       ('kickoff' in play_type or 'kickoff' in play_text or
                        'punt' in play_type or 'punt' in play_text))
        
        if is_return_td:
            # For return TDs: if opponent is on offense (they punted/kicked),
            # then our team scored on the return
            offense = p.get('offense', '') or ''
            is_opponent_offense = offense.lower() != team_name.lower()
            if is_opponent_offense:
                tds_scored.append(p)
        else:
            # For non-return TDs (like blocked punts run back), our team on offense = their TD
            offense = p.get('offense', '') or ''
            if offense.lower() == team_name.lower():
                tds_scored.append(p)
    
    tds_allowed = []
    for p in special_teams_plays:
        if not p.get('scoring', False):
            continue
        play_type = p.get('play_type', '').lower()
        play_text = p.get('play_text', '').lower()
        has_td = 'touchdown' in play_type or 'touchdown' in play_text or ' for a td' in play_text
        
        if not has_td:
            continue
        
        # Check if this is a return TD
        is_return_td = (('return' in play_type or 'return' in play_text) and
                       ('kickoff' in play_type or 'kickoff' in play_text or
                        'punt' in play_type or 'punt' in play_text))
        
        if is_return_td:
            # For return TDs: if our team is on offense (they punted/kicked),
            # then opponent scored on the return (our team allowed it)
            offense = p.get('offense', '') or ''
            if offense.lower() == team_name.lower():
                tds_allowed.append(p)
        else:
            # For non-return TDs, opponent on offense = their TD
            offense = p.get('offense', '') or ''
            if offense.lower() != team_name.lower():
                tds_allowed.append(p)
    
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
    
    # Count punt blocks
    # Punt blocks: when opponent is punting (they're on offense) and we block it
    punt_blocks = []
    for play in special_teams_plays:
        play_type = play.get('play_type', '').lower()
        play_text = play.get('play_text', '').lower()
        offense = play.get('offense', '') or ''
        is_opponent_offense = offense.lower() != team_name.lower()
        
        # Check if it's a punt block
        # Must have "blocked punt" or "punt blocked" in play type or text
        # This excludes false positives like "Illegal Block in Back" penalties on punts
        has_blocked_punt_in_type = 'blocked punt' in play_type or 'punt blocked' in play_type
        has_blocked_punt_in_text = 'blocked punt' in play_text or 'punt blocked' in play_text
        
        is_punt_block = (
            (has_blocked_punt_in_type or has_blocked_punt_in_text) and
            is_opponent_offense  # Opponent is punting, we blocked it
        )
        
        if is_punt_block:
            punt_blocks.append(play)
    
    # Punt blocks allowed: when we're punting and opponent blocks it
    punt_blocks_allowed = []
    for play in special_teams_plays:
        play_type = play.get('play_type', '').lower()
        play_text = play.get('play_text', '').lower()
        offense = play.get('offense', '') or ''
        is_our_offense = offense.lower() == team_name.lower()
        
        # Check if it's a punt block allowed
        # Must have "blocked punt" or "punt blocked" in play type or text
        # This excludes false positives like "Illegal Block in Back" penalties on punts
        has_blocked_punt_in_type = 'blocked punt' in play_type or 'punt blocked' in play_type
        has_blocked_punt_in_text = 'blocked punt' in play_text or 'punt blocked' in play_text
        
        is_punt_block_allowed = (
            (has_blocked_punt_in_type or has_blocked_punt_in_text) and
            is_our_offense  # We're punting, opponent blocked it
        )
        
        if is_punt_block_allowed:
            punt_blocks_allowed.append(play)
    
    # Group by game
    game_stats = defaultdict(lambda: {
        'total_plays': 0,
        'explosive': 0,
        'bad_results': 0,
        'plays': []
    })
    
    for play in special_teams_plays:
        game_id = play.get('game_id')
        offense = play.get('offense', '') or ''
        is_our = offense.lower() == team_name.lower()
        
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
        'punt_blocks': len(punt_blocks),
        'punt_blocks_allowed': len(punt_blocks_allowed),
        'plays': all_plays_flat,
        'total_games': unique_games,
        'game_stats': dict(game_stats)
    }

