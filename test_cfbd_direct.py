#!/usr/bin/env python3
"""
Test CFBD API directly with HTTP requests to verify API key
"""

import requests
import json

def test_cfbd_direct():
    """Test CFBD API with direct HTTP requests"""
    
    # Load API key from config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    print("Testing CFBD API with direct HTTP requests...")
    print("=" * 50)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Get games
    print("1. Testing games endpoint...")
    try:
        response = requests.get(f"{base_url}/games", headers=headers, params={'year': 2024, 'week': 1})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            games = response.json()
            print(f"✅ Success! Found {len(games)} games")
            if games:
                print(f"Sample game: {games[0].get('home_team', 'Unknown')} vs {games[0].get('away_team', 'Unknown')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n2. Testing plays endpoint...")
    try:
        response = requests.get(f"{base_url}/plays", headers=headers, params={'year': 2024, 'week': 1, 'team': 'Michigan'})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            plays = response.json()
            print(f"✅ Success! Found {len(plays)} plays")
            if plays:
                play = plays[0]
                print("Sample play structure:")
                for key, value in play.items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n3. Testing teams endpoint...")
    try:
        response = requests.get(f"{base_url}/teams/fbs", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            teams = response.json()
            print(f"✅ Success! Found {len(teams)} FBS teams")
            if teams:
                print(f"Sample team: {teams[0].get('school', 'Unknown')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cfbd_direct()
