import json
import requests
import os
from datetime import datetime
import re

# Game configuration
GAME_ID = 401752876
GAME_DATE = "October 18, 2025"
TEAM_PERSPECTIVE = "Rutgers"
TEAM_COLORS = {
    "Rutgers": {"primary": "#D21034", "secondary": "#FFFFFF"},  # Scarlet Red and White
    "Oregon": {"primary": "#154733", "secondary": "#FEE123"}  # Green and Yellow
}

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please ensure it exists with your API key.")
        return None

def fetch_raw_game_data():
    """Fetch raw game data from ESPN API using the same approach as Northwestern"""
    print(f"Fetching raw game data for Game ID {GAME_ID}...")
    
    # Fetch header data
    header_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{GAME_ID}"
    plays_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{GAME_ID}/competitions/{GAME_ID}/plays"
    boxscore_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{GAME_ID}/competitions/{GAME_ID}/boxscore"
    
    try:
        # Fetch all data
        header_response = requests.get(header_url)
        header_response.raise_for_status()
        header_data = header_response.json()
        
        plays_response = requests.get(plays_url)
        plays_response.raise_for_status()
        plays_data = plays_response.json()
        
        # Try to fetch boxscore, but don't fail if it's not available
        try:
            boxscore_response = requests.get(boxscore_url)
            boxscore_response.raise_for_status()
            boxscore_data = boxscore_response.json()
        except requests.exceptions.RequestException:
            print("Warning: Boxscore not available, using empty boxscore")
            boxscore_data = {}
        
        # Combine data into single structure (same as Northwestern)
        combined_data = {
            "header": header_data,
            "plays": plays_data,
            "boxscore": boxscore_data,
            "drives": plays_data.get("drives", {}),
            "fetched_at": datetime.now().isoformat()
        }
        
        # Create directory if it doesn't exist
        os.makedirs('data/oregon_rutgers', exist_ok=True)
        
        # Save raw data
        with open('data/oregon_rutgers/raw_game_data.json', 'w') as f:
            json.dump(combined_data, f, indent=2)
        
        print(f"✓ Raw game data saved to data/oregon_rutgers/raw_game_data.json")
        return combined_data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching raw game data: {e}")
        return None

def extract_team_info(data):
    """Extract team information and basic statistics"""
    teams_data = {}
    
    # Extract from header competitors
    competitors = data.get('header', {}).get('competitions', [{}])[0].get('competitors', [])
    game_name = data.get('header', {}).get('name', '')
    
    # Determine team names from game name
    # Game name format: "Oregon Ducks at Rutgers Scarlet Knights"
    if 'Oregon' in game_name and 'Rutgers' in game_name:
        # Oregon is away (first), Rutgers is home (second)
        team_mapping = {}
        for i, comp in enumerate(competitors):
            team_id = comp.get('id')
            home_away = comp.get('homeAway', '')
            if home_away == 'away':
                team_mapping[team_id] = 'Oregon'
            elif home_away == 'home':
                team_mapping[team_id] = 'Rutgers'
    else:
        # Fallback to unknown
        team_mapping = {comp.get('id'): 'Unknown' for comp in competitors}
    
    for comp in competitors:
        team_id = comp.get('id')
        team_name = team_mapping.get(team_id, 'Unknown')
        team_abbrev = comp.get('team', {}).get('abbreviation', 'UNK')
        
        teams_data[team_id] = {
            'id': team_id,
            'name': team_name,
            'display_name': team_name,
            'abbreviation': team_abbrev,
            'color': comp.get('team', {}).get('color', '#000000'),
            'alternate_color': comp.get('team', {}).get('alternateColor', '#FFFFFF'),
            'stats': {}
        }
    
    # Extract stats from boxscore
    boxscore = data.get('boxscore', {})
    if 'teams' in boxscore:
        for team_boxscore in boxscore['teams']:
            team_id = team_boxscore['team']['id']
            if team_id in teams_data:
                for stat in team_boxscore.get('statistics', []):
                    teams_data[team_id]['stats'][stat['label']] = stat['displayValue']
    
    return teams_data

def extract_scoring_drives(data):
    """Extract quarter-by-quarter scores and running totals from drives data"""
    scoring_drives = [d for d in data.get('drives', {}).get('items', []) if d.get('isScore', False)]
    
    quarter_scores = {1: {'Rutgers': 0, 'Oregon': 0}, 2: {'Rutgers': 0, 'Oregon': 0}, 
                     3: {'Rutgers': 0, 'Oregon': 0}, 4: {'Rutgers': 0, 'Oregon': 0}}
    
    running_totals = {'Rutgers': 0, 'Oregon': 0}
    
    for drive in scoring_drives:
        team_display = drive['team']['displayName']
        result = drive.get('result', '')
        quarter = drive.get('period', 1)
        
        # Map team names to our standard format
        if 'Rutgers' in team_display:
            team = 'Rutgers'
        elif 'Oregon' in team_display:
            team = 'Oregon'
        else:
            team = team_display
        
        points = 0
        if result == 'TD':
            points = 7
        elif result == 'FG':
            points = 3
        
        if points > 0:
            quarter_scores[quarter][team] += points
            running_totals[team] += points
    
    # Calculate running totals for each quarter
    final_running_totals = {q: {'Rutgers': 0, 'Oregon': 0} for q in range(1, 5)}
    current_rutgers_score = 0
    current_oregon_score = 0
    
    for q in range(1, 5):
        current_rutgers_score += quarter_scores[q]['Rutgers']
        current_oregon_score += quarter_scores[q]['Oregon']
        final_running_totals[q]['Rutgers'] = current_rutgers_score
        final_running_totals[q]['Oregon'] = current_oregon_score
    
    return quarter_scores, final_running_totals

def extract_play_by_play_data(data, teams_data):
    """Extract 3rd/4th down data and explosive plays from play-by-play"""
    drives = data.get('drives', {}).get('items', [])
    
    third_down_data = {'Rutgers': {'attempts': 0, 'conversions': 0}, 'Oregon': {'attempts': 0, 'conversions': 0}}
    fourth_down_data = {'Rutgers': {'attempts': 0, 'conversions': 0}, 'Oregon': {'attempts': 0, 'conversions': 0}}
    explosive_plays = {'Rutgers': [], 'Oregon': []}
    fourth_down_plays = {'Rutgers': [], 'Oregon': []}
    
    for drive in drives:
        if 'plays' in drive and 'items' in drive['plays']:
            for play in drive['plays']['items']:
                if not isinstance(play, dict):
                    continue
                
                # Determine which team this play belongs to
                team_participants = play.get('teamParticipants', [])
                current_team = None
                
                for participant in team_participants:
                    if participant.get('type') == 'offense':
                        team_id = participant.get('id', '')
                        # Map team ID to standard name using teams_data
                        for tid, team_info in teams_data.items():
                            if tid == team_id:
                                current_team = team_info['name']
                                break
                        break
                
                if not current_team:
                    continue
                
                # Extract play details
                yards = play.get('statYardage', 0)
                down = play.get('start', {}).get('down', 0)
                distance = play.get('start', {}).get('distance', 0)
                play_type = play.get('type', {}).get('text', '')
                play_text = play.get('text', '')
                quarter = play.get('period', {}).get('number', 0)
                time = play.get('clock', {}).get('displayValue', 'N/A')
                
                # Filter out special teams plays
                if play_type in ["Kickoff", "Punt", "Extra Point Good", "Field Goal Good", "Timeout", "End Period", "End of Half", "End of Game"]:
                    continue
                
                # 3rd down analysis
                if down == 3:
                    third_down_data[current_team]['attempts'] += 1
                    if yards >= distance:
                        third_down_data[current_team]['conversions'] += 1
                
                # 4th down analysis
                if down == 4:
                    fourth_down_data[current_team]['attempts'] += 1
                    if yards >= distance:
                        fourth_down_data[current_team]['conversions'] += 1
                    
                    # Store 4th down play details
                    fourth_down_plays[current_team].append({
                        'yards': yards,
                        'distance': distance,
                        'converted': yards >= distance,
                        'quarter': quarter,
                        'time': time,
                        'play_type': play_type,
                        'description': play_text
                    })
                
                # Explosive plays (20+ yards)
                if yards >= 20:
                    explosive_plays[current_team].append({
                        'yards': yards,
                        'quarter': quarter,
                        'time': time,
                        'down_distance': f"{down} & {distance}",
                        'play_type': play_type,
                        'description': play_text
                    })
    
    return third_down_data, fourth_down_data, explosive_plays, fourth_down_plays

def extract_player_leaders(data):
    """Extract top rushers and receivers from the game"""
    # This would typically come from the boxscore or play-by-play analysis
    # For now, we'll create placeholder data that can be filled from actual analysis
    player_leaders = {
        'Rutgers': {
            'rushing': [],
            'receiving': []
        },
        'Oregon': {
            'rushing': [],
            'receiving': []
        }
    }
    
    # TODO: Implement actual player leader extraction from play-by-play data
    # This would involve tracking individual player stats from each play
    
    return player_leaders

def calculate_possession_times(data):
    """Calculate possession time per quarter"""
    drives = data.get('drives', {}).get('items', [])
    
    possession_times = {1: {'Rutgers': 0, 'Oregon': 0}, 2: {'Rutgers': 0, 'Oregon': 0}, 
                       3: {'Rutgers': 0, 'Oregon': 0}, 4: {'Rutgers': 0, 'Oregon': 0}}
    
    for drive in drives:
        if 'plays' in drive and 'items' in drive['plays']:
            # Determine which team this drive belongs to
            team_display = drive.get('team', {}).get('displayName', '')
            if 'Rutgers' in team_display:
                team = 'Rutgers'
            elif 'Oregon' in team_display:
                team = 'Oregon'
            else:
                continue
            
            # Calculate drive duration
            drive_duration = 0
            for play in drive['plays']['items']:
                if isinstance(play, dict):
                    # Extract time from play clock
                    clock = play.get('clock', {})
                    if 'displayValue' in clock:
                        time_str = clock['displayValue']
                        # Parse time string (e.g., "12:34")
                        if ':' in time_str:
                            minutes, seconds = map(int, time_str.split(':'))
                            drive_duration += minutes * 60 + seconds
            
            # Add to appropriate quarter
            quarter = drive.get('period', 1)
            possession_times[quarter][team] += drive_duration
    
    return possession_times

def extract_turnover_data(data, teams_data):
    """Extract turnover information"""
    drives = data.get('drives', {}).get('items', [])
    
    turnovers = {'Rutgers': 0, 'Oregon': 0}
    turnover_types = {'Rutgers': [], 'Oregon': []}
    
    for drive in drives:
        if 'plays' in drive and 'items' in drive['plays']:
            for play in drive['plays']['items']:
                if not isinstance(play, dict):
                    continue
                
                play_type = play.get('type', {}).get('text', '')
                play_text = play.get('text', '')
                
                # Check for turnover indicators
                if any(keyword in play_text.lower() for keyword in ['interception', 'fumble', 'recovered', 'lost']):
                    # Determine which team this affects
                    team_participants = play.get('teamParticipants', [])
                    for participant in team_participants:
                        if participant.get('type') == 'offense':
                            team_id = participant.get('id', '')
                            # Map team ID to standard name using teams_data
                            for tid, team_info in teams_data.items():
                                if tid == team_id:
                                    team_name = team_info['name']
                                    if team_name in ['Rutgers', 'Oregon']:
                                        turnovers[team_name] += 1
                                        turnover_types[team_name].append({
                                            'type': play_type,
                                            'description': play_text,
                                            'quarter': play.get('period', {}).get('number', 0)
                                        })
                                    break
    
    return turnovers, turnover_types

def main():
    print("Oregon vs Rutgers Game Data Extraction")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Fetch raw game data
    raw_data = fetch_raw_game_data()
    if not raw_data:
        return
    
    print("\nExtracting team information...")
    teams_data = extract_team_info(raw_data)
    
    print("Extracting scoring data...")
    quarter_scores, running_quarter_totals = extract_scoring_drives(raw_data)
    
    # Calculate final scores from the last quarter
    final_scores = {
        'Rutgers': running_quarter_totals[4]['Rutgers'],
        'Oregon': running_quarter_totals[4]['Oregon']
    }
    
    print("Extracting play-by-play data...")
    third_down_data, fourth_down_data, explosive_plays, fourth_down_plays = extract_play_by_play_data(raw_data, teams_data)
    
    print("Extracting player leaders...")
    player_leaders = extract_player_leaders(raw_data)
    
    print("Calculating possession times...")
    possession_times = calculate_possession_times(raw_data)
    
    print("Extracting turnover data...")
    turnovers, turnover_types = extract_turnover_data(raw_data, teams_data)
    
    # Compile all extracted data
    extracted_data = {
        'game_id': GAME_ID,
        'date': GAME_DATE,
        'team_perspective': TEAM_PERSPECTIVE,
        'team_colors': TEAM_COLORS,
        'teams_data': teams_data,
        'final_scores': final_scores,
        'quarter_scores': quarter_scores,
        'running_quarter_scores': running_quarter_totals,
        'third_down_analysis': {
            'Rutgers': f"{third_down_data['Rutgers']['conversions']}/{third_down_data['Rutgers']['attempts']} ({third_down_data['Rutgers']['conversions']/max(third_down_data['Rutgers']['attempts'], 1)*100:.1f}%)",
            'Oregon': f"{third_down_data['Oregon']['conversions']}/{third_down_data['Oregon']['attempts']} ({third_down_data['Oregon']['conversions']/max(third_down_data['Oregon']['attempts'], 1)*100:.1f}%)"
        },
        'fourth_down_analysis': {
            'Rutgers': f"{fourth_down_data['Rutgers']['conversions']}/{fourth_down_data['Rutgers']['attempts']} ({fourth_down_data['Rutgers']['conversions']/max(fourth_down_data['Rutgers']['attempts'], 1)*100:.1f}%)",
            'Oregon': f"{fourth_down_data['Oregon']['conversions']}/{fourth_down_data['Oregon']['attempts']} ({fourth_down_data['Oregon']['conversions']/max(fourth_down_data['Oregon']['attempts'], 1)*100:.1f}%)"
        },
        'explosive_plays': explosive_plays,
        'fourth_down_plays': fourth_down_plays,
        'player_leaders': player_leaders,
        'possession_times': possession_times,
        'turnovers': turnovers,
        'turnover_types': turnover_types,
        'extracted_at': datetime.now().isoformat()
    }
    
    # Save extracted data
    output_file = 'data/oregon_rutgers/extracted_data.json'
    with open(output_file, 'w') as f:
        json.dump(extracted_data, f, indent=2)
    
    print(f"\n✓ Extracted data saved to {output_file}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("EXTRACTION SUMMARY")
    print("=" * 50)
    print(f"Game: Oregon vs Rutgers (ID: {GAME_ID})")
    print(f"Date: {GAME_DATE}")
    print(f"Final Score: Rutgers {final_scores['Rutgers']}, Oregon {final_scores['Oregon']}")
    print(f"3rd Down: Rutgers {third_down_data['Rutgers']['conversions']}/{third_down_data['Rutgers']['attempts']}, Oregon {third_down_data['Oregon']['conversions']}/{third_down_data['Oregon']['attempts']}")
    print(f"4th Down: Rutgers {fourth_down_data['Rutgers']['conversions']}/{fourth_down_data['Rutgers']['attempts']}, Oregon {fourth_down_data['Oregon']['conversions']}/{fourth_down_data['Oregon']['attempts']}")
    print(f"Explosive Plays: Rutgers {len(explosive_plays['Rutgers'])}, Oregon {len(explosive_plays['Oregon'])}")
    print(f"Turnovers: Rutgers {turnovers['Rutgers']}, Oregon {turnovers['Oregon']}")

if __name__ == "__main__":
    main()