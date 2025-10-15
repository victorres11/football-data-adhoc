# Game Review Generation Instructions

## Overview
This document provides detailed instructions for generating comprehensive college football game reviews using the templated system. The goal is to create accurate, detailed, and professional game reviews that match the Oregon template structure with minimal revisions.

## ⚠️ CRITICAL: Always Use 2025 Season Data

**IMPORTANT:** All season statistics, player data, and conference averages must be sourced from the **2025 season**. Never use 2024 or any other year's data. This includes:
- Player season statistics from CFBD API
- Team season averages
- Conference averages (Big Ten, etc.)
- All comparative data

**API Endpoints:** Always append `&year=2025` to CFBD API calls for season data.

## Data Sources
- **Primary**: ESPN API (`https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}`)
- **Secondary**: CFBD API for conference averages and season statistics (**MUST USE 2025**)
- **Score Extraction**: `data['header']['competitions'][0]['competitors']`
- **Play Data**: `data['drives']['previous']`
- **Player Stats**: `data['boxscore']['teams']`

## ⚠️ MANDATORY: Extract Game Data First

**CRITICAL REQUIREMENT:** Before generating any HTML content, you MUST extract and verify all game data from the ESPN API. Never use placeholder text or estimated values.

## 🚫 NEVER USE ESTIMATES - DATA DRIVEN ONLY

**ABSOLUTELY FORBIDDEN:** Never estimate, guess, or approximate any statistics. If data is not available from the API, either:
1. **Find the correct API endpoint** that provides the data
2. **Extract from a different data source** (play-by-play, drives, etc.)
3. **Leave the field blank** with a note that data is unavailable
4. **Do not generate the report** until all required data is available

**Examples of what is FORBIDDEN:**
- "Estimated 3rd down rate based on game outcome"
- "Approximated possession times"
- "Guessed turnover counts"
- "Assumed play counts"

**Examples of what is REQUIRED:**
- Extract 3rd down conversions/attempts from actual play-by-play data
- Calculate possession times from drive data with actual clock times
- Count turnovers from actual game statistics
- Count plays from actual play-by-play data

### Required Data Extraction Steps:
1. **Fetch Raw Game Data** from ESPN API
2. **Extract Team Statistics** from `data['boxscore']['teams']`
3. **Extract Drive Data** from `data['drives']['previous']`
4. **Extract Player Leaders** from `data['leaders']`
5. **Calculate Possession Times** from drive data
6. **Extract Turnover Information** from team stats
7. **Extract 3rd/4th Down Data** from play-by-play or drives data
8. **Verify All Numbers** before populating HTML

### Step 7: Extract 3rd/4th Down Data (CRITICAL)
**NEVER estimate 3rd/4th down rates.** You MUST extract this data from actual game data:

```python
# Method 1: From drives data
for drive in drives:
    if 'plays' in drive:
        for play in drive['plays']:
            if play.get('down') == 3:
                # Count 3rd down attempts and conversions
                
# Method 2: From play-by-play data
pbp_url = f'https://site.api.espn.com/apis/site/v2/sports/football/college-football/playbyplay?event={game_id}'
pbp_data = requests.get(pbp_url).json()
# Parse plays to count 3rd/4th down attempts and conversions

# Method 3: From boxscore statistics
for team in boxscore['teams']:
    for stat in team['statistics']:
        if stat['label'] == '3rd Down Conv.':
            conversions = stat['displayValue']
        elif stat['label'] == '3rd Downs':
            attempts = stat['displayValue']
```

**If 3rd/4th down data is not available, DO NOT generate the report.**

### Data Validation Checklist:
- [ ] Final score matches ESPN data
- [ ] Team stats (yards, downs, turnovers) are accurate
- [ ] Possession times sum to 15:00 per quarter
- [ ] Turnover counts match team statistics
- [ ] 3rd/4th down conversion rates are calculated correctly
- [ ] **Quarter-by-quarter scores are extracted from drives data**
- [ ] **Running totals match final score**
- [ ] **Defensive scores (INT TD, fumble returns) are included**
- [ ] No placeholder text like "[To be filled from game data]"

**FAILURE TO EXTRACT REAL DATA WILL RESULT IN INCOMPLETE REPORTS**

## Data Extraction Workflow

### Step 1: Fetch and Parse Game Data
```python
# Example data extraction workflow
import requests
import json

# Fetch game data
game_id = "401752864"
url = f'https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}'
response = requests.get(url)
data = response.json()

# Extract team stats
boxscore = data['boxscore']
teams = boxscore['teams']

for team in teams:
    team_name = team['team']['displayName']
    stats = team['statistics']
    
    # Extract key statistics
    for stat in stats:
        if stat['label'] in ['Total Yards', 'Rushing', 'Passing', '3rd down efficiency', '4th down efficiency', 'Turnovers']:
            print(f"{team_name} {stat['label']}: {stat['displayValue']}")
```

### Step 2: Calculate Derived Statistics
- **3rd Down Rate**: `conversions / attempts * 100`
- **4th Down Rate**: `conversions / attempts * 100` (Go For It attempts only)
- **Yards Per Rush**: `rushing_yards / rushing_attempts`
- **Yards Per Pass**: `passing_yards / pass_attempts`
- **Possession Time**: Sum drive times by quarter
- **Quarter-by-Quarter Scores**: Extract from drives data, track running totals

### Step 2.5: Extract Quarter-by-Quarter Scoring (CRITICAL)
```python
# Extract quarter-by-quarter scores from drives
quarter_scores = {1: {'team1': 0, 'team2': 0}, 2: {'team1': 0, 'team2': 0}, 3: {'team1': 0, 'team2': 0}, 4: {'team1': 0, 'team2': 0}}

for drive in drives:
    if drive.get('isScore', False):
        team = drive.get('team', {}).get('displayName', '')
        result = drive.get('result', '')
        quarter = drive.get('end', {}).get('period', {}).get('number', 0)
        
        points = 7 if result == 'TD' else 3 if result == 'FG' else 0
        if points > 0:
            quarter_scores[quarter][team] += points

# Calculate running totals
running_totals = {1: {'team1': 0, 'team2': 0}, 2: {'team1': 0, 'team2': 0}, 3: {'team1': 0, 'team2': 0}, 4: {'team1': 0, 'team2': 0}}
for q in [1, 2, 3, 4]:
    running_totals[q]['team1'] = sum(quarter_scores[i]['team1'] for i in range(1, q+1))
    running_totals[q]['team2'] = sum(quarter_scores[i]['team2'] for i in range(1, q+1))
```

### Step 2.6: Handle Defensive Scores (CRITICAL)
```python
# Check for defensive scores (INT TD, fumble returns, etc.)
for drive in drives:
    if drive.get('isScore', False):
        result = drive.get('result', '')
        description = drive.get('description', '')
        
        # Handle defensive touchdowns
        if 'INT TD' in description or 'fumble return' in description:
            # Determine which team scored (opposite of drive team)
            drive_team = drive.get('team', {}).get('displayName', '')
            scoring_team = 'Team2' if 'Team1' in drive_team else 'Team1'
            quarter = drive.get('end', {}).get('period', {}).get('number', 0)
            quarter_scores[quarter][scoring_team] += 7
```

### Step 3: Validate Data Before HTML Generation
- Verify all numbers are realistic
- Check that possession times sum to 15:00 per quarter
- Ensure turnover counts match team statistics
- Confirm no placeholder text remains

## Common Mistakes to Avoid

### ❌ DO NOT:
- Use placeholder text like "[To be filled from game data]"
- **Estimate or guess game statistics - NEVER USE ESTIMATES**
- Use 2024 data instead of 2025
- Generate HTML before extracting real data
- Skip data validation steps
- Use generic analysis without game-specific data
- **Assume quarter-by-quarter scores without extracting from drives data**
- **Ignore defensive scores (INT TD, fumble returns)**
- **Use estimated game flow patterns**
- **Estimate 3rd/4th down rates - extract from actual data**
- **Guess possession times - calculate from drive data**
- **Approximate any statistics - use real data only**

### ✅ ALWAYS:
- Extract real data from ESPN API first
- Verify all numbers before HTML generation
- Use 2025 season data for comparisons
- **Extract 3rd/4th down data from actual play-by-play or drives data**
- **Calculate possession times from actual drive clock data**
- **Count turnovers from actual game statistics**
- **Use only verified, extracted data - NO ESTIMATES EVER**
- Calculate derived statistics accurately
- Include specific game details in analysis
- Validate possession times sum to 15:00 per quarter
- **Extract quarter-by-quarter scores from drives data**
- **Include defensive scores in quarter totals**
- **Validate running totals match final score**

## Report Structure & Template

### 1. Header Section
**Format**: Clean header without score display
```html
<div class="header">
    <h1>🏈 [Team] vs [Opponent] Game Review</h1>
    <div class="game-info">Game ID: [ID] | [Date]</div>
    <p><strong>Result:</strong> [Team] [result description] vs [Opponent], [season record context]</p>
</div>
```

### 2. Team Stats Comparison (ESPN-Style)
**Format**: Side-by-side comparison with conference averages
```html
<div class="team-comparison">
    <div class="comparison-row">
        <div class="team-stat [opponent-color]">[opponent-stat]</div>
        <div class="stat-label">[Stat Name]</div>
        <div class="team-stat [team-color]">[team-stat]</div>
        <div class="conference-avg">Big Ten Avg: [conference-avg]</div>
    </div>
</div>
```

**Required Stats**:
- Total Yards
- 1st Downs
- Penalties
- 3rd Downs
- 4th Downs
- Possession
- Rushing Yards
- Yards per Rush
- Passing Yards
- Yards per Pass
- Turnovers

### 3. Executive Summary
**Requirements**:
- Game result (win/loss/tie) with emoji
- Final score
- Key performance metrics
- Balanced analysis with strengths and weaknesses
- Season context

### 4. Offensive Analysis (Team-Focused)
**Format**: 5-column comparison table
```html
<div class="offensive-comparison">
    <div class="comparison-header">
        <div class="stat-label">Stat</div>
        <div class="header-label">Game</div>
        <div class="header-label">[Team] Season</div>
        <div class="header-label">[Opponent] Allows</div>
        <div class="header-label">Big Ten Avg</div>
    </div>
</div>
```

**Required Stats**:
- Total Yards
- Rushing Yards
- Passing Yards
- 3rd Down Rate
- Yards per Rush
- Yards per Pass
- **4th Down Rate** (add this row to offensive analysis)

**Color Coding**:
- Blue: Game performance
- Green: Team's season average
- Red: Opponent's defensive average
- Gray: Big Ten conference average

### 5. Defensive Analysis (Team-Focused)
**Format**: 5-column comparison table
```html
<div class="defensive-comparison">
    <div class="comparison-header">
        <div class="stat-label">Stat</div>
        <div class="header-label">Game</div>
        <div class="header-label">[Team] Allows</div>
        <div class="header-label">[Opponent] Season</div>
        <div class="header-label">Big Ten Avg</div>
    </div>
</div>
```

**Required Stats**:
- Total Yards Allowed
- Rushing Yards Allowed
- Passing Yards Allowed
- 3rd Down Rate Allowed
- Yards per Rush Allowed
- Yards per Pass Allowed
- **4th Down % Allowed** (add this row to defensive analysis)

### 6. Play Selection Breakdown
**Format**: JavaScript-populated breakdown with filtered play types
```html
<h3>📊 Play Selection Breakdown (Grouped)</h3>
<div class="play-breakdown" id="groupedPlayBreakdown">
    <!-- Will be populated by JavaScript -->
</div>

<h3>📊 Detailed Play Types</h3>
<div class="play-breakdown" id="playBreakdown">
    <!-- Will be populated by JavaScript -->
</div>
```

**JavaScript Filter**: Only show these play types in detailed breakdown:
- Pass Reception
- Pass Incompletion
- Sack
- Passing Touchdown
- Rush
- Rushing Touchdown

**Remove**: Kickoff, Punt, Field Goal Good, Penalty, End Period

### 7. Special Teams Notes
**Format**: Insight boxes for each category
```html
<div class="insight-box">
    <h3>Field Goals</h3>
    <p><strong>[Team]:</strong> [attempts] ([results])</p>
    <p><strong>[Opponent]:</strong> [attempts] ([results])</p>
</div>
```

**Categories**:
- Field Goals (attempts, converted/failed)
- Punts (numbers, averages)
- Returns (punt returns, kickoff returns)

### 8. Game Narrative (Quarter-by-Quarter)
**Format**: 4-column grid with quarter cards
```html
<div class="quarter-grid">
    <div class="quarter-card">
        <div class="quarter-number">Q[1-4]</div>
        <div><strong>Plays:</strong> [count]</div>
        <div><strong>Yards:</strong> [yards]</div>
        <div><strong>Scores:</strong> [count]</div>
        <div><strong>Possession:</strong> [Team] [time], [Opponent] [time]</div>
        <div style="margin-top: 8px; font-size: 0.9em;">
            <div style="color: #ddd;">[Team]: [play description]</div>
        </div>
        <div style="margin-top: 10px;"><strong>End Score:</strong> [score]</div>
    </div>
</div>
```

**Required Data**:
- Total plays per quarter
- Total yards per quarter
- Number of scores per quarter
- **Possession time by quarter** (normalize drive durations to 15:00 per quarter total)
- Actual scoring details (team, play description)
- Score at end of each quarter

**Possession Time Calculation**:
- Get total game possession from boxscore (should equal 60:00 combined)
- Calculate each team's percentage of total possession
- For each quarter, normalize drive durations to ensure total equals 15:00
- Formula: (team_drive_time / quarter_total_drive_time) × 15:00

### 9. Key Players & Threats
**Format**: Individual player cards
```html
<div class="key-player">
    <h4>[Player Name] ([Position])</h4>
    <p><strong>Game Stats:</strong> [actual game statistics]</p>
    <p><strong>Season Stats:</strong> [season averages from CFBD API - 2025 ONLY]</p>
    <p><strong>Performance:</strong> <span style="color: #51cf66;">↑ Overperformed</span> / <span style="color: #ff6b6b;">↓ Underperformed</span></p>
    <p><strong>Analysis:</strong> [detailed performance analysis]</p>
</div>
```

**Required Players**:
- Quarterback
- Top rusher
- Top receiver
- Defensive standout

**⚠️ CRITICAL:** Always use `&year=2025` in CFBD API calls for player season stats. Double-check that all season data is from 2025, not 2024.

### 10. Situational Football Analysis
**Format**: Insight boxes for each situation
```html
<div class="insight-box">
    <h3>3rd Down Efficiency</h3>
    <p><strong>Overall:</strong> [conversions]/[attempts] ([percentage]%)</p>
    <p><strong>Short (1-3 yards):</strong> [conversions]/[attempts] conversions</p>
    <p><strong>Medium (4-7 yards):</strong> [conversions]/[attempts] conversions</p>
    <p><strong>Long (8+ yards):</strong> [conversions]/[attempts] conversions</p>
</div>
```

**Categories**:
- 3rd Down Efficiency (short/medium/long)
- 4th Down Decision Making (attempts/conversions/rate)
- Red Zone Efficiency (trips/TDs/field goals)

### 11. 4th Down Tables
**Format**: Side-by-side tables for both teams
```html
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
    <div>
        <h3 class="[team-color]">[Team] 4th Down Attempts</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Q</th>
                    <th>Clock</th>
                    <th>Down & Distance</th>
                    <th>Field Pos</th>
                    <th>Decision</th>
                    <th>Result</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                <!-- 4th down plays -->
            </tbody>
        </table>
    </div>
</div>
```

### 12. Explosive Plays Analysis
**Format**: Insight boxes with play details
```html
<div class="insight-box">
    <h3>Big Plays (20+ yards)</h3>
    <div class="explosive-play">
        <strong>[Team]:</strong> [play description] ([quarter], [time])
    </div>
</div>
```

**Categories**:
- Big Plays (20+ yards) - exclude special teams
- Chunk Plays (10-19 yards) - exclude special teams
- Negative Plays (negative yardage)

### 13. Turnover Analysis
**Format**: Highlighted turnover section
```html
<div class="turnover-highlight">
    <h3>Critical Turnovers</h3>
    <p><strong>[Quarter], [Time]:</strong> [turnover description] ([score] score)</p>
</div>
```

### 14. Game Script Analysis
**Format**: Stats grid with play count captions
```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">[percentage]%</div>
        <div class="stat-label">Run When Leading</div>
        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">[X] plays</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">[percentage]%</div>
        <div class="stat-label">Run When Trailing</div>
        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">[X] plays</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">[percentage]%</div>
        <div class="stat-label">Run When Tied</div>
        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">[X] plays</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">[time]</div>
        <div class="stat-label">Time of Possession</div>
    </div>
</div>
```

**Required**: Add play count captions below each percentage to show sample size

### 15. Season Performance Context
**⚠️ REMOVED**: This section should be omitted from new game reviews to streamline the page and avoid redundancy with the offensive/defensive analysis sections.

### 16. Comprehensive Game Takeaways
**Format**: Multiple insight boxes
```html
<div class="insight-box">
    <h3>Offensive Weaknesses</h3>
    <p>• [weakness 1]</p>
    <p>• [weakness 2]</p>
</div>
```

**Categories**:
- Offensive Weaknesses
- Defensive Tendencies
- Key Matchups to Exploit
- Game Plan Recommendations

## Styling Requirements

### Color Scheme
- **Team Colors**: Use primary team colors for branding
- **Background**: Team-themed gradient background
- **Comparison Colors**:
  - Blue (#3498db): Game performance
  - Green (#2ecc71): Team season averages
  - Red (#e74c3c): Opponent averages
  - Gray (#7f8c8d): Conference averages

### Layout
- **Container**: Max-width 1200px, centered
- **Sections**: White background with rounded corners and shadows
- **Grid Layouts**: Responsive grid for comparisons
- **Typography**: Segoe UI font family
- **Spacing**: Consistent padding and margins

## Data Accuracy Requirements

### Critical Data Points
1. **Final Score**: Extract from `header.competitions[0].competitors`
2. **Team Records**: Use CFBD API for current season records
3. **4th Down Analysis**: Count only "Go For It" attempts vs all 4th down plays
4. **Explosive Plays**: Exclude field goals, punts, kickoffs
5. **Season Averages**: Calculate per-game averages from season totals

### Data Extraction & Calculation Details

#### Game Stats Calculation
- **Total Plays**: Count all offensive plays (exclude special teams)
- **Rushing Yards**: Sum all rushing attempts from play-by-play
- **Passing Yards**: Sum all passing completions from play-by-play
- **3rd Down Rate**: (3rd down conversions) / (3rd down attempts) × 100
- **4th Down Rate**: (4th down conversions) / (4th down "Go For It" attempts) × 100
- **Yards per Rush**: Total rushing yards / total rushing attempts
- **Yards per Pass**: Total passing yards / total pass attempts (including sacks)

#### Season Stats from CFBD API
- **Always use `&year=2025`** in API calls
- **Calculate per-game averages**: Divide season totals by games played
- **4th Down Stats**: Use `fourthDownConversions` / `fourthDowns` for rate
- **Defensive Stats**: Use `*Opponent` fields (e.g., `totalYardsOpponent`)

#### Conference Averages
- **Source**: `big_ten_2025_stats.json` (pre-calculated)
- **Use for**: All Big Ten Avg columns in comparison tables
- **Format**: Per-game averages, not season totals

#### Possession Time Calculation
- **Method**: Analyze drive data from ESPN API
- **Normalize**: Ensure each quarter totals 15:00 combined
- **Formula**: Split cross-quarter drives based on clock times
- **Validation**: Total game possession should equal 60:00

### Conference Data Integration
- **Always attempt** to fetch conference averages via CFBD API
- **Calculate per-game averages** from season totals (divide by games played)
- **Include all available stats**: yards per rush/pass, 3rd down rates, etc.
- **Mark clearly** when conference data is unavailable

## Common Issues & Solutions

### Data Issues
- **"No offensive play data available"**: Check ESPN API response structure, may need to handle `$ref` links
- **Incorrect team names**: ESPN API sometimes returns team IDs instead of names, map manually
- **Missing possession times**: Calculate from drive data, normalize to 15:00 per quarter
- **Wrong year data**: Always verify `&year=2025` in CFBD API calls
- **Incomplete season stats**: Check if team has played enough games for meaningful averages

### Structural Issues
- **Duplicate sections**: Ensure only one Game Narrative, one Offensive Analysis, etc.
- **Broken layouts**: Verify CSS classes match Oregon template exactly
- **Missing sections**: Check that all required sections are present and in correct order
- **Incorrect color coding**: Blue=game, Green=season, Red=opponent, Gray=conference

### Content Issues
- **Weak executive summary**: Include game result, key metrics, balanced analysis
- **Missing 4th down data**: Extract from play-by-play, count only "Go For It" attempts
- **Incorrect turnover analysis**: Verify actual turnovers from game data
- **Generic insights**: Make analysis specific to the actual game performance

## Quality Checklist
- [ ] Final score is accurate
- [ ] Game result (win/loss/tie) is correct
- [ ] Team records are current season records
- [ ] All comparison tables have complete data (no N/A values)
- [ ] 4th down analysis shows "Go For It" attempts only
- [ ] Explosive plays exclude special teams
- [ ] Conference averages are included where available
- [ ] Team colors are used for branding
- [ ] All sections follow the template structure
- [ ] No duplicate sections
- [ ] No "No data available" messages
- [ ] 4th down rate included in both offensive and defensive analysis
- [ ] Play count captions added to Game Script Analysis percentages
- [ ] Detailed play types filtered to only show key offensive plays
- [ ] Season Performance Context section removed

## Workflow
1. **Fetch Game Data**: ESPN API for play-by-play and boxscore
2. **Fetch Season Data**: CFBD API for team and conference averages
3. **Generate HTML**: Use template structure with team-specific data
4. **Apply Branding**: Team colors and styling
5. **Quality Check**: Verify all data accuracy and completeness

---

## Additional Critical Requirements

### Conference Averages Calculation
- **Big Ten Teams Only**: When calculating conference averages, filter to Big Ten teams only
- **Teams Included**: Illinois, Indiana, Iowa, Maryland, Michigan, Michigan State, Minnesota, Nebraska, Northwestern, Ohio State, Penn State, Purdue, Rutgers, Wisconsin, Oregon, UCLA, USC, Washington
- **Turnover Margin**: Always verify calculation - should be positive for Big Ten (+1.8 average)
- **Data Source**: Use `big_ten_2025_stats.json` filtered to Big Ten teams only

### Data Validation Requirements
- **Quarter-by-Quarter Scores**: MUST extract from drives data, never estimate
- **Defensive Scores**: Include INT TD, fumble returns in quarter totals
- **Possession Times**: Must sum to 15:00 per quarter (account for cross-quarter drives)
- **Turnover Counts**: Verify against team statistics
- **Conference Averages**: Double-check calculations against raw data

### Common Data Errors to Avoid
- ❌ **DO NOT**: Use placeholder text like "[To be filled from game data]"
- ❌ **DO NOT**: Estimate quarter-by-quarter scores without drives data
- ❌ **DO NOT**: Include all FBS teams in Big Ten averages (use only 18 Big Ten teams)
- ❌ **DO NOT**: Show negative turnover margin for Big Ten (+1.8 is correct)
- ❌ **DO NOT**: Skip defensive scores in quarter totals

### Final Quality Checklist
- [ ] All quarter scores extracted from drives data
- [ ] Defensive scores included in quarter totals
- [ ] Possession times sum to 15:00 per quarter
- [ ] Big Ten averages calculated from Big Ten teams only
- [ ] Turnover margin shows +1.8 for Big Ten
- [ ] No placeholder text remains
- [ ] All game statistics match ESPN data

---

**Note**: This template structure ensures consistent, professional game reviews that can be easily replicated for any team and game.