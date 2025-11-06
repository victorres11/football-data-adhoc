#!/usr/bin/env python3
"""
Debug script to check penalty positioning in chart
"""

import json
import requests

def fetch_win_probability_data(game_id):
    """Fetch win probability data from ESPN API"""
    url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('winprobability', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching win probability data: {e}")
        return []

def load_game_data():
    """Load existing game data"""
    with open('data/game_401752873/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    return game_data

def debug_chart_positioning():
    """Debug penalty positioning in chart"""
    game_data = load_game_data()
    plays = game_data.get('plays', {}).get('items', [])
    
    # Get win probability data
    win_prob_data = fetch_win_probability_data(401752873)
    
    print(f"Total plays: {len(plays)}")
    print(f"Total win probability entries: {len(win_prob_data)}")
    print("=" * 60)
    
    # Find penalties
    penalties = []
    for i, play in enumerate(plays):
        play_type_id = play.get('type', {}).get('id', '')
        if play_type_id == '8':  # Penalty type ID
            short_text = play.get('shortText', '')
            team_committed = "Unknown"
            if 'washington penalty' in short_text.lower():
                team_committed = "Washington"
            elif 'michigan penalty' in short_text.lower():
                team_committed = "Michigan"
            
            penalties.append({
                'play_number': i + 1,
                'play_id': play.get('id', ''),
                'team': team_committed,
                'short_text': short_text,
                'yards': play.get('statYardage', 0)
            })
    
    print(f"Found {len(penalties)} penalties:")
    print("=" * 60)
    
    # Check win probability data structure
    print("Win probability data structure:")
    if win_prob_data:
        print(f"First entry keys: {list(win_prob_data[0].keys())}")
        print(f"Sample entry: {win_prob_data[0]}")
        print()
    
    # Check penalty matching
    print("Penalty matching analysis:")
    print("=" * 60)
    
    # Create win probability lookup
    win_prob_by_play_id = {}
    for i, entry in enumerate(win_prob_data):
        play_id = entry.get('playId', '')
        if play_id:
            win_prob_by_play_id[play_id] = {
                'index': i,
                'homeWinPercentage': entry['homeWinPercentage']
            }
    
    print(f"Win probability entries with playId: {len(win_prob_by_play_id)}")
    
    matched_penalties = 0
    for penalty in penalties:
        play_id = penalty['play_id']
        if play_id in win_prob_by_play_id:
            wp_data = win_prob_by_play_id[play_id]
            print(f"✓ Play #{penalty['play_number']} ({penalty['team']}) - Matched at index {wp_data['index']}, win prob: {wp_data['homeWinPercentage']*100:.1f}%")
            matched_penalties += 1
        else:
            print(f"✗ Play #{penalty['play_number']} ({penalty['team']}) - No match for play ID: {play_id}")
    
    print(f"\nMatched penalties: {matched_penalties}/{len(penalties)}")
    
    # Show some sample play IDs
    print("\nSample play IDs from penalties:")
    for penalty in penalties[:3]:
        print(f"  {penalty['play_id']}")
    
    print("\nSample play IDs from win probability:")
    for i, entry in enumerate(win_prob_data[:3]):
        print(f"  {entry.get('playId', 'NO_PLAY_ID')}")

if __name__ == "__main__":
    debug_chart_positioning()
