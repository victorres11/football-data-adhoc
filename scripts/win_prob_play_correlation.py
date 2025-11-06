#!/usr/bin/env python3
"""
Win Probability + Play-by-Play Correlation Analysis
Show how win probability data connects to specific plays
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
    
    with open('data/game_401752873/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return game_data, teams_data

def correlate_win_prob_with_plays(win_prob_data, plays_data):
    """Show how win probability data correlates with specific plays"""
    print("=== WIN PROBABILITY + PLAY CORRELATION ===")
    
    # Create a mapping of play IDs to plays for quick lookup
    play_lookup = {}
    for play in plays_data.get('plays', {}).get('items', []):
        play_id = play.get('id')
        if play_id:
            play_lookup[play_id] = play
    
    print(f"Win probability entries: {len(win_prob_data)}")
    print(f"Play-by-play entries: {len(play_lookup)}")
    
    # Find matches
    matched_plays = []
    unmatched_win_prob = []
    
    for win_prob_entry in win_prob_data:
        play_id = win_prob_entry['playId']
        if play_id in play_lookup:
            matched_plays.append({
                'win_prob': win_prob_entry,
                'play': play_lookup[play_id]
            })
        else:
            unmatched_win_prob.append(win_prob_entry)
    
    print(f"Matched plays: {len(matched_plays)}")
    print(f"Unmatched win probability entries: {len(unmatched_win_prob)}")
    
    return matched_plays, unmatched_win_prob

def show_critical_plays_with_win_prob(matched_plays):
    """Show the most critical plays with their win probability impact"""
    print("\n=== CRITICAL PLAYS WITH WIN PROBABILITY ===")
    
    # Calculate win probability changes
    plays_with_changes = []
    
    for i in range(1, len(matched_plays)):
        current = matched_plays[i]
        previous = matched_plays[i-1]
        
        home_change = current['win_prob']['homeWinPercentage'] - previous['win_prob']['homeWinPercentage']
        
        if abs(home_change) > 0.05:  # 5% or more change
            plays_with_changes.append({
                'play': current['play'],
                'win_prob': current['win_prob'],
                'change': home_change,
                'index': i
            })
    
    # Sort by magnitude of change
    plays_with_changes.sort(key=lambda x: abs(x['change']), reverse=True)
    
    print(f"Found {len(plays_with_changes)} plays with significant win probability changes")
    print(f"\nTop 10 Most Impactful Plays:")
    print(f"{'Qtr':<4} {'Time':<8} {'Change':<10} {'Win%':<8} {'Play Description':<60}")
    print("-" * 100)
    
    for play_data in plays_with_changes[:10]:
        play = play_data['play']
        win_prob = play_data['win_prob']
        change = play_data['change']
        
        quarter = play.get('period', {}).get('number', '')
        time = play.get('clock', {}).get('displayValue', '')
        change_str = f"{change*100:+.1f}%"
        win_pct = f"{win_prob['homeWinPercentage']*100:.1f}%"
        description = play.get('shortText', '')[:60]
        
        print(f"{quarter:<4} {time:<8} {change_str:<10} {win_pct:<8} {description:<60}")

def show_play_sequence_with_win_prob(matched_plays, start_index=0, count=10):
    """Show a sequence of plays with their win probability"""
    print(f"\n=== PLAY SEQUENCE WITH WIN PROBABILITY (Plays {start_index+1}-{start_index+count}) ===")
    print(f"{'Seq':<4} {'Qtr':<4} {'Time':<8} {'Win%':<8} {'Change':<10} {'Play Description':<50}")
    print("-" * 90)
    
    for i in range(start_index, min(start_index + count, len(matched_plays))):
        play_data = matched_plays[i]
        play = play_data['play']
        win_prob = play_data['win_prob']
        
        # Calculate change from previous play
        if i > 0:
            prev_win_prob = matched_plays[i-1]['win_prob']['homeWinPercentage']
            change = win_prob['homeWinPercentage'] - prev_win_prob
            change_str = f"{change*100:+.1f}%"
        else:
            change_str = "N/A"
        
        quarter = play.get('period', {}).get('number', '')
        time = play.get('clock', {}).get('displayValue', '')
        win_pct = f"{win_prob['homeWinPercentage']*100:.1f}%"
        description = play.get('shortText', '')[:50]
        
        print(f"{i+1:<4} {quarter:<4} {time:<8} {win_pct:<8} {change_str:<10} {description:<50}")

def analyze_scoring_plays_with_win_prob(matched_plays):
    """Analyze how scoring plays affected win probability"""
    print(f"\n=== SCORING PLAYS WIN PROBABILITY IMPACT ===")
    
    scoring_plays = []
    
    for i in range(1, len(matched_plays)):
        play_data = matched_plays[i]
        play = play_data['play']
        
        # Check if this is a scoring play
        if play.get('scoringPlay', False):
            prev_win_prob = matched_plays[i-1]['win_prob']['homeWinPercentage']
            current_win_prob = play_data['win_prob']['homeWinPercentage']
            change = current_win_prob - prev_win_prob
            
            scoring_plays.append({
                'play': play,
                'win_prob': play_data['win_prob'],
                'change': change,
                'index': i
            })
    
    if scoring_plays:
        print(f"Found {len(scoring_plays)} scoring plays")
        print(f"{'Qtr':<4} {'Time':<8} {'Change':<10} {'Win%':<8} {'Scoring Play':<50}")
        print("-" * 90)
        
        for scoring_play in scoring_plays:
            play = scoring_play['play']
            win_prob = scoring_play['win_prob']
            change = scoring_play['change']
            
            quarter = play.get('period', {}).get('number', '')
            time = play.get('clock', {}).get('displayValue', '')
            change_str = f"{change*100:+.1f}%"
            win_pct = f"{win_prob['homeWinPercentage']*100:.1f}%"
            description = play.get('shortText', '')[:50]
            
            print(f"{quarter:<4} {time:<8} {change_str:<10} {win_pct:<8} {description:<50}")
    else:
        print("No scoring plays found in the matched data")

def main():
    print("Win Probability + Play-by-Play Correlation Analysis")
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
    
    # Correlate the data
    matched_plays, unmatched = correlate_win_prob_with_plays(win_prob_data, game_data)
    
    if not matched_plays:
        print("No matches found between win probability and play data")
        return
    
    # Show different analyses
    show_critical_plays_with_win_prob(matched_plays)
    show_play_sequence_with_win_prob(matched_plays, 0, 15)  # First 15 plays
    analyze_scoring_plays_with_win_prob(matched_plays)
    
    # Save correlated data
    correlated_data = {
        'matched_plays': matched_plays,
        'unmatched_win_prob': unmatched,
        'total_matches': len(matched_plays),
        'total_win_prob_entries': len(win_prob_data),
        'match_rate': len(matched_plays) / len(win_prob_data) * 100
    }
    
    import os
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/win_prob_play_correlation.json', 'w') as f:
        json.dump(correlated_data, f, indent=2)
    
    print(f"\nCorrelated data saved to: data/game_401752873/win_prob_play_correlation.json")
    print(f"Match rate: {correlated_data['match_rate']:.1f}%")

if __name__ == "__main__":
    main()
