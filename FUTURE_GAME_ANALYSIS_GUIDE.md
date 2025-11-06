# Future Game Analysis Guide

This guide explains how to recreate the enhanced play-by-play analysis for any college football game using ESPN's APIs.

## 🎯 Overview

The enhanced analysis includes:
- Complete play-by-play table with win probability
- Penalty impact analysis
- Interactive win probability chart with quarter shading
- Major inflection points analysis
- Precise timing using `clock.value`

## 📋 Prerequisites

1. **Python environment** with required packages:
   ```bash
   pip install requests
   ```

2. **ESPN Game ID** - Find this in the URL: `https://www.espn.com/college-football/game/_/gameId/{GAME_ID}`

## 🚀 Step-by-Step Process

### Step 1: Choose Your Data Source

**Option A: Internal API (Recommended)**
- **Pros**: Unified structure, complete data, precise timing
- **Cons**: Requires pagination handling
- **Use when**: You want the most complete and consistent data

**Option B: Public API (Fallback)**
- **Pros**: Simpler structure, single request
- **Cons**: May have incomplete data, nested structure
- **Use when**: Internal API fails or you need quick analysis

### Step 2: Fetch Game Data

#### For Internal API (Recommended):

```python
#!/usr/bin/env python3
"""
Fetch game data using internal API
"""
import requests
import json
import os

def fetch_internal_api_data(game_id):
    """Fetch complete game data from internal API"""
    
    # 1. Fetch all plays with pagination
    all_plays = []
    page = 0
    page_size = 25
    
    while True:
        plays_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays?page={page}&limit={page_size}"
        
        response = requests.get(plays_url)
        if response.status_code != 200:
            break
            
        data = response.json()
        plays = data.get('items', [])
        all_plays.extend(plays)
        
        # Check if we've got all pages
        if page >= data.get('pageCount', 1) - 1:
            break
            
        page += 1
    
    # 2. Fetch win probability data
    wp_url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    wp_response = requests.get(wp_url)
    wp_data = wp_response.json().get('winprobability', [])
    
    # 3. Fetch teams data
    teams_data = {}
    # You'll need to determine team IDs from the game data
    
    return all_plays, wp_data, teams_data
```

#### For Public API (Fallback):

```python
def fetch_public_api_data(game_id):
    """Fetch game data from public API"""
    
    # Fetch main game data
    game_url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    response = requests.get(game_url)
    game_data = response.json()
    
    # Extract plays from drives
    plays = []
    drives = game_data.get('drives', {})
    for drive_list in [drives.get('previous', []), drives.get('current', [])]:
        for drive in drive_list:
            plays.extend(drive.get('plays', []))
    
    # Extract win probability
    wp_data = game_data.get('winprobability', [])
    
    return plays, wp_data, game_data
```

### Step 3: Create Analysis Script

Create a script based on `scripts/rebuild_northwestern_internal_api.py`:

```python
#!/usr/bin/env python3
"""
Enhanced play-by-play analysis for any game
"""
import json
import os
import re
from datetime import datetime

def load_game_data(game_id):
    """Load game data from files"""
    with open(f'data/game_{game_id}_internal/all_plays.json', 'r') as f:
        plays = json.load(f)
    
    with open(f'data/game_{game_id}/win_probability_data.json', 'r') as f:
        win_prob_data = json.load(f)
    
    with open(f'data/game_{game_id}/teams_data.json', 'r') as f:
        teams_data = json.load(f)
    
    return plays, win_prob_data, teams_data

def create_win_probability_lookup(win_prob_data):
    """Create lookup for win probability data by playId"""
    win_prob_lookup = {}
    
    if isinstance(win_prob_data, list):
        entries = win_prob_data
    else:
        entries = win_prob_data.get('winprobability', [])
    
    for entry in entries:
        play_id = entry.get('playId')
        if play_id:
            win_prob_lookup[play_id] = entry
    
    return win_prob_lookup

def analyze_penalties(plays, win_prob_lookup):
    """Analyze penalties in the game"""
    penalties = []
    
    for i, play in enumerate(plays):
        play_text = play.get('text', '').lower()
        
        is_penalty = False
        team_committed = "Unknown"
        
        # Check for penalty type
        play_type_id = play.get('type', {}).get('id', '')
        if play_type_id == '8':
            is_penalty = True
        elif 'penalty' in play_text:
            is_penalty = True
        
        if is_penalty:
            # Determine which team committed the penalty
            # You'll need to customize this based on the teams
            if 'team1' in play_text or 'home' in play_text:
                team_committed = "Team 1"
            elif 'team2' in play_text or 'away' in play_text:
                team_committed = "Team 2"
            
            if team_committed != "Unknown":
                # Calculate win probability change
                play_id = play.get('id', '')
                wp_data = win_prob_lookup.get(play_id)
                
                wp_change = 0
                if wp_data and i > 0:
                    prev_play = plays[i-1]
                    prev_play_id = prev_play.get('id', '')
                    prev_wp_data = win_prob_lookup.get(prev_play_id)
                    
                    if prev_wp_data:
                        prev_home_wp = prev_wp_data.get('homeWinPercentage', 0) * 100
                        curr_home_wp = wp_data.get('homeWinPercentage', 0) * 100
                        wp_change = curr_home_wp - prev_home_wp
                
                penalties.append({
                    'play': play,
                    'play_number': i + 1,
                    'team_committed': team_committed,
                    'description': play.get('text', ''),
                    'change': wp_change
                })
    
    return penalties

def categorize_inflection_point(play_number, wp_change, plays):
    """Categorize what type of play caused the inflection point"""
    if play_number <= len(plays):
        play = plays[play_number - 1]
        play_type = play.get('type', {}).get('text', '').lower()
        play_text = play.get('text', '').lower()
        
        # Check for turnovers
        if 'interception' in play_text or 'fumble' in play_text or 'turnover' in play_text:
            return '🔄 Turnover'
        
        # Check for scores
        if 'touchdown' in play_text or 'field goal' in play_text or 'safety' in play_text:
            return '🏈 Score'
        
        # Check for explosive plays (long gains)
        yardage_match = re.search(r'(\d+)\s+yds?', play_text)
        if yardage_match:
            yards = int(yardage_match.group(1))
            if yards >= 20:
                return '💥 Explosive Play'
        
        # Check for first downs
        if '1st down' in play_text or 'first down' in play_text:
            return '📈 1st Down'
        
        # Check for 4th down plays
        if '4th' in play_text or 'fourth' in play_text:
            return '🎯 4th Down'
        
        # Check for penalties
        if 'penalty' in play_text:
            return '🚩 Penalty'
        
        # Check for significant yardage gains (10+ yards)
        if yardage_match:
            yards = int(yardage_match.group(1))
            if yards >= 10:
                return '📊 Significant Gain'
        
        # Default categorization based on play type
        if play_type == 'rush':
            return '🏃 Rush'
        elif play_type == 'pass':
            return '🏈 Pass'
        elif play_type == 'kickoff':
            return '🏈 Kickoff'
        elif play_type == 'punt':
            return '🏈 Punt'
        else:
            return f'📋 {play_type.title()}'
    
    return '❓ Unknown'

def generate_enhanced_html_table(plays, teams_data, win_prob_lookup, game_id):
    """Generate enhanced HTML table"""
    
    # Create aligned data: match win probability to plays by playId
    aligned_data = []
    for i, play in enumerate(plays):
        play_id = play.get('id')
        wp_data = win_prob_lookup.get(play_id)
        
        if wp_data:
            aligned_data.append({
                'play_index': i,
                'play_number': i + 1,
                'play': play,
                'wp_data': wp_data
            })
    
    # Sort by play number to ensure chronological order
    aligned_data.sort(key=lambda x: x['play_number'])
    
    # Analyze penalties
    penalties = analyze_penalties(plays, win_prob_lookup)
    
    # Calculate inflection points
    inflection_points = []
    for i, item in enumerate(aligned_data):
        if i > 0:
            prev_home_wp = aligned_data[i-1]['wp_data']['homeWinPercentage'] * 100
            curr_home_wp = item['wp_data']['homeWinPercentage'] * 100
            wp_change = curr_home_wp - prev_home_wp
            
            if abs(wp_change) >= 5.0:
                play_number = item['play_number']
                play = item['play']
                category = categorize_inflection_point(play_number, wp_change, plays)
                play_text = play.get('text', '')
                
                inflection_points.append({
                    'play_number': play_number,
                    'change': wp_change,
                    'home_wp': curr_home_wp,
                    'away_wp': 100 - curr_home_wp,
                    'category': category,
                    'play_text': play_text
                })
    
    # Generate HTML (similar to existing script)
    # ... (include the full HTML generation code)
    
    return html

def main():
    game_id = "401752866"  # Replace with your game ID
    
    # Load data
    plays, win_prob_data, teams_data = load_game_data(game_id)
    
    # Create win probability lookup
    win_prob_lookup = create_win_probability_lookup(win_prob_data)
    
    # Generate enhanced HTML
    html = generate_enhanced_html_table(plays, teams_data, win_prob_lookup, game_id)
    
    # Save to file
    output_file = f"enhanced_pbp_game_{game_id}.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Enhanced HTML table saved to: {output_file}")

if __name__ == "__main__":
    main()
```

### Step 4: Customize for Your Game

1. **Update Game ID**: Change `game_id` variable
2. **Update Team Names**: Modify penalty detection logic
3. **Update Team IDs**: Get correct team IDs from the data
4. **Update Game Title**: Change the HTML title and headers

### Step 5: Run the Analysis

```bash
python your_analysis_script.py
```

## 🔧 Key Customizations

### Team Identification
```python
# Update these based on your game
if 'team1_name' in play_text or 'home_team' in play_text:
    team_committed = "Team 1"
elif 'team2_name' in play_text or 'away_team' in play_text:
    team_committed = "Team 2"
```

### Game Information
```python
# Update in HTML generation
game_title = "Your Game Title"
game_date = "Your Game Date"
home_team = "Home Team Name"
away_team = "Away Team Name"
```

## 📊 Data Structure Differences

### Internal API Structure:
```json
{
  "plays": {
    "items": [
      {
        "id": "play_id",
        "text": "play description",
        "clock": {"value": 900.0, "displayValue": "15:00"},
        "period": {"number": 1}
      }
    ]
  }
}
```

### Public API Structure:
```json
{
  "drives": {
    "previous": [
      {
        "plays": [
          {
            "id": "play_id",
            "text": "play description",
            "clock": {"displayValue": "15:00"},
            "period": {"number": 1}
          }
        ]
      }
    ]
  }
}
```

## 🎯 Best Practices

1. **Always use Internal API first** - it's more complete and consistent
2. **Handle pagination** for the internal API plays endpoint
3. **Use `clock.value`** for precise timing calculations
4. **Test with a few plays** before running the full analysis
5. **Save intermediate data** for debugging
6. **Customize team detection** for each game

## 🚨 Common Issues

1. **Missing win probability data**: Check if the game has ended
2. **Incomplete plays**: Use internal API with full pagination
3. **Team detection fails**: Customize the penalty detection logic
4. **Timing issues**: Use `clock.value` instead of `displayValue`

## 📁 File Structure

```
data/
├── game_{game_id}/
│   ├── all_plays.json (internal API)
│   ├── win_probability_data.json
│   ├── teams_data.json
│   └── complete_game_data.json (public API)
└── enhanced_pbp_game_{game_id}.html
```

This guide should help you recreate the enhanced analysis for any college football game! 🚀
