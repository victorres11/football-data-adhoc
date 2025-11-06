#!/usr/bin/env python3
"""
Comprehensive CFBD API Demonstration
Shows actual data from CollegeFootballData.com API
"""

import requests
import json
from datetime import datetime

def demonstrate_cfbd_api():
    """Demonstrate the actual CFBD API data structure and capabilities"""
    
    # Load API key from config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("CFBD API - Actual Data Demonstration")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10]}...")
    print()
    
    # 1. Get games for a specific week
    print("1. GAMES ENDPOINT")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={'year': 2024, 'week': 1})
        if response.status_code == 200:
            games = response.json()
            print(f"✅ Found {len(games)} games in Week 1, 2024")
            
            # Show sample game
            if games:
                game = games[0]
                print(f"Sample game: {game.get('home_team', 'Unknown')} vs {game.get('away_team', 'Unknown')}")
                print(f"Game ID: {game.get('id')}")
                print(f"Date: {game.get('start_date')}")
                print(f"Completed: {game.get('completed')}")
                print(f"Home Score: {game.get('home_points')}")
                print(f"Away Score: {game.get('away_points')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n2. PLAYS ENDPOINT")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/plays", headers=headers, params={'year': 2024, 'week': 1, 'team': 'Michigan'})
        if response.status_code == 200:
            plays = response.json()
            print(f"✅ Found {len(plays)} plays for Michigan in Week 1, 2024")
            
            # Show detailed structure of first play
            if plays:
                play = plays[0]
                print("\n=== DETAILED PLAY STRUCTURE ===")
                for key, value in play.items():
                    print(f"{key}: {value}")
                
                # Save sample data
                with open('cfbd_actual_play_data.json', 'w') as f:
                    json.dump(play, f, indent=2)
                print(f"\n📁 Full play data saved to: cfbd_actual_play_data.json")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n3. TEAMS ENDPOINT")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/teams/fbs", headers=headers)
        if response.status_code == 200:
            teams = response.json()
            print(f"✅ Found {len(teams)} FBS teams")
            
            # Show sample team
            if teams:
                team = teams[0]
                print(f"Sample team: {team.get('school', 'Unknown')}")
                print(f"Conference: {team.get('conference', 'Unknown')}")
                print(f"Division: {team.get('division', 'Unknown')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n4. ADVANCED STATS ENDPOINT")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/stats/game/advanced", headers=headers, params={'year': 2024, 'week': 1})
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Found {len(stats)} advanced game stats")
            
            if stats:
                stat = stats[0]
                print(f"Sample game: {stat.get('gameId')}")
                print(f"Team: {stat.get('team')}")
                print(f"Offense EPA: {stat.get('offense', {}).get('overall', {}).get('epa', 'N/A')}")
                print(f"Defense EPA: {stat.get('defense', {}).get('overall', {}).get('epa', 'N/A')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n5. WIN PROBABILITY ENDPOINT")
    print("-" * 30)
    try:
        # Get a specific game ID first
        games_response = requests.get(f"{base_url}/games", headers=headers, params={'year': 2024, 'week': 1})
        if games_response.status_code == 200:
            games = games_response.json()
            if games:
                game_id = games[0]['id']
                response = requests.get(f"{base_url}/metrics/wp", headers=headers, params={'gameId': game_id})
                if response.status_code == 200:
                    wp_data = response.json()
                    print(f"✅ Found win probability data for game {game_id}")
                    if wp_data:
                        print(f"Sample WP entry: {wp_data[0]}")
                else:
                    print(f"❌ WP Failed: {response.text}")
        else:
            print(f"❌ Games Failed: {games_response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n=== CFBD API ADVANTAGES ===")
    advantages = [
        "🎯 **Structured Data**: Clean, consistent JSON responses",
        "📊 **Advanced Analytics**: PPA, EPA, success rate built-in",
        "🔍 **Rich Filtering**: Filter by team, week, season, play type",
        "⚡ **Performance**: Fast, reliable API with good rate limits",
        "📈 **Historical Data**: Access to comprehensive historical datasets",
        "🛠️ **Developer Friendly**: Well-documented, consistent endpoints",
        "📋 **Standardized Fields**: Consistent field names and data types",
        "🏈 **College Football Focused**: Purpose-built for CFB analysis"
    ]
    
    for advantage in advantages:
        print(advantage)
    
    print("\n=== COMPARISON: CFBD vs ESPN ===")
    print("CFBD API:")
    print("  ✅ Structured, consistent data format")
    print("  ✅ Advanced analytics (PPA, EPA) included")
    print("  ✅ Better filtering and querying capabilities")
    print("  ✅ Comprehensive historical data")
    print("  ✅ Purpose-built for college football")
    print("  ❌ Requires API key (free registration)")
    print("  ❌ Rate limits (but generous)")
    
    print("\nESPN API:")
    print("  ✅ No authentication required")
    print("  ✅ Real-time data access")
    print("  ✅ Win probability data")
    print("  ❌ Inconsistent data structures")
    print("  ❌ Limited historical data")
    print("  ❌ Manual JSON parsing required")
    print("  ❌ Varying endpoint structures")

if __name__ == "__main__":
    demonstrate_cfbd_api()
