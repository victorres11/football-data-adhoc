# Scripts

This folder contains Python scripts for analyzing football data.

## calculate_successful_runs.py

Calculates the "Successful Run Rate" metric for rushing attempts.

### Success Criteria:
- **1st Down**: Gain ≥40% of yards to go (round 0.4 down, 0.5+ up)
- **2nd Down**: Gain ≥60% of yards to go (round 0.4 down, 0.5+ up)  
- **3rd/4th Down**: Gain 100% of yards to go (convert) OR touchdown
- **Any Down**: Touchdown = always successful

### Usage:
```bash
python3 scripts/calculate_successful_runs.py
```

### Input:
- `data/maryland/maryland_rush_attempts_corrected.json`

### Output:
- `data/maryland/maryland_successful_runs_analysis.json`
- Console summary with statistics

### Dependencies:
- Python 3.6+
- json (built-in)
- math (built-in)
