#!/usr/bin/env python3
"""
Test win probability endpoints for ESPN API
"""

import requests
import json
from datetime import datetime

def test_endpoint_1(game_id):
    """Test the site.api.espn.com endpoint"""
    print(f"Testing Endpoint 1: site.api.espn.com")
    print("-" * 50)
    
    url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Successfully fetched data")
        print(f"Response size: {len(json.dumps(data)):,} characters")
        
        # Check for winprobability data
        if 'winprobability' in data:
            win_prob = data['winprobability']
            print(f"✓ Found winprobability data with {len(win_prob)} entries")
            
            if win_prob:
                print(f"Sample entry: {win_prob[0]}")
                return data
        else:
            print("✗ No winprobability data found")
            
        # Check what other data is available
        print(f"Available keys: {list(data.keys())}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
        return None

def test_endpoint_2(game_id):
    """Test the sports.core.api.espn.com endpoint"""
    print(f"\nTesting Endpoint 2: sports.core.api.espn.com")
    print("-" * 50)
    
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/probabilities?limit=200"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Successfully fetched data")
        print(f"Response size: {len(json.dumps(data)):,} characters")
        
        # Check for probabilities data
        if 'items' in data:
            items = data['items']
            print(f"✓ Found {len(items)} probability entries")
            
            if items:
                print(f"Sample entry: {items[0]}")
                return data
        else:
            print("✗ No items data found")
            
        # Check what other data is available
        print(f"Available keys: {list(data.keys())}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
        return None

def analyze_win_probability_data(data, endpoint_name):
    """Analyze the win probability data"""
    print(f"\nAnalyzing {endpoint_name} Win Probability Data")
    print("=" * 60)
    
    if not data:
        print("No data to analyze")
        return
    
    # Look for win probability data in different possible locations
    win_prob_data = None
    
    if 'winprobability' in data:
        win_prob_data = data['winprobability']
        print(f"Found winprobability array with {len(win_prob_data)} entries")
    elif 'items' in data:
        win_prob_data = data['items']
        print(f"Found items array with {len(win_prob_data)} entries")
    elif 'probabilities' in data:
        win_prob_data = data['probabilities']
        print(f"Found probabilities array with {len(win_prob_data)} entries")
    else:
        print("No win probability data found in expected locations")
        print(f"Available keys: {list(data.keys())}")
        return
    
    if win_prob_data and len(win_prob_data) > 0:
        # Analyze the data structure
        sample = win_prob_data[0]
        print(f"\nSample entry structure:")
        print(json.dumps(sample, indent=2))
        
        # Look for key fields
        key_fields = ['play_id', 'home_win_percentage', 'away_win_percentage', 'homeWinPercentage', 'awayWinPercentage']
        found_fields = []
        for field in key_fields:
            if field in sample:
                found_fields.append(field)
        
        print(f"\nKey fields found: {found_fields}")
        
        # Show first few entries
        print(f"\nFirst 5 entries:")
        for i, entry in enumerate(win_prob_data[:5]):
            print(f"  {i+1}: {entry}")
        
        # Calculate some basic stats if we have percentage data
        if 'home_win_percentage' in sample or 'homeWinPercentage' in sample:
            home_pct_field = 'home_win_percentage' if 'home_win_percentage' in sample else 'homeWinPercentage'
            percentages = [entry.get(home_pct_field, 0) for entry in win_prob_data if home_pct_field in entry]
            
            if percentages:
                print(f"\nWin Probability Statistics:")
                print(f"  Initial home win %: {percentages[0]:.1f}%")
                print(f"  Final home win %: {percentages[-1]:.1f}%")
                print(f"  Max home win %: {max(percentages):.1f}%")
                print(f"  Min home win %: {min(percentages):.1f}%")
                print(f"  Average home win %: {sum(percentages)/len(percentages):.1f}%")

def main():
    print("Testing ESPN Win Probability Endpoints")
    print("Game ID: 401752873 (Washington vs Michigan)")
    print("=" * 70)
    
    game_id = 401752873
    
    # Test both endpoints
    data1 = test_endpoint_1(game_id)
    data2 = test_endpoint_2(game_id)
    
    # Analyze the data
    analyze_win_probability_data(data1, "Endpoint 1")
    analyze_win_probability_data(data2, "Endpoint 2")
    
    # Save the data for further analysis
    import os
    os.makedirs('data/game_401752873', exist_ok=True)
    
    if data1:
        with open('data/game_401752873/win_probability_endpoint1.json', 'w') as f:
            json.dump(data1, f, indent=2)
        print(f"\nEndpoint 1 data saved to: data/game_401752873/win_probability_endpoint1.json")
    
    if data2:
        with open('data/game_401752873/win_probability_endpoint2.json', 'w') as f:
            json.dump(data2, f, indent=2)
        print(f"Endpoint 2 data saved to: data/game_401752873/win_probability_endpoint2.json")

if __name__ == "__main__":
    main()
