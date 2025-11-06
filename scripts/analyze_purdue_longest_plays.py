#!/usr/bin/env python3
"""
Analyze Purdue's longest play from scrimmage in each game
Using local data from data/purdue_games/
"""

import json
import os
from datetime import datetime

def load_game_data(game_id):
    """Load game data from local file"""
    filename = f'data/purdue_games/game_{game_id}.json'
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        return None
    except Exception as e:
        print(f"  ✗ Error loading {filename}: {e}")
        return None

def find_purdue_longest_play(data, game_id):
    """Find Purdue's longest play of scrimmage from game data"""
    if not data:
        return None
    
    # Get game info
    header = data.get('header', {})
    game_name = header.get('name', f'Game {game_id}')
    game_date = header.get('date', 'Unknown Date')
    
    # Get drives data
    drives = data.get('drives', {}).get('items', [])
    
    # Purdue team IDs (they could be home or away)
    # Based on game analysis, Purdue is team ID 2509 in some games
    # Let me check both possible IDs
    purdue_team_ids = ["77", "2509"]  # Possible Purdue team IDs
    
    purdue_plays = []
    max_yards = 0
    longest_play = None
    
    for drive in drives:
        if 'plays' in drive and 'items' in drive['plays']:
            for play in drive['plays']['items']:
                # Skip if play is not a dictionary
                if not isinstance(play, dict):
                    continue
                
                # Check if this is a Purdue offensive play
                team_participants = play.get('teamParticipants', [])
                is_purdue_offense = False
                
                for participant in team_participants:
                    if participant.get('type') == 'offense':
                        team_id = participant.get('id', '')
                        if team_id in purdue_team_ids:
                            is_purdue_offense = True
                            break
                
                if is_purdue_offense:
                    yards = play.get('statYardage', 0)
                    play_type = play.get('type', {}).get('text', '')
                    play_text = play.get('text', '')
                    
                    # Filter out special teams plays
                    if not any(st in play_type.lower() for st in ['punt', 'kickoff', 'field goal']):
                        play_info = {
                            'yards': yards,
                            'play_type': play_type,
                            'play_text': play_text,
                            'quarter': play.get('period', {}).get('number'),
                            'time': play.get('clock', {}).get('displayValue'),
                            'down': play.get('start', {}).get('down'),
                            'distance': play.get('start', {}).get('distance'),
                            'yard_line': play.get('start', {}).get('possessionText', '')
                        }
                        
                        purdue_plays.append(play_info)
                        
                        if yards > max_yards:
                            max_yards = yards
                            longest_play = play_info
    
    return {
        'game_id': game_id,
        'game_name': game_name,
        'game_date': game_date,
        'total_plays': len(purdue_plays),
        'longest_play': longest_play,
        'max_yards': max_yards,
        'all_plays': purdue_plays
    }

def create_summary_table(results):
    """Create a summary table of all games"""
    print("\n" + "=" * 100)
    print("PURDUE LONGEST PLAYS SUMMARY - ALL GAMES")
    print("=" * 100)
    print(f"{'Game':<25} {'Date':<12} {'Yards':<6} {'Quarter':<8} {'Time':<8} {'Description'}")
    print("-" * 100)
    
    for result in results:
        if result and result['longest_play']:
            play = result['longest_play']
            game_short = result['game_name'].replace('Purdue Boilermakers', 'Purdue').replace(' at ', ' @ ')
            date_short = result['game_date'][:10] if result['game_date'] != 'Unknown Date' else 'Unknown'
            print(f"{game_short:<25} {date_short:<12} {play['yards']:<6} Q{play['quarter']:<7} {play['time']:<8} {play['play_text'][:50]}...")
        else:
            print(f"{result['game_name']:<25} {'Unknown':<12} {'N/A':<6} {'N/A':<8} {'N/A':<8} No plays found")

def main():
    print("Purdue Longest Plays Analysis")
    print("Analyzing all 6 Purdue games from local data")
    print("=" * 60)
    
    # Game IDs to analyze
    game_ids = [
        401752801,  # Ball State vs Purdue
        401752819,  # Southern Illinois vs Purdue  
        401752832,  # USC vs Purdue
        401752848,  # Purdue vs Notre Dame
        401752861,  # Illinois vs Purdue
        401752864   # Purdue vs Minnesota
    ]
    
    results = []
    
    for game_id in game_ids:
        print(f"\nAnalyzing Game {game_id}...")
        
        # Load game data
        data = load_game_data(game_id)
        
        if data:
            # Find Purdue's longest play
            result = find_purdue_longest_play(data, game_id)
            results.append(result)
            
            if result and result['longest_play']:
                play = result['longest_play']
                print(f"  ✓ {result['game_name']}")
                print(f"    Longest play: {play['yards']} yards")
                print(f"    Quarter: Q{play['quarter']} {play['time']}")
                print(f"    Play: {play['play_text'][:80]}...")
                print(f"    Total Purdue plays: {result['total_plays']}")
            else:
                print(f"  ✗ No Purdue plays found")
        else:
            print(f"  ✗ Could not load game data")
            results.append(None)
    
    # Create summary table
    create_summary_table(results)
    
    # Find overall longest play
    all_longest_plays = [r for r in results if r and r['longest_play']]
    if all_longest_plays:
        overall_longest = max(all_longest_plays, key=lambda x: x['max_yards'])
        print(f"\n🏆 OVERALL LONGEST PLAY:")
        print(f"   {overall_longest['max_yards']} yards - {overall_longest['game_name']}")
        print(f"   {overall_longest['longest_play']['play_text']}")
    
    # Save detailed results
    output_data = {
        'analysis_date': datetime.now().isoformat(),
        'total_games': len(game_ids),
        'games_analyzed': len([r for r in results if r]),
        'results': results
    }
    
    with open('purdue_longest_plays_analysis.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDetailed analysis saved to: purdue_longest_plays_analysis.json")

if __name__ == "__main__":
    main()
