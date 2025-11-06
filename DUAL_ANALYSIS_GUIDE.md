# Dual Analysis Guide

This guide explains how to create both types of analysis for the same game: **Game Reviews** and **Enhanced Play-by-Play**.

## 🎯 Two Analysis Types

### 1. **Game Reviews** (`game_reviews/`)
- **Purpose**: Strategic analysis and coaching insights
- **Content**: Narrative storytelling, key moments, visual breakdowns
- **Audience**: Coaches, analysts, strategic planning
- **Output**: HTML files with detailed analysis and screenshots

### 2. **Enhanced Play-by-Play** (`enhanced_analysis/`)
- **Purpose**: Statistical analysis and data visualization
- **Content**: Complete play-by-play, win probability, charts
- **Audience**: Data analysts, researchers, comprehensive coverage
- **Output**: Interactive HTML files with charts and tables

## 🚀 Running Both for the Same Game

### Step 1: Choose Your Game
```bash
GAME_ID="401752866"  # Northwestern vs Penn State
GAME_TITLE="Northwestern vs Penn State"
```

### Step 2: Create Enhanced Play-by-Play Analysis
```bash
# Use the enhanced analysis system
python scripts/rebuild_northwestern_internal_api.py
# This creates: enhanced_analysis/enhanced_pbp_northwestern_pennstate_internal.html
```

### Step 3: Create Game Review Analysis
```bash
# Use the traditional game review system
python scripts/create_game_review.py --game-id $GAME_ID --title "$GAME_TITLE"
# This creates: game_reviews/northwestern_pennstate_game_review.html
```

## 📁 File Organization for Same Game

```
data/
├── game_401752866/
│   ├── all_plays.json                    # Raw play data
│   ├── win_probability_data.json         # Win probability data
│   ├── teams_data.json                   # Team information
│   └── complete_game_data.json           # Full game data
├── images/
│   └── northwestern_pennstate/            # Game screenshots
│       ├── key_plays/
│       ├── formations/
│       └── analysis/
└── enhanced_analysis/
    └── enhanced_pbp_northwestern_pennstate.html
└── game_reviews/
    └── northwestern_pennstate_game_review.html
```

## 🔧 Script Modifications Needed

### For Enhanced Analysis:
```python
# scripts/enhanced_analysis_template.py
def create_enhanced_analysis(game_id, home_team, away_team):
    """Create enhanced play-by-play analysis"""
    # Load data
    plays, wp_data, teams_data = load_game_data(game_id)
    
    # Generate analysis
    html = generate_enhanced_html_table(plays, teams_data, wp_data)
    
    # Save to enhanced_analysis/
    output_file = f"enhanced_analysis/enhanced_pbp_{home_team.lower()}_{away_team.lower()}.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    return output_file
```

### For Game Review:
```python
# scripts/game_review_template.py
def create_game_review(game_id, home_team, away_team):
    """Create traditional game review analysis"""
    # Load data
    plays, wp_data, teams_data = load_game_data(game_id)
    
    # Generate review
    html = generate_game_review_html(plays, teams_data, wp_data)
    
    # Save to game_reviews/
    output_file = f"game_reviews/{home_team.lower()}_{away_team.lower()}_game_review.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    return output_file
```

## 🎯 Combined Workflow

### Option 1: Sequential Analysis
```bash
# 1. Create enhanced analysis first
python scripts/create_enhanced_analysis.py --game-id 401752866

# 2. Create game review second
python scripts/create_game_review.py --game-id 401752866

# 3. Both analyses are now available
```

### Option 2: Combined Script
```python
# scripts/create_dual_analysis.py
def create_dual_analysis(game_id, home_team, away_team):
    """Create both types of analysis for the same game"""
    
    # Create enhanced analysis
    enhanced_file = create_enhanced_analysis(game_id, home_team, away_team)
    print(f"✓ Enhanced analysis: {enhanced_file}")
    
    # Create game review
    review_file = create_game_review(game_id, home_team, away_team)
    print(f"✓ Game review: {review_file}")
    
    # Create index linking both
    create_analysis_index(game_id, home_team, away_team, enhanced_file, review_file)
    
    return enhanced_file, review_file
```

## 📊 Analysis Comparison

| Aspect | Game Review | Enhanced PBP |
|--------|-------------|--------------|
| **Data Coverage** | Key moments | Complete game |
| **Visual Elements** | Screenshots, diagrams | Charts, tables |
| **Narrative** | Storytelling | Statistical |
| **Audience** | Coaches | Analysts |
| **Depth** | Strategic insights | Data completeness |
| **Time Investment** | High (manual analysis) | Low (automated) |

## 🎯 When to Use Both

### Use Both When:
- **Comprehensive analysis** is needed
- **Different audiences** require different formats
- **Complete coverage** from multiple perspectives
- **Research projects** needing both strategic and statistical views

### Use Enhanced PBP Only When:
- **Quick statistical analysis** is sufficient
- **Data-driven insights** are the priority
- **Time constraints** limit manual analysis

### Use Game Review Only When:
- **Strategic analysis** is the focus
- **Coaching insights** are needed
- **Visual breakdowns** are important
- **Narrative storytelling** is required

## 🚀 Best Practices

1. **Start with Enhanced PBP** for quick statistical overview
2. **Create Game Review** for strategic insights on key moments
3. **Cross-reference** between both analyses
4. **Use consistent naming** for easy organization
5. **Create index pages** linking both analyses

## 📁 Example Output Structure

```
enhanced_analysis/
├── enhanced_pbp_northwestern_pennstate.html
└── enhanced_pbp_michigan_washington.html

game_reviews/
├── northwestern_pennstate_game_review.html
└── michigan_washington_game_review.html

analysis_index/
├── northwestern_pennstate_index.html  # Links to both analyses
└── michigan_washington_index.html     # Links to both analyses
```

This approach gives you **complete coverage** with both strategic and statistical perspectives! 🚀
