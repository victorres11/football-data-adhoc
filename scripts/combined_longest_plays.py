#!/usr/bin/env python3
"""
Find the top 10 longest plays from both teams in Northwestern vs Penn State game
Game ID: 401752866
"""

import json

def load_game_data():
    """Load the Northwestern vs Penn State game data"""
    with open('data/northwestern/game_401752866.json', 'r') as f:
        return json.load(f)

def get_all_plays(data):
    """Get all plays from both teams"""
    print("Analyzing Northwestern vs Penn State game for all plays...")
    
    # Get drives data
    drives = data.get('drives', {}).get('items', [])
    
    # Team IDs
    northwestern_id = "77"  # Away team
    penn_state_id = "213"   # Home team
    
    all_plays = []
    
    for drive in drives:
        if 'plays' in drive and 'items' in drive['plays']:
            for play in drive['plays']['items']:
                # Skip if play is not a dictionary
                if not isinstance(play, dict):
                    continue
                
                # Check team participants to identify the offensive team
                team_participants = play.get('teamParticipants', [])
                offensive_team = None
                team_name = None
                
                for participant in team_participants:
                    if participant.get('type') == 'offense':
                        team_id = participant.get('id', '')
                        if team_id == northwestern_id:
                            offensive_team = 'Northwestern'
                            team_name = 'Northwestern Wildcats'
                        elif team_id == penn_state_id:
                            offensive_team = 'Penn State'
                            team_name = 'Penn State Nittany Lions'
                        break
                
                if offensive_team:
                    yards = play.get('statYardage', 0)
                    play_type = play.get('type', {}).get('text', '')
                    play_text = play.get('text', '')
                    
                    # Filter out special teams plays
                    if not any(st in play_type.lower() for st in ['punt', 'kickoff', 'field goal']):
                        play_info = {
                            'yards': yards,
                            'team': offensive_team,
                            'team_name': team_name,
                            'play_type': play_type,
                            'play_text': play_text,
                            'quarter': play.get('period', {}).get('number'),
                            'time': play.get('clock', {}).get('displayValue'),
                            'down': play.get('start', {}).get('down'),
                            'distance': play.get('start', {}).get('distance'),
                            'yard_line': play.get('start', {}).get('possessionText', '')
                        }
                        
                        all_plays.append(play_info)
    
    return all_plays

def create_combined_table(plays, title, filename):
    """Create an HTML table of all plays sorted by yards"""
    # Sort plays by yards (descending)
    sorted_plays = sorted(plays, key=lambda x: x['yards'], reverse=True)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .long-play {{ background-color: #d4edda; }}
            .medium-play {{ background-color: #fff3cd; }}
            .short-play {{ background-color: #f8d7da; }}
            .northwestern {{ background-color: #e3f2fd; }}
            .penn-state {{ background-color: #f3e5f5; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p><strong>Total plays analyzed:</strong> {len(plays)}</p>
        <table>
            <tr>
                <th>Yards</th>
                <th>Team</th>
                <th>Quarter</th>
                <th>Time</th>
                <th>Down & Distance</th>
                <th>Field Position</th>
                <th>Play Type</th>
                <th>Play Description</th>
            </tr>
    """
    
    for play in sorted_plays:
        # Color code based on yardage
        if play['yards'] >= 20:
            row_class = "long-play"
        elif play['yards'] >= 10:
            row_class = "medium-play"
        else:
            row_class = "short-play"
        
        # Add team-specific styling
        if play['team'] == 'Northwestern':
            row_class += " northwestern"
        else:
            row_class += " penn-state"
        
        html_content += f"""
            <tr class="{row_class}">
                <td><strong>{play['yards']}</strong></td>
                <td><strong>{play['team']}</strong></td>
                <td>Q{play['quarter']}</td>
                <td>{play['time']}</td>
                <td>{play['down']} & {play['distance']}</td>
                <td>{play['yard_line']}</td>
                <td>{play['play_type']}</td>
                <td>{play['play_text']}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(filename, 'w') as f:
        f.write(html_content)
    
    print(f"HTML table saved to: {filename}")

def main():
    print("Combined Longest Plays Analysis")
    print("Northwestern vs Penn State - October 11, 2025")
    print("=" * 60)
    
    # Load game data
    data = load_game_data()
    
    # Get all plays
    all_plays = get_all_plays(data)
    
    print(f"\nTotal plays analyzed: {len(all_plays)}")
    
    # Sort by yards and show top 10
    sorted_plays = sorted(all_plays, key=lambda x: x['yards'], reverse=True)
    
    print(f"\n🏆 TOP 10 LONGEST PLAYS:")
    print("=" * 100)
    print(f"{'Rank':<4} {'Yards':<5} {'Team':<12} {'Quarter':<8} {'Time':<8} {'Down':<8} {'Description'}")
    print("-" * 100)
    
    for i, play in enumerate(sorted_plays[:10], 1):
        print(f"{i:<4} {play['yards']:<5} {play['team']:<12} Q{play['quarter']:<6} {play['time']:<8} {play['down']}&{play['distance']:<6} {play['play_text'][:50]}...")
    
    # Team breakdown
    northwestern_plays = [p for p in all_plays if p['team'] == 'Northwestern']
    penn_state_plays = [p for p in all_plays if p['team'] == 'Penn State']
    
    print(f"\n📊 TEAM BREAKDOWN:")
    print(f"Northwestern: {len(northwestern_plays)} plays")
    print(f"Penn State: {len(penn_state_plays)} plays")
    
    if northwestern_plays:
        nw_longest = max(northwestern_plays, key=lambda x: x['yards'])
        print(f"Northwestern longest: {nw_longest['yards']} yards - {nw_longest['play_text'][:50]}...")
    
    if penn_state_plays:
        ps_longest = max(penn_state_plays, key=lambda x: x['yards'])
        print(f"Penn State longest: {ps_longest['yards']} yards - {ps_longest['play_text'][:50]}...")
    
    # Create HTML table
    if all_plays:
        create_combined_table(all_plays, "All Plays - Northwestern vs Penn State", "combined_plays_table.html")
        
        # Save data as JSON
        data_output = {
            'game': 'Northwestern vs Penn State',
            'date': 'October 11, 2025',
            'game_id': '401752866',
            'total_plays': len(all_plays),
            'northwestern_plays': len(northwestern_plays),
            'penn_state_plays': len(penn_state_plays),
            'top_10_longest': sorted_plays[:10],
            'all_plays': sorted_plays
        }
        
        with open('combined_plays_analysis.json', 'w') as f:
            json.dump(data_output, f, indent=2)
        
        print(f"\nData saved to: combined_plays_analysis.json")

if __name__ == "__main__":
    main()
