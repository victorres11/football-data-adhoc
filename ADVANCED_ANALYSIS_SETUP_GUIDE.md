# Advanced Team Analysis Setup Guide

This guide documents everything needed to set up the Advanced Team Analysis app for two new teams.

## Overview

The Advanced Team Analysis app provides comprehensive play-by-play analysis for two teams, including:
- Middle 8 Analysis
- Explosive Plays Analysis
- Penalty Analysis
- 4th Down Decision Analysis
- Post Turnover Analysis
- Special Teams Analysis
- Red Zone / Green Zone / Tight Red Zone Analysis
- Situational Receiving Analysis (SIS Data)

## Prerequisites

1. **Python Environment**: Python 3.8+ with virtual environment
2. **Data Sources**:
   - Play-by-play JSON files for both teams
   - SIS data JSON file (for Situational Receiving Analysis)
   - BYE weeks JSON file

## Directory Structure

```
advanced_reports_yogi/
├── {team1}_play_by_play/          # e.g., washington_play_by_play/
│   ├── game_401752805_*.json
│   ├── game_401752821_*.json
│   └── ...
├── {team2}_play_by_play/          # e.g., wisconsin_play_by_play/
│   ├── game_401752696_*.json
│   ├── game_401752820_*.json
│   └── ...
├── sis-data/
│   └── {team1}_{team2}_analysis_{year}.json
└── bye_weeks.json
```

## Step-by-Step Setup

### 1. Prepare Play-by-Play Data

#### 1.1 Create Team Folders
Create folders named `{team_name}_play_by_play` (lowercase) in `advanced_reports_yogi/`:
- Example: `washington_play_by_play/`, `wisconsin_play_by_play/`

#### 1.2 Play-by-Play JSON File Format

Each game file should be named: `game_{game_id}_{description}_week_{week}.json`

**Required Structure:**
```json
{
  "game_info": {
    "game_id": 401752805,
    "home_team": "Washington",
    "away_team": "Colorado State",
    "week": 1,
    "date": "2025-08-31 03:00:00+00:00",
    "total_plays": 172,
    "conference": false,
    "home_conference": "Big Ten",
    "away_conference": "Mountain West",
    "home_power4": true,
    "away_power4": false
  },
  "plays": [
    {
      "id": "401752805101929901",
      "drive_id": "4017528053",
      "game_id": 401752805,
      "offense": "Colorado State",
      "defense": "Washington",
      "period": 1,
      "clock": "seconds=0 minutes=7",
      "yard_line": 24,
      "yards_to_goal": 24,
      "down": 1,
      "distance": 10,
      "yards_gained": 22,
      "scoring": false,
      "play_type": "Rush",
      "play_text": "...",
      "ppa": 0.45,
      "explosive_play": false,
      "play_classification": "offense",
      "middle_eight": false,
      "turnover": false,
      "no_play": false,
      "penalty_type": null,
      "penalty_decision": null,
      "penalty_category": null,
      "drive_started_after_turnover": false
    }
  ]
}
```

**Required Fields in `game_info`:**
- `game_id`: Unique game identifier
- `home_team`: Home team name (must match team folder name, case-insensitive)
- `away_team`: Away team name
- `week`: Week number (1-17)
- `date`: Game date/time
- `conference`: Boolean - true if conference game
- `home_power4`: Boolean - true if home team is Power 4
- `away_power4`: Boolean - true if away team is Power 4

**Required Fields in Each Play:**
- `offense`: Team on offense
- `defense`: Team on defense
- `game_id`: Must match game_info.game_id
- `period`: Quarter (1-4)
- `clock`: Time remaining
- `yards_to_goal`: Yards to goal line
- `down`: Down number (1-4)
- `distance`: Yards to first down
- `yards_gained`: Yards gained on play
- `play_type`: Type of play
- `play_text`: Play description
- `play_classification`: "offense", "defense", or "special_teams"
- `explosive_play`: Boolean
- `middle_eight`: Boolean
- `turnover`: Boolean
- `penalty_type`: String or null
- `penalty_decision`: "accepted", "declined", or null
- `penalty_category`: "offensive_holding", "defensive_holding", "special_teams_holding", or null

### 2. Prepare SIS Data

#### 2.1 SIS Data File Location
Place SIS data file at: `advanced_reports_yogi/sis-data/{team1}_{team2}_analysis_{year}.json`

#### 2.2 SIS Data Structure

The SIS data must contain `task_9` data with the following structure:

```json
{
  "data": {
    "task_9": {
      "washington": {
        "3rd_down": {
          "by_week": {
            "9": {
              "week": 9,
              "opponent": "Illinois",
              "game_id": 401752880,
              "is_conference": true,
              "is_power4_opponent": true,
              "stats": {
                "targets": 5,
                "receptions": 4,
                "first_downs": 4,
                "touchdowns": 0,
                "yards": 59
              },
              "players": [...]
            }
          },
          "total": {...}
        },
        "redzone": {
          "by_week": {...},
          "total": {...}
        }
      },
      "wisconsin": {...}
    }
  }
}
```

**Important**: Each week entry in `by_week` must include:
- `game_id`: Matches game_id from play-by-play data
- `is_conference`: Boolean for conference filtering
- `is_power4_opponent`: Boolean for Power 4 filtering

#### 2.3 Enrich SIS Data with Game Metadata

**Run the enrichment script** to automatically add `game_id`, `is_conference`, and `is_power4_opponent` to SIS data:

```bash
python3 scripts/enrich_sis_data_with_game_info.py \
  advanced_reports_yogi/sis-data/{team1}_{team2}_analysis_{year}.json \
  advanced_reports_yogi
```

This script:
1. Loads play-by-play game data for both teams
2. Matches SIS weeks to game IDs by week number and opponent name
3. Adds `game_id`, `is_conference`, and `is_power4_opponent` to each week entry
4. Saves the enriched data back to the JSON file

**Note**: The script matches games by `(week, opponent_lowercase)`. If opponent names don't match exactly, you may need to update the SIS data manually.

### 3. Create BYE Weeks File

Create `advanced_reports_yogi/bye_weeks.json`:

```json
{
  "Team1": {
    "bye_weeks": [3],
    "season": 2025
  },
  "Team2": {
    "bye_weeks": [5],
    "season": 2025
  }
}
```

Replace `Team1` and `Team2` with actual team names (must match folder names, case-sensitive).

### 4. Update Code for New Teams

#### 4.1 Update `generate_advanced_analysis_app.py`

**Find and replace team names** throughout the file:
- Search for "Washington" and "Wisconsin"
- Replace with your new team names
- Update team colors if desired (search for `#4a90e2` for Washington blue, `#c41e3a` for Wisconsin red)

**Key locations to update:**
1. **Line ~30-45**: Team data loading
   ```python
   washington_data = load_team_data("Washington", data_dir)
   wisconsin_data = load_team_data("Wisconsin", data_dir)
   ```

2. **Line ~64-82**: SIS data loading
   ```python
   wash_situational = analyze_situational_receiving(sis_data, "Washington", washington_games)
   wisc_situational = analyze_situational_receiving(sis_data, "Wisconsin", wisconsin_games)
   ```

3. **Line ~84-110**: Data serialization
   ```python
   all_data_json = json.dumps({
       'washington': {...},
       'wisconsin': {...}
   })
   ```

4. **HTML sections**: Update team names in headers, labels, and navigation

#### 4.2 Update SIS Data Loading

In `scripts/analyze_situational_receiving.py`, ensure team names match:
- The `team_name.lower()` used to access SIS data (line ~53, ~94)
- Team names in the SIS JSON file (`"washington"`, `"wisconsin"` keys)

#### 4.3 Update Navigation and Headers

Search for and replace:
- Navigation menu items
- Section headers
- Chart titles
- Table headers

### 5. Generate the HTML App

Run the generation script:

```bash
cd /path/to/project
source venv/bin/activate
python3 scripts/generate_advanced_analysis_app.py
```

This will create `advanced_analysis_app.html` in the project root.

### 6. Verify Data

#### 6.1 Check Game Count
- Verify both teams have the same number of games
- Check that BYE weeks are correctly identified

#### 6.2 Check SIS Data Enrichment
- Open the SIS JSON file
- Verify each week entry has `game_id`, `is_conference`, and `is_power4_opponent`
- Check that game_ids match play-by-play data

#### 6.3 Test Filtering
- Open the generated HTML file
- Test all filter combinations:
  - Conference Only
  - Non-Conference Only
  - Power 4 Opponents Only
  - Last 3 Games
- Verify Situational Receiving section updates with filters

## Common Issues and Solutions

### Issue: SIS Data Not Filtering

**Symptoms**: Situational Receiving section doesn't update when filters are applied.

**Solution**:
1. Verify SIS data has been enriched (check for `game_id`, `is_conference`, `is_power4_opponent` in each week entry)
2. Run the enrichment script again if fields are missing
3. Check browser console for JavaScript errors

### Issue: Opponent Name Mismatch

**Symptoms**: Enrichment script shows "Could not find game for Week X vs Opponent"

**Solution**:
1. Check opponent name spelling in SIS data vs play-by-play data
2. Check for special characters or abbreviations (e.g., "Miami OH" vs "Miami (OH)")
3. Manually update opponent names in SIS data to match play-by-play data

### Issue: Missing Game Data

**Symptoms**: Charts show gaps or incorrect week numbers

**Solution**:
1. Verify all game files are in the correct team folder
2. Check that `game_info.week` matches the file name
3. Ensure BYE weeks are correctly listed in `bye_weeks.json`

### Issue: Team Name Case Sensitivity

**Symptoms**: Data not loading or incorrect team identification

**Solution**:
- Team folder names must be lowercase: `{team}_play_by_play`
- Team names in code should match exactly (case-sensitive in some places)
- SIS data keys should be lowercase: `"washington"`, `"wisconsin"`

## File Checklist

Before generating the app, verify:

- [ ] Both team folders exist: `{team1}_play_by_play/`, `{team2}_play_by_play/`
- [ ] All game JSON files are in correct folders
- [ ] Each game file has complete `game_info` with all required fields
- [ ] Each play has required fields (especially `offense`, `defense`, `game_id`)
- [ ] SIS data file exists: `sis-data/{team1}_{team2}_analysis_{year}.json`
- [ ] SIS data has `task_9` with both teams' data
- [ ] SIS data has been enriched (run `enrich_sis_data_with_game_info.py`)
- [ ] `bye_weeks.json` exists with correct team names and bye weeks
- [ ] Code updated with new team names throughout `generate_advanced_analysis_app.py`

## Testing Checklist

After generation, test:

- [ ] All sections load without errors
- [ ] Summary cards show correct totals
- [ ] Charts display data for both teams
- [ ] Tables populate with play data
- [ ] Filters work for all sections (except Situational Receiving initially)
- [ ] Situational Receiving section displays data
- [ ] Situational Receiving filters work (after enrichment)
- [ ] Navigation links work
- [ ] Responsive design works on mobile/tablet

## Maintenance

### Adding New Games

1. Add new game JSON file to appropriate team folder
2. Update SIS data if needed (for Situational Receiving)
3. Re-run enrichment script if SIS data was updated
4. Regenerate HTML app

### Updating SIS Data

1. Update SIS JSON file with new data
2. Run enrichment script: `python3 scripts/enrich_sis_data_with_game_info.py`
3. Regenerate HTML app

## Scripts Reference

### `enrich_sis_data_with_game_info.py`
Enriches SIS data with game metadata for filtering.

**Usage:**
```bash
python3 scripts/enrich_sis_data_with_game_info.py [sis_file_path] [data_dir]
```

**Parameters:**
- `sis_file_path`: Path to SIS data JSON (default: `advanced_reports_yogi/sis-data/washington_wisconsin_analysis_2025.json`)
- `data_dir`: Directory containing play-by-play data (default: `advanced_reports_yogi`)

**What it does:**
1. Loads play-by-play game data for both teams
2. Creates lookup by (week, opponent)
3. Matches SIS weeks to games
4. Adds `game_id`, `is_conference`, `is_power4_opponent` to each week entry
5. Saves enriched data back to JSON

### `generate_advanced_analysis_app.py`
Main script to generate the HTML analysis app.

**Usage:**
```bash
python3 scripts/generate_advanced_analysis_app.py [output_file] [data_dir]
```

**Parameters:**
- `output_file`: Output HTML file path (default: `advanced_analysis_app.html`)
- `data_dir`: Directory containing data files (default: `advanced_reports_yogi`)

## Data Field Reference

### Play-by-Play Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `game_id` | integer | Unique game identifier | `401752805` |
| `offense` | string | Team on offense | `"Washington"` |
| `defense` | string | Team on defense | `"Colorado State"` |
| `period` | integer | Quarter (1-4) | `1` |
| `clock` | string | Time remaining | `"seconds=0 minutes=7"` |
| `yards_to_goal` | integer | Yards to goal line | `24` |
| `down` | integer | Down number (1-4) | `1` |
| `distance` | integer | Yards to first down | `10` |
| `yards_gained` | integer | Yards gained | `22` |
| `play_type` | string | Type of play | `"Rush"` |
| `play_text` | string | Play description | `"..."` |
| `play_classification` | string | "offense", "defense", or "special_teams" | `"offense"` |
| `explosive_play` | boolean | Is explosive play | `false` |
| `penalty_type` | string/null | Penalty type | `"Holding"` or `null` |
| `penalty_decision` | string/null | "accepted", "declined", or null | `"accepted"` |
| `penalty_category` | string/null | For holding: "offensive_holding", "defensive_holding", "special_teams_holding" | `"offensive_holding"` |

### SIS Data Required Fields (after enrichment)

| Field | Type | Description | Location |
|-------|------|-------------|----------|
| `game_id` | integer | Game ID from play-by-play | `task_9.{team}.{situation}.by_week.{week}.game_id` |
| `is_conference` | boolean | Conference game flag | `task_9.{team}.{situation}.by_week.{week}.is_conference` |
| `is_power4_opponent` | boolean | Power 4 opponent flag | `task_9.{team}.{situation}.by_week.{week}.is_power4_opponent` |
| `opponent` | string | Opponent name | `task_9.{team}.{situation}.by_week.{week}.opponent` |
| `stats` | object | Weekly stats | `task_9.{team}.{situation}.by_week.{week}.stats` |
| `players` | array | Player-level data | `task_9.{team}.{situation}.by_week.{week}.players` |

## Notes

- Team names are case-sensitive in some contexts (folder names lowercase, code uses proper case)
- Opponent name matching is case-insensitive but must match exactly otherwise
- The enrichment script will warn about unmatched games - fix these manually if needed
- All filtering happens client-side in JavaScript for performance
- SIS data filtering requires enriched data (run enrichment script first)

