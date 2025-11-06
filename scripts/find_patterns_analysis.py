#!/usr/bin/env python3
"""
Find interesting patterns in Washington and Wisconsin play-by-play data
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.load_advanced_pbp_data import load_team_data

def analyze_patterns():
    """Run comprehensive pattern analysis"""
    
    print("=" * 80)
    print("PATTERN ANALYSIS: Washington vs Wisconsin")
    print("=" * 80)
    
    # Load data
    wash_data = load_team_data("Washington")
    wisc_data = load_team_data("Wisconsin")
    
    wash_plays = [p for p in wash_data['all_plays'] if p.get('offense', '').lower() == 'washington']
    wisc_plays = [p for p in wisc_data['all_plays'] if p.get('offense', '').lower() == 'wisconsin']
    
    print(f"\nWashington: {len(wash_plays)} offensive plays across {wash_data['total_games']} games")
    print(f"Wisconsin: {len(wisc_plays)} offensive plays across {wisc_data['total_games']} games")
    
    # Pattern 1: PPA distribution by game situation
    print("\n" + "=" * 80)
    print("PATTERN 1: PPA Performance by Down and Distance")
    print("=" * 80)
    analyze_ppa_by_situation(wash_plays, wisc_plays)
    
    # Pattern 2: Explosive play frequency by quarter
    print("\n" + "=" * 80)
    print("PATTERN 2: Explosive Play Distribution by Quarter")
    print("=" * 80)
    analyze_explosive_by_quarter(wash_plays, wisc_plays)
    
    # Pattern 3: Turnover timing patterns
    print("\n" + "=" * 80)
    print("PATTERN 3: Turnover Timing Analysis")
    print("=" * 80)
    analyze_turnover_timing(wash_data, wisc_data)
    
    # Pattern 4: Penalty correlation with explosive plays
    print("\n" + "=" * 80)
    print("PATTERN 4: Penalty Impact on Explosive Plays")
    print("=" * 80)
    analyze_penalty_explosive_correlation(wash_plays, wisc_plays)
    
    # Pattern 5: Middle 8 performance vs other quarters
    print("\n" + "=" * 80)
    print("PATTERN 5: Middle 8 vs Regular Quarter Performance")
    print("=" * 80)
    analyze_middle8_vs_regular(wash_plays, wisc_plays)
    
    # Pattern 6: Field position efficiency
    print("\n" + "=" * 80)
    print("PATTERN 6: Field Position Efficiency")
    print("=" * 80)
    analyze_field_position_efficiency(wash_plays, wisc_plays)
    
    # Pattern 7: Drive success after explosive plays
    print("\n" + "=" * 80)
    print("PATTERN 7: Drive Outcomes After Explosive Plays")
    print("=" * 80)
    analyze_post_explosive_drives(wash_data, wisc_data)
    
    # Pattern 8: Conference vs Non-Conference performance
    print("\n" + "=" * 80)
    print("PATTERN 8: Conference vs Non-Conference Performance")
    print("=" * 80)
    analyze_conference_split(wash_plays, wisc_plays)

def analyze_ppa_by_situation(wash_plays, wisc_plays):
    """Analyze PPA by down and distance"""
    def get_ppa_stats(plays, team_name):
        by_down_distance = defaultdict(list)
        for play in plays:
            ppa = play.get('ppa')
            if ppa is not None and play.get('play_classification') != 'special_teams':
                down = play.get('down', 0)
                distance = play.get('distance', 0)
                key = f"{down} & {distance}"
                by_down_distance[key].append(float(ppa))
        
        stats = {}
        for key, ppas in by_down_distance.items():
            if len(ppas) >= 3:  # Only include situations with 3+ plays
                stats[key] = {
                    'count': len(ppas),
                    'avg': sum(ppas) / len(ppas),
                    'max': max(ppas),
                    'min': min(ppas)
                }
        return stats
    
    wash_stats = get_ppa_stats(wash_plays, "Washington")
    wisc_stats = get_ppa_stats(wisc_plays, "Wisconsin")
    
    # Find situations where teams differ significantly
    all_situations = set(list(wash_stats.keys()) + list(wisc_stats.keys()))
    
    print("\nSituations with significant PPA differences (min 3 plays each):")
    differences = []
    for sit in all_situations:
        if sit in wash_stats and sit in wisc_stats:
            diff = wash_stats[sit]['avg'] - wisc_stats[sit]['avg']
            if abs(diff) > 0.3:  # Significant difference
                differences.append((sit, diff, wash_stats[sit], wisc_stats[sit]))
    
    differences.sort(key=lambda x: abs(x[1]), reverse=True)
    for sit, diff, wash_s, wisc_s in differences[:10]:
        print(f"  {sit:15} | Wash: {wash_s['avg']:6.3f} ({wash_s['count']:2} plays) | "
              f"Wisc: {wisc_s['avg']:6.3f} ({wisc_s['count']:2} plays) | Diff: {diff:+6.3f}")

def analyze_explosive_by_quarter(wash_plays, wisc_plays):
    """Analyze explosive play distribution"""
    def get_explosive_stats(plays):
        by_quarter = defaultdict(int)
        total_by_quarter = defaultdict(int)
        for play in plays:
            if play.get('play_classification') != 'special_teams':
                qtr = play.get('period', 0)
                total_by_quarter[qtr] += 1
                if play.get('explosive_play'):
                    by_quarter[qtr] += 1
        
        return {q: (by_quarter[q], total_by_quarter[q], 
                    by_quarter[q] / total_by_quarter[q] * 100 if total_by_quarter[q] > 0 else 0)
                for q in total_by_quarter}
    
    wash_exp = get_explosive_stats(wash_plays)
    wisc_exp = get_explosive_stats(wisc_plays)
    
    print("\nExplosive Play Rate by Quarter:")
    print(f"{'Quarter':<10} | {'Washington':<20} | {'Wisconsin':<20}")
    print("-" * 60)
    for qtr in sorted(set(list(wash_exp.keys()) + list(wisc_exp.keys()))):
        wash_count, wash_total, wash_pct = wash_exp.get(qtr, (0, 0, 0))
        wisc_count, wisc_total, wisc_pct = wisc_exp.get(qtr, (0, 0, 0))
        print(f"Q{qtr:<9} | {wash_count:2}/{wash_total:3} ({wash_pct:5.1f}%) | "
              f"{wisc_count:2}/{wisc_total:3} ({wisc_pct:5.1f}%)")

def analyze_turnover_timing(wash_data, wisc_data):
    """Analyze when turnovers occur"""
    def analyze_turnovers(plays, team_name):
        turnovers = [p for p in plays if p.get('turnover')]
        by_quarter = Counter(p.get('period') for p in turnovers)
        by_down = Counter(p.get('down') for p in turnovers)
        by_field_pos = []
        for p in turnovers:
            ytg = p.get('yards_to_goal', 0)
            if ytg > 0:
                if ytg <= 20:
                    by_field_pos.append('Red Zone')
                elif ytg <= 40:
                    by_field_pos.append('Opponent Territory')
                else:
                    by_field_pos.append('Own Territory')
        
        return {
            'total': len(turnovers),
            'by_quarter': dict(by_quarter),
            'by_down': dict(by_down),
            'by_field_pos': Counter(by_field_pos)
        }
    
    wash_to = analyze_turnovers(wash_data['all_plays'], "Washington")
    wisc_to = analyze_turnovers(wisc_data['all_plays'], "Wisconsin")
    
    print(f"\nWashington Turnovers: {wash_to['total']}")
    print(f"  By Quarter: {wash_to['by_quarter']}")
    print(f"  By Down: {wash_to['by_down']}")
    print(f"  By Field Position: {dict(wash_to['by_field_pos'])}")
    
    print(f"\nWisconsin Turnovers: {wisc_to['total']}")
    print(f"  By Quarter: {wisc_to['by_quarter']}")
    print(f"  By Down: {wisc_to['by_down']}")
    print(f"  By Field Position: {dict(wisc_to['by_field_pos'])}")

def analyze_penalty_explosive_correlation(wash_plays, wisc_plays):
    """Check if penalties correlate with explosive plays"""
    def analyze_correlation(plays):
        # Plays with penalties in the same drive
        penalty_drives = set()
        explosive_drives = set()
        
        for play in plays:
            drive_id = play.get('drive_id')
            game_id = play.get('game_id')
            drive_key = f"{game_id}_{drive_id}"
            if play.get('penalty_type'):
                penalty_drives.add(drive_key)
            if play.get('explosive_play') and play.get('play_classification') != 'special_teams':
                explosive_drives.add(drive_key)
        
        # Drives with both penalties and explosive plays
        both = penalty_drives & explosive_drives
        
        return {
            'penalty_drives': len(penalty_drives),
            'explosive_drives': len(explosive_drives),
            'both': len(both),
            'correlation': len(both) / len(penalty_drives) * 100 if penalty_drives else 0
        }
    
    wash_corr = analyze_correlation(wash_plays)
    wisc_corr = analyze_correlation(wisc_plays)
    
    print(f"\nWashington:")
    print(f"  Drives with penalties: {wash_corr['penalty_drives']}")
    print(f"  Drives with explosive plays: {wash_corr['explosive_drives']}")
    print(f"  Drives with both: {wash_corr['both']} ({wash_corr['correlation']:.1f}% of penalty drives)")
    
    print(f"\nWisconsin:")
    print(f"  Drives with penalties: {wisc_corr['penalty_drives']}")
    print(f"  Drives with explosive plays: {wisc_corr['explosive_drives']}")
    print(f"  Drives with both: {wisc_corr['both']} ({wisc_corr['correlation']:.1f}% of penalty drives)")

def analyze_middle8_vs_regular(wash_plays, wisc_plays):
    """Compare Middle 8 performance to regular quarters"""
    def compare_performance(plays):
        middle8 = [p for p in plays if p.get('middle_eight')]
        regular = [p for p in plays if not p.get('middle_eight') and p.get('play_classification') != 'special_teams']
        
        def get_stats(play_list):
            ppas = [float(p.get('ppa')) for p in play_list if p.get('ppa') is not None]
            explosive = sum(1 for p in play_list if p.get('explosive_play'))
            return {
                'plays': len(play_list),
                'avg_ppa': sum(ppas) / len(ppas) if ppas else 0,
                'explosive_rate': explosive / len(play_list) * 100 if play_list else 0
            }
        
        return {
            'middle8': get_stats(middle8),
            'regular': get_stats(regular)
        }
    
    wash_perf = compare_performance(wash_plays)
    wisc_perf = compare_performance(wisc_plays)
    
    print("\nWashington:")
    print(f"  Middle 8:  {wash_perf['middle8']['plays']} plays, "
          f"PPA: {wash_perf['middle8']['avg_ppa']:.3f}, "
          f"Explosive: {wash_perf['middle8']['explosive_rate']:.1f}%")
    print(f"  Regular:   {wash_perf['regular']['plays']} plays, "
          f"PPA: {wash_perf['regular']['avg_ppa']:.3f}, "
          f"Explosive: {wash_perf['regular']['explosive_rate']:.1f}%")
    
    print("\nWisconsin:")
    print(f"  Middle 8:  {wisc_perf['middle8']['plays']} plays, "
          f"PPA: {wisc_perf['middle8']['avg_ppa']:.3f}, "
          f"Explosive: {wisc_perf['middle8']['explosive_rate']:.1f}%")
    print(f"  Regular:   {wisc_perf['regular']['plays']} plays, "
          f"PPA: {wisc_perf['regular']['avg_ppa']:.3f}, "
          f"Explosive: {wisc_perf['regular']['explosive_rate']:.1f}%")

def analyze_field_position_efficiency(wash_plays, wisc_plays):
    """Analyze PPA by field position"""
    def get_field_pos_stats(plays):
        zones = {
            'Own 0-20': (0, 20),
            'Own 21-40': (21, 40),
            'Own 41-50': (41, 50),
            'Opp 50-40': (51, 60),
            'Opp 39-20': (61, 80),
            'Red Zone': (81, 100)
        }
        
        zone_stats = defaultdict(lambda: {'ppas': [], 'explosive': 0, 'total': 0})
        
        for play in plays:
            if play.get('play_classification') != 'special_teams':
                ytg = play.get('yards_to_goal', 0)
                ppa = play.get('ppa')
                
                for zone_name, (min_ytg, max_ytg) in zones.items():
                    if min_ytg <= ytg <= max_ytg:
                        zone_stats[zone_name]['total'] += 1
                        if ppa is not None:
                            zone_stats[zone_name]['ppas'].append(float(ppa))
                        if play.get('explosive_play'):
                            zone_stats[zone_name]['explosive'] += 1
                        break
        
        return {zone: {
            'avg_ppa': sum(stats['ppas']) / len(stats['ppas']) if stats['ppas'] else 0,
            'explosive_rate': stats['explosive'] / stats['total'] * 100 if stats['total'] > 0 else 0,
            'plays': stats['total']
        } for zone, stats in zone_stats.items()}
    
    wash_zones = get_field_pos_stats(wash_plays)
    wisc_zones = get_field_pos_stats(wisc_plays)
    
    print("\nField Position Efficiency:")
    print(f"{'Zone':<20} | {'Washington PPA':<15} | {'Wisconsin PPA':<15}")
    print("-" * 60)
    for zone in ['Own 0-20', 'Own 21-40', 'Own 41-50', 'Opp 50-40', 'Opp 39-20', 'Red Zone']:
        wash_ppa = wash_zones.get(zone, {}).get('avg_ppa', 0)
        wisc_ppa = wisc_zones.get(zone, {}).get('avg_ppa', 0)
        wash_count = wash_zones.get(zone, {}).get('plays', 0)
        wisc_count = wisc_zones.get(zone, {}).get('plays', 0)
        print(f"{zone:<20} | {wash_ppa:6.3f} ({wash_count:3}) | {wisc_ppa:6.3f} ({wisc_count:3})")

def analyze_post_explosive_drives(wash_data, wisc_data):
    """Analyze what happens after explosive plays"""
    def analyze_drives(plays, team_name):
        explosive_plays = [p for p in plays if p.get('explosive_play') and p.get('play_classification') != 'special_teams']
        
        drive_outcomes = []
        for exp_play in explosive_plays:
            drive_id = exp_play.get('drive_id')
            game_id = exp_play.get('game_id')
            
            # Find all plays in this drive after the explosive play
            drive_plays = [p for p in plays 
                          if p.get('drive_id') == drive_id and p.get('game_id') == game_id]
            
            # Check if drive ended in score
            scored = any(p.get('scoring') for p in drive_plays)
            turnover = any(p.get('turnover') for p in drive_plays)
            
            drive_outcomes.append({
                'scored': scored,
                'turnover': turnover,
                'explosive_yards': exp_play.get('yards_gained', 0)
            })
        
        total = len(drive_outcomes) if drive_outcomes else 1
        return {
            'total_explosive': len(explosive_plays),
            'scored': sum(1 for d in drive_outcomes if d['scored']),
            'turnover': sum(1 for d in drive_outcomes if d['turnover']),
            'neither': sum(1 for d in drive_outcomes if not d['scored'] and not d['turnover'])
        }
    
    wash_drives = analyze_drives(wash_data['all_plays'], "Washington")
    wisc_drives = analyze_drives(wisc_data['all_plays'], "Wisconsin")
    
    print(f"\nWashington Drives with Explosive Plays:")
    print(f"  Total: {wash_drives['total_explosive']}")
    if wash_drives['total_explosive'] > 0:
        print(f"  Resulted in Score: {wash_drives['scored']} ({wash_drives['scored']/wash_drives['total_explosive']*100:.1f}%)")
        print(f"  Resulted in Turnover: {wash_drives['turnover']} ({wash_drives['turnover']/wash_drives['total_explosive']*100:.1f}%)")
        print(f"  Neither: {wash_drives['neither']} ({wash_drives['neither']/wash_drives['total_explosive']*100:.1f}%)")
    
    print(f"\nWisconsin Drives with Explosive Plays:")
    print(f"  Total: {wisc_drives['total_explosive']}")
    if wisc_drives['total_explosive'] > 0:
        print(f"  Resulted in Score: {wisc_drives['scored']} ({wisc_drives['scored']/wisc_drives['total_explosive']*100:.1f}%)")
        print(f"  Resulted in Turnover: {wisc_drives['turnover']} ({wisc_drives['turnover']/wisc_drives['total_explosive']*100:.1f}%)")
        print(f"  Neither: {wisc_drives['neither']} ({wisc_drives['neither']/wisc_drives['total_explosive']*100:.1f}%)")

def analyze_conference_split(wash_plays, wisc_plays):
    """Compare conference vs non-conference performance"""
    def split_performance(plays):
        conf = [p for p in plays if p.get('is_conference')]
        non_conf = [p for p in plays if not p.get('is_conference')]
        
        def get_stats(play_list):
            ppas = [float(p.get('ppa')) for p in play_list if p.get('ppa') is not None and p.get('play_classification') != 'special_teams']
            explosive = sum(1 for p in play_list if p.get('explosive_play') and p.get('play_classification') != 'special_teams')
            return {
                'plays': len(play_list),
                'avg_ppa': sum(ppas) / len(ppas) if ppas else 0,
                'explosive_rate': explosive / len(play_list) * 100 if play_list else 0
            }
        
        return {
            'conference': get_stats(conf),
            'non_conference': get_stats(non_conf)
        }
    
    wash_split = split_performance(wash_plays)
    wisc_split = split_performance(wisc_plays)
    
    print("\nWashington:")
    print(f"  Conference:     PPA: {wash_split['conference']['avg_ppa']:.3f}, "
          f"Explosive: {wash_split['conference']['explosive_rate']:.1f}%")
    print(f"  Non-Conference: PPA: {wash_split['non_conference']['avg_ppa']:.3f}, "
          f"Explosive: {wash_split['non_conference']['explosive_rate']:.1f}%")
    
    print("\nWisconsin:")
    print(f"  Conference:     PPA: {wisc_split['conference']['avg_ppa']:.3f}, "
          f"Explosive: {wisc_split['conference']['explosive_rate']:.1f}%")
    print(f"  Non-Conference: PPA: {wisc_split['non_conference']['avg_ppa']:.3f}, "
          f"Explosive: {wisc_split['non_conference']['explosive_rate']:.1f}%")

if __name__ == "__main__":
    analyze_patterns()

