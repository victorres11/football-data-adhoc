#!/usr/bin/env python3
"""
Win Probability Game Analysis - Integrate win probability data with play-by-play analysis
"""

import json
import requests
from datetime import datetime

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
    
    with open('data/game_401752873/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return game_data, teams_data

def get_team_name(team_id, teams_data):
    """Get team name from team ID"""
    team_id_str = str(team_id)
    if team_id_str in teams_data:
        return teams_data[team_id_str].get('displayName', f'Team {team_id}')
    return f'Team {team_id}'

def analyze_momentum_shifts(win_prob_data, plays_data):
    """Identify key momentum shifts in the game"""
    print("=== MOMENTUM SHIFTS ANALYSIS ===")
    
    if not win_prob_data:
        print("No win probability data available")
        return
    
    # Find plays with biggest win probability changes
    momentum_shifts = []
    
    for i in range(1, len(win_prob_data)):
        current = win_prob_data[i]
        previous = win_prob_data[i-1]
        
        home_change = current['homeWinPercentage'] - previous['homeWinPercentage']
        
        if abs(home_change) > 0.05:  # 5% or more change
            momentum_shifts.append({
                'play_id': current['playId'],
                'home_win_pct': current['homeWinPercentage'],
                'change': home_change,
                'index': i
            })
    
    # Sort by magnitude of change
    momentum_shifts.sort(key=lambda x: abs(x['change']), reverse=True)
    
    print(f"Found {len(momentum_shifts)} significant momentum shifts (>5% change)")
    print(f"\nTop 5 Momentum Shifts:")
    print(f"{'Play ID':<20} {'Home Win %':<12} {'Change':<10} {'Direction':<10}")
    print("-" * 60)
    
    for shift in momentum_shifts[:5]:
        direction = "↑ Michigan" if shift['change'] > 0 else "↓ Michigan"
        print(f"{shift['play_id']:<20} {shift['home_win_pct']*100:>8.1f}% {shift['change']*100:>+7.1f}% {direction:<10}")
    
    return momentum_shifts

def analyze_critical_plays(win_prob_data, plays_data):
    """Identify the most critical plays that changed win probability"""
    print("\n=== CRITICAL PLAYS ANALYSIS ===")
    
    if not win_prob_data:
        print("No win probability data available")
        return
    
    # Find plays with biggest impact
    critical_plays = []
    
    for i in range(1, len(win_prob_data)):
        current = win_prob_data[i]
        previous = win_prob_data[i-1]
        
        home_change = current['homeWinPercentage'] - previous['homeWinPercentage']
        
        if abs(home_change) > 0.1:  # 10% or more change
            # Find the corresponding play
            play_id = current['playId']
            play_info = None
            
            for play in plays_data.get('plays', {}).get('items', []):
                if play.get('id') == play_id:
                    play_info = play
                    break
            
            if play_info:
                critical_plays.append({
                    'play_id': play_id,
                    'home_win_pct': current['homeWinPercentage'],
                    'change': home_change,
                    'play_text': play_info.get('text', ''),
                    'short_text': play_info.get('shortText', ''),
                    'quarter': play_info.get('period', {}).get('number', ''),
                    'time': play_info.get('clock', {}).get('displayValue', ''),
                    'play_type': play_info.get('type', {}).get('text', '')
                })
    
    # Sort by magnitude of change
    critical_plays.sort(key=lambda x: abs(x['change']), reverse=True)
    
    print(f"Found {len(critical_plays)} critical plays (>10% win probability change)")
    print(f"\nMost Critical Plays:")
    print(f"{'Qtr':<4} {'Time':<8} {'Change':<10} {'Play Description':<60}")
    print("-" * 90)
    
    for play in critical_plays[:10]:
        change_str = f"{play['change']*100:+.1f}%"
        description = play['short_text'][:60] if len(play['short_text']) > 60 else play['short_text']
        print(f"{play['quarter']:<4} {play['time']:<8} {change_str:<10} {description:<60}")
    
    return critical_plays

def analyze_quarter_by_quarter_momentum(win_prob_data, plays_data):
    """Analyze win probability changes by quarter"""
    print("\n=== QUARTER-BY-QUARTER MOMENTUM ===")
    
    if not win_prob_data:
        print("No win probability data available")
        return
    
    # Group plays by quarter
    quarter_data = {}
    
    for prob_entry in win_prob_data:
        play_id = prob_entry['playId']
        
        # Find the corresponding play to get quarter info
        for play in plays_data.get('plays', {}).get('items', []):
            if play.get('id') == play_id:
                quarter = play.get('period', {}).get('number', 1)
                
                if quarter not in quarter_data:
                    quarter_data[quarter] = []
                
                quarter_data[quarter].append({
                    'home_win_pct': prob_entry['homeWinPercentage'],
                    'play_id': play_id,
                    'time': play.get('clock', {}).get('displayValue', ''),
                    'play_text': play.get('shortText', '')
                })
                break
    
    # Analyze each quarter
    for quarter in sorted(quarter_data.keys()):
        plays = quarter_data[quarter]
        if not plays:
            continue
            
        start_pct = plays[0]['home_win_pct']
        end_pct = plays[-1]['home_win_pct']
        change = end_pct - start_pct
        
        print(f"\nQ{quarter}:")
        print(f"  Start: {start_pct*100:.1f}% → End: {end_pct*100:.1f}% (Change: {change*100:+.1f}%)")
        
        # Find biggest swing in this quarter
        max_change = 0
        max_change_play = None
        
        for i in range(1, len(plays)):
            change = plays[i]['home_win_pct'] - plays[i-1]['home_win_pct']
            if abs(change) > abs(max_change):
                max_change = change
                max_change_play = plays[i]
        
        if max_change_play:
            print(f"  Biggest swing: {max_change*100:+.1f}% at {max_change_play['time']} - {max_change_play['play_text'][:50]}")

def create_win_probability_summary(win_prob_data):
    """Create a summary of win probability throughout the game"""
    print("\n=== WIN PROBABILITY SUMMARY ===")
    
    if not win_prob_data:
        print("No win probability data available")
        return
    
    initial = win_prob_data[0]['homeWinPercentage']
    final = win_prob_data[-1]['homeWinPercentage']
    
    # Find min and max
    min_pct = min(entry['homeWinPercentage'] for entry in win_prob_data)
    max_pct = max(entry['homeWinPercentage'] for entry in win_prob_data)
    
    # Find when each extreme occurred
    min_play = min(win_prob_data, key=lambda x: x['homeWinPercentage'])
    max_play = max(win_prob_data, key=lambda x: x['homeWinPercentage'])
    
    print(f"Initial Home Win Probability: {initial*100:.1f}%")
    print(f"Final Home Win Probability: {final*100:.1f}%")
    print(f"Lowest Home Win Probability: {min_pct*100:.1f}%")
    print(f"Highest Home Win Probability: {max_pct*100:.1f}%")
    print(f"Total Change: {(final-initial)*100:+.1f}%")
    
    # Calculate average
    avg_pct = sum(entry['homeWinPercentage'] for entry in win_prob_data) / len(win_prob_data)
    print(f"Average Home Win Probability: {avg_pct*100:.1f}%")
    
    # Time spent in different ranges
    ranges = {
        'Michigan Dominant (80-100%)': 0,
        'Michigan Favored (60-80%)': 0,
        'Close Game (40-60%)': 0,
        'Washington Favored (20-40%)': 0,
        'Washington Dominant (0-20%)': 0
    }
    
    for entry in win_prob_data:
        pct = entry['homeWinPercentage']
        if pct >= 0.8:
            ranges['Michigan Dominant (80-100%)'] += 1
        elif pct >= 0.6:
            ranges['Michigan Favored (60-80%)'] += 1
        elif pct >= 0.4:
            ranges['Close Game (40-60%)'] += 1
        elif pct >= 0.2:
            ranges['Washington Favored (20-40%)'] += 1
        else:
            ranges['Washington Dominant (0-20%)'] += 1
    
    print(f"\nTime Spent in Each Range:")
    for range_name, count in ranges.items():
        percentage = (count / len(win_prob_data)) * 100
        print(f"  {range_name}: {count} plays ({percentage:.1f}%)")

def main():
    print("Win Probability Game Analysis")
    print("Game ID: 401752873 | Date: October 18, 2025")
    print("=" * 70)
    
    game_id = 401752873
    
    # Fetch win probability data
    print("Fetching win probability data...")
    win_prob_data = fetch_win_probability_data(game_id)
    
    if not win_prob_data:
        print("No win probability data available")
        return
    
    # Load existing game data
    game_data, teams_data = load_game_data()
    
    # Run analyses
    create_win_probability_summary(win_prob_data)
    analyze_momentum_shifts(win_prob_data, game_data)
    analyze_critical_plays(win_prob_data, game_data)
    analyze_quarter_by_quarter_momentum(win_prob_data, game_data)
    
    # Save analysis
    analysis_results = {
        'win_probability_data': win_prob_data,
        'analyzed_at': datetime.now().isoformat()
    }
    
    import os
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/win_probability_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\nWin probability analysis saved to: data/game_401752873/win_probability_analysis.json")

if __name__ == "__main__":
    main()
