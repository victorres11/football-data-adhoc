#!/usr/bin/env python3
"""
Extract top rushers and receivers from Purdue vs Minnesota game data
"""

import json

def extract_player_stats(data):
    """Extract top rushers and receivers from the leaders data"""
    
    leaders = data['leaders']
    
    # Leader 0 is Minnesota, Leader 1 is Purdue (based on the data structure)
    minnesota_leaders = leaders[0]['leaders']
    purdue_leaders = leaders[1]['leaders']
    
    # Extract rushing and receiving stats
    minnesota_rushers = []
    minnesota_receivers = []
    purdue_rushers = []
    purdue_receivers = []
    
    # Process Minnesota leaders
    for category in minnesota_leaders:
        if category['name'] == 'rushingYards' and 'leaders' in category:
            for leader in category['leaders']:
                athlete = leader['athlete']
                minnesota_rushers.append({
                    'name': athlete['fullName'],
                    'position': athlete['position']['abbreviation'],
                    'jersey': athlete['jersey'],
                    'stats': leader['displayValue'],
                    'yards': leader['mainStat']['value']
                })
        elif category['name'] == 'receivingYards' and 'leaders' in category:
            for leader in category['leaders']:
                athlete = leader['athlete']
                minnesota_receivers.append({
                    'name': athlete['fullName'],
                    'position': athlete['position']['abbreviation'],
                    'jersey': athlete['jersey'],
                    'stats': leader['displayValue'],
                    'yards': leader['mainStat']['value']
                })
    
    # Process Purdue leaders
    for category in purdue_leaders:
        if category['name'] == 'rushingYards' and 'leaders' in category:
            for leader in category['leaders']:
                athlete = leader['athlete']
                purdue_rushers.append({
                    'name': athlete['fullName'],
                    'position': athlete['position']['abbreviation'],
                    'jersey': athlete['jersey'],
                    'stats': leader['displayValue'],
                    'yards': leader['mainStat']['value']
                })
        elif category['name'] == 'receivingYards' and 'leaders' in category:
            for leader in category['leaders']:
                athlete = leader['athlete']
                purdue_receivers.append({
                    'name': athlete['fullName'],
                    'position': athlete['position']['abbreviation'],
                    'jersey': athlete['jersey'],
                    'stats': leader['displayValue'],
                    'yards': leader['mainStat']['value']
                })
    
    return {
        'purdue': {
            'rushers': purdue_rushers,
            'receivers': purdue_receivers
        },
        'minnesota': {
            'rushers': minnesota_rushers,
            'receivers': minnesota_receivers
        }
    }

def main():
    """Main function to extract player stats"""
    print("Purdue vs Minnesota - Top Player Stats Extraction")
    print("=" * 50)
    
    # Load Purdue game data
    with open('data/purdue/game_401752864/raw_game_data.json', 'r') as f:
        data = json.load(f)
    
    # Extract player stats
    player_stats = extract_player_stats(data)
    
    # Print results
    print("\nPurdue Top Players:")
    print("Top Rushers:")
    for i, rusher in enumerate(player_stats['purdue']['rushers'], 1):
        print(f"  {i}. #{rusher['jersey']} {rusher['name']} ({rusher['position']}) - {rusher['stats']}")
    
    print("\nTop Receivers:")
    for i, receiver in enumerate(player_stats['purdue']['receivers'], 1):
        print(f"  {i}. #{receiver['jersey']} {receiver['name']} ({receiver['position']}) - {receiver['stats']}")
    
    print("\nMinnesota Top Players:")
    print("Top Rushers:")
    for i, rusher in enumerate(player_stats['minnesota']['rushers'], 1):
        print(f"  {i}. #{rusher['jersey']} {rusher['name']} ({rusher['position']}) - {rusher['stats']}")
    
    print("\nTop Receivers:")
    for i, receiver in enumerate(player_stats['minnesota']['receivers'], 1):
        print(f"  {i}. #{receiver['jersey']} {receiver['name']} ({receiver['position']}) - {receiver['stats']}")
    
    # Save to file
    with open('data/purdue/game_401752864/player_stats.json', 'w') as f:
        json.dump(player_stats, f, indent=2)
    
    print(f"\n✓ Player stats saved to: data/purdue/game_401752864/player_stats.json")

if __name__ == "__main__":
    main()
