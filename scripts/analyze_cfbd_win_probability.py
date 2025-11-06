#!/usr/bin/env python3
"""
Analyze CFBD data to understand win probability structure
"""

import json
import os

def analyze_cfbd_win_probability():
    """Analyze CFBD win probability data"""
    
    # Load the sorted CFBD data
    cfbd_file = 'cfbd_plays_401752873_sorted.json'
    if not os.path.exists(cfbd_file):
        print("❌ SORTED CFBD data file not found")
        return
    
    with open(cfbd_file, 'r') as f:
        plays = json.load(f)
    
    print(f"📊 Analyzing {len(plays)} CFBD plays for win probability data...")
    print("=" * 60)
    
    # Analyze win probability fields
    wp_fields = {}
    wp_values = set()
    has_wp = 0
    missing_wp = 0
    
    print("🔍 Analyzing win probability fields...")
    
    for i, play in enumerate(plays):
        # Check for win probability related fields
        home_wp = play.get('homeWinProbability', '')
        away_wp = play.get('awayWinProbability', '')
        
        if home_wp or away_wp:
            has_wp += 1
            if home_wp:
                wp_values.add(f"Home: {home_wp}")
            if away_wp:
                wp_values.add(f"Away: {away_wp}")
        else:
            missing_wp += 1
        
        # Store field analysis
        for key, value in play.items():
            if 'win' in key.lower() or 'prob' in key.lower():
                if key not in wp_fields:
                    wp_fields[key] = {'count': 0, 'values': set(), 'missing': 0}
                
                if value and value != '':
                    wp_fields[key]['count'] += 1
                    wp_fields[key]['values'].add(str(value))
                else:
                    wp_fields[key]['missing'] += 1
    
    print(f"\n📊 Win Probability Analysis:")
    print(f"  Plays with win probability: {has_wp}")
    print(f"  Plays missing win probability: {missing_wp}")
    print(f"  Unique win probability values: {len(wp_values)}")
    
    print(f"\n🔍 Win Probability Fields Analysis:")
    for field, data in wp_fields.items():
        print(f"  {field}:")
        print(f"    Present: {data['count']}")
        print(f"    Missing: {data['missing']}")
        print(f"    Sample values: {list(data['values'])[:5]}")
        print()
    
    # Show sample plays with and without win probability
    print("📋 Sample plays WITH win probability:")
    count = 0
    for play in plays:
        if (play.get('homeWinProbability') or play.get('awayWinProbability')) and count < 5:
            print(f"  Play {play.get('playNumber', 'N/A')}: {play.get('playText', '')[:50]}...")
            print(f"    Home WP: {play.get('homeWinProbability')}")
            print(f"    Away WP: {play.get('awayWinProbability')}")
            print()
            count += 1
    
    print("📋 Sample plays MISSING win probability:")
    count = 0
    for play in plays:
        if not play.get('homeWinProbability') and not play.get('awayWinProbability') and count < 5:
            print(f"  Play {play.get('playNumber', 'N/A')}: {play.get('playText', '')[:50]}...")
            print(f"    Home WP: {play.get('homeWinProbability')}")
            print(f"    Away WP: {play.get('awayWinProbability')}")
            print()
            count += 1
    
    # Check if win probability is in a different structure
    print("🔍 Checking for alternative win probability structures...")
    
    # Look for nested win probability data
    nested_wp = 0
    for play in plays:
        for key, value in play.items():
            if isinstance(value, dict) and ('win' in key.lower() or 'prob' in key.lower()):
                nested_wp += 1
                print(f"  Found nested WP in {key}: {value}")
    
    if nested_wp > 0:
        print(f"  Found {nested_wp} plays with nested win probability data")
    else:
        print(f"  No nested win probability data found")
    
    # Check if win probability is in a separate array
    print(f"\n🔍 Checking for separate win probability data...")
    
    # Look for any field that might contain win probability
    wp_related_fields = []
    for play in plays:
        for key, value in play.items():
            if 'win' in key.lower() or 'prob' in key.lower() or 'percentage' in key.lower():
                if key not in wp_related_fields:
                    wp_related_fields.append(key)
    
    print(f"  Win probability related fields: {wp_related_fields}")
    
    # Check if there's a separate win probability endpoint
    print(f"\n🔍 Checking if CFBD has separate win probability endpoint...")
    print(f"  CFBD might require a separate API call for win probability data")
    print(f"  Similar to how ESPN has separate winprobability endpoint")
    
    return plays

if __name__ == "__main__":
    analyze_cfbd_win_probability()
