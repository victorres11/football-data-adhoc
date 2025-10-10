# Maryland Football - Successful Run Rate Analysis

A web dashboard analyzing Maryland's rushing performance using the "Successful Run Rate" metric.

## 🏈 About

This project analyzes college football rushing attempts using a custom success metric:

- **1st Down**: Need ≥40% of yards to go (rounded: 0.4 down, 0.5+ up)
- **2nd Down**: Need ≥60% of yards to go (rounded: 0.4 down, 0.5+ up)  
- **3rd/4th Down**: Need 100% of yards to go (convert) OR touchdown
- **Any Down**: Touchdown = always successful

## 📊 Results

- **Overall Success Rate**: 47.4% (9/19 attempts)
- **1st Down**: 60% success rate
- **2nd Down**: 20% success rate  
- **3rd Down**: 50% success rate

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
