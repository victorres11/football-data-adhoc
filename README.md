# College Football Analysis Suite

A comprehensive analysis platform for college football games, featuring enhanced play-by-play analysis with win probability, interactive charts, and advanced metrics.

## 🏈 About

This project provides comprehensive analysis of college football games with advanced features:

- **Enhanced Play-by-Play**: Complete game analysis with win probability
- **Interactive Charts**: Win probability visualization with quarter shading
- **Penalty Analysis**: Impact analysis with win probability deltas
- **Inflection Points**: Major momentum changes (5%+ WP swings)
- **Precise Timing**: Game clock analysis using raw seconds data

## 📁 Project Structure

- **`enhanced_analysis/`** - Enhanced play-by-play analysis with win probability, charts, and advanced features
- **`game_reviews/`** - Traditional game review analysis with strategic insights and visual breakdowns
- **`scripts/`** - Python scripts for data fetching and analysis
- **`data/`** - Raw game data and analysis results
- **`images/`** - Game screenshots and visualizations

## 🚀 Quick Start

### Enhanced Play-by-Play Analysis
1. Navigate to `enhanced_analysis/` directory
2. Open any HTML file in your browser
3. Features include: win probability charts, penalty analysis, quarter shading, inflection points

### Creating New Analysis
1. Follow the guide in `FUTURE_GAME_ANALYSIS_GUIDE.md`
2. Use scripts in `scripts/` directory
3. Generate enhanced analysis files

## 🚀 Deploy to GitHub Pages

1. **Create a new repository on GitHub**
   - Go to [github.com/new](https://github.com/new)
   - Name it `maryland-football-analysis` (or any name you prefer)
   - Make it public
   - Don't initialize with README (we already have one)

2. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit: Maryland football analysis dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Click "Settings" tab
   - Scroll down to "Pages" section
   - Under "Source", select "Deploy from a branch"
   - Choose "main" branch and "/ (root)" folder
   - Click "Save"

4. **Access your site**
   - Your dashboard will be available at: `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`
   - It may take a few minutes to deploy

## 📁 Project Structure

```
├── index.html                                    # Main dashboard
├── scripts/
│   ├── calculate_successful_runs.py             # Analysis script
│   └── README.md                                # Script documentation
├── data/
│   ├── maryland/                                # Maryland team data
│   │   ├── game_data.json                       # Raw ESPN API data
│   │   ├── maryland_rush_attempts.json          # Initial extraction
│   │   ├── maryland_rush_attempts_corrected.json # Complete data
│   │   └── maryland_successful_runs_analysis.json # Final analysis
│   └── README.md                                # Data documentation
└── README.md                                    # This file
```

**Note:** Data files are excluded from GitHub via `.gitignore`

## 🎯 Features

- Responsive design for mobile and desktop
- Interactive statistics breakdown
- Complete table of all 19 rush attempts
- Color-coded success/failure indicators
- Player performance analysis
- Game flow by quarter

## 📈 Data Source

Analysis based on ESPN API data from Maryland vs Washington game (Event ID: 401752857).
