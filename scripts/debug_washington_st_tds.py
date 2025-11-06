#!/usr/bin/env python3
"""
Debug script to find Washington special teams touchdowns
"""

import json
from pathlib import Path
from load_advanced_pbp_data import load_team_data

# Load Washington data
washington_data = load_team_data("Washington", "advanced_reports_yogi")

# Filter to special teams plays
special_teams_plays = [
    p for p in washington_data['all_plays'] 
    if p.get('play_classification') == 'special_teams'
]

# Separate by offense (our special teams) vs defense (opponent special teams)
our_st_plays = [
    p for p in special_teams_plays
    if p.get('offense', '').lower() == 'washington'
]

# Also check opponent special teams plays (returns, etc.)
opponent_st_plays = [
    p for p in special_teams_plays
    if p.get('offense', '').lower() != 'washington'
]

print(f"\n\nChecking ALL special teams plays (including opponent) for Washington TDs:")
all_td_plays = []
for play in special_teams_plays:
    play_type = (play.get('play_type', '') or '').lower()
    play_text = (play.get('play_text', '') or '').lower()
    if 'touchdown' in play_type or 'touchdown' in play_text:
        all_td_plays.append(play)

print(f"Found {len(all_td_plays)} total special teams plays with 'touchdown':\n")
for play in all_td_plays:
    print(f"Week: {play.get('game_week')}")
    print(f"Opponent: {play.get('opponent')}")
    print(f"Offense: {play.get('offense')}")
    print(f"Play Type: {play.get('play_type')}")
    print(f"Play Text: {play.get('play_text', '')}")
    print(f"Scoring: {play.get('scoring')}")
    print("-" * 80)

print(f"Total Washington special teams plays: {len(our_st_plays)}")
print(f"\nWashington special teams plays with scoring=True:")
scoring_plays = [p for p in our_st_plays if p.get('scoring', False)]
print(f"Found {len(scoring_plays)} scoring plays\n")

for play in scoring_plays:
    print(f"Week: {play.get('game_week')}")
    print(f"Opponent: {play.get('opponent')}")
    print(f"Play Type: {play.get('play_type')}")
    print(f"Play Text: {play.get('play_text', '')[:150]}")
    print(f"Scoring: {play.get('scoring')}")
    print(f"Yards Gained: {play.get('yards_gained')}")
    
    # Check if it contains touchdown
    play_type = (play.get('play_type', '') or '').lower()
    play_text = (play.get('play_text', '') or '').lower()
    has_td = 'touchdown' in play_type or 'touchdown' in play_text
    print(f"Has 'touchdown' in type/text: {has_td}")
    print("-" * 80)

print(f"\n\nSearching for 'touchdown' in all Washington special teams plays:")
td_plays = []
for play in our_st_plays:
    play_type = (play.get('play_type', '') or '').lower()
    play_text = (play.get('play_text', '') or '').lower()
    if 'touchdown' in play_type or 'touchdown' in play_text:
        td_plays.append(play)

print(f"Found {len(td_plays)} plays with 'touchdown' in type/text:\n")
for play in td_plays:
    print(f"Week: {play.get('game_week')}")
    print(f"Opponent: {play.get('opponent')}")
    print(f"Play Type: {play.get('play_type')}")
    print(f"Play Text: {play.get('play_text', '')}")
    print(f"Scoring: {play.get('scoring')}")
    print(f"Offense: {play.get('offense')}")
    print("-" * 80)

print(f"\n\nAll Washington special teams plays (first 20):")
for i, play in enumerate(our_st_plays[:20]):
    print(f"\n{i+1}. Week {play.get('game_week')} vs {play.get('opponent')}")
    print(f"   Type: {play.get('play_type')}")
    print(f"   Text: {play.get('play_text', '')[:100]}")
    print(f"   Scoring: {play.get('scoring')}")

