#!/usr/bin/env python3
"""
Calculate Successful Run Rate for Maryland rushing attempts.

Success Criteria:
- 1st Down: Gain ≥40% of yards to go (round 0.4 down, 0.5+ up)
- 2nd Down: Gain ≥60% of yards to go (round 0.4 down, 0.5+ up)  
- 3rd/4th Down: Gain 100% of yards to go (convert) OR touchdown
- Any Down: Touchdown = always successful
"""

import json
import math

def round_yards_needed(yards):
    """Round yards needed: 0.4 and below round down, 0.5+ round up"""
    if yards - int(yards) <= 0.4:
        return int(yards)
    else:
        return math.ceil(yards)

def is_successful_run(play):
    """Determine if a rush attempt is successful based on down and yards gained"""
    start_down = play['startDown']
    start_distance = play['startDistance']
    yards_gained = play['statYardage']
    is_touchdown = play['scoringPlay']
    
    # Any touchdown is always successful
    if is_touchdown:
        return True, "Touchdown"
    
    # Calculate yards needed based on down
    if start_down == 1:
        # 1st down: need 40% of yards to go
        yards_needed = start_distance * 0.4
        yards_needed_rounded = round_yards_needed(yards_needed)
        success = yards_gained >= yards_needed_rounded
        reason = f"1st down: need {yards_needed_rounded} yards (40% of {start_distance}), gained {yards_gained}"
        
    elif start_down == 2:
        # 2nd down: need 60% of yards to go
        yards_needed = start_distance * 0.6
        yards_needed_rounded = round_yards_needed(yards_needed)
        success = yards_gained >= yards_needed_rounded
        reason = f"2nd down: need {yards_needed_rounded} yards (60% of {start_distance}), gained {yards_gained}"
        
    elif start_down in [3, 4]:
        # 3rd/4th down: need 100% of yards to go (convert)
        success = yards_gained >= start_distance
        reason = f"{start_down}rd down: need {start_distance} yards (100% to convert), gained {yards_gained}"
        
    else:
        # Fallback for any other down
        success = False
        reason = f"Unknown down: {start_down}"
    
    return success, reason

def calculate_successful_run_rate():
    """Calculate successful run rate for all Maryland rush attempts"""
    
    # Read the rush attempts data
    with open('maryland_rush_attempts.json', 'r') as f:
        plays = json.load(f)
    
    total_attempts = len(plays)
    successful_runs = 0
    analyzed_plays = []
    
    # Analyze each play
    for play in plays:
        is_successful, reason = is_successful_run(play)
        
        if is_successful:
            successful_runs += 1
        
        # Add analysis to play data
        play_analysis = play.copy()
        play_analysis['isSuccessful'] = is_successful
        play_analysis['successReason'] = reason
        
        # Calculate yards needed for display
        start_down = play['startDown']
        start_distance = play['startDistance']
        
        if start_down == 1:
            yards_needed = round_yards_needed(start_distance * 0.4)
        elif start_down == 2:
            yards_needed = round_yards_needed(start_distance * 0.6)
        elif start_down in [3, 4]:
            yards_needed = start_distance
        else:
            yards_needed = 0
            
        play_analysis['yardsNeeded'] = yards_needed
        analyzed_plays.append(play_analysis)
    
    # Calculate success rate
    success_rate = (successful_runs / total_attempts) * 100
    
    # Create output structure
    output = {
        "summary": {
            "totalAttempts": total_attempts,
            "successfulRuns": successful_runs,
            "successfulRunRate": f"{success_rate:.1f}%"
        },
        "plays": analyzed_plays
    }
    
    # Write results to file
    with open('maryland_successful_runs_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print(f"Maryland Successful Run Rate Analysis")
    print(f"=====================================")
    print(f"Total Rush Attempts: {total_attempts}")
    print(f"Successful Runs: {successful_runs}")
    print(f"Successful Run Rate: {success_rate:.1f}%")
    print(f"\nResults saved to: maryland_successful_runs_analysis.json")
    
    return output

if __name__ == "__main__":
    calculate_successful_run_rate()
