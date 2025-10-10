# Data

This folder contains raw and processed football data organized by team.

## Structure

```
data/
├── maryland/
│   ├── game_data.json                           # Raw ESPN API data
│   ├── maryland_rush_attempts.json              # Initial rush attempts extraction
│   ├── maryland_rush_attempts_corrected.json    # Corrected data (includes TDs)
│   └── maryland_successful_runs_analysis.json   # Final analysis results
└── README.md
```

## Data Sources

- **ESPN API**: College football game data
- **Game**: Maryland vs Washington (Event ID: 401752857)
- **Date**: October 4, 2025

## File Descriptions

### game_data.json
Complete raw data from ESPN API including:
- Play-by-play data
- Team statistics
- Player statistics
- Game information

### maryland_rush_attempts.json
Initial extraction of Maryland rushing plays (missing touchdowns).

### maryland_rush_attempts_corrected.json
Complete extraction including:
- Regular rushes (`type.text == "Rush"`)
- Rushing touchdowns (`type.text == "Rushing Touchdown"`)
- 20 total rush attempts

### maryland_successful_runs_analysis.json
Final analysis with success calculations:
- Success/failure for each play
- Summary statistics
- Detailed play breakdown
