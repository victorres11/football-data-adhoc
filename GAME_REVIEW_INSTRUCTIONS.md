# Game Review Generation Instructions

## Overview
This document provides detailed instructions for generating comprehensive college football game reviews using the templated system. The goal is to create accurate, detailed, and professional game reviews that match the Oregon template structure with minimal revisions.

## Data Sources
- **Primary**: ESPN API (`https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}`)
- **Secondary**: CFBD API for conference averages and season statistics
- **Score Extraction**: `data['header']['competitions'][0]['competitors']`
- **Play Data**: `data['drives']['previous']`
- **Player Stats**: `data['boxscore']['teams']`

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

### 6. Play Selection Breakdown
**Format**: Side-by-side visual breakdown
```html
<div class="play-breakdown">
    <div class="play-type">
        <h4>Rush Offense</h4>
        <div class="percentage">[percentage]%</div>
        <p>[attempts] attempts, [yards] yards</p>
    </div>
    <div class="play-type">
        <h4>Pass Offense</h4>
        <div class="percentage">[percentage]%</div>
        <p>[attempts] attempts, [yards] yards</p>
    </div>
</div>
```

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
- **Possession time by quarter** (calculate from drive durations)
- Actual scoring details (team, play description)
- Score at end of each quarter

### 9. Key Players & Threats
**Format**: Individual player cards
```html
<div class="key-player">
    <h4>[Player Name] ([Position])</h4>
    <p><strong>Stats:</strong> [detailed stats]</p>
    <p><strong>Analysis:</strong> [performance analysis]</p>
</div>
```

**Required Players**:
- Quarterback
- Top rusher
- Top receiver
- Defensive standout

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
**Format**: Insight boxes for analysis
```html
<div class="insight-box">
    <h3>Time of Possession</h3>
    <p><strong>[Team]:</strong> [time] ([percentage]%)</p>
    <p><strong>[Opponent]:</strong> [time] ([percentage]%)</p>
</div>
```

### 15. Season Performance Context
**Format**: Conference averages and game context
```html
<div class="insight-box">
    <h3>Big Ten Conference Averages (2025)</h3>
    <p><strong>3rd Down Conversion Rate:</strong> [percentage]%</p>
    <p><strong>4th Down Conversion Rate:</strong> [percentage]%</p>
    <!-- Additional conference stats -->
</div>
```

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

### Conference Data Integration
- **Always attempt** to fetch conference averages via CFBD API
- **Calculate per-game averages** from season totals (divide by games played)
- **Include all available stats**: yards per rush/pass, 3rd down rates, etc.
- **Mark clearly** when conference data is unavailable

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

## Workflow
1. **Fetch Game Data**: ESPN API for play-by-play and boxscore
2. **Fetch Season Data**: CFBD API for team and conference averages
3. **Generate HTML**: Use template structure with team-specific data
4. **Apply Branding**: Team colors and styling
5. **Quality Check**: Verify all data accuracy and completeness

---

**Note**: This template structure ensures consistent, professional game reviews that can be easily replicated for any team and game.