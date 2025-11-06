#!/usr/bin/env python3
"""
Find Washington special teams touchdowns - check all plays
"""

import json
from pathlib import Path
from load_advanced_pbp_data import load_team_data

# Load Washington data
washington_data = load_team_data("Washington", "advanced_reports_yogi")

# Check all plays for special teams touchdowns
all_plays = washington_data['all_plays']

print("Searching for special teams touchdowns in ALL plays...")
print("Looking for plays with: kickoff/punt + return + touchdown\n")

td_candidates = []
for play in all_plays:
    play_type = (play.get('play_type', '') or '').lower()
    play_text = (play.get('play_text', '') or '').lower()
    
    # Check if it's a special teams type play
    is_st = ('kickoff' in play_type or 'kickoff' in play_text or 
             'punt' in play_type or 'punt' in play_text or
             'return' in play_type or 'return' in play_text)
    
    # Check if it mentions touchdown
    has_td = ('touchdown' in play_type or 'touchdown' in play_text or
              ' td ' in play_text or play_text.endswith(' td') or
              'touchdown' in play.get('play_type', '').lower())
    
    # Check if Washington is on offense (for returns they scored)
    is_wash = play.get('offense', '').lower() == 'washington'
    
    if is_st and has_td:
        td_candidates.append(play)
        print(f"Week: {play.get('game_week')}")
        print(f"Opponent: {play.get('opponent')}")
        print(f"Offense: {play.get('offense')}")
        print(f"Play Classification: {play.get('play_classification')}")
        print(f"Play Type: {play.get('play_type')}")
        print(f"Play Text: {play.get('play_text', '')}")
        print(f"Scoring: {play.get('scoring')}")
        print(f"Yards Gained: {play.get('yards_gained')}")
        print("-" * 80)

if not td_candidates:
    print("\nNo special teams touchdowns found. Checking all scoring plays...")
    scoring_plays = [p for p in all_plays if p.get('scoring', False) and p.get('offense', '').lower() == 'washington']
    print(f"\nFound {len(scoring_plays)} total Washington scoring plays")
    
    for play in scoring_plays[:10]:  # Show first 10
        play_type = (play.get('play_type', '') or '').lower()
        play_text = (play.get('play_text', '') or '').lower()
        is_st = play.get('play_classification') == 'special_teams'
        has_td = 'touchdown' in play_type or 'touchdown' in play_text
        print(f"\nWeek {play.get('game_week')} vs {play.get('opponent')}")
        print(f"  Type: {play.get('play_type')}")
        print(f"  Text: {play.get('play_text', '')[:100]}")
        print(f"  ST Classification: {is_st}")
        print(f"  Has TD: {has_td}")
        print(f"  Scoring: {play.get('scoring')}")

