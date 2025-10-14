#!/usr/bin/env python3
"""
Generate possession times for Purdue vs Minnesota game
"""

import json
import os
from collections import defaultdict

def analyze_drives_for_possession_times(data, teams):
    """Analyze drives to calculate possession times by quarter"""
    print("Analyzing drives for possession times...")
    
    drives = []
    
    # Try different drive data structures
    if 'drives' in data:
        if 'previous' in data['drives']:
            drives = data['drives']['previous']
        elif 'items' in data['drives']:
            drives = data['drives']['items']
        else:
            print("No drives data available")
            return {}
    else:
        print("No drives data available")
        return {}
    
    quarter_stats = defaultdict(lambda: {
        'plays': 0, 
        'yards': 0, 
        'scores': [],
        'possession_times': defaultdict(lambda: 0)
    })
    
    for drive in drives:
        if 'start' not in drive or 'end' not in drive:
            continue
            
        start_quarter = drive['start']['period']['number']
        end_quarter = drive['end']['period']['number']
        
        # Handle team ID - could be direct ID or $ref
        if 'team' in drive:
            if isinstance(drive['team'], dict):
                if 'id' in drive['team']:
                    team_id = drive['team']['id']
                elif '$ref' in drive['team']:
                    # Extract team ID from $ref URL
                    ref_url = drive['team']['$ref']
                    if 'teams/2509' in ref_url:
                        team_id = '2509'  # Purdue
                    elif 'teams/135' in ref_url:
                        team_id = '135'  # Minnesota
                    else:
                        continue
                else:
                    continue
            else:
                team_id = drive['team']
        else:
            continue
            
        team_name = teams.get(team_id, {}).get('name', f'Team {team_id}')
        
        # Parse drive time (format: "2:48", "0:20", etc.)
        if 'timeElapsed' in drive and 'displayValue' in drive['timeElapsed']:
            time_str = drive['timeElapsed']['displayValue']
            try:
                minutes, seconds = map(int, time_str.split(':'))
                drive_seconds = minutes * 60 + seconds
            except:
                drive_seconds = 0
        else:
            drive_seconds = 0
        
        # Get play count - use offensivePlays if available, otherwise estimate from description
        play_count = drive.get('offensivePlays', 0)
        if play_count == 0 and 'description' in drive:
            # Try to extract play count from description like "6 plays, 15 yards, 2:29"
            try:
                desc_parts = drive['description'].split(',')
                if len(desc_parts) > 0:
                    play_count = int(desc_parts[0].split()[0])
            except:
                play_count = 1  # Fallback
        
        # Handle drives that span quarters
        if start_quarter == end_quarter:
            # Drive stays in same quarter
            quarter_stats[start_quarter]['plays'] += play_count
            quarter_stats[start_quarter]['yards'] += drive.get('yards', 0)
            quarter_stats[start_quarter]['possession_times'][team_name] += drive_seconds
        else:
            # Drive spans quarters - split the time based on clock positions
            if 'start' in drive and 'end' in drive:
                start_clock = drive['start'].get('clock', {}).get('displayValue', '15:00')
                end_clock = drive['end'].get('clock', {}).get('displayValue', '0:00')
                
                try:
                    # Parse clock times (format: "14:09", "11:02", etc.)
                    start_min, start_sec = map(int, start_clock.split(':'))
                    end_min, end_sec = map(int, end_clock.split(':'))
                    
                    start_total_sec = start_min * 60 + start_sec
                    end_total_sec = end_min * 60 + end_sec
                    
                    # Calculate time in each quarter
                    time_in_start_quarter = start_total_sec  # Time remaining in start quarter
                    time_in_end_quarter = 900 - end_total_sec  # Time elapsed in end quarter (15:00 - end_clock)
                    
                    # Ensure we don't exceed total drive time
                    total_split_time = time_in_start_quarter + time_in_end_quarter
                    if total_split_time > drive_seconds:
                        # If split exceeds drive time, assign proportionally
                        ratio = drive_seconds / total_split_time if total_split_time > 0 else 0
                        time_in_start_quarter = int(time_in_start_quarter * ratio)
                        time_in_end_quarter = drive_seconds - time_in_start_quarter
                    
                    # Assign plays and yards to both quarters, but split time
                    quarter_stats[start_quarter]['plays'] += play_count
                    quarter_stats[start_quarter]['yards'] += drive.get('yards', 0)
                    quarter_stats[start_quarter]['possession_times'][team_name] += time_in_start_quarter
                    
                    quarter_stats[end_quarter]['plays'] += play_count
                    quarter_stats[end_quarter]['yards'] += drive.get('yards', 0)
                    quarter_stats[end_quarter]['possession_times'][team_name] += time_in_end_quarter
                except:
                    # Fallback: assign full time to end quarter
                    quarter_stats[end_quarter]['plays'] += play_count
                    quarter_stats[end_quarter]['yards'] += drive.get('yards', 0)
                    quarter_stats[end_quarter]['possession_times'][team_name] += drive_seconds
        
        # Check for scoring
        if drive.get('isScore', False):
            scoring_quarter = end_quarter if start_quarter != end_quarter else start_quarter
            quarter_stats[scoring_quarter]['scores'].append({
                'team': team_name,
                'play': drive.get('description', 'Score'),
                'type': drive.get('result', 'Unknown')
            })
    
    # Convert possession times back to MM:SS format
    for quarter, stats in quarter_stats.items():
        possession_times = {}
        for team, total_seconds in stats['possession_times'].items():
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            possession_times[team] = f"{minutes}:{seconds:02d}"
        stats['possession_times'] = possession_times
    
    return dict(quarter_stats)

def main():
    """Main function to generate Purdue possession times"""
    print("Purdue vs Minnesota Possession Times Generation")
    print("=" * 50)
    
    # Load existing Purdue data
    with open('data/purdue/game_401752864/raw_game_data.json', 'r') as f:
        data = json.load(f)
    
    # Define teams
    teams = {
        '2509': {
            'id': '2509',
            'name': 'Purdue Boilermakers',
            'short_name': 'Purdue',
            'abbreviation': 'PUR',
            'home_away': 'away'
        },
        '135': {
            'id': '135',
            'name': 'Minnesota Golden Gophers',
            'short_name': 'Minnesota',
            'abbreviation': 'MIN',
            'home_away': 'home'
        }
    }
    
    # Generate possession times
    quarters = analyze_drives_for_possession_times(data, teams)
    
    # Load existing game narrative
    with open('data/purdue/game_401752864/game_narrative.json', 'r') as f:
        narrative = json.load(f)
    
    # Update with possession times
    for quarter, stats in quarters.items():
        if quarter in narrative['quarters']:
            narrative['quarters'][quarter]['possession_times'] = stats['possession_times']
    
    # Save updated game narrative
    with open('data/purdue/game_401752864/game_narrative.json', 'w') as f:
        json.dump(narrative, f, indent=2)
    
    print("✓ Updated Purdue game narrative with possession times")
    
    # Print possession times summary
    print("\nPossession Times by Quarter:")
    for quarter, stats in quarters.items():
        print(f"Q{quarter}: {stats['possession_times']}")
    
    print(f"\n✓ Purdue possession times generation complete!")

if __name__ == "__main__":
    main()
