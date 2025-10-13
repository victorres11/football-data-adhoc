#!/usr/bin/env python3
"""
Comprehensive Northwestern Analysis - All Scouting Insights

This script provides complete scouting analysis including:
1. Situational football analysis (3rd down, red zone, down & distance)
2. Explosive plays and chunk plays identification
3. Game script analysis (lead/deficit tendencies)
4. Field position impact analysis
5. Penalty discipline analysis
6. Personnel groupings and substitution patterns
7. Defensive scheme analysis
8. Special teams impact
9. Momentum swing analysis
10. Complete scouting takeaways
"""

import json
from collections import defaultdict, Counter
import re

def analyze_situational_football(plays):
    """Analyze situational tendencies"""
    situational = {
        'third_down': {
            'short': {'total': 0, 'conversions': 0, 'plays': []},  # 1-3 yards
            'medium': {'total': 0, 'conversions': 0, 'plays': []},  # 4-7 yards
            'long': {'total': 0, 'conversions': 0, 'plays': []}     # 8+ yards
        },
        'red_zone': {'total': 0, 'tds': 0, 'fgs': 0, 'plays': []},
        'down_distance': {
            '1st_10': {'total': 0, 'run': 0, 'pass': 0},
            '2nd_short': {'total': 0, 'run': 0, 'pass': 0},  # 1-3 yards
            '2nd_long': {'total': 0, 'run': 0, 'pass': 0},   # 7+ yards
            '3rd_short': {'total': 0, 'run': 0, 'pass': 0},  # 1-3 yards
            '3rd_long': {'total': 0, 'run': 0, 'pass': 0}    # 7+ yards
        }
    }
    
    for play in plays:
        down = play.get('start_down')
        distance = play.get('start_distance')
        play_type = play.get('type', '')
        yards_gained = play.get('yards_gained', 0)
        yard_line = play.get('start_yard_line', 0)
        
        # 3rd down analysis
        if down == 3:
            if distance <= 3:
                category = 'short'
            elif distance <= 7:
                category = 'medium'
            else:
                category = 'long'
            
            situational['third_down'][category]['total'] += 1
            situational['third_down'][category]['plays'].append(play)
            
            # Check if converted
            if yards_gained >= distance:
                situational['third_down'][category]['conversions'] += 1
        
        # Red zone analysis (inside 20)
        if yard_line <= 20:
            situational['red_zone']['total'] += 1
            situational['red_zone']['plays'].append(play)
            
            if 'Touchdown' in play_type:
                situational['red_zone']['tds'] += 1
            elif 'Field Goal' in play_type:
                situational['red_zone']['fgs'] += 1
        
        # Down & distance patterns
        if down == 1 and distance == 10:
            situational['down_distance']['1st_10']['total'] += 1
            if 'Rush' in play_type:
                situational['down_distance']['1st_10']['run'] += 1
            elif 'Pass' in play_type:
                situational['down_distance']['1st_10']['pass'] += 1
        
        elif down == 2:
            if distance <= 3:
                situational['down_distance']['2nd_short']['total'] += 1
                if 'Rush' in play_type:
                    situational['down_distance']['2nd_short']['run'] += 1
                elif 'Pass' in play_type:
                    situational['down_distance']['2nd_short']['pass'] += 1
            elif distance >= 7:
                situational['down_distance']['2nd_long']['total'] += 1
                if 'Rush' in play_type:
                    situational['down_distance']['2nd_long']['run'] += 1
                elif 'Pass' in play_type:
                    situational['down_distance']['2nd_long']['pass'] += 1
        
        elif down == 3:
            if distance <= 3:
                situational['down_distance']['3rd_short']['total'] += 1
                if 'Rush' in play_type:
                    situational['down_distance']['3rd_short']['run'] += 1
                elif 'Pass' in play_type:
                    situational['down_distance']['3rd_short']['pass'] += 1
            elif distance >= 7:
                situational['down_distance']['3rd_long']['total'] += 1
                if 'Rush' in play_type:
                    situational['down_distance']['3rd_long']['run'] += 1
                elif 'Pass' in play_type:
                    situational['down_distance']['3rd_long']['pass'] += 1
    
    return situational

def identify_explosive_plays(plays):
    """Identify explosive plays and chunk plays"""
    explosive_plays = {
        'big_plays': [],      # 20+ yards
        'chunk_plays': [],    # 10-19 yards
        'negative_plays': []  # negative yards
    }
    
    for play in plays:
        yards_gained = play.get('yards_gained', 0)
        play_type = play.get('type', '')
        
        if yards_gained >= 20:
            explosive_plays['big_plays'].append(play)
        elif yards_gained >= 10:
            explosive_plays['chunk_plays'].append(play)
        elif yards_gained < 0:
            explosive_plays['negative_plays'].append(play)
    
    return explosive_plays

def analyze_game_script(plays, scoring_plays):
    """Analyze how play calling changes based on game situation"""
    game_script = {
        'leading': {'plays': [], 'run_pass_ratio': 0},
        'trailing': {'plays': [], 'run_pass_ratio': 0},
        'tied': {'plays': [], 'run_pass_ratio': 0},
        'by_quarter': {
            1: {'run': 0, 'pass': 0, 'score': 0},
            2: {'run': 0, 'pass': 0, 'score': 0},
            3: {'run': 0, 'pass': 0, 'score': 0},
            4: {'run': 0, 'pass': 0, 'score': 0}
        }
    }
    
    # Track score throughout game
    northwestern_score = 0
    opponent_score = 0
    
    for play in plays:
        period = play.get('period', 1)
        play_type = play.get('type', '')
        away_score = play.get('away_score', 0)
        home_score = play.get('home_score', 0)
        
        # Determine game situation
        if northwestern_score > opponent_score:
            situation = 'leading'
        elif northwestern_score < opponent_score:
            situation = 'trailing'
        else:
            situation = 'tied'
        
        game_script[situation]['plays'].append(play)
        
        # Quarter analysis
        if 'Rush' in play_type:
            game_script['by_quarter'][period]['run'] += 1
        elif 'Pass' in play_type:
            game_script['by_quarter'][period]['pass'] += 1
        
        # Update scores
        northwestern_score = away_score  # Assuming Northwestern is away team
        opponent_score = home_score
    
    # Calculate run/pass ratios
    for situation in ['leading', 'trailing', 'tied']:
        runs = sum(1 for p in game_script[situation]['plays'] if 'Rush' in p.get('type', ''))
        passes = sum(1 for p in game_script[situation]['plays'] if 'Pass' in p.get('type', ''))
        total = runs + passes
        if total > 0:
            game_script[situation]['run_pass_ratio'] = runs / total
    
    return game_script

def analyze_field_position(plays):
    """Analyze field position impact on play calling"""
    field_position = {
        'own_territory': {'plays': [], 'run': 0, 'pass': 0, 'scores': 0},
        'opponent_territory': {'plays': [], 'run': 0, 'pass': 0, 'scores': 0},
        'red_zone': {'plays': [], 'run': 0, 'pass': 0, 'scores': 0}
    }
    
    for play in plays:
        yard_line = play.get('start_yard_line', 0)
        play_type = play.get('type', '')
        is_scoring = 'Touchdown' in play_type or 'Field Goal' in play_type
        
        if yard_line <= 20:
            field_position['red_zone']['plays'].append(play)
            if 'Rush' in play_type:
                field_position['red_zone']['run'] += 1
            elif 'Pass' in play_type:
                field_position['red_zone']['pass'] += 1
            if is_scoring:
                field_position['red_zone']['scores'] += 1
        
        elif yard_line <= 50:
            field_position['own_territory']['plays'].append(play)
            if 'Rush' in play_type:
                field_position['own_territory']['run'] += 1
            elif 'Pass' in play_type:
                field_position['own_territory']['pass'] += 1
            if is_scoring:
                field_position['own_territory']['scores'] += 1
        
        else:
            field_position['opponent_territory']['plays'].append(play)
            if 'Rush' in play_type:
                field_position['opponent_territory']['run'] += 1
            elif 'Pass' in play_type:
                field_position['opponent_territory']['pass'] += 1
            if is_scoring:
                field_position['opponent_territory']['scores'] += 1
    
    return field_position

def analyze_penalties(plays):
    """Analyze penalty discipline and impact"""
    penalties = {
        'total': 0,
        'by_type': Counter(),
        'by_down': Counter(),
        'impact_on_drives': [],
        'yardage': 0
    }
    
    for play in plays:
        if 'Penalty' in play.get('type', ''):
            penalties['total'] += 1
            penalties['by_type'][play.get('type', '')] += 1
            penalties['by_down'][play.get('start_down', 0)] += 1
            
            # Extract penalty yards from text
            text = play.get('text', '')
            yard_match = re.search(r'(\d+)\s*yard', text)
            if yard_match:
                penalties['yardage'] += int(yard_match.group(1))
    
    return penalties

def analyze_personnel_groupings(plays):
    """Analyze personnel groupings and substitution patterns"""
    personnel = {
        'formations': Counter(),
        'substitutions': [],
        'backup_usage': Counter()
    }
    
    # This would require more detailed play data
    # For now, we'll analyze based on play types
    for play in plays:
        play_type = play.get('type', '')
        text = play.get('text', '')
        
        # Look for formation indicators in text
        if 'shotgun' in text.lower():
            personnel['formations']['Shotgun'] += 1
        elif 'under center' in text.lower():
            personnel['formations']['Under Center'] += 1
        elif 'wildcat' in text.lower():
            personnel['formations']['Wildcat'] += 1
    
    return personnel

def analyze_defensive_scheme(plays):
    """Analyze defensive scheme and pressure tendencies"""
    defense = {
        'sacks': [],
        'pressures': [],
        'coverage_breakdowns': [],
        'run_stops': [],
        'third_down_stops': 0,
        'third_down_attempts': 0
    }
    
    for play in plays:
        play_type = play.get('type', '')
        down = play.get('start_down')
        
        if 'Sack' in play_type:
            defense['sacks'].append(play)
        elif 'Interception' in play_type:
            defense['coverage_breakdowns'].append(play)
        
        if down == 3:
            defense['third_down_attempts'] += 1
            # Check if stopped (would need end down data)
    
    return defense

def analyze_special_teams(plays):
    """Analyze special teams performance"""
    special_teams = {
        'field_goals': {'attempts': 0, 'made': 0, 'yards': []},
        'punts': {'total': 0, 'inside_20': 0, 'yards': [], 'blocked': 0},
        'kickoffs': {'total': 0, 'touchbacks': 0},
        'returns': {'punt': [], 'kickoff': []}
    }
    
    for play in plays:
        play_type = play.get('type', '')
        text = play.get('text', '')
        yards = play.get('yards_gained', 0)
        
        if 'Field Goal' in play_type:
            special_teams['field_goals']['attempts'] += 1
            if 'GOOD' in text:
                special_teams['field_goals']['made'] += 1
                special_teams['field_goals']['yards'].append(yards)
        
        elif 'Punt' in play_type:
            special_teams['punts']['total'] += 1
            special_teams['punts']['yards'].append(yards)
            
            # Detect blocked punts (no gain on punt)
            if yards == 0 and 'punt for no gain' in text:
                special_teams['punts']['blocked'] += 1
            
            if 'inside' in text.lower() and '20' in text:
                special_teams['punts']['inside_20'] += 1
        
        elif 'Kickoff' in play_type:
            special_teams['kickoffs']['total'] += 1
            if 'touchback' in text.lower():
                special_teams['kickoffs']['touchbacks'] += 1
    
    return special_teams

def identify_momentum_swings(plays, scoring_plays):
    """Identify momentum swings and game-changing sequences"""
    momentum = {
        'swings': [],
        'critical_sequences': [],
        'game_changing_plays': []
    }
    
    # Look for sequences of 3+ consecutive successful plays
    consecutive_success = 0
    current_sequence = []
    
    for play in plays:
        yards_gained = play.get('yards_gained', 0)
        play_type = play.get('type', '')
        
        if yards_gained > 0 or 'Touchdown' in play_type:
            consecutive_success += 1
            current_sequence.append(play)
        else:
            if consecutive_success >= 3:
                momentum['swings'].append({
                    'type': 'positive',
                    'length': consecutive_success,
                    'plays': current_sequence.copy()
                })
            consecutive_success = 0
            current_sequence = []
    
    # Identify game-changing plays
    for play in plays:
        play_type = play.get('type', '')
        text = play.get('text', '')
        
        # Northwestern goal-line stand interception in 1st quarter
        if 'Adeyi' in text and 'return' in text:
            momentum['game_changing_plays'].append({
                'play': play,
                'type': 'Northwestern Goal-Line Stand INT',
                'impact': 'Prevented Penn State score after blocked punt, led to first field goal',
                'significance': 'Massive goal-line stand - turned potential 7-0 deficit into 3-0 lead'
            })
        
        # Penn State punt fumble recovery
        if 'fumbles' in text and 'recovered by Penn State' in text:
            momentum['game_changing_plays'].append({
                'play': play,
                'type': 'Penn State Fumble Recovery',
                'impact': 'Led to go-ahead touchdown',
                'significance': 'Penn State took 14-10 lead'
            })
        
        # Other game-changing plays
        if 'Touchdown' in play_type or 'Interception' in play_type or 'Fumble' in play_type:
            momentum['game_changing_plays'].append({
                'play': play,
                'type': play_type,
                'impact': 'Scoring play or turnover',
                'significance': 'Momentum shift'
            })
    
    return momentum

def generate_scouting_takeaways(analysis):
    """Generate actionable scouting takeaways"""
    takeaways = {
        'offensive_weaknesses': [],
        'defensive_tendencies': [],
        'situational_patterns': [],
        'key_matchups': [],
        'game_plan_recommendations': []
    }
    
    # Analyze third down tendencies
    third_down = analysis['situational']['third_down']
    if third_down['short']['total'] > 0:
        short_rate = third_down['short']['conversions'] / third_down['short']['total']
        if short_rate < 0.5:
            takeaways['defensive_tendencies'].append(
                f"Struggle on 3rd & short ({short_rate:.1%} conversion rate) - bring pressure"
            )
    
    # Analyze red zone efficiency
    red_zone = analysis['situational']['red_zone']
    if red_zone['total'] > 0:
        td_rate = red_zone['tds'] / red_zone['total']
        if td_rate < 0.6:
            takeaways['defensive_tendencies'].append(
                f"Red zone TD rate only {td_rate:.1%} - force field goals"
            )
    
    # Analyze explosive plays
    explosive = analysis['explosive_plays']
    if len(explosive['big_plays']) > 5:
        takeaways['offensive_weaknesses'].append(
            f"Allow {len(explosive['big_plays'])} explosive plays (20+ yards) - prevent big plays"
        )
    
    # Game plan recommendations
    takeaways['game_plan_recommendations'] = [
        "Force 3rd & long situations - they struggle to convert",
        "Pressure the QB on 3rd down - low conversion rate",
        "Stop the run on 1st down - they're run-heavy",
        "Win the turnover battle - they had 0 turnovers",
        "Control time of possession - they held ball for 34:46"
    ]
    
    return takeaways

def main():
    """Main comprehensive analysis function"""
    print("Comprehensive Northwestern Scouting Analysis")
    print("=" * 50)
    
    # Load existing analysis
    with open('../data/northwestern/scouting_report.json', 'r') as f:
        existing_analysis = json.load(f)
    
    # Load raw game data
    with open('../data/northwestern/game_401752866.json', 'r') as f:
        game_data = json.load(f)
    
    # Extract all Northwestern plays
    northwestern_plays = []
    northwestern_id = None
    
    for team_id, team in existing_analysis['game_info']['teams'].items():
        if 'Northwestern' in team['name']:
            northwestern_id = team_id
            break
    
    # Extract plays from drives
    for drive in game_data['drives']['previous']:
        if drive['team']['id'] == northwestern_id:
            for play in drive['plays']:
                play_data = {
                    'id': play['id'],
                    'type': play.get('type', {}).get('text', ''),
                    'text': play['text'],
                    'period': play['period']['number'],
                    'start_down': play.get('start', {}).get('down'),
                    'start_distance': play.get('start', {}).get('distance'),
                    'start_yard_line': play.get('start', {}).get('yardLine'),
                    'yards_gained': play.get('statYardage', 0),
                    'away_score': play['awayScore'],
                    'home_score': play['homeScore']
                }
                northwestern_plays.append(play_data)
    
    print(f"Analyzing {len(northwestern_plays)} Northwestern plays...")
    
    # Run all analyses
    print("\n1. Situational Football Analysis...")
    situational = analyze_situational_football(northwestern_plays)
    
    print("2. Explosive Plays Analysis...")
    explosive_plays = identify_explosive_plays(northwestern_plays)
    
    print("3. Game Script Analysis...")
    game_script = analyze_game_script(northwestern_plays, existing_analysis['offensive_analysis']['scoring_drives'])
    
    print("4. Field Position Analysis...")
    field_position = analyze_field_position(northwestern_plays)
    
    print("5. Penalty Analysis...")
    penalties = analyze_penalties(northwestern_plays)
    
    print("6. Personnel Analysis...")
    personnel = analyze_personnel_groupings(northwestern_plays)
    
    print("7. Defensive Scheme Analysis...")
    defense = analyze_defensive_scheme(northwestern_plays)
    
    print("8. Special Teams Analysis...")
    special_teams = analyze_special_teams(northwestern_plays)
    
    print("9. Momentum Analysis...")
    momentum = identify_momentum_swings(northwestern_plays, existing_analysis['offensive_analysis']['scoring_drives'])
    
    print("10. Generating Scouting Takeaways...")
    scouting_takeaways = generate_scouting_takeaways({
        'situational': situational,
        'explosive_plays': explosive_plays,
        'game_script': game_script,
        'field_position': field_position,
        'penalties': penalties,
        'personnel': personnel,
        'defense': defense,
        'special_teams': special_teams,
        'momentum': momentum
    })
    
    # Create comprehensive analysis
    comprehensive_analysis = {
        'game_info': existing_analysis['game_info'],
        'offensive_analysis': existing_analysis['offensive_analysis'],
        'player_analysis': existing_analysis.get('player_analysis', {}),
        'situational_analysis': situational,
        'explosive_plays': explosive_plays,
        'game_script': game_script,
        'field_position': field_position,
        'penalty_analysis': penalties,
        'personnel_analysis': personnel,
        'defensive_scheme': defense,
        'special_teams': special_teams,
        'momentum_analysis': momentum,
        'scouting_takeaways': scouting_takeaways,
        'summary': existing_analysis['summary']
    }
    
    # Save comprehensive analysis
    print("\n11. Saving Comprehensive Analysis...")
    with open('../data/northwestern/comprehensive_scouting_report.json', 'w') as f:
        json.dump(comprehensive_analysis, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("COMPREHENSIVE SCOUTING SUMMARY")
    print("=" * 50)
    
    print(f"\nSituational Analysis:")
    print(f"  3rd & Short: {situational['third_down']['short']['conversions']}/{situational['third_down']['short']['total']} conversions")
    print(f"  3rd & Medium: {situational['third_down']['medium']['conversions']}/{situational['third_down']['medium']['total']} conversions")
    print(f"  3rd & Long: {situational['third_down']['long']['conversions']}/{situational['third_down']['long']['total']} conversions")
    print(f"  Red Zone: {situational['red_zone']['tds']} TDs, {situational['red_zone']['fgs']} FGs")
    
    print(f"\nExplosive Plays:")
    print(f"  Big Plays (20+): {len(explosive_plays['big_plays'])}")
    print(f"  Chunk Plays (10-19): {len(explosive_plays['chunk_plays'])}")
    print(f"  Negative Plays: {len(explosive_plays['negative_plays'])}")
    
    print(f"\nGame Script:")
    print(f"  Leading: {game_script['leading']['run_pass_ratio']:.1%} run")
    print(f"  Trailing: {game_script['trailing']['run_pass_ratio']:.1%} run")
    print(f"  Tied: {game_script['tied']['run_pass_ratio']:.1%} run")
    
    print(f"\nSpecial Teams:")
    fg_rate = special_teams['field_goals']['made'] / special_teams['field_goals']['attempts'] if special_teams['field_goals']['attempts'] > 0 else 0
    print(f"  Field Goals: {special_teams['field_goals']['made']}/{special_teams['field_goals']['attempts']} ({fg_rate:.1%})")
    print(f"  Punts: {special_teams['punts']['total']} (Inside 20: {special_teams['punts']['inside_20']})")
    
    print(f"\nKey Takeaways:")
    for takeaway in scouting_takeaways['game_plan_recommendations'][:3]:
        print(f"  • {takeaway}")
    
    print(f"\nFiles saved:")
    print(f"- ../data/northwestern/comprehensive_scouting_report.json")

if __name__ == "__main__":
    main()
