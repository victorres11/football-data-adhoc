#!/usr/bin/env python3
"""
Northwestern vs Penn State Scouting Report Analysis

Analyzes Northwestern's 22-21 upset victory over Penn State to create
a comprehensive scouting report focusing on tendencies, strengths, and weaknesses.
"""

import json
import math
from collections import defaultdict, Counter

def round_yards_needed(yards):
    """Round yards needed: 0.4 and below round down, 0.5+ round up"""
    if yards - int(yards) <= 0.4:
        return int(yards)
    else:
        return math.ceil(yards)

def is_successful_run(play):
    """Determine if a rush attempt is successful based on down and yards gained"""
    start_down = play.get('start', {}).get('down')
    start_distance = play.get('start', {}).get('distance')
    yards_gained = play.get('statYardage', 0)
    is_touchdown = play.get('scoringPlay', False)
    
    # Any touchdown is always successful
    if is_touchdown:
        return True, "Touchdown"
    
    # Calculate yards needed based on down
    if not start_down or not start_distance:
        return False, "Missing down/distance data"
    
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

def extract_team_info(data):
    """Extract team information and IDs"""
    teams = {}
    for team in data['boxscore']['teams']:
        team_id = team['team']['id']
        teams[team_id] = {
            'id': team_id,
            'name': team['team']['displayName'],
            'short_name': team['team']['shortDisplayName'],
            'abbreviation': team['team']['abbreviation'],
            'home_away': team['homeAway']
        }
    return teams

def analyze_offensive_plays(data, team_id):
    """Analyze all offensive plays for a team"""
    plays = []
    drives = data['drives']['previous']
    
    for drive in drives:
        if drive['team']['id'] == team_id:
            for play in drive['plays']:
                play_data = {
                    'id': play['id'],
                    'sequence': play['sequenceNumber'],
                    'text': play['text'],
                    'type': play.get('type', {}).get('text', ''),
                    'period': play['period']['number'],
                    'clock': play['clock']['displayValue'],
                    'scoring_play': play['scoringPlay'],
                    'start_down': play.get('start', {}).get('down'),
                    'start_distance': play.get('start', {}).get('distance'),
                    'start_yard_line': play.get('start', {}).get('yardLine'),
                    'end_down': play.get('end', {}).get('down'),
                    'end_distance': play.get('end', {}).get('distance'),
                    'end_yard_line': play.get('end', {}).get('yardLine'),
                    'yards_gained': play.get('statYardage', 0),
                    'away_score': play['awayScore'],
                    'home_score': play['homeScore']
                }
                plays.append(play_data)
    
    return plays

def analyze_play_selection(plays):
    """Analyze play selection tendencies"""
    analysis = {
        'total_plays': len(plays),
        'by_type': Counter(),
        'by_down': defaultdict(Counter),
        'by_quarter': defaultdict(Counter),
        'by_situation': defaultdict(Counter),
        'rush_attempts': [],
        'pass_attempts': [],
        'successful_runs': 0,
        'total_rush_yards': 0,
        'total_pass_yards': 0
    }
    
    for play in plays:
        play_type = play['type']
        down = play['start_down']
        quarter = play['period']
        yards = play['yards_gained']
        
        # Count by type
        analysis['by_type'][play_type] += 1
        
        # Count by down
        if down:
            analysis['by_down'][down][play_type] += 1
        
        # Count by quarter
        analysis['by_quarter'][quarter][play_type] += 1
        
        # Analyze rush attempts
        if play_type in ['Rush', 'Rushing Touchdown']:
            analysis['rush_attempts'].append(play)
            analysis['total_rush_yards'] += yards
            
            # Calculate successful run rate
            if play['start_down'] and play['start_distance']:
                success, reason = is_successful_run(play)
                if success:
                    analysis['successful_runs'] += 1
        
        # Analyze pass attempts
        elif play_type in ['Pass Reception', 'Pass Incompletion', 'Passing Touchdown']:
            analysis['pass_attempts'].append(play)
            if play_type == 'Pass Reception':
                analysis['total_pass_yards'] += yards
        
        # Situational analysis
        if down and play['start_distance']:
            if down == 1:
                analysis['by_situation']['1st_down'][play_type] += 1
            elif down == 2:
                analysis['by_situation']['2nd_down'][play_type] += 1
            elif down == 3:
                analysis['by_situation']['3rd_down'][play_type] += 1
            elif down == 4:
                analysis['by_situation']['4th_down'][play_type] += 1
    
    # Calculate efficiency metrics
    if analysis['rush_attempts']:
        analysis['successful_run_rate'] = (analysis['successful_runs'] / len(analysis['rush_attempts'])) * 100
        analysis['yards_per_rush'] = analysis['total_rush_yards'] / len(analysis['rush_attempts'])
    else:
        analysis['successful_run_rate'] = 0
        analysis['yards_per_rush'] = 0
    
    if analysis['pass_attempts']:
        analysis['yards_per_pass'] = analysis['total_pass_yards'] / len(analysis['pass_attempts'])
    else:
        analysis['yards_per_pass'] = 0
    
    return analysis

def analyze_scoring_drives(data, team_id):
    """Analyze scoring drives"""
    scoring_drives = []
    drives = data['drives']['previous']
    
    for drive in drives:
        if drive['team']['id'] == team_id:
            # Check if drive resulted in score
            has_scoring_play = any(play['scoringPlay'] for play in drive['plays'])
            if has_scoring_play:
                drive_analysis = {
                    'description': drive['description'],
                    'plays': len(drive['plays']),
                    'yards': drive['yards'],
                    'time_elapsed': drive['timeElapsed']['displayValue'],
                    'result': drive['result'],
                    'scoring_plays': [play for play in drive['plays'] if play['scoringPlay']],
                    'key_plays': []
                }
                
                # Identify key plays (big gains, conversions, etc.)
                for play in drive['plays']:
                    if (play.get('statYardage', 0) >= 15 or 
                        play['type']['text'] in ['Rushing Touchdown', 'Passing Touchdown'] or
                        (play.get('start', {}).get('down') == 3 and play.get('end', {}).get('down') == 1)):
                        drive_analysis['key_plays'].append({
                            'text': play['text'],
                            'type': play['type']['text'],
                            'yards': play.get('statYardage', 0)
                        })
                
                scoring_drives.append(drive_analysis)
    
    return scoring_drives

def analyze_turnovers(data, team_id):
    """Analyze turnovers for and against a team"""
    turnovers = {
        'forced': [],
        'committed': []
    }
    
    drives = data['drives']['previous']
    
    for drive in drives:
        for play in drive['plays']:
            play_type = play.get('type', {}).get('text', '')
            if play_type in ['Fumble Recovery', 'Interception']:
                # Determine if this team forced or committed the turnover
                if drive['team']['id'] == team_id:
                    # This team's drive - check if they lost possession
                    if play_type in ['Fumble Recovery', 'Interception']:
                        # Check if it's a turnover (not a recovery by the offense)
                        turnovers['committed'].append({
                            'type': play_type,
                            'text': play['text'],
                            'period': play['period']['number'],
                            'clock': play['clock']['displayValue'],
                            'score': f"{play['awayScore']}-{play['homeScore']}"
                        })
                else:
                    # Opponent's drive - check if this team forced turnover
                    turnovers['forced'].append({
                        'type': play_type,
                        'text': play['text'],
                        'period': play['period']['number'],
                        'clock': play['clock']['displayValue'],
                        'score': f"{play['awayScore']}-{play['homeScore']}"
                    })
    
    return turnovers

def analyze_defensive_performance(data, team_id):
    """Analyze defensive performance (opponent's offensive stats)"""
    # Find opponent team ID
    teams = extract_team_info(data)
    opponent_id = None
    for tid, team in teams.items():
        if tid != team_id:
            opponent_id = tid
            break
    
    if not opponent_id:
        return {}
    
    # Analyze opponent's offensive plays
    opponent_plays = analyze_offensive_plays(data, opponent_id)
    
    defensive_stats = {
        'plays_allowed': len(opponent_plays),
        'yards_allowed': sum(play['yards_gained'] for play in opponent_plays),
        'first_downs_allowed': 0,
        'third_down_stops': 0,
        'third_down_attempts': 0,
        'sacks': 0,
        'tackles_for_loss': 0
    }
    
    for play in opponent_plays:
        # Count first downs allowed
        if play['start_down'] == 1 and play['end_down'] == 1 and play['yards_gained'] >= 10:
            defensive_stats['first_downs_allowed'] += 1
        
        # Count third down stops
        if play['start_down'] == 3:
            defensive_stats['third_down_attempts'] += 1
            if play['end_down'] == 4:  # Stopped on third down
                defensive_stats['third_down_stops'] += 1
        
        # Look for defensive plays (sacks, TFLs)
        if 'sack' in play['text'].lower():
            defensive_stats['sacks'] += 1
        elif 'loss' in play['text'].lower() and play['yards_gained'] < 0:
            defensive_stats['tackles_for_loss'] += 1
    
    # Calculate third down stop rate
    if defensive_stats['third_down_attempts'] > 0:
        defensive_stats['third_down_stop_rate'] = (defensive_stats['third_down_stops'] / defensive_stats['third_down_attempts']) * 100
    else:
        defensive_stats['third_down_stop_rate'] = 0
    
    return defensive_stats

def build_game_narrative(data, teams):
    """Build quarter-by-quarter game narrative"""
    narrative = {
        'final_score': {},
        'quarters': {},
        'momentum_swings': [],
        'key_moments': []
    }
    
    # Get final score
    for team_id, team in teams.items():
        narrative['final_score'][team['name']] = {
            'score': data['boxscore']['teams'][0]['statistics'][0]['value'] if team['home_away'] == 'home' else data['boxscore']['teams'][1]['statistics'][0]['value'],
            'home_away': team['home_away']
        }
    
    # Analyze by quarter
    drives = data['drives']['previous']
    quarter_stats = defaultdict(lambda: {'plays': 0, 'yards': 0, 'scores': []})
    
    for drive in drives:
        quarter = drive['start']['period']['number']
        team_name = teams[drive['team']['id']]['name']
        
        quarter_stats[quarter]['plays'] += len(drive['plays'])
        quarter_stats[quarter]['yards'] += drive['yards']
        
        # Check for scoring
        if any(play['scoringPlay'] for play in drive['plays']):
            scoring_play = next(play for play in drive['plays'] if play['scoringPlay'])
            quarter_stats[quarter]['scores'].append({
                'team': team_name,
                'play': scoring_play['text'],
                'type': scoring_play['type']['text']
            })
    
    narrative['quarters'] = dict(quarter_stats)
    
    return narrative

def main():
    """Main analysis function"""
    print("Northwestern vs Penn State Scouting Report Analysis")
    print("=" * 60)
    
    # Load game data
    with open('../data/northwestern/game_401752866.json', 'r') as f:
        data = json.load(f)
    
    # Extract team information
    teams = extract_team_info(data)
    
    # Find Northwestern team ID
    northwestern_id = None
    for team_id, team in teams.items():
        if 'Northwestern' in team['name']:
            northwestern_id = team_id
            break
    
    if not northwestern_id:
        print("Error: Could not find Northwestern team ID")
        return
    
    northwestern_team = teams[northwestern_id]
    print(f"Analyzing: {northwestern_team['name']}")
    
    # Analyze Northwestern's offensive performance
    print("\n1. Analyzing Northwestern Offensive Plays...")
    northwestern_plays = analyze_offensive_plays(data, northwestern_id)
    play_selection = analyze_play_selection(northwestern_plays)
    
    # Analyze scoring drives
    print("2. Analyzing Scoring Drives...")
    scoring_drives = analyze_scoring_drives(data, northwestern_id)
    
    # Analyze turnovers
    print("3. Analyzing Turnovers...")
    turnovers = analyze_turnovers(data, northwestern_id)
    
    # Analyze defensive performance
    print("4. Analyzing Defensive Performance...")
    defensive_stats = analyze_defensive_performance(data, northwestern_id)
    
    # Build game narrative
    print("5. Building Game Narrative...")
    narrative = build_game_narrative(data, teams)
    
    # Compile comprehensive scouting report
    scouting_report = {
        'game_info': {
            'teams': teams,
            'northwestern_team': northwestern_team,
            'final_score': narrative['final_score']
        },
        'offensive_analysis': {
            'play_selection': play_selection,
            'scoring_drives': scoring_drives
        },
        'defensive_analysis': defensive_stats,
        'turnovers': turnovers,
        'game_narrative': narrative,
        'summary': {
            'total_offensive_plays': len(northwestern_plays),
            'successful_run_rate': play_selection.get('successful_run_rate', 0),
            'yards_per_rush': play_selection.get('yards_per_rush', 0),
            'yards_per_pass': play_selection.get('yards_per_pass', 0),
            'scoring_drives_count': len(scoring_drives),
            'turnover_margin': len(turnovers['forced']) - len(turnovers['committed'])
        }
    }
    
    # Save analysis files
    print("\n6. Saving Analysis Files...")
    
    # Save comprehensive report
    with open('../data/northwestern/scouting_report.json', 'w') as f:
        json.dump(scouting_report, f, indent=2)
    
    # Save individual components
    with open('../data/northwestern/offensive_analysis.json', 'w') as f:
        json.dump({
            'play_selection': play_selection,
            'scoring_drives': scoring_drives
        }, f, indent=2)
    
    with open('../data/northwestern/defensive_analysis.json', 'w') as f:
        json.dump(defensive_stats, f, indent=2)
    
    with open('../data/northwestern/key_plays.json', 'w') as f:
        json.dump({
            'turnovers': turnovers,
            'momentum_swings': narrative.get('momentum_swings', []),
            'key_moments': narrative.get('key_moments', [])
        }, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SCOUTING REPORT SUMMARY")
    print("=" * 60)
    print(f"Team: {northwestern_team['name']}")
    print(f"Total Offensive Plays: {scouting_report['summary']['total_offensive_plays']}")
    print(f"Successful Run Rate: {scouting_report['summary']['successful_run_rate']:.1f}%")
    print(f"Yards per Rush: {scouting_report['summary']['yards_per_rush']:.1f}")
    print(f"Yards per Pass: {scouting_report['summary']['yards_per_pass']:.1f}")
    print(f"Scoring Drives: {scouting_report['summary']['scoring_drives_count']}")
    print(f"Turnover Margin: {scouting_report['summary']['turnover_margin']:+d}")
    print(f"Turnovers Forced: {len(turnovers['forced'])}")
    print(f"Turnovers Committed: {len(turnovers['committed'])}")
    
    print(f"\nFiles saved:")
    print(f"- ../data/northwestern/scouting_report.json")
    print(f"- ../data/northwestern/offensive_analysis.json")
    print(f"- ../data/northwestern/defensive_analysis.json")
    print(f"- ../data/northwestern/key_plays.json")

if __name__ == "__main__":
    main()
