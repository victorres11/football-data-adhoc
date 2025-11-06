# Enhanced Play-by-Play Analysis

This directory contains enhanced play-by-play analysis pages with advanced features.

## 📊 Features

- **Complete play-by-play table** with win probability
- **Penalty impact analysis** with win probability deltas
- **Interactive win probability chart** with quarter shading
- **Major inflection points** analysis (5%+ WP changes)
- **Precise timing** using `clock.value` from internal API

## 📁 Files

### Michigan vs Washington (Game ID: 401752873)
- **File**: `enhanced_pbp_mich_uw.html`
- **Features**: Full analysis with penalty impact and inflection points
- **Published**: Available on GitHub Pages

### Northwestern vs Penn State (Game ID: 401752866)
- **File**: `enhanced_pbp_northwestern_pennstate.html` (Original)
- **File**: `enhanced_pbp_northwestern_pennstate_internal.html` (Internal API)
- **Features**: Quarter shading, precise timing, unified data structure
- **Published**: Available on GitHub Pages

## 🚀 How to Create New Analysis

See `../FUTURE_GAME_ANALYSIS_GUIDE.md` for detailed instructions on creating enhanced analysis for any game.

## 🔧 Technical Details

- **Data Source**: ESPN Internal API (`sports.core.api.espn.com`)
- **Chart Library**: Chart.js with custom quarter shading
- **Timing**: Uses `clock.value` (raw seconds) for precision
- **Structure**: Unified `plays.items[]` format across all games

## 📈 Analysis Components

1. **Play-by-Play Table**
   - Play number, quarter, time
   - Win probability and change
   - Down/distance and yard line
   - Play description

2. **Penalty Analysis**
   - Team-specific penalty counts
   - Win probability impact
   - Detailed penalty descriptions

3. **Win Probability Chart**
   - Interactive line chart
   - Quarter shading (Q1, Q2, Q3, Q4)
   - Penalty impact markers
   - Major inflection points

4. **Inflection Points**
   - Plays with 5%+ win probability changes
   - Categorized by play type
   - Play descriptions included

## 🎯 Usage

Open any HTML file in a web browser to view the enhanced analysis. All features are interactive and self-contained.
