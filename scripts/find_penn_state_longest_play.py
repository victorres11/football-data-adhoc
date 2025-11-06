#!/usr/bin/env python3
"""
Find Penn State's longest play of scrimmage from Northwestern vs Penn State game
Game ID: 401752866
"""

import json

def load_game_data():
    """Load the Northwestern vs Penn State game data"""
    with open('data/northwestern/game_401752866.json', 'r') as f:
        return json.load(f)

def find_penn_state_longest_play(data):
    """Find Penn State's longest play of scrimmage"""
    print("Analyzing Northwestern vs Penn State game for Penn State's longest play...")
    
    # Get drives data
    drives = data.get('drives', {}).get('items', [])
    
    # Penn State is team ID 213 (home team)
    penn_state_id = "213"
    
    penn_state_plays = []
    max_yards = 0
    longest_play = None
    
    for drive in drives:
        if 'plays' in drive and 'items' in drive['plays']:
            for play in drive['plays']['items']:
                # Skip if play is not a dictionary
                if not isinstance(play, dict):
                    continue
                
                # Check if this is a Penn State offensive play
                team_participants = play.get('teamParticipants', [])
                is_penn_state_offense = False
                
                for participant in team_participants:
                    if participant.get('type') == 'offense':
                        team_id = participant.get('id', '')
                        if team_id == penn_state_id:
                            is_penn_state_offense = True
                            break
                
                if is_penn_state_offense:
                    yards = play.get('statYardage', 0)
                    play_type = play.get('type', {}).get('text', '')
                    play_text = play.get('text', '')
                    
                    # Filter out special teams plays
                    if not any(st in play_type.lower() for st in ['punt', 'kickoff', 'field goal']):
                        play_info = {
                            'yards': yards,
                            'play_type': play_type,
                            'play_text': play_text,
                            'quarter': play.get('period', {}).get('number'),
                            'time': play.get('clock', {}).get('displayValue'),
                            'down': play.get('start', {}).get('down'),
                            'distance': play.get('start', {}).get('distance'),
                            'yard_line': play.get('start', {}).get('possessionText', '')
                        }
                        
                        penn_state_plays.append(play_info)
                        
                        if yards > max_yards:
                            max_yards = yards
                            longest_play = play_info
    
    return penn_state_plays, longest_play, max_yards

def create_plays_table(plays, title, filename):
    """Create an HTML table of plays sorted by yards"""
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
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p><strong>Total Penn State plays analyzed:</strong> {len(plays)}</p>
        <table>
            <tr>
                <th>Yards</th>
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
        
        html_content += f"""
            <tr class="{row_class}">
                <td><strong>{play['yards']}</strong></td>
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
    print("Penn State Longest Play Analysis")
    print("Northwestern vs Penn State - October 11, 2025")
    print("=" * 60)
    
    # Load game data
    data = load_game_data()
    
    # Find Penn State's longest play
    penn_state_plays, longest_play, max_yards = find_penn_state_longest_play(data)
    
    print(f"\nTotal Penn State plays analyzed: {len(penn_state_plays)}")
    
    if longest_play:
        print(f"\n🏆 LONGEST PLAY OF SCRIMMAGE:")
        print(f"   Yards: {longest_play['yards']}")
        print(f"   Quarter: Q{longest_play['quarter']}")
        print(f"   Time: {longest_play['time']}")
        print(f"   Down & Distance: {longest_play['down']} & {longest_play['distance']}")
        print(f"   Field Position: {longest_play['yard_line']}")
        print(f"   Play Type: {longest_play['play_type']}")
        print(f"   Description: {longest_play['play_text']}")
    else:
        print("No Penn State plays found.")
    
    # Show top 10 longest plays
    if penn_state_plays:
        sorted_plays = sorted(penn_state_plays, key=lambda x: x['yards'], reverse=True)
        print(f"\n📊 TOP 10 LONGEST PLAYS:")
        print("-" * 80)
        for i, play in enumerate(sorted_plays[:10], 1):
            print(f"{i:2d}. {play['yards']:2d} yards - Q{play['quarter']} {play['time']} - {play['play_text'][:60]}...")
    
    # Create HTML table
    if penn_state_plays:
        create_plays_table(penn_state_plays, "Penn State Plays - Northwestern vs Penn State", "penn_state_plays_table.html")
        
        # Save data as JSON
        data_output = {
            'game': 'Northwestern vs Penn State',
            'date': 'October 11, 2025',
            'game_id': '401752866',
            'total_plays': len(penn_state_plays),
            'longest_play': longest_play,
            'max_yards': max_yards,
            'all_plays': sorted(penn_state_plays, key=lambda x: x['yards'], reverse=True)
        }
        
        with open('penn_state_plays_analysis.json', 'w') as f:
            json.dump(data_output, f, indent=2)
        
        print(f"\nData saved to: penn_state_plays_analysis.json")

if __name__ == "__main__":
    main()
