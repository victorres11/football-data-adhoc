#!/usr/bin/env python3
"""
Corrected analysis of Washington Huskies at Michigan Wolverines game
This version uses the actual game scores from plays rather than individual scoreValues
"""

import json
import os
from datetime import datetime

def load_data():
    """Load all game data"""
    with open('data/game_401752873/complete_game_data.json', 'r') as f:
        game_data = json.load(f)
    
    with open('data/game_401752873/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return game_data, teams_data

def get_team_name(team_id, teams_data):
    """Get team name from team ID"""
    team_id_str = str(team_id)
    if team_id_str in teams_data:
        return teams_data[team_id_str].get('displayName', f'Team {team_id}')
    return f'Team {team_id}'

def get_final_scores_from_plays(data, teams_data):
    """Get final scores by looking at the last play with score information"""
    print("=== CORRECTED SCORING ANALYSIS ===")
    
    plays = data.get('plays', {}).get('items', [])
    
    # Find the last play with score information
    last_play_with_scores = None
    for play in reversed(plays):
        if 'awayScore' in play and 'homeScore' in play:
            last_play_with_scores = play
            break
    
    if last_play_with_scores:
        away_score = last_play_with_scores.get('awayScore', 0)
        home_score = last_play_with_scores.get('homeScore', 0)
        
        # Determine which team is home/away
        competitions = data.get('header', {}).get('competitions', [])
        if competitions:
            competitors = competitions[0].get('competitors', [])
            for competitor in competitors:
                team_id = competitor.get('id')
                team_name = get_team_name(team_id, teams_data)
                home_away = competitor.get('homeAway', '')
                
                if home_away == 'home':
                    home_team_name = team_name
                elif home_away == 'away':
                    away_team_name = team_name
        
        print(f"Final Scores (from last play with scores):")
        print(f"  {away_team_name}: {away_score} points")
        print(f"  {home_team_name}: {home_score} points")
        
        return {
            away_team_name: away_score,
            home_team_name: home_score
        }
    
    return {}

def analyze_scoring_plays_detailed(data, teams_data):
    """Analyze individual scoring plays"""
    print("\n=== INDIVIDUAL SCORING PLAYS ===")
    
    plays = data.get('plays', {}).get('items', [])
    
    scoring_plays = []
    team_scores_from_plays = {}
    team_touchdowns = {}
    team_field_goals = {}
    
    for play in plays:
        if play.get('scoringPlay', False):
            scoring_plays.append(play)
            
            # Get team - for scoring plays, team info is directly in the play
            team = play.get('team', {})
            if team and '$ref' in team:
                # Extract team ID from the reference URL
                team_ref = team['$ref']
                team_id = team_ref.split('/')[-1].split('?')[0]  # Get the last part before query params
                team_name = get_team_name(team_id, teams_data)
                
                # Get points scored from the play
                points = play.get('scoreValue', 0)
                if team_name not in team_scores_from_plays:
                    team_scores_from_plays[team_name] = 0
                team_scores_from_plays[team_name] += points
                
                # Count touchdowns and field goals
                play_type = play.get('type', {}).get('text', '')
                if 'Touchdown' in play_type:
                    if team_name not in team_touchdowns:
                        team_touchdowns[team_name] = 0
                    team_touchdowns[team_name] += 1
                elif 'Field Goal' in play_type:
                    if team_name not in team_field_goals:
                        team_field_goals[team_name] = 0
                    team_field_goals[team_name] += 1
    
    print(f"Total scoring plays: {len(scoring_plays)}")
    
    print(f"\nScores from individual plays:")
    for team, points in team_scores_from_plays.items():
        print(f"  {team}: {points} points")
    
    print(f"\nTouchdowns by team:")
    for team, count in team_touchdowns.items():
        print(f"  {team}: {count} touchdowns")
    
    print(f"\nField goals by team:")
    for team, count in team_field_goals.items():
        print(f"  {team}: {count} field goals")
    
    return {
        'total_scoring_plays': len(scoring_plays),
        'team_scores_from_plays': team_scores_from_plays,
        'team_touchdowns': team_touchdowns,
        'team_field_goals': team_field_goals
    }

def main():
    print("Corrected Analysis: Washington Huskies at Michigan Wolverines")
    print("Game ID: 401752873 | Date: October 18, 2025")
    print("=" * 70)
    
    # Load all data
    game_data, teams_data = load_data()
    
    # Get final scores from game data
    final_scores = get_final_scores_from_plays(game_data, teams_data)
    
    # Analyze individual scoring plays
    scoring_analysis = analyze_scoring_plays_detailed(game_data, teams_data)
    
    # Compare the two methods
    print(f"\n=== COMPARISON ===")
    print("Final scores from game data vs Individual play scores:")
    for team, final_score in final_scores.items():
        play_score = scoring_analysis['team_scores_from_plays'].get(team, 0)
        difference = final_score - play_score
        print(f"  {team}:")
        print(f"    Game score: {final_score}")
        print(f"    Play scores: {play_score}")
        print(f"    Difference: {difference} (likely extra points)")
    
    # Save corrected analysis
    corrected_analysis = {
        'final_scores': final_scores,
        'scoring_analysis': scoring_analysis,
        'analyzed_at': datetime.now().isoformat()
    }
    
    os.makedirs('data/game_401752873', exist_ok=True)
    with open('data/game_401752873/corrected_analysis.json', 'w') as f:
        json.dump(corrected_analysis, f, indent=2)
    
    print(f"\nCorrected analysis saved to: data/game_401752873/corrected_analysis.json")

if __name__ == "__main__":
    main()
