#!/usr/bin/env python3
"""
Debug script to understand the coordinate system issue
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

def debug_coordinates():
    """Debug the coordinate system"""
    
    # Get data
    game_data = load_game_data()
    plays = game_data.get('plays', {}).get('items', [])
    win_prob_data = fetch_win_probability_data(401752873)
    
    print("=== COORDINATE SYSTEM DEBUG ===")
    print(f"Total plays: {len(plays)}")
    print(f"Total win probability entries: {len(win_prob_data)}")
    print()
    
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
                'short_text': short_text
            })
    
    print(f"Found {len(penalties)} penalties:")
    for penalty in penalties:
        print(f"  Play {penalty['play_number']}: {penalty['team']} - {penalty['short_text']}")
    
    print("\n=== CHART DATA STRUCTURE ===")
    print("Chart will have data points:")
    print("  Index 0: Play 1")
    print("  Index 1: Play 6") 
    print("  Index 2: Play 11")
    print("  Index 3: Play 16")
    print("  Index 4: Play 21")
    print("  ...")
    print(f"  Index {len(win_prob_data)//5 - 1}: Play {len(win_prob_data)}")
    
    print("\n=== PENALTY POSITIONING ===")
    for penalty in penalties:
        play_number = penalty['play_number']
        
        # Method 1: Direct index
        direct_index = play_number - 1
        print(f"Play {play_number}: Direct index = {direct_index}")
        
        # Method 2: Chart coordinate (every 5th)
        chart_coord = (play_number - 1) / 5
        print(f"Play {play_number}: Chart coord = {chart_coord}")
        
        # Method 3: Find closest chart data point
        closest_chart_index = (play_number - 1) // 5
        print(f"Play {play_number}: Closest chart index = {closest_chart_index}")
        
        print()

if __name__ == "__main__":
    debug_coordinates()
