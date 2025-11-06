#!/usr/bin/env python3
"""
Oregon Explosive Plays Analysis
Fetches play-by-play data from ESPN API for Oregon games and analyzes explosive plays (20+ yards)
"""

import requests
import json
from collections import defaultdict

def fetch_game_data(game_id):
    """Fetch game data from ESPN API"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game {game_id}: {e}")
        return None

def extract_oregon_plays(data):
    """Extract all Oregon plays from game data"""
    oregon_plays = []
    
    if not data or 'drives' not in data:
        return oregon_plays
    
    # Get Oregon team info from header
    oregon_team_name = None
    if 'header' in data and 'competitions' in data['header']:
        for competitor in data['header']['competitions'][0]['competitors']:
            team_name = competitor['team']['displayName']
            if 'Oregon' in team_name:
                oregon_team_name = team_name
                break
    
    if not oregon_team_name:
        print("Could not find Oregon team")
        return oregon_plays
    
    # Extract plays from drives
    drives_data = data['drives'].get('previous', [])
    print(f"Found {len(drives_data)} drives")
    
    # Oregon player names to identify Oregon plays
    oregon_players = [
        'Dante Moore', 'Noah Whittington', 'Jordon Davison', 'Dakorien Moore', 
        'Gary Bryant', 'Malik Benson', 'Kenyon Sadiq', 'Justius Lowe', 'Kyler Kasper',
        'Jay Harris', 'Jayden Limar', 'Dierre Hill', 'Jeremiah McClellan',
        'Atticus Sappington', 'Brandon Finney', 'Austin Novosad', 'Luke Moga'
    ]
    
    # Common opponent player names to exclude
    opponent_players = [
        'Drew Allar', 'Zane Flores', 'Justin Lamson', 'Preston Stone', 'Maalik Murphy',
        'Colby Frokjer', 'Gage Hurych', 'Taco Dowler', 'Christian Fitzpatrick',
        'Griffin Wilde', 'Drew Wagner', 'Taz Reddicks', 'Rocky Lencioni'
    ]
    
    for i, drive in enumerate(drives_data):
        if 'plays' in drive:
            for play in drive['plays']:
                play_text = play.get('text', '')
                
                # First check if it's an opponent play (exclude these)
                is_opponent_play = False
                for player in opponent_players:
                    if player in play_text:
                        is_opponent_play = True
                        break
                
                if is_opponent_play:
                    continue
                
                # Check if this is an Oregon play by looking for Oregon players
                is_oregon_play = False
                for player in oregon_players:
                    if player in play_text:
                        is_oregon_play = True
                        break
                
                # Also check for Oregon-specific plays (kicks, etc.)
                if not is_oregon_play:
                    if any(keyword in play_text.lower() for keyword in ['oregon', 'ore', 'ducks']):
                        is_oregon_play = True
                
                if is_oregon_play:
                    oregon_plays.append(play)
    
    print(f"Total Oregon plays found: {len(oregon_plays)}")
    
    return oregon_plays

def analyze_explosive_plays(plays):
    """Analyze plays to find explosive plays (20+ yards) - OFFENSIVE PLAYS ONLY"""
    explosive_plays = []
    
    # Keywords that indicate defensive plays to exclude
    defensive_keywords = [
        'intercepted', 'interception', 'fumble recovery', 'fumbled', 'recovered by',
        'punt return', 'kickoff return', 'blocked', 'sack', 'tackle'
    ]
    
    for play in plays:
        play_text = play.get('text', '').lower()
        
        # Skip defensive plays
        is_defensive_play = any(keyword in play_text for keyword in defensive_keywords)
        if is_defensive_play:
            continue
        
        # Skip special teams plays (punts, kickoffs, field goals)
        special_teams_keywords = ['kickoff', 'punt', 'field goal', 'fg good', 'fg missed']
        is_special_teams = any(keyword in play_text for keyword in special_teams_keywords)
        if is_special_teams:
            continue
        
        # Get yardage from different possible fields
        yards_gained = 0
        
        # Try different yardage fields
        if 'statYardage' in play:
            yards_gained = play['statYardage']
        elif 'start' in play and 'end' in play:
            start_yard = play['start'].get('yardLine', 0)
            end_yard = play['end'].get('yardLine', 0)
            yards_gained = abs(end_yard - start_yard)
        
        # Check if it's an explosive play (20+ yards)
        if yards_gained >= 20:
            explosive_play = {
                'text': play.get('text', ''),
                'yards': yards_gained,
                'quarter': play.get('period', {}).get('number', 0),
                'clock': play.get('clock', {}).get('displayValue', ''),
                'type': play.get('type', {}).get('text', ''),
                'scoring_play': play.get('scoringPlay', False)
            }
            explosive_plays.append(explosive_play)
    
    return explosive_plays

def main():
    """Main analysis function"""
    # Oregon game IDs
    game_ids = [401752804, 401752824, 401752831, 401752841, 401752854]
    
    all_explosive_plays = []
    game_results = {}
    
    print("🏈 Oregon Explosive Plays Analysis")
    print("=" * 50)
    
    for game_id in game_ids:
        print(f"\n📊 Analyzing Game ID: {game_id}")
        
        # Fetch game data
        data = fetch_game_data(game_id)
        if not data:
            print(f"❌ Failed to fetch data for game {game_id}")
            continue
        
        # Get game info
        game_info = "Unknown Game"
        if 'header' in data and 'competitions' in data['header']:
            competition = data['header']['competitions'][0]
            teams = [comp['team']['displayName'] for comp in competition['competitors']]
            game_info = f"{teams[0]} vs {teams[1]}"
        
        print(f"🎮 Game: {game_info}")
        
        # Extract Oregon plays
        oregon_plays = extract_oregon_plays(data)
        print(f"📈 Total Oregon plays: {len(oregon_plays)}")
        
        # Find explosive plays
        explosive_plays = analyze_explosive_plays(oregon_plays)
        print(f"💥 Explosive plays (20+ yards): {len(explosive_plays)}")
        
        # Store results
        game_results[game_id] = {
            'game_info': game_info,
            'total_plays': len(oregon_plays),
            'explosive_plays': len(explosive_plays),
            'explosive_play_details': explosive_plays
        }
        
        all_explosive_plays.extend(explosive_plays)
        
        # Show explosive play details
        if explosive_plays:
            print("   Explosive plays:")
            for play in explosive_plays:
                print(f"   • Q{play['quarter']} {play['clock']}: {play['text']} ({play['yards']} yards)")
        else:
            print("   No explosive plays found")
    
    # Calculate season average
    total_games = len(game_results)
    total_explosive_plays = len(all_explosive_plays)
    season_average = total_explosive_plays / total_games if total_games > 0 else 0
    
    print("\n" + "=" * 50)
    print("📊 SEASON SUMMARY")
    print("=" * 50)
    print(f"Total games analyzed: {total_games}")
    print(f"Total explosive plays: {total_explosive_plays}")
    print(f"Season average per game: {season_average:.2f}")
    
    print("\n📈 Game-by-Game Breakdown:")
    for game_id, result in game_results.items():
        print(f"  {result['game_info']}: {result['explosive_plays']} explosive plays")
    
    # Compare to Indiana game (2 explosive plays)
    indiana_explosive_plays = 2
    print(f"\n🎯 COMPARISON TO INDIANA GAME")
    print("=" * 50)
    print(f"Oregon vs Indiana: {indiana_explosive_plays} explosive plays")
    print(f"Oregon season average: {season_average:.2f} explosive plays per game")
    
    if indiana_explosive_plays > season_average:
        difference = indiana_explosive_plays - season_average
        print(f"📈 Indiana game: {difference:.2f} ABOVE season average")
    elif indiana_explosive_plays < season_average:
        difference = season_average - indiana_explosive_plays
        print(f"📉 Indiana game: {difference:.2f} BELOW season average")
    else:
        print("📊 Indiana game: EXACTLY at season average")
    
    # Save detailed results
    results = {
        'season_summary': {
            'total_games': total_games,
            'total_explosive_plays': total_explosive_plays,
            'season_average': season_average,
            'indiana_game_explosive_plays': indiana_explosive_plays
        },
        'game_results': game_results,
        'all_explosive_plays': all_explosive_plays
    }
    
    with open('/Users/victorres/projects2/successful-run/oregon_explosive_plays_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: oregon_explosive_plays_analysis.json")

if __name__ == "__main__":
    main()
