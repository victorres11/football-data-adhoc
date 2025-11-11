#!/usr/bin/env python3
"""
Generate comprehensive HTML analysis app comparing any two teams
Generic parameterized version - can be used for any team pair
"""

import json
import sys
from pathlib import Path
from load_advanced_pbp_data import load_team_data, filter_plays, get_game_list
from analyze_middle_eight import analyze_middle_eight
from analyze_explosive_plays import analyze_explosive_plays
from analyze_penalties import analyze_penalties
from analyze_4th_downs import analyze_4th_downs
from analyze_post_turnover import analyze_post_turnover
from analyze_special_teams import analyze_special_teams
from analyze_red_zone import analyze_red_zone
from analyze_situational_receiving import load_sis_data, analyze_situational_receiving
from analyze_deep_targets import analyze_deep_targets


def normalize_team_name(team_name: str) -> str:
    """
    Normalize team name for use in file paths and data keys.
    Converts to lowercase and replaces spaces with underscores.
    """
    return team_name.lower().replace(" ", "_").replace("-", "_")


def generate_html_app(team_name1: str = "Washington", team_name2: str = "Wisconsin",
                      output_file: str = None, data_dir: str = "advanced_reports_yogi",
                      sis_data_file: str = None, year: int = 2025):
    """
    Generate the comprehensive HTML analysis app with all analyses pre-computed
    
    Args:
        team_name1: Name of first team (default: "Washington")
        team_name2: Name of second team (default: "Wisconsin")
        output_file: Output HTML file path (default: "{team1}_{team2}_analysis_app.html")
        data_dir: Directory containing play-by-play data (default: "advanced_reports_yogi")
        sis_data_file: Path to SIS data JSON file (default: auto-generated from team names)
        year: Season year for SIS data file naming (default: 2025)
    """
    
    # Normalize team names for file paths and keys
    team1_key = normalize_team_name(team_name1)
    team2_key = normalize_team_name(team_name2)
    
    # Set default output file if not provided
    if output_file is None:
        output_file = f"{team1_key}_{team2_key}_analysis_app.html"
    
    # Set default SIS data file if not provided
    if sis_data_file is None:
        sis_data_file = f"{data_dir}/sis-data/{team1_key}_{team2_key}_analysis_{year}.json"
    
    # Load data for both teams
    print(f"Loading team data for {team_name1} and {team_name2}...")
    team1_data = load_team_data(team_name1, data_dir)
    team2_data = load_team_data(team_name2, data_dir)
    
    print(f"Running analyses for {team_name1}...")
    team1_middle8 = analyze_middle_eight(team1_data['all_plays'], team_name1)
    team1_explosive = analyze_explosive_plays(team1_data['all_plays'], team_name1)
    team1_penalties = analyze_penalties(team1_data['all_plays'], team_name1)
    team1_4th = analyze_4th_downs(team1_data['all_plays'], team_name1)
    team1_turnover = analyze_post_turnover(team1_data['all_plays'], team_name1)
    team1_st = analyze_special_teams(team1_data['all_plays'], team_name1)
    team1_redzone = analyze_red_zone(team1_data['all_plays'], team_name1)
    
    print(f"Running analyses for {team_name2}...")
    team2_middle8 = analyze_middle_eight(team2_data['all_plays'], team_name2)
    team2_explosive = analyze_explosive_plays(team2_data['all_plays'], team_name2)
    team2_penalties = analyze_penalties(team2_data['all_plays'], team_name2)
    team2_4th = analyze_4th_downs(team2_data['all_plays'], team_name2)
    team2_turnover = analyze_post_turnover(team2_data['all_plays'], team_name2)
    team2_st = analyze_special_teams(team2_data['all_plays'], team_name2)
    team2_redzone = analyze_red_zone(team2_data['all_plays'], team_name2)
    
    # Get game lists for filtering
    team1_games = get_game_list(team1_data)
    team2_games = get_game_list(team2_data)
    
    # Load BYE weeks data
    # Handle both relative and absolute paths
    if Path(data_dir).is_absolute():
        bye_weeks_path = Path(data_dir) / "bye_weeks.json"
    else:
        # Try from current directory, then from parent
        bye_weeks_path = Path(data_dir) / "bye_weeks.json"
        if not bye_weeks_path.exists():
            bye_weeks_path = Path("..") / data_dir / "bye_weeks.json"
    
    bye_weeks_data = {}
    if bye_weeks_path.exists():
        try:
            with open(bye_weeks_path, 'r') as f:
                bye_weeks_data = json.load(f)
            print(f"BYE weeks data loaded: {bye_weeks_data}")
        except Exception as e:
            print(f"Warning: Could not load BYE weeks data: {e}")
    else:
        print(f"Warning: BYE weeks file not found at {bye_weeks_path}")
    
    # Load SIS data and analyze situational receiving stats
    print("Loading SIS data...")
    try:
        sis_data = load_sis_data(sis_data_file)
        team1_situational = analyze_situational_receiving(sis_data, team_name1, team1_games)
        team2_situational = analyze_situational_receiving(sis_data, team_name2, team2_games)
        team1_deep_targets = analyze_deep_targets(sis_data, team_name1)
        team2_deep_targets = analyze_deep_targets(sis_data, team_name2)
        print("SIS situational receiving data loaded successfully")
        print("SIS deep target data loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load SIS data: {e}")
        team1_situational = {
            '3rd_down': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'redzone': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'game_mapping': {}
        }
        team2_situational = {
            '3rd_down': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'redzone': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'game_mapping': {}
        }
        team1_deep_targets = {
            'passing': {'total': {}, 'by_game': {}, 'last_3_games': {}, 'big_ten_rank': None},
            'receiving': {'total': {}, 'by_game': {}, 'last_3_games': {}, 'players': []}
        }
        team2_deep_targets = {
            'passing': {'total': {}, 'by_game': {}, 'last_3_games': {}, 'big_ten_rank': None},
            'receiving': {'total': {}, 'by_game': {}, 'last_3_games': {}, 'players': []}
        }
    
    # Serialize all analysis data for JavaScript
    # Use normalized team keys for JavaScript data structure
    all_data_json = json.dumps({
        team1_key: {
            'middle8': team1_middle8,
            'explosive': team1_explosive,
            'penalties': team1_penalties,
            '4thdowns': team1_4th,
            'turnover': team1_turnover,
            'specialteams': team1_st,
            'redzone': team1_redzone,
            'situational': team1_situational,
            'deep_targets': team1_deep_targets,
            'games': team1_games,
            'all_plays': team1_data['all_plays']
        },
        team2_key: {
            'middle8': team2_middle8,
            'explosive': team2_explosive,
            'penalties': team2_penalties,
            '4thdowns': team2_4th,
            'turnover': team2_turnover,
            'specialteams': team2_st,
            'redzone': team2_redzone,
            'situational': team2_situational,
            'deep_targets': team2_deep_targets,
            'games': team2_games,
            'all_plays': team2_data['all_plays']
        },
        'bye_weeks': bye_weeks_data
    })
    
    # Serialize for backwards compatibility (using normalized keys)
    team1_plays_json = json.dumps(team1_data['all_plays'])
    team2_plays_json = json.dumps(team2_data['all_plays'])
    team1_games_json = json.dumps(team1_games)
    team2_games_json = json.dumps(team2_games)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Team Analysis - {team_name1} vs {team_name2}</title>
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'><rect width='32' height='32' fill='%23002d72'/><text x='16' y='22' font-family='Arial,sans-serif' font-size='18' font-weight='bold' fill='white' text-anchor='middle'>B10</text></svg>" type="image/svg+xml">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <!-- DataTables -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: relative;
        }}
        
        .header-badge {{
            position: absolute;
            bottom: 15px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-align: right;
        }}
        
        .header-badge .made-by {{
            font-size: 0.7em;
            font-weight: 400;
            text-transform: lowercase;
            display: block;
            margin-bottom: 2px;
            opacity: 0.9;
        }}
        
        .header-badge .company {{
            text-transform: uppercase;
            display: block;
        }}
        
        @media (max-width: 768px) {{
            .header-badge {{
                position: static;
                display: inline-block;
                margin-top: 10px;
                font-size: 0.75em;
                padding: 6px 12px;
                text-align: center;
            }}
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .filters {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .filters h2 {{
            margin-bottom: 15px;
            color: #667eea;
        }}
        
        .filter-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .filter-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-item label {{
            font-weight: 600;
            margin-bottom: 5px;
            color: #555;
            font-size: 0.9em;
        }}
        
        .filter-item select,
        .filter-item input {{
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.95em;
        }}
        
        .filter-item select[multiple] {{
            height: 100px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            text-align: left;
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }}
        
        .summary-card:hover {{
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
            border-color: #c0c0c0;
        }}
        
        .summary-card h3 {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        
        .summary-card .value {{
            font-size: 2.2em;
            font-weight: 700;
            color: #333;
            margin-bottom: 0;
            line-height: 1.2;
        }}
        
        .summary-card .label {{
            font-size: 0.8em;
            color: #888;
            margin-top: 4px;
        }}
        
        .team-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .team-section {{
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .team-section.{team1_key} {{
            border-left-color: #8B0000;
        }}
        
        .team-section.{team2_key} {{
            border-left-color: #DC143C;
        }}
        
        .team-section h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .definition-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .notice-banner {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-left: 4px solid #ffc107;
            color: #856404;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 0.9em;
            display: flex;
            align-items: center;
        }}
        
        .notice-banner::before {{
            content: "⚠️";
            margin-right: 8px;
            font-size: 1.2em;
        }}
        
        .definition-box p {{
            margin: 0;
            line-height: 1.6;
            font-size: 0.95em;
        }}
        
        .plays-browser {{
            margin-top: 20px;
        }}
        
        .team-section-browser {{
            margin-bottom: 30px;
        }}
        
        .team-header-browser {{
            background: #667eea;
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            font-size: 1.3em;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
        }}
        
        .team-header-browser.{team1_key} {{
            background: #8B0000;
        }}
        
        .team-header-browser.{team2_key} {{
            background: #DC143C;
        }}
        
        .game-section-browser {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}
        
        .game-header-browser {{
            background: #f0f0f0;
            padding: 12px 16px;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 8px;
            border-left: 3px solid #667eea;
        }}
        
        .quarter-section-browser {{
            margin-left: 20px;
            margin-bottom: 10px;
        }}
        
        .quarter-header-browser {{
            background: #f8f8f8;
            padding: 10px 14px;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 6px;
            border-left: 2px solid #999;
        }}
        
        .drive-section-browser {{
            margin-left: 20px;
            margin-bottom: 8px;
        }}
        
        .drive-header-browser {{
            background: #fafafa;
            padding: 8px 12px;
            border-radius: 3px;
            font-weight: 500;
            cursor: pointer;
            margin-bottom: 4px;
            border-left: 2px solid #ccc;
        }}
        
        .plays-table-browser {{
            margin-left: 20px;
            margin-top: 8px;
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        .plays-table-browser th {{
            background: #e8e8e8;
            padding: 8px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #ddd;
        }}
        
        .plays-table-browser td {{
            padding: 6px 8px;
            border: 1px solid #ddd;
        }}
        
        .plays-table-browser tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        .collapsible-content {{
            display: none;
        }}
        
        .collapsible-content.expanded {{
            display: block;
        }}
        
        .expand-icon {{
            display: inline-block;
            margin-right: 8px;
            transition: transform 0.2s;
        }}
        
        .expand-icon.expanded {{
            transform: rotate(90deg);
        }}
        
        .insight-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 16px 20px;
            border-radius: 4px;
            margin-bottom: 20px;
            margin-top: 10px;
        }}
        
        .insight-box h4 {{
            margin: 0 0 10px 0;
            color: #1976d2;
            font-size: 1.05em;
        }}
        
        .insight-box ul {{
            margin: 8px 0 0 0;
            padding-left: 20px;
        }}
        
        .insight-box li {{
            margin: 5px 0;
            line-height: 1.5;
        }}
        
        .definition-box strong {{
            font-weight: 600;
            font-size: 1.05em;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-bottom: 30px;
        }}
        
        /* SIS Data Section Styling - Option 4 Combination Approach */
        .section.sis-section {{
            background: #f8f9fa;
            border: 2px dashed #6c757d;
            border-radius: 8px;
        }}
        
        .section.sis-section h2 {{
            position: relative;
            padding-right: 120px;
        }}
        
        .sis-badge {{
            display: inline-block;
            background: #6c757d;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.6em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
        }}
        
        .section.sis-section .summary-card {{
            border-color: #6c757d;
            background: white;
        }}
        
        .section.sis-section .summary-card:hover {{
            border-color: #495057;
            box-shadow: 0 2px 8px rgba(108, 117, 125, 0.15);
        }}
        
        .sis-info-box {{
            background: #e9ecef;
            border-left: 4px solid #6c757d;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #495057;
        }}
        
        .sis-info-box strong {{
            color: #343a40;
        }}
        
        /* Main Container with Sidebar */
        body {{
            margin: 0;
            padding: 0;
        }}
        
        .main-wrapper {{
            display: flex;
            flex-direction: row;
            min-height: 100vh;
        }}
        
        @media (max-width: 768px) {{
            .main-wrapper {{
                flex-direction: column;
            }}
        }}
        
        /* Smooth Scrolling */
        html {{
            scroll-behavior: smooth;
        }}
        
        /* Navigation Menu - Fixed Left Sidebar */
        .nav-menu {{
            position: fixed;
            left: 0;
            top: 0;
            width: 240px;
            height: 100vh;
            background: rgba(248, 249, 250, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid #e0e0e0;
            padding: 20px 15px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 2px 0 8px rgba(0,0,0,0.05);
        }}
        
        .nav-menu::-webkit-scrollbar {{
            width: 6px;
        }}
        
        .nav-menu::-webkit-scrollbar-track {{
            background: transparent;
        }}
        
        .nav-menu::-webkit-scrollbar-thumb {{
            background: #ccc;
            border-radius: 3px;
        }}
        
        .nav-menu::-webkit-scrollbar-thumb:hover {{
            background: #999;
        }}
        
        .nav-menu h2 {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.1em;
            color: #667eea;
            font-weight: 600;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .nav-links {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        
        .nav-links li {{
            margin: 0;
        }}
        
        .nav-links a {{
            display: block;
            padding: 10px 12px;
            background: transparent;
            border: none;
            border-radius: 6px;
            text-decoration: none;
            color: #555;
            transition: all 0.2s ease;
            font-size: 0.9em;
            font-weight: 400;
        }}
        
        .nav-links a:hover {{
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
        }}
        
        .nav-links a:active {{
            background: rgba(102, 126, 234, 0.15);
        }}
        
        .nav-links a.active {{
            background: rgba(102, 126, 234, 0.15);
            color: #667eea;
            font-weight: 500;
        }}
        
        /* Filters in Nav Menu */
        .nav-filters {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .nav-filters h3 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 0.95em;
            color: #667eea;
            font-weight: 600;
        }}
        
        .nav-filter-item {{
            margin-bottom: 15px;
        }}
        
        .nav-filter-item label {{
            display: block;
            margin-bottom: 6px;
            font-size: 0.85em;
            color: #555;
            font-weight: 500;
        }}
        
        .nav-filter-item select {{
            width: 100%;
            padding: 8px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.85em;
            background: white;
            color: #333;
            cursor: pointer;
        }}
        
        .nav-filter-item select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
        }}
        
        .nav-filter-buttons {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 15px;
        }}
        
        .nav-filter-btn {{
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .nav-filter-btn.apply {{
            background: #667eea;
            color: white;
        }}
        
        .nav-filter-btn.apply:hover {{
            background: #5568d3;
        }}
        
        .nav-filter-btn.reset {{
            background: #f0f0f0;
            color: #555;
        }}
        
        .nav-filter-btn.reset:hover {{
            background: #e0e0e0;
        }}
        
        /* Content Area */
        .content-area {{
            margin-left: 240px;
            width: calc(100% - 240px);
            padding: 20px 40px;
            flex-grow: 1;
        }}
        
        @media (max-width: 1024px) {{
            .nav-menu {{
                width: 200px;
            }}
            .content-area {{
                margin-left: 200px;
                width: calc(100% - 200px);
                padding: 20px 30px;
            }}
        }}
        
        @media (max-width: 768px) {{
            .nav-menu {{
                display: none;
            }}
            .content-area {{
                margin-left: 0;
                width: 100%;
                padding: 20px;
            }}
        }}
        
        .dataTables_wrapper {{
            margin-top: 20px;
        }}
        
        .dataTables_wrapper .dataTables_scroll {{
            margin-top: 10px;
        }}
        
        .dataTables_wrapper .dataTables_scrollBody {{
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        table td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        
        table tr:hover {{
            background: #f5f5f5;
        }}
        
        table tr.opponent-row {{
            background-color: #fff3e0;
            border-left: 3px solid #ff9800;
        }}
        
        table tr.opponent-row:hover {{
            background-color: #ffe0b2;
        }}
        
        table tr.team-row {{
            background-color: #ffffff;
        }}
        
        table tr.team-row:hover {{
            background-color: #f5f5f5;
        }}
        
        /* 4th Down Conversion Highlighting */
        table tr.converted-success {{
            background-color: rgba(76, 175, 80, 0.08) !important;
            border-left: 3px solid rgba(76, 175, 80, 0.6);
        }}
        
        table tr.converted-success:hover {{
            background-color: rgba(76, 175, 80, 0.12) !important;
            border-left-color: rgba(76, 175, 80, 0.8);
        }}
        
        table tr.converted-failed {{
            background-color: rgba(244, 67, 54, 0.08) !important;
            border-left: 3px solid rgba(244, 67, 54, 0.6);
        }}
        
        table tr.converted-failed:hover {{
            background-color: rgba(244, 67, 54, 0.12) !important;
            border-left-color: rgba(244, 67, 54, 0.8);
        }}
        
        /* Top 25 Big Ten Rank Highlighting */
        table tr.top-25-rank {{
            background-color: #e8f5e9 !important;
            border-left: 3px solid #4caf50;
        }}
        
        table tr.top-25-rank:hover {{
            background-color: #c8e6c9 !important;
        }}
        
        /* Hide DataTables search and pagination */
        .dataTables_filter {{
            display: none;
        }}
        
        .dataTables_paginate {{
            display: none;
        }}
        
        .dataTables_info {{
            display: none;
        }}
        
        .dataTables_length {{
            display: none;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge.success {{
            background: #4caf50;
            color: white;
        }}
        
        .badge.danger {{
            background: #f44336;
            color: white;
        }}
        
        .badge.warning {{
            background: #ff9800;
            color: white;
        }}
        
        .badge.info {{
            background: #2196f3;
            color: white;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.95em;
            margin: 5px;
        }}
        
        .btn:hover {{
            background: #5568d3;
        }}
        
        @media (max-width: 768px) {{
            .team-comparison {{
                grid-template-columns: 1fr;
            }}
            
            .summary-cards {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="main-wrapper">
        <!-- Navigation Menu - Fixed Left Sidebar -->
        <nav class="nav-menu">
            <h2>Navigation</h2>
            <ul class="nav-links">
                <li><a href="#middleEightSection">Middle 8 Analysis</a></li>
                <li><a href="#explosivePlaysSection">Explosive Plays</a></li>
                <li><a href="#penaltySection">Penalty Analysis</a></li>
                <li><a href="#fourthDownSection">4th Down Decisions</a></li>
                <li><a href="#postTurnoverSection">Post Turnover</a></li>
                <li><a href="#specialTeamsSection">Special Teams</a></li>
                <li><a href="#redZoneSection">Red Zone / Green Zone</a></li>
                <li><a href="#situationalReceivingSection">Situational Receiving</a></li>
                <li><a href="#deepTargetSection">Deep Target Analysis</a></li>
                <li><a href="#allPlaysSection">All Plays Browser</a></li>
            </ul>
            
            <!-- Filters at Bottom of Nav -->
            <div class="nav-filters">
                <h3>Filters</h3>
                <div class="nav-filter-item">
                    <label>Game Type</label>
                    <select id="conferenceFilter">
                        <option value="all">All Games</option>
                        <option value="conference">Conference Only</option>
                        <option value="non-conference">Non-Conference Only</option>
                        <option value="power4">Power 4 Opponents Only</option>
                    </select>
                </div>
                <div class="nav-filter-item">
                    <label>Time Period</label>
                    <select id="timePeriodFilter">
                        <option value="all">All Games</option>
                        <option value="last3">Last 3 Games</option>
                    </select>
                </div>
                <div class="nav-filter-buttons">
                    <button class="nav-filter-btn apply" onclick="applyFilters()">Apply Filters</button>
                    <button class="nav-filter-btn reset" onclick="resetFilters()">Reset</button>
                </div>
            </div>
        </nav>
        
        <!-- Main Content Area -->
        <div class="content-area">
            <div class="container">
                <header>
                    <h1>Advanced Team Analysis</h1>
                    <p>{team_name1} vs {team_name2} - Comprehensive Play-by-Play Analysis</p>
                    <div class="header-badge">
                        <span class="made-by">made by</span>
                        <span class="company">VT Sports Solutions</span>
                    </div>
                </header>
                
                <div class="notice-banner">
                    This analysis is best viewed on a computer or tablet. Mobile viewing may have limited functionality.
                </div>
        
        <!--
        <div class="filters">
            <h2>Filters</h2>
            <div class="filter-group">
                <div class="filter-item">
                    <label>Game Type</label>
                    <select id="conferenceFilter">
                        <option value="all">All Games</option>
                        <option value="conference">Conference Only</option>
                        <option value="non-conference">Non-Conference Only</option>
                        <option value="power4">Power 4 Opponents Only</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label>Time Period</label>
                    <select id="timePeriodFilter">
                        <option value="all">All Games</option>
                        <option value="last3">Last 3 Games</option>
                    </select>
                </div>
            </div>
            <button class="btn" onclick="applyFilters()">Apply Filters</button>
            <button class="btn" onclick="resetFilters()">Reset</button>
        </div>
        -->
        
        <!-- Middle 8 Analysis -->
        <div class="section" id="middleEightSection">
            <h2>Middle 8 Analysis</h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> The "Middle 8" refers to the final 4 minutes of the first half and the first 4 minutes of the second half.</p>
            </div>
            <div class="insight-box">
                <h4>Key Insights:</h4>
                <ul>
                    <li><strong>Performance Gap:</strong> Both teams show decreased performance during Middle 8 periods compared to regular game time.</li>
                    <li><strong>Explosive Rate:</strong> Teams show varying explosive play rates during Middle 8 periods.</li>
                </ul>
            </div>
            <div id="middleEightSummary"></div>
            <div class="chart-container">
                <canvas id="middleEightChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="middleEightTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
            <table id="middleEightTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Scoring Team</th>
                        <th>Drive</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Result</th>
                        <th>Points</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
            <table id="middleEightTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Scoring Team</th>
                        <th>Drive</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Result</th>
                        <th>Points</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- Explosive Plays Analysis -->
        <div class="section" id="explosivePlaysSection">
            <h2>Explosive Plays Analysis</h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> Explosive plays are runs of 15+ yards or passes of 20+ yards while on offense.</p>
            </div>
            <div class="insight-box">
                <h4>Key Insights:</h4>
                <ul>
                    <li><strong>Drive Conversion:</strong> Teams show varying rates of converting explosive plays into scores.</li>
                    <li><strong>Quarterly Distribution:</strong> Explosive play rates vary by quarter for both teams.</li>
                    <li><strong>2nd & Long Efficiency:</strong> Teams show different efficiency levels on difficult 2nd down situations.</li>
                </ul>
            </div>
            <div id="explosivePlaysSummary"></div>
            <div class="chart-container">
                <canvas id="explosivePlaysChart"></canvas>
            </div>
            <div class="chart-container" style="margin-top: 30px;">
                <canvas id="explosivePlaysTrendChartWash"></canvas>
            </div>
            <div class="chart-container" style="margin-top: 30px;">
                <canvas id="explosivePlaysTrendChartWisc"></canvas>
            </div>
            <div style="display: flex; gap: 20px; margin-top: 30px;">
                <div class="chart-container" style="flex: 1;">
                    <canvas id="explosiveRunPassChartWash"></canvas>
                </div>
                <div class="chart-container" style="flex: 1;">
                    <canvas id="explosiveRunPassChartWisc"></canvas>
                </div>
            </div>
            <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
            <table id="explosivePlaysTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Down</th>
                        <th>Distance</th>
                        <th>Play Type</th>
                        <th>Yards Gained</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
            <table id="explosivePlaysTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Down</th>
                        <th>Distance</th>
                        <th>Play Type</th>
                        <th>Yards Gained</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- Penalty Analysis -->
        <div class="section" id="penaltySection">
            <h2>Penalty Analysis</h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> Penalties can significantly impact field position, drive outcomes, and game flow. This analysis tracks all penalties (both accepted and declined) to identify patterns in penalty frequency, types, and timing. High penalty counts often correlate with discipline issues and can cost teams field position and scoring opportunities.</p>
            </div>
            <div class="insight-box">
                <h4>Key Insights:</h4>
                <ul>
                    <li><strong>Penalty-Explosive Correlation:</strong> Teams show varying correlations between penalties and explosive plays on the same drives.</li>
                </ul>
            </div>
            <div id="penaltySummary"></div>
            <div class="chart-container">
                <canvas id="penaltyChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="penaltyTrendChart"></canvas>
            </div>
            
            <!-- Additional Penalty Visualizations -->
            <h3 style="margin-top: 40px; color: #667eea; font-size: 1.3em;">Penalty Breakdowns</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                <div class="chart-container">
                    <canvas id="penaltyByQuarterChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="penaltyTypeChart"></canvas>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                <div class="chart-container">
                    <canvas id="penaltyByDownChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="penaltyByHalfChart"></canvas>
                </div>
            </div>
            
            <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
            <table id="penaltyTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Penalty Type</th>
                        <th>Decision</th>
                        <th>Yards Lost</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
            <table id="penaltyTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Penalty Type</th>
                        <th>Decision</th>
                        <th>Yards Lost</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- 4th Down Analysis -->
        <div class="section" id="fourthDownSection">
            <h2>4th Down Decision Analysis</h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> This analysis focuses on "Go For It" 4th down decisions (excluding punts and field goal attempts).</p>
            </div>
            <div class="insight-box">
                <h4>Key Insights:</h4>
                <ul>
                    <li><strong>4th & 1 Dominance:</strong> Teams show varying efficiency levels on critical 4th & 1 situations.</li>
                    <li><strong>Situational Efficiency:</strong> Teams perform differently across various down/distance situations.</li>
                </ul>
            </div>
            <div id="fourthDownSummary"></div>
            <div class="chart-container">
                <canvas id="fourthDownChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="fourthDownTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
            <table id="fourthDownTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Yard Line</th>
                        <th>Distance</th>
                        <th>Play Type</th>
                        <th>Converted</th>
                        <th>Yards Gained</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
            <table id="fourthDownTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Yard Line</th>
                        <th>Distance</th>
                        <th>Play Type</th>
                        <th>Converted</th>
                        <th>Yards Gained</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- Post Turnover Analysis -->
        <div class="section" id="postTurnoverSection">
            <h2>Post Turnover Analysis</h2>
            <div class="insight-box">
                <h4>Key Insights:</h4>
                <ul>
                    <li><strong>1st Quarter Turnover Problem:</strong> Teams show varying turnover rates in the first quarter, which can indicate game-opening script execution issues.</li>
                    <li><strong>Field Position:</strong> Teams show different patterns in where turnovers occur on the field.</li>
                </ul>
            </div>
            <div id="postTurnoverSummary"></div>
            <div class="chart-container">
                <canvas id="postTurnoverChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="postTurnoverTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
            <table id="postTurnoverTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Turnover Type</th>
                        <th>Offense</th>
                        <th>Drive Result</th>
                        <th>Points Scored</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
            <table id="postTurnoverTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Turnover Type</th>
                        <th>Offense</th>
                        <th>Drive Result</th>
                        <th>Points Scored</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- Special Teams Analysis -->
        <div class="section" id="specialTeamsSection">
            <h2>Special Teams Analysis</h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> Special teams encompasses kickoffs, punts, field goals, and returns. This analysis focuses on explosive special teams plays (35+ yard kick returns, 20+ yard punt returns) and explosive returns allowed by opponents. Special teams can swing field position and momentum, making it a critical phase of the game that often determines close contests.</p>
            </div>
            <div class="insight-box">
                <h4>Key Insights:</h4>
                <ul>
                    <li><strong>Red Zone Efficiency:</strong> Teams show varying performance levels in the red zone, indicating different play-calling effectiveness in compressed space.</li>
                    <li><strong>Own Territory Struggles:</strong> Teams show different performance levels in their own 21-40 yard line zone.</li>
                </ul>
            </div>
            <div id="specialTeamsSummary"></div>
            <div class="chart-container">
                <canvas id="specialTeamsTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
            <table id="specialTeamsTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Play Type</th>
                        <th>Result</th>
                        <th>Yards</th>
                        <th>Explosive</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
            <table id="specialTeamsTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Play Type</th>
                        <th>Result</th>
                        <th>Yards</th>
                        <th>Explosive</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- Red Zone / Green Zone Analysis -->
        <div class="section" id="redZoneSection">
            <h2>Red Zone / Green Zone Analysis</h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> The Tight Red Zone (10 yards to goal and in), Red Zone (20 yards to goal and in), and Green Zone (30 yards to goal and in) are critical scoring areas. Success in these zones is measured by scoring rate (TDs and FGs), conversion rates on 3rd/4th down, and PPA. Teams that consistently score in the red zone win more games, while teams that struggle often settle for field goals or turn the ball over.</p>
            </div>
            <div id="redZoneSummary"></div>
            <div class="chart-container">
                <canvas id="redZoneChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
            <h4 style="color: #b71c1c; margin-top: 20px;">Tight Red Zone Plays (10 & In)</h4>
            <table id="tightRedZoneTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Down</th>
                        <th>Dist</th>
                        <th>YTG</th>
                        <th>Play Type</th>
                        <th>Yards</th>
                        <th>Scoring</th>
                        <th>Explosive</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h4 style="color: #4a90e2; margin-top: 20px;">Green Zone Plays (30 & In)</h4>
            <table id="greenZoneTableWash" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Down</th>
                        <th>Dist</th>
                        <th>YTG</th>
                        <th>Play Type</th>
                        <th>Yards</th>
                        <th>Scoring</th>
                        <th>Explosive</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
            <h4 style="color: #b71c1c; margin-top: 20px;">Tight Red Zone Plays (10 & In)</h4>
            <table id="tightRedZoneTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Down</th>
                        <th>Dist</th>
                        <th>YTG</th>
                        <th>Play Type</th>
                        <th>Yards</th>
                        <th>Scoring</th>
                        <th>Explosive</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <h4 style="color: #c41e3a; margin-top: 20px;">Green Zone Plays (30 & In)</h4>
            <table id="greenZoneTableWisc" class="display">
                <thead>
                    <tr>
                        <th>Week</th>
                        <th>Opponent</th>
                        <th>Period</th>
                        <th>Clock</th>
                        <th>Down</th>
                        <th>Dist</th>
                        <th>YTG</th>
                        <th>Play Type</th>
                        <th>Yards</th>
                        <th>Scoring</th>
                        <th>Explosive</th>
                        <th>PPA</th>
                        <th>Play Description</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <!-- Situational Receiving Analysis (SIS Data) -->
        <div class="section sis-section" id="situationalReceivingSection">
            <h2>Situational Receiving Analysis <span class="sis-badge">SIS</span></h2>
            
            <!-- 3rd Down Receiving -->
            <div style="margin-bottom: 40px;">
                <h3 style="color: #667eea; margin-bottom: 15px; font-size: 1.4em;">3rd Down Receiving</h3>
                <div id="thirdDownSummary"></div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                    <div class="chart-container">
                        <canvas id="thirdDownChartWash"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="thirdDownChartWisc"></canvas>
                    </div>
                </div>
                <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
                <table id="thirdDownTableWash" class="display">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Opponent</th>
                            <th>Player</th>
                            <th>Targets</th>
                            <th>Receptions</th>
                            <th>Reception %</th>
                            <th>First Downs</th>
                            <th>TDs</th>
                            <th>Yards</th>
                            <th>Big Ten Rank</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
                <table id="thirdDownTableWisc" class="display">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Opponent</th>
                            <th>Player</th>
                            <th>Targets</th>
                            <th>Receptions</th>
                            <th>Reception %</th>
                            <th>First Downs</th>
                            <th>TDs</th>
                            <th>Yards</th>
                            <th>Big Ten Rank</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <!-- Red Zone Receiving -->
            <div style="margin-top: 50px;">
                <h3 style="color: #667eea; margin-bottom: 15px; font-size: 1.4em;">Red Zone Receiving</h3>
                <div id="redZoneReceivingSummary"></div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                    <div class="chart-container">
                        <canvas id="redZoneReceivingChartWash"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="redZoneReceivingChartWisc"></canvas>
                    </div>
                </div>
                <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
                <table id="redZoneReceivingTableWash" class="display">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Opponent</th>
                            <th>Player</th>
                            <th>Targets</th>
                            <th>Receptions</th>
                            <th>Reception %</th>
                            <th>TDs</th>
                            <th>Yards</th>
                            <th>Big Ten Rank</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
                <table id="redZoneReceivingTableWisc" class="display">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Opponent</th>
                            <th>Player</th>
                            <th>Targets</th>
                            <th>Receptions</th>
                            <th>Reception %</th>
                            <th>TDs</th>
                            <th>Yards</th>
                            <th>Big Ten Rank</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <!-- Deep Target Analysis (SIS Data) -->
        <div class="section sis-section" id="deepTargetSection">
            <h2>Deep Target Analysis (20+ Air Yards) <span class="sis-badge">SIS</span></h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> Deep targets are pass attempts with 20 or more air yards. This section analyzes both passing attempts and receiving targets for deep ball plays.</p>
            </div>
            
            <!-- Combined Summary -->
            <div style="margin-bottom: 40px;">
                <h3 style="color: #667eea; margin-bottom: 15px; font-size: 1.4em;">Deep Target Summary</h3>
                <div id="deepTargetSummary"></div>
            </div>
            
            <!-- Passing Charts -->
            <div style="margin-bottom: 40px;">
                <h3 style="color: #667eea; margin-bottom: 15px; font-size: 1.4em;">Deep Ball Passing</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                    <div class="chart-container">
                        <canvas id="deepPassingChartWash"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="deepPassingChartWisc"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Receiving Charts -->
            <div style="margin-top: 50px;">
                <h3 style="color: #667eea; margin-bottom: 15px; font-size: 1.4em;">Deep Ball Receiving</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                    <div class="chart-container">
                        <canvas id="deepReceivingChartWash"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="deepReceivingChartWisc"></canvas>
                    </div>
                </div>
                <h3 style="margin-top: 30px; color: #8B0000;">{team_name1}</h3>
                <table id="deepReceivingTableWash" class="display">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Opponent</th>
                            <th>Player</th>
                            <th>Targets</th>
                            <th>Receptions</th>
                            <th>Reception %</th>
                            <th>Yards</th>
                            <th>Air Yards</th>
                            <th>TDs</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <h3 style="margin-top: 30px; color: #DC143C;">{team_name2}</h3>
                <table id="deepReceivingTableWisc" class="display">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Opponent</th>
                            <th>Player</th>
                            <th>Targets</th>
                            <th>Receptions</th>
                            <th>Reception %</th>
                            <th>Yards</th>
                            <th>Air Yards</th>
                            <th>TDs</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <!-- All Plays Browser -->
        <div class="section" id="allPlaysSection">
            <h2>All Plays Browser</h2>
            <div class="definition-box">
                <p><strong>Definition:</strong> Browse all plays organized by team, game, quarter, and drive. Click to expand any section to view detailed play information.</p>
            </div>
            <div id="allPlaysContainer"></div>
        </div>
    </div>
    
    <script>
        // Data from Python - All pre-computed analyses
        const allData = JSON.parse({all_data_json!r});
        // Team keys (normalized for data access)
        const team1Key = '{team1_key}';
        const team2Key = '{team2_key}';
        const team1Name = '{team_name1}';
        const team2Name = '{team_name2}';
        // Store original data for filtering (deep copy to avoid reference issues)
        const originalAllData = {{
            [team1Key]: JSON.parse(JSON.stringify(allData[team1Key])),
            [team2Key]: JSON.parse(JSON.stringify(allData[team2Key]))
        }};
        // Plays and games data
        const team1Plays = {team1_plays_json};
        const team2Plays = {team2_plays_json};
        const team1Games = {team1_games_json};
        const team2Games = {team2_games_json};
        
        // Charts storage
        const charts = {{}};
        
        // Helper function to format clock from "seconds=X minutes=Y" to "MM:SS"
        function formatClock(clockStr) {{
            if (!clockStr || typeof clockStr !== 'string') return '';
            
            // Parse format like "seconds=26 minutes=13"
            const secondsMatch = clockStr.match(/seconds=(\d+)/);
            const minutesMatch = clockStr.match(/minutes=(\d+)/);
            
            if (secondsMatch && minutesMatch) {{
                const minutes = parseInt(minutesMatch[1], 10);
                const seconds = parseInt(secondsMatch[1], 10);
                return `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            }}
            
            // If parsing fails, return original
            return clockStr;
        }}
        
        function parseClockToSeconds(clockStr) {{
            if (!clockStr) return 0;
            const minutesMatch = clockStr.match(/minutes=(\\d+)/);
            const secondsMatch = clockStr.match(/seconds=(\\d+)/);
            if (minutesMatch && secondsMatch) {{
                const minutes = parseInt(minutesMatch[1], 10);
                const seconds = parseInt(secondsMatch[1], 10);
                return minutes * 60 + seconds;
            }}
            return 0;
        }}
        
        function sortPlaysChronologically(plays) {{
            return plays.slice().sort((a, b) => {{
                // First sort by week
                const weekA = a.game_week || 0;
                const weekB = b.game_week || 0;
                if (weekA !== weekB) return weekA - weekB;
                
                // Then by period
                const periodA = a.period || 0;
                const periodB = b.period || 0;
                if (periodA !== periodB) return periodA - periodB;
                
                // Then by clock (higher time = earlier in period, so sort descending)
                const clockA = parseClockToSeconds(a.clock);
                const clockB = parseClockToSeconds(b.clock);
                return clockB - clockA;  // Descending (more time = earlier)
            }});
        }}
        
        function sortDrivesChronologically(drives) {{
            return drives.slice().sort((a, b) => {{
                // First sort by week
                const weekA = a.game_week || 0;
                const weekB = b.game_week || 0;
                if (weekA !== weekB) return weekA - weekB;
                
                // Then by period
                const periodA = a.period || 0;
                const periodB = b.period || 0;
                if (periodA !== periodB) return periodA - periodB;
                
                // Then by clock (higher time = earlier in period, so sort descending)
                const clockA = parseClockToSeconds(a.clock);
                const clockB = parseClockToSeconds(b.clock);
                return clockB - clockA;  // Descending (more time = earlier)
            }});
        }}
        
        // Helper function to add week-based classes to table rows
        function addWeekClass(row, weekValue) {{
            // Extract week number from week value (could be number or string like "Week 1")
            let weekNum = 0;
            if (typeof weekValue === 'number') {{
                weekNum = weekValue;
            }} else if (typeof weekValue === 'string') {{
                const match = weekValue.match(/\\d+/);
                if (match) weekNum = parseInt(match[0], 10);
            }}
            
            // Add class based on week number (week-1, week-2, etc.)
            if (weekNum > 0) {{
                $(row).addClass('week-' + weekNum);
            }}
        }}
        
        // Create master week mapping - includes all weeks from 1 to max_week, with BYE weeks as 0
        const masterWeekMapping = (function() {{
            // Get BYE weeks data (if available)
            const byeWeeks = allData.bye_weeks || {{}};
            const team1ByeWeeks = new Set(byeWeeks[team1Name]?.bye_weeks || []);
            const team2ByeWeeks = new Set(byeWeeks[team2Name]?.bye_weeks || []);
            
            // Get all unique game IDs and their week numbers
            const allGameIds = new Set();
            team1Games.forEach(g => {{ if (g.game_id) allGameIds.add(g.game_id); }});
            team2Games.forEach(g => {{ if (g.game_id) allGameIds.add(g.game_id); }});
            
            // Get week for each game from the game lists
            const allGames = Array.from(allGameIds).map(gameId => {{
                const washGame = team1Games.find(g => g.game_id === gameId);
                const wiscGame = team2Games.find(g => g.game_id === gameId);
                const week = washGame?.week || wiscGame?.week || 0;
                return {{ gameId, week: week }};
            }});
            
            // Find the maximum week number
            const maxWeek = Math.max(...allGames.map(g => g.week).filter(w => w > 0), 0);
            
            // Create mapping: gameId -> week number
            const gameIdToWeek = {{}};
            allGames.forEach(game => {{
                if (game.week > 0) {{
                    gameIdToWeek[game.gameId] = game.week;
                }}
            }});
            
            // Create week-to-opponent mappings for both teams
            // Explicitly mark BYE weeks if they exist in the bye_weeks data
            const team1WeekToOpponent = {{}};
            team1Games.forEach(game => {{
                if (game.week && game.opponent) {{
                    team1WeekToOpponent[game.week] = game.opponent;
                }}
            }});
            // Mark BYE weeks explicitly (opponent will be 'BYE' or undefined)
            team1ByeWeeks.forEach(week => {{
                if (!team1WeekToOpponent[week]) {{
                    team1WeekToOpponent[week] = 'BYE';
                }}
            }});
            
            const team2WeekToOpponent = {{}};
            team2Games.forEach(game => {{
                if (game.week && game.opponent) {{
                    team2WeekToOpponent[game.week] = game.opponent;
                }}
            }});
            // Mark BYE weeks explicitly (opponent will be 'BYE' or undefined)
            team2ByeWeeks.forEach(week => {{
                if (!team2WeekToOpponent[week]) {{
                    team2WeekToOpponent[week] = 'BYE';
                }}
            }});
            
            // Create week labels for all weeks (1 to maxWeek)
            const weekLabels = [];
            for (let week = 1; week <= maxWeek; week++) {{
                weekLabels.push(`Week ${{week}}`);
            }}
            
            return {{ gameIdToWeek, allGames: allGames, weekLabels, maxWeek, team1WeekToOpponent, team2WeekToOpponent, team1ByeWeeks, team2ByeWeeks }};
        }})();
        
        // Helper function to get week number for a game ID
        function getWeekForGameId(gameId) {{
            return masterWeekMapping.gameIdToWeek[gameId] || null;
        }}
        
        // Helper function to get master game mapping (for backward compatibility - deprecated)
        function createGameIdToGameNumberMapping(plays) {{
            // Return week mapping instead of sequential game numbers
            return masterWeekMapping.gameIdToWeek;
        }}
        
        // Helper function to calculate trends by week (includes BYE weeks with 0)
        function calculateTrendsByWeek(plays, teamName, metricFn) {{
            const byWeek = {{}};
            plays.forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                if (!byWeek[week]) {{
                    byWeek[week] = {{ plays: [] }};
                }}
                byWeek[week].plays.push(play);
            }});
            
            // Create array with all weeks (1 to maxWeek), filling in 0 for BYE weeks
            const values = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                const weekPlays = byWeek[week]?.plays || [];
                values.push(metricFn(weekPlays, teamName));
            }}
            
            return {{ weeks: masterWeekMapping.weekLabels, values: values }};
        }}
        
        function calculateTurnoverTrends(plays, teamName) {{
            const byWeek = {{}};
            plays.forEach(play => {{
                if (play.turnover === true) {{
                    const gameId = play.game_id;
                    if (!gameId) return;
                    const week = getWeekForGameId(gameId);
                    if (!week) return;
                    
                    if (!byWeek[week]) {{
                        byWeek[week] = {{ ourTO: 0, oppTO: 0 }};
                    }}
                    const isOur = play.offense?.toLowerCase() === teamName.toLowerCase();
                    if (isOur) {{
                        byWeek[week].ourTO++;
                    }} else {{
                        byWeek[week].oppTO++;
                    }}
                }}
            }});
            
            const ourTurnovers = [];
            const oppTurnovers = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                ourTurnovers.push(byWeek[week]?.ourTO || 0);
                oppTurnovers.push(byWeek[week]?.oppTO || 0);
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                ourTurnovers: ourTurnovers,
                oppTurnovers: oppTurnovers
            }};
        }}
        
        function calculateNetPointsByWeek(plays, teamName) {{
            const turnovers = plays.filter(p => p.turnover === true);
            const postTurnoverPlays = plays.filter(p => p.drive_started_after_turnover === true);
            
            const byWeek = {{}};
            
            turnovers.forEach(turnover => {{
                const gameId = turnover.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                if (!byWeek[week]) {{
                    byWeek[week] = {{ pointsScored: 0, pointsAllowed: 0 }};
                }}
                
                const isOurTurnover = turnover.offense?.toLowerCase() === teamName.toLowerCase();
                
                // Find subsequent drive
                const nextDrivePlays = postTurnoverPlays.filter(p => 
                    p.game_id === turnover.game_id && p.drive_id !== turnover.drive_id
                );
                
                let drivePoints = 0;
                nextDrivePlays.forEach(p => {{
                    if (p.scoring === true) {{
                        if (p.play_type?.includes('Touchdown')) {{
                            drivePoints = 7;
                        }} else if (p.play_type?.includes('Field Goal')) {{
                            drivePoints = 3;
                        }}
                    }}
                }});
                
                if (isOurTurnover) {{
                    byWeek[week].pointsAllowed += drivePoints;
                }} else {{
                    byWeek[week].pointsScored += drivePoints;
                }}
            }});
            
            const netPoints = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                const weekData = byWeek[week] || {{ pointsScored: 0, pointsAllowed: 0 }};
                netPoints.push(weekData.pointsScored - weekData.pointsAllowed);
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                netPoints: netPoints
            }};
        }}
        
        function calculateMiddle8Trends(plays, teamName) {{
            const byWeek = {{}};
            plays.filter(p => p.middle_eight === true).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                if (!byWeek[week]) {{
                    byWeek[week] = {{ scored: 0, allowed: 0 }};
                }}
                if (play.scoring === true) {{
                    const points = play.play_type?.includes('Touchdown') ? 7 : (play.play_type?.includes('Field Goal') ? 3 : 0);
                    const isOur = play.offense?.toLowerCase() === teamName.toLowerCase();
                    if (isOur) {{
                        byWeek[week].scored += points;
                    }} else {{
                        byWeek[week].allowed += points;
                    }}
                }}
            }});
            
            const scored = [];
            const allowed = [];
            const net = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                const weekData = byWeek[week] || {{ scored: 0, allowed: 0 }};
                scored.push(weekData.scored);
                allowed.push(weekData.allowed);
                net.push(weekData.scored - weekData.allowed);
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                scored: scored,
                allowed: allowed,
                net: net
            }};
        }}
        
        function calculateExplosiveTrends(plays, teamName) {{
            const byWeek = {{}};
            plays.filter(p => 
                p.explosive_play === true && 
                p.play_classification !== 'special_teams'
            ).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                if (!byWeek[week]) {{
                    byWeek[week] = {{ ours: 0, allowed: 0 }};
                }}
                const isOurs = play.offense?.toLowerCase() === teamName.toLowerCase();
                if (isOurs) {{
                    byWeek[week].ours++;
                }} else {{
                    byWeek[week].allowed++;
                }}
            }});
            
            const ours = [];
            const allowed = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                const weekData = byWeek[week] || {{ ours: 0, allowed: 0 }};
                ours.push(weekData.ours);
                allowed.push(weekData.allowed);
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                ours: ours,
                allowed: allowed
            }};
        }}
        
        function calculateSpecialTeamsExplosiveTrends(plays, teamName) {{
            // Check if special teams play is explosive: 35+ kick return, 20+ punt return
            function isSpecialTeamsExplosive(play) {{
                if (play.play_classification !== 'special_teams') return false;
                const pt = (play.play_type || '').toLowerCase();
                const ptxt = (play.play_text || '').toLowerCase();
                
                // For returns, we need to parse the return yards from the play text
                // because yards_gained might include the kick/punt distance
                function parseReturnYards(playText) {{
                    if (!playText) return 0;
                    
                    // Look for patterns like "returns for X yds" or "returns for no gain"
                    // Examples:
                    // "returns for 56 yds" -> 56
                    // "returns for no gain" -> 0
                    // "return for 20 yds" -> 20
                    const returnMatch = playText.match(/return[s]? for (?:no gain|(\d+) (?:yd|yard))/i);
                    if (returnMatch) {{
                        if (returnMatch[1]) {{
                            return parseInt(returnMatch[1], 10);
                        }} else {{
                            return 0; // "no gain"
                        }}
                    }}
                    
                    // Fallback: if we can't parse, return 0 to be safe
                    return 0;
                }}
                
                // Kick return: 35+ yards
                if ((pt.includes('kickoff') || ptxt.includes('kickoff')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    const returnYards = parseReturnYards(play.play_text);
                    return returnYards >= 35;
                }}
                
                // Punt return: 20+ yards
                if ((pt.includes('punt') || ptxt.includes('punt')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    const returnYards = parseReturnYards(play.play_text);
                    return returnYards >= 20;
                }}
                
                return false;
            }}
            
            const byWeek = {{}};
            plays.filter(p => isSpecialTeamsExplosive(p)).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                if (!byWeek[week]) {{
                    byWeek[week] = {{ ours: 0, allowed: 0 }};
                }}
                
                // For return plays, check defense field (returning team)
                // For other ST plays, check offense field
                const playType = (play.play_type || '').toLowerCase();
                const playText = (play.play_text || '').toLowerCase();
                const isReturn = (
                    (playType.includes('return') || playText.includes('return')) &&
                    (playType.includes('kickoff') || playText.includes('kickoff') ||
                     playType.includes('punt') || playText.includes('punt'))
                );
                
                const isOurs = isReturn 
                    ? (play.defense?.toLowerCase().trim() || '') === (teamName.toLowerCase().trim() || '')
                    : (play.offense?.toLowerCase().trim() || '') === (teamName.toLowerCase().trim() || '');
                
                if (isOurs) {{
                    byWeek[week].ours++;
                }} else {{
                    byWeek[week].allowed++;
                }}
            }});
            
            const ours = [];
            const allowed = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                const weekData = byWeek[week] || {{ ours: 0, allowed: 0 }};
                ours.push(weekData.ours);
                allowed.push(weekData.allowed);
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                ours: ours,
                allowed: allowed
            }};
        }}
        
        function calculatePenaltyTrends(plays, teamName) {{
            const byWeek = {{}};
            plays.filter(p => p.penalty_type != null && (p.offense?.toLowerCase() === teamName.toLowerCase() || p.defense?.toLowerCase() === teamName.toLowerCase())).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                if (!byWeek[week]) {{
                    byWeek[week] = 0;
                }}
                byWeek[week]++;
            }});
            
            const values = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                values.push(byWeek[week] || 0);
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                values: values
            }};
        }}
        
        function extractPenaltyYards(playText, penaltyType) {{
            // Extract penalty yards from play text
            // First try to find explicit yardage in text
            const textLower = playText.toLowerCase();
            
            // Pattern 1: (X yards) or (X yard) in parentheses
            let matches = textLower.match(/\\((\d+)\\s*yard/);
            if (matches) {{
                return parseInt(matches[1]);
            }}
            
            // Pattern 2: X yards from (distance pattern like "15 yards from")
            matches = textLower.match(/(\d+)\\s*yards?\\s+from/);
            if (matches) {{
                return parseInt(matches[1]);
            }}
            
            // Pattern 3: Look near 'penalty' keyword
            const penaltyIdx = textLower.indexOf('penalty');
            if (penaltyIdx >= 0) {{
                const afterText = textLower.substring(penaltyIdx, penaltyIdx + 50);
                matches = afterText.match(/(\d+)\\s*yard/);
                if (matches) {{
                    return parseInt(matches[1]);
                }}
            }}
            
            // If no explicit yardage found, use standard penalty yardages based on type
            const penaltyTypeLower = (penaltyType || '').toLowerCase();
            if (penaltyTypeLower.includes('personal foul') || 
                penaltyTypeLower.includes('unsportsmanlike') ||
                penaltyTypeLower.includes('roughing')) {{
                return 15;
            }} else if (penaltyTypeLower.includes('pass interference')) {{
                return 15; // Can vary, but default to 15
            }} else if (penaltyTypeLower.includes('holding') || 
                       penaltyTypeLower.includes('illegal block')) {{
                return 10;
            }} else if (penaltyTypeLower.includes('false start') ||
                       penaltyTypeLower.includes('offside') ||
                       penaltyTypeLower.includes('delay of game')) {{
                return 5;
            }} else if (penaltyTypeLower.includes('illegal formation') ||
                       penaltyTypeLower.includes('illegal shift')) {{
                return 5;
            }}
            
            // Default: try to use yards_gained if reasonable (1-20 yards)
            // Otherwise return 0
            return 0;
        }}
        
        function calculateNetPenaltyYardsByWeek(plays, teamName) {{
            // Calculate net penalty yards per week (team's penalty yards - opponent's penalty yards)
            // Positive values mean opponent had more penalty yards (good for team)
            const teamYardsByWeek = {{}};
            const opponentYardsByWeek = {{}};
            
            // Team name variations for matching in play text
            const teamNameLower = teamName.toLowerCase();
            const teamNameShort = teamNameLower.substring(0, 4); // First 4 chars (e.g., "wash", "wisc")
            
            plays.forEach(play => {{
                if (play.penalty_type == null) return;
                
                // Only count accepted penalties
                if (play.penalty_decision !== 'accepted') return;
                
                const gameId = play.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                const playText = (play.play_text || '').toLowerCase();
                
                // Extract penalty yards from text (not from yards_gained which includes return yards)
                const yards = extractPenaltyYards(play.play_text || '', play.penalty_type);
                
                // Determine which team committed the penalty by checking play text
                // Look for patterns like team name in penalty text, "PENALTY [TEAM]", etc.
                let teamCommittedPenalty = false;
                
                // Check for team name in penalty context - look for patterns:
                // "PENALTY [TEAM]", "[TEAM] Penalty", etc.
                const penaltyPatterns = [
                    'penalty ' + teamNameShort,
                    'penalty ' + teamNameLower,
                    teamNameLower + ' penalty',
                    teamNameShort + ' penalty'
                ];
                
                for (const pattern of penaltyPatterns) {{
                    if (playText.includes(pattern)) {{
                        teamCommittedPenalty = true;
                        break;
                    }}
                }}
                
                if (teamCommittedPenalty) {{
                    // Team committed penalty
                    if (!teamYardsByWeek[week]) teamYardsByWeek[week] = 0;
                    teamYardsByWeek[week] += yards;
                }} else {{
                    // Opponent committed penalty (any penalty that's not explicitly team's)
                    // Only count if there's a penalty mentioned (to avoid double counting)
                    if (playText.includes('penalty')) {{
                        if (!opponentYardsByWeek[week]) opponentYardsByWeek[week] = 0;
                        opponentYardsByWeek[week] += yards;
                    }}
                }}
            }});
            
            // Map to weeks and fill in BYE weeks with 0
            const values = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                const teamYards = teamYardsByWeek[week] || 0;
                const oppYards = opponentYardsByWeek[week] || 0;
                values.push(oppYards - teamYards); // Positive = opponent had more (good), negative = team had more (bad)
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                values: values
            }};
        }}
        
        function calculate4thDownTrends(plays, teamName) {{
            const byWeek = {{}};
            plays.filter(p => p.down === 4 && p.offense?.toLowerCase() === teamName.toLowerCase() && !p.play_type?.toLowerCase().includes('punt') && !p.play_type?.toLowerCase().includes('field goal') && !p.play_type?.toLowerCase().includes('timeout')).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                const week = getWeekForGameId(gameId);
                if (!week) return;
                
                if (!byWeek[week]) {{
                    byWeek[week] = {{ attempts: 0, conversions: 0 }};
                }}
                byWeek[week].attempts++;
                const playText = play.play_text?.toLowerCase() || '';
                if (playText.includes('1st down') || playText.includes('first down') || playText.includes('touchdown') || (play.yards_gained >= play.distance)) {{
                    byWeek[week].conversions++;
                }}
            }});
            
            const attempts = [];
            const conversions = [];
            const rates = [];
            for (let week = 1; week <= masterWeekMapping.maxWeek; week++) {{
                const weekData = byWeek[week] || {{ attempts: 0, conversions: 0 }};
                attempts.push(weekData.attempts);
                conversions.push(weekData.conversions);
                const rate = weekData.attempts > 0 ? (weekData.conversions / weekData.attempts * 100) : 0;
                rates.push(rate);
            }}
            
            return {{
                weeks: masterWeekMapping.weekLabels,
                attempts: attempts,
                conversions: conversions,
                rates: rates
            }};
        }}
        
        // Initialize filters (no longer needed - removed filter dropdowns)
        function initializeFilters() {{
            // Filters are now simple dropdowns that don't need population
        }}
        
        // Helper function to safely update or initialize DataTable
        function safeUpdateDataTable(selector, tableData, config) {{
            try {{
                const $table = $(selector);
                if (!$table.length) return;
                
                if ($.fn.DataTable.isDataTable(selector)) {{
                    // Table already exists - update data
                    const table = $table.DataTable();
                    table.clear();
                    table.rows.add(tableData);
                    table.draw();
                }} else {{
                    // Table doesn't exist - initialize it
                    $table.DataTable(config);
                }}
            }} catch (e) {{
                console.warn('Error updating DataTable for', selector, e);
                // Fallback: destroy and recreate
                try {{
                    if ($.fn.DataTable.isDataTable(selector)) {{
                        $(selector).DataTable().destroy();
                    }}
                    $(selector).DataTable(config);
                }} catch (e2) {{
                    console.error('Failed to recreate DataTable for', selector, e2);
                }}
            }}
        }}
        
        // Filter functions
        function getFilters() {{
            return {{
                conference_only: document.getElementById('conferenceFilter').value === 'conference',
                non_conference_only: document.getElementById('conferenceFilter').value === 'non-conference',
                power4_only: document.getElementById('conferenceFilter').value === 'power4',
                last_3_games: document.getElementById('timePeriodFilter').value === 'last3'
            }};
        }}
        
        function filterPlays(plays, filters) {{
            let filtered = plays;
            
            // Filter by conference/non-conference/power4
            if (filters.conference_only) {{
                filtered = filtered.filter(p => p.is_conference === true);
            }} else if (filters.non_conference_only) {{
                filtered = filtered.filter(p => p.is_conference === false);
            }} else if (filters.power4_only) {{
                filtered = filtered.filter(p => p.is_power4_opponent === true);
            }}
            
            // Filter by last 3 games
            if (filters.last_3_games) {{
                const games = [...new Set(filtered.map(p => p.game_id))];
                const gameWeeks = games.map(gid => ({{
                    id: gid,
                    week: filtered.find(p => p.game_id === gid)?.game_week || 0
                }})).sort((a, b) => a.week - b.week);
                const last3 = gameWeeks.slice(-3).map(g => g.id);
                filtered = filtered.filter(p => last3.includes(p.game_id));
            }}
            
            return filtered;
        }}
        
        // Analysis functions (simplified versions that run in browser)
        // Note: For full analysis, we'd need to run the Python scripts and embed results
        // For now, we'll do basic filtering and display
        
        function populateMiddleEight() {{
            const team1 = allData[team1Key].middle8;
            const team2 = allData[team2Key].middle8;
            
            // Summary cards
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section {team1_key}">
                        <h3>{team_name1}</h3>
                        <div class="summary-cards">
                            <div class="summary-card">
                                <h3>Points Scored</h3>
                                <div class="value">${{team1.total_points_scored}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Points Allowed</h3>
                                <div class="value">${{team1.total_points_allowed}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Net Points</h3>
                                <div class="value">${{team1.total_net_points}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Avg Net/Game</h3>
                                <div class="value">${{team1.avg_net_per_game.toFixed(1)}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Last 3 Net</h3>
                                <div class="value">${{team1.last_3_games?.net_points || 0}}</div>
                            </div>
                        </div>
                    </div>
                    <div class="team-section {team2_key}">
                        <h3>{team_name2}</h3>
                        <div class="summary-cards">
                            <div class="summary-card">
                                <h3>Points Scored</h3>
                                <div class="value">${{team2.total_points_scored}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Points Allowed</h3>
                                <div class="value">${{team2.total_points_allowed}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Net Points</h3>
                                <div class="value">${{team2.total_net_points}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Avg Net/Game</h3>
                                <div class="value">${{team2.avg_net_per_game.toFixed(1)}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Last 3 Net</h3>
                                <div class="value">${{team2.last_3_games?.net_points || 0}}</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('middleEightSummary').innerHTML = summaryHtml;
            
            // Chart
            const ctx = document.getElementById('middleEightChart').getContext('2d');
            if (charts.middleEight) charts.middleEight.destroy();
            charts.middleEight = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Points Scored', 'Points Allowed', 'Net Points'],
                    datasets: [
                        {{
                            label: team1Name,
                            data: [team1.total_points_scored, team1.total_points_allowed, team1.total_net_points],
                            backgroundColor: 'rgba(139, 0, 0, 0.6)'
                        }},
                        {{
                            label: team2Name,
                            data: [team2.total_points_scored, team2.total_points_allowed, team2.total_net_points],
                            backgroundColor: 'rgba(220, 20, 60, 0.6)'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false
                }}
            }});
            
            // Trend chart - net points by week (use filtered plays if available)
            const team1PlaysForTrend = typeof allData[team1Key].middle8._filtered_plays !== 'undefined' ? 
                allData[team1Key].middle8._filtered_plays : team1Plays;
            const team2PlaysForTrend = typeof allData[team2Key].middle8._filtered_plays !== 'undefined' ? 
                allData[team2Key].middle8._filtered_plays : team2Plays;
            const team1Trends = calculateMiddle8Trends(team1PlaysForTrend, team1Name);
            const team2Trends = calculateMiddle8Trends(team2PlaysForTrend, team2Name);
            
            // Trend functions already return data for all weeks (1 to maxWeek), including BYE weeks with 0
            const allWeeks = team1Trends.weeks;
            const team1NetPointsAllWeeks = team1Trends.net;
            const team2NetPointsAllWeeks = team2Trends.net;
            
            const ctxTrend = document.getElementById('middleEightTrendChart').getContext('2d');
            if (charts.middleEightTrend) charts.middleEightTrend.destroy();
            charts.middleEightTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ label: team1Name + ' Net Points', data: team1NetPointsAllWeeks, borderColor: 'rgba(139, 0, 0, 1)', backgroundColor: 'rgba(139, 0, 0, 0.1)', fill: true }},
                        {{ label: team2Name + ' Net Points', data: team2NetPointsAllWeeks, borderColor: 'rgba(220, 20, 60, 1)', backgroundColor: 'rgba(220, 20, 60, 0.1)', fill: true }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    scales: {{ 
                        y: {{ 
                            beginAtZero: false,
                            ticks: {{
                                callback: function(value) {{
                                    return value;
                                }}
                            }}
                        }} 
                    }}, 
                    plugins: {{ 
                        title: {{ display: true, text: 'Middle 8 Net Points by Week' }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed.y;
                                    const sign = value >= 0 ? '+' : '';
                                    const week = context.dataIndex + 1;
                                    const teamName = context.dataset.label.includes(team1Name) ? team1Name : team2Name;
                                    const opponent = teamName === team1Name ? 
                                        (masterWeekMapping.team1WeekToOpponent[week] || 'BYE') : 
                                        (masterWeekMapping.team2WeekToOpponent[week] || 'BYE');
                                    return context.dataset.label + ': ' + sign + value + (opponent === 'BYE' ? ' (BYE)' : ' vs ' + opponent);
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Tables - separate for each team (sort chronologically)
            const washSorted = sortDrivesChronologically(team1.scoring_drives);
            const washTableData = washSorted.map(d => [
                d.game_week || '',
                d.opponent || '',
                d.scoring_team || (d.is_offense ? team1Name : (d.opponent || '')),
                d.drive_number || '',
                d.period || '',
                formatClock(d.clock || ''),
                d.play_type || '',
                d.points || 0,
                d.play_text || '',
                d.scoring_team || (d.is_offense ? team1Name : (d.opponent || ''))  // Store scoring team for row class
            ]);
            const wiscSorted = sortDrivesChronologically(team2.scoring_drives);
            const wiscTableData = wiscSorted.map(d => [
                d.game_week || '',
                d.opponent || '',
                d.scoring_team || (d.is_offense ? team2Name : (d.opponent || '')),
                d.drive_number || '',
                d.period || '',
                formatClock(d.clock || ''),
                d.play_type || '',
                d.points || 0,
                d.play_text || '',
                d.scoring_team || (d.is_offense ? team2Name : (d.opponent || ''))  // Store scoring team for row class
            ]);
            
            const washMiddle8Config = {{
                data: washTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }},
                    {{ title: 'Opponent' }},
                    {{ title: 'Scoring Team' }},
                    {{ title: 'Drive' }},
                    {{ title: 'Period' }},
                    {{ title: 'Clock' }},
                    {{ title: 'Result' }},
                    {{ title: 'Points' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for scoring team check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const scoringTeam = data[9]; // Last column (hidden, index 9)
                    if (scoringTeam && scoringTeam.toLowerCase() !== team1Name.toLowerCase()) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#middleEightTableWash', washTableData, washMiddle8Config);
            
            const wiscMiddle8Config = {{
                data: wiscTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }},
                    {{ title: 'Opponent' }},
                    {{ title: 'Scoring Team' }},
                    {{ title: 'Drive' }},
                    {{ title: 'Period' }},
                    {{ title: 'Clock' }},
                    {{ title: 'Result' }},
                    {{ title: 'Points' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for scoring team check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const scoringTeam = data[9]; // Last column (hidden, index 9)
                    if (scoringTeam && scoringTeam.toLowerCase() !== team2Name.toLowerCase()) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#middleEightTableWisc', wiscTableData, wiscMiddle8Config);
        }}
        
        function populateExplosivePlays() {{
            const team1 = allData[team1Key].explosive;
            const team2 = allData[team2Key].explosive;
            
            // If total_runs/total_passes don't exist (from Python data), calculate them from plays
            if (typeof team1.total_runs === 'undefined' && team1.plays) {{
                team1.total_runs = team1.plays.filter(p => {{
                    const pt = (p.play_type || '').toLowerCase();
                    return pt.includes('rush') || pt.includes('run') || pt === 'sack';
                }}).length;
                team1.total_passes = team1.plays.filter(p => {{
                    const pt = (p.play_type || '').toLowerCase();
                    return pt.includes('pass') || pt.includes('reception') || pt.includes('incompletion') || pt.includes('interception');
                }}).length;
            }}
            if (typeof team2.total_runs === 'undefined' && team2.plays) {{
                team2.total_runs = team2.plays.filter(p => {{
                    const pt = (p.play_type || '').toLowerCase();
                    return pt.includes('rush') || pt.includes('run') || pt === 'sack';
                }}).length;
                team2.total_passes = team2.plays.filter(p => {{
                    const pt = (p.play_type || '').toLowerCase();
                    return pt.includes('pass') || pt.includes('reception') || pt.includes('incompletion') || pt.includes('interception');
                }}).length;
            }}
            
            // Calculate allowed explosive plays stats
            const team1PlaysForAllowed = typeof allData[team1Key].explosive._filtered_plays !== 'undefined' ? 
                allData[team1Key].explosive._filtered_plays : team1Plays;
            const team2PlaysForAllowed = typeof allData[team2Key].explosive._filtered_plays !== 'undefined' ? 
                allData[team2Key].explosive._filtered_plays : team2Plays;
            
            // Calculate allowed explosive plays (by opponent, excluding special teams)
            const washAllowedPlays = team1PlaysForAllowed.filter(p => 
                p.explosive_play === true && 
                p.offense?.toLowerCase() !== team1Name.toLowerCase() &&
                p.play_classification !== 'special_teams'
            );
            const wiscAllowedPlays = team2PlaysForAllowed.filter(p => 
                p.explosive_play === true && 
                p.offense?.toLowerCase() !== team2Name.toLowerCase() &&
                p.play_classification !== 'special_teams'
            );
            
            // Calculate allowed stats
            const washAllowedTotal = washAllowedPlays.length;
            const washAllowedGames = new Set(washAllowedPlays.map(p => p.game_id)).size;
            const washAllowedPerGame = washAllowedGames > 0 ? washAllowedTotal / washAllowedGames : 0;
            
            // Calculate allowed runs and passes
            const washAllowedRuns = washAllowedPlays.filter(p => {{
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('rush') || pt.includes('run') || pt === 'sack';
            }}).length;
            const washAllowedPasses = washAllowedPlays.filter(p => {{
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('pass') || pt.includes('reception') || pt.includes('incompletion') || pt.includes('interception');
            }}).length;
            
            // Last 3 games allowed
            const washGames = [...new Set(washAllowedPlays.map(p => p.game_id))].map(gid => ({{
                id: gid,
                week: washAllowedPlays.find(p => p.game_id === gid)?.game_week || 0
            }})).sort((a, b) => a.week - b.week);
            const washLast3GameIds = washGames.slice(-3).map(g => g.id);
            const washAllowedLast3 = washAllowedPlays.filter(p => washLast3GameIds.includes(p.game_id)).length;
            const washAllowedLast3Runs = washAllowedPlays.filter(p => {{
                if (!washLast3GameIds.includes(p.game_id)) return false;
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('rush') || pt.includes('run') || pt === 'sack';
            }}).length;
            const washAllowedLast3Passes = washAllowedPlays.filter(p => {{
                if (!washLast3GameIds.includes(p.game_id)) return false;
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('pass') || pt.includes('reception') || pt.includes('incompletion') || pt.includes('interception');
            }}).length;
            
            const wiscAllowedTotal = wiscAllowedPlays.length;
            const wiscAllowedGames = new Set(wiscAllowedPlays.map(p => p.game_id)).size;
            const wiscAllowedPerGame = wiscAllowedGames > 0 ? wiscAllowedTotal / wiscAllowedGames : 0;
            
            // Calculate allowed runs and passes
            const wiscAllowedRuns = wiscAllowedPlays.filter(p => {{
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('rush') || pt.includes('run') || pt === 'sack';
            }}).length;
            const wiscAllowedPasses = wiscAllowedPlays.filter(p => {{
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('pass') || pt.includes('reception') || pt.includes('incompletion') || pt.includes('interception');
            }}).length;
            
            const wiscGames = [...new Set(wiscAllowedPlays.map(p => p.game_id))].map(gid => ({{
                id: gid,
                week: wiscAllowedPlays.find(p => p.game_id === gid)?.game_week || 0
            }})).sort((a, b) => a.week - b.week);
            const wiscLast3GameIds = wiscGames.slice(-3).map(g => g.id);
            const wiscAllowedLast3 = wiscAllowedPlays.filter(p => wiscLast3GameIds.includes(p.game_id)).length;
            const wiscAllowedLast3Runs = wiscAllowedPlays.filter(p => {{
                if (!wiscLast3GameIds.includes(p.game_id)) return false;
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('rush') || pt.includes('run') || pt === 'sack';
            }}).length;
            const wiscAllowedLast3Passes = wiscAllowedPlays.filter(p => {{
                if (!wiscLast3GameIds.includes(p.game_id)) return false;
                const pt = (p.play_type || '').toLowerCase();
                return pt.includes('pass') || pt.includes('reception') || pt.includes('incompletion') || pt.includes('interception');
            }}).length;
            
            // Summary
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section {team1_key}">
                        <h3>{team_name1}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{team1.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{team1.avg_per_game.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Runs</h3><div class="value">${{team1.total_runs || 0}}</div></div>
                            <div class="summary-card"><h3>Passes</h3><div class="value">${{team1.total_passes || 0}}</div></div>
                            <div class="summary-card"><h3>Allowed Total</h3><div class="value">${{washAllowedTotal}}</div></div>
                            <div class="summary-card"><h3>Allowed Per Game</h3><div class="value">${{washAllowedPerGame.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Allowed Runs</h3><div class="value">${{washAllowedRuns}}</div></div>
                            <div class="summary-card"><h3>Allowed Passes</h3><div class="value">${{washAllowedPasses}}</div></div>
                            <div class="summary-card"><h3>Total Last 3</h3><div class="value">${{team1.last_3_games.total}}</div></div>
                            <div class="summary-card"><h3>Allowed Last 3</h3><div class="value">${{washAllowedLast3}}</div></div>
                        </div>
                    </div>
                    <div class="team-section {team2_key}">
                        <h3>{team_name2}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{team2.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{team2.avg_per_game.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Runs</h3><div class="value">${{team2.total_runs || 0}}</div></div>
                            <div class="summary-card"><h3>Passes</h3><div class="value">${{team2.total_passes || 0}}</div></div>
                            <div class="summary-card"><h3>Allowed Total</h3><div class="value">${{wiscAllowedTotal}}</div></div>
                            <div class="summary-card"><h3>Allowed Per Game</h3><div class="value">${{wiscAllowedPerGame.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Allowed Runs</h3><div class="value">${{wiscAllowedRuns}}</div></div>
                            <div class="summary-card"><h3>Allowed Passes</h3><div class="value">${{wiscAllowedPasses}}</div></div>
                            <div class="summary-card"><h3>Total Last 3</h3><div class="value">${{team2.last_3_games.total}}</div></div>
                            <div class="summary-card"><h3>Allowed Last 3</h3><div class="value">${{wiscAllowedLast3}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('explosivePlaysSummary').innerHTML = summaryHtml;
            
            // Chart
            const ctx = document.getElementById('explosivePlaysChart').getContext('2d');
            if (charts.explosive) charts.explosive.destroy();
            charts.explosive = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Season Total', 'Per Game', 'Last 3 Games'],
                    datasets: [
                        {{
                            label: team1Name,
                            data: [team1.total_explosive_plays, team1.avg_per_game, team1.last_3_games.total],
                            backgroundColor: 'rgba(139, 0, 0, 0.6)'
                        }},
                        {{
                            label: team2Name,
                            data: [team2.total_explosive_plays, team2.avg_per_game, team2.last_3_games.total],
                            backgroundColor: 'rgba(220, 20, 60, 0.6)'
                        }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Trend charts - split into two stacked bar charts (one per team)
            const team1PlaysForTrend = typeof allData[team1Key].explosive._filtered_plays !== 'undefined' ? 
                allData[team1Key].explosive._filtered_plays : team1Plays;
            const team2PlaysForTrend = typeof allData[team2Key].explosive._filtered_plays !== 'undefined' ? 
                allData[team2Key].explosive._filtered_plays : team2Plays;
            const team1Trends = calculateExplosiveTrends(team1PlaysForTrend, team1Name);
            const team2Trends = calculateExplosiveTrends(team2PlaysForTrend, team2Name);
            
            // Team 1 line chart
            const ctxTrendWash = document.getElementById('explosivePlaysTrendChartWash').getContext('2d');
            if (charts.explosiveTrendWash) charts.explosiveTrendWash.destroy();
            charts.explosiveTrendWash = new Chart(ctxTrendWash, {{
                type: 'line',
                data: {{
                    labels: team1Trends.weeks,
                    datasets: [
                        {{
                            label: team1Name,
                            data: team1Trends.ours,
                            borderColor: 'rgba(139, 0, 0, 1)',
                            backgroundColor: 'rgba(139, 0, 0, 0.1)',
                            fill: true,
                            tension: 0.1
                        }},
                        {{
                            label: 'Allowed',
                            data: team1Trends.allowed,
                            borderColor: 'rgba(128, 128, 128, 1)',
                            backgroundColor: 'rgba(128, 128, 128, 0.1)',
                            fill: true,
                            tension: 0.1
                        }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: {{ 
                        y: {{ 
                            beginAtZero: true
                        }} 
                    }}, 
                    plugins: {{ 
                        title: {{ display: true, text: '${{team1Name}} - Explosive Plays by Week' }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    const week = context.dataIndex + 1;
                                    const opponent = masterWeekMapping.team1WeekToOpponent[week] || 'BYE';
                                    return label + ': ' + value + (opponent === 'BYE' ? ' (BYE)' : ' vs ' + opponent);
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Team 2 line chart
            const ctxTrendWisc = document.getElementById('explosivePlaysTrendChartWisc').getContext('2d');
            if (charts.explosiveTrendWisc) charts.explosiveTrendWisc.destroy();
            charts.explosiveTrendWisc = new Chart(ctxTrendWisc, {{
                type: 'line',
                data: {{
                    labels: team2Trends.weeks,
                    datasets: [
                        {{
                            label: team2Name,
                            data: team2Trends.ours,
                            borderColor: 'rgba(220, 20, 60, 1)',
                            backgroundColor: 'rgba(220, 20, 60, 0.1)',
                            fill: true,
                            tension: 0.1
                        }},
                        {{
                            label: 'Allowed',
                            data: team2Trends.allowed,
                            borderColor: 'rgba(128, 128, 128, 1)',
                            backgroundColor: 'rgba(128, 128, 128, 0.1)',
                            fill: true,
                            tension: 0.1
                        }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: {{ 
                        y: {{ 
                            beginAtZero: true
                        }} 
                    }}, 
                    plugins: {{ 
                        title: {{ display: true, text: '${{team2Name}} - Explosive Plays by Week' }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    const week = context.dataIndex + 1;
                                    const opponent = masterWeekMapping.team2WeekToOpponent[week] || 'BYE';
                                    return label + ': ' + value + (opponent === 'BYE' ? ' (BYE)' : ' vs ' + opponent);
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Run vs Pass Bar Charts - side by side (with Team Name and Allowed)
            const ctxRunPassWash = document.getElementById('explosiveRunPassChartWash').getContext('2d');
            if (charts.explosiveRunPassWash) charts.explosiveRunPassWash.destroy();
            charts.explosiveRunPassWash = new Chart(ctxRunPassWash, {{
                type: 'bar',
                data: {{
                    labels: ['Runs', 'Passes'],
                    datasets: [
                        {{
                            label: team1Name,
                            data: [team1.total_runs || 0, team1.total_passes || 0],
                            backgroundColor: ['rgba(139, 0, 0, 0.6)', 'rgba(139, 0, 0, 0.4)']
                        }},
                        {{
                            label: 'Allowed',
                            data: [washAllowedRuns, washAllowedPasses],
                            backgroundColor: ['rgba(128, 128, 128, 0.6)', 'rgba(128, 128, 128, 0.4)']
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: '${{team1Name}} - Run vs Pass Explosives', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }}
                    }},
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
            
            const ctxRunPassWisc = document.getElementById('explosiveRunPassChartWisc').getContext('2d');
            if (charts.explosiveRunPassWisc) charts.explosiveRunPassWisc.destroy();
            charts.explosiveRunPassWisc = new Chart(ctxRunPassWisc, {{
                type: 'bar',
                data: {{
                    labels: ['Runs', 'Passes'],
                    datasets: [
                        {{
                            label: team2Name,
                            data: [team2.total_runs || 0, team2.total_passes || 0],
                            backgroundColor: ['rgba(220, 20, 60, 0.6)', 'rgba(220, 20, 60, 0.4)']
                        }},
                        {{
                            label: 'Allowed',
                            data: [wiscAllowedRuns, wiscAllowedPasses],
                            backgroundColor: ['rgba(128, 128, 128, 0.6)', 'rgba(128, 128, 128, 0.4)']
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: '${{team2Name}} - Run vs Pass Explosives', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }}
                    }},
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
            
            // Tables - separate for each team (sort chronologically)
            const washSorted = sortPlaysChronologically(team1.plays);
            const washTableData = washSorted.map(p => [
                p.game_week || '',
                p.opponent || '',
                p.period || '',
                formatClock(p.clock || ''),
                p.down || '',
                p.distance || '',
                p.play_type || '',
                p.yards_gained || 0,
                p.ppa ? p.ppa.toFixed(2) : '',
                p.play_text || '',
                p.offense || ''  // Store offense for row class
            ]);
            const wiscSorted = sortPlaysChronologically(team2.plays);
            const wiscTableData = wiscSorted.map(p => [
                p.game_week || '',
                p.opponent || '',
                p.period || '',
                formatClock(p.clock || ''),
                p.down || '',
                p.distance || '',
                p.play_type || '',
                p.yards_gained || 0,
                p.ppa ? p.ppa.toFixed(2) : '',
                p.play_text || '',
                p.offense || ''  // Store offense for row class
            ]);
            
            const washExplosiveConfig = {{
                data: washTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }},
                    {{ title: 'Clock' }}, {{ title: 'Down' }}, {{ title: 'Distance' }},
                    {{ title: 'Play Type' }}, {{ title: 'Yards' }}, {{ title: 'PPA' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for offense check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const offense = data[10]; // Last column (hidden)
                    if (offense && offense.toLowerCase() !== team1Name.toLowerCase()) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#explosivePlaysTableWash', washTableData, washExplosiveConfig);
            
            const wiscExplosiveConfig = {{
                data: wiscTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }},
                    {{ title: 'Clock' }}, {{ title: 'Down' }}, {{ title: 'Distance' }},
                    {{ title: 'Play Type' }}, {{ title: 'Yards' }}, {{ title: 'PPA' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for offense check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const offense = data[10]; // Last column (hidden)
                    if (offense && offense.toLowerCase() !== team2Name.toLowerCase()) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#explosivePlaysTableWisc', wiscTableData, wiscExplosiveConfig);
        }}
        
        function populatePenalties() {{
            const team1 = allData[team1Key].penalties;
            const team2 = allData[team2Key].penalties;
            
            // Calculate yards per game
            const washYardsPerGame = team1.total_games > 0 ? (team1.total_penalty_yards || 0) / team1.total_games : 0;
            const wiscYardsPerGame = team2.total_games > 0 ? (team2.total_penalty_yards || 0) / team2.total_games : 0;
            
            // Calculate last 3 yards per game
            const washLast3Games = team1.last_3_games?.games?.length || 0;
            const washLast3YardsPerGame = washLast3Games > 0 ? (team1.last_3_games?.yards || 0) / washLast3Games : 0;
            const wiscLast3Games = team2.last_3_games?.games?.length || 0;
            const wiscLast3YardsPerGame = wiscLast3Games > 0 ? (team2.last_3_games?.yards || 0) / wiscLast3Games : 0;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section {team1_key}">
                        <h3>{team_name1}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{team1.total_penalties}}</div></div>
                            <div class="summary-card"><h3>Accepted</h3><div class="value">${{team1.accepted}}</div></div>
                            <div class="summary-card"><h3>Penalty Yards/G</h3><div class="value">${{washYardsPerGame.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{team1.avg_per_game.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Last 3 Yards/G</h3><div class="value">${{washLast3YardsPerGame.toFixed(1)}}</div></div>
                        </div>
                    </div>
                    <div class="team-section {team2_key}">
                        <h3>{team_name2}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{team2.total_penalties}}</div></div>
                            <div class="summary-card"><h3>Accepted</h3><div class="value">${{team2.accepted}}</div></div>
                            <div class="summary-card"><h3>Penalty Yards/G</h3><div class="value">${{wiscYardsPerGame.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{team2.avg_per_game.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Last 3 Yards/G</h3><div class="value">${{wiscLast3YardsPerGame.toFixed(1)}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('penaltySummary').innerHTML = summaryHtml;
            
            const ctx = document.getElementById('penaltyChart').getContext('2d');
            if (charts.penalties) charts.penalties.destroy();
            charts.penalties = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Total', 'Accepted', 'Penalty Yards/G'],
                    datasets: [
                        {{ label: team1Name, data: [team1.total_penalties, team1.accepted, washYardsPerGame], backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: [team2.total_penalties, team2.accepted, wiscYardsPerGame], backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Trend chart - net penalty yards per week
            const team1PlaysForTrend = typeof allData[team1Key].penalties._filtered_plays !== 'undefined' ? 
                allData[team1Key].penalties._filtered_plays : team1Plays;
            const team2PlaysForTrend = typeof allData[team2Key].penalties._filtered_plays !== 'undefined' ? 
                allData[team2Key].penalties._filtered_plays : team2Plays;
            const team1NetYards = calculateNetPenaltyYardsByWeek(team1PlaysForTrend, team1Name);
            const team2NetYards = calculateNetPenaltyYardsByWeek(team2PlaysForTrend, team2Name);
            
            // Trend functions already return data for all weeks (1 to maxWeek), including BYE weeks with 0
            const allWeeks = team1NetYards.weeks;
            const team1NetYardsAllWeeks = team1NetYards.values;
            const team2NetYardsAllWeeks = team2NetYards.values;
            
            const ctxTrend = document.getElementById('penaltyTrendChart').getContext('2d');
            if (charts.penaltyTrend) charts.penaltyTrend.destroy();
            charts.penaltyTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ label: team1Name + ' Net Yards', data: team1NetYardsAllWeeks, borderColor: 'rgba(139, 0, 0, 1)', backgroundColor: 'rgba(139, 0, 0, 0.1)', fill: true }},
                        {{ label: team2Name + ' Net Yards', data: team2NetYardsAllWeeks, borderColor: 'rgba(220, 20, 60, 1)', backgroundColor: 'rgba(220, 20, 60, 0.1)', fill: true }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    scales: {{ 
                        y: {{ 
                            beginAtZero: false,
                            ticks: {{
                                callback: function(value) {{
                                    return value;
                                }}
                            }}
                        }} 
                    }}, 
                    plugins: {{ 
                        title: {{ display: true, text: 'Net Penalty Yards per Game (Positive = Opponent had more, Negative = Team had more)' }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed.y;
                                    const sign = value >= 0 ? '+' : '';
                                    const week = context.dataIndex + 1;
                                    const teamName = context.dataset.label.includes(team1Name) ? team1Name : team2Name;
                                    const opponent = teamName === team1Name ? 
                                        (masterWeekMapping.team1WeekToOpponent[week] || 'BYE') : 
                                        (masterWeekMapping.team2WeekToOpponent[week] || 'BYE');
                                    return context.dataset.label + ': ' + sign + value + ' yards' + (opponent === 'BYE' ? ' (BYE)' : ' vs ' + opponent);
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Penalties by Quarter Chart
            const washByQuarter = {{1: 0, 2: 0, 3: 0, 4: 0}};
            const wiscByQuarter = {{1: 0, 2: 0, 3: 0, 4: 0}};
            team1.plays.forEach(p => {{
                const qtr = p.period || 0;
                if (qtr >= 1 && qtr <= 4) washByQuarter[qtr]++;
            }});
            team2.plays.forEach(p => {{
                const qtr = p.period || 0;
                if (qtr >= 1 && qtr <= 4) wiscByQuarter[qtr]++;
            }});
            
            const ctxByQuarter = document.getElementById('penaltyByQuarterChart').getContext('2d');
            if (charts.penaltyByQuarter) charts.penaltyByQuarter.destroy();
            charts.penaltyByQuarter = new Chart(ctxByQuarter, {{
                type: 'bar',
                data: {{
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [
                        {{ label: team1Name, data: [washByQuarter[1], washByQuarter[2], washByQuarter[3], washByQuarter[4]], backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: [wiscByQuarter[1], wiscByQuarter[2], wiscByQuarter[3], wiscByQuarter[4]], backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: 'Penalties by Quarter', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }}
                    }},
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
            
            // Penalty Type Breakdown
            // Note: The penalty_type in plays already uses penalty_category for holding penalties
            // (handled in analyzePenalties function), so we just need to use it directly
            const washPenaltyTypes = {{}};
            const wiscPenaltyTypes = {{}};
            team1.plays.forEach(p => {{
                const type = p.penalty_type || 'Unknown';
                washPenaltyTypes[type] = (washPenaltyTypes[type] || 0) + 1;
            }});
            team2.plays.forEach(p => {{
                const type = p.penalty_type || 'Unknown';
                wiscPenaltyTypes[type] = (wiscPenaltyTypes[type] || 0) + 1;
            }});
            
            // Get top penalty types (combine both teams)
            const allTypes = new Set([...Object.keys(washPenaltyTypes), ...Object.keys(wiscPenaltyTypes)]);
            const topTypes = Array.from(allTypes)
                .map(type => ({{
                    type: type,
                    wash: washPenaltyTypes[type] || 0,
                    wisc: wiscPenaltyTypes[type] || 0,
                    total: (washPenaltyTypes[type] || 0) + (wiscPenaltyTypes[type] || 0)
                }}))
                .sort((a, b) => b.total - a.total)
                .slice(0, 8)
                .map(t => t.type);
            
            const ctxType = document.getElementById('penaltyTypeChart').getContext('2d');
            if (charts.penaltyType) charts.penaltyType.destroy();
            charts.penaltyType = new Chart(ctxType, {{
                type: 'bar',
                data: {{
                    labels: topTypes,
                    datasets: [
                        {{ label: team1Name, data: topTypes.map(t => washPenaltyTypes[t] || 0), backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: topTypes.map(t => wiscPenaltyTypes[t] || 0), backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: 'Penalties by Type (Top 8)', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }}
                    }},
                    scales: {{ 
                        y: {{ beginAtZero: true }},
                        x: {{ ticks: {{ maxRotation: 45, minRotation: 45 }} }}
                    }}
                }}
            }});
            
            // Penalties by Down
            const washByDown = {{1: 0, 2: 0, 3: 0, 4: 0}};
            const wiscByDown = {{1: 0, 2: 0, 3: 0, 4: 0}};
            team1.plays.forEach(p => {{
                const down = p.down || 0;
                if (down >= 1 && down <= 4) washByDown[down]++;
            }});
            team2.plays.forEach(p => {{
                const down = p.down || 0;
                if (down >= 1 && down <= 4) wiscByDown[down]++;
            }});
            
            const ctxByDown = document.getElementById('penaltyByDownChart').getContext('2d');
            if (charts.penaltyByDown) charts.penaltyByDown.destroy();
            charts.penaltyByDown = new Chart(ctxByDown, {{
                type: 'bar',
                data: {{
                    labels: ['1st Down', '2nd Down', '3rd Down', '4th Down'],
                    datasets: [
                        {{ label: team1Name, data: [washByDown[1], washByDown[2], washByDown[3], washByDown[4]], backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: [wiscByDown[1], wiscByDown[2], wiscByDown[3], wiscByDown[4]], backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: 'Penalties by Down', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }}
                    }},
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
            
            // Penalties by Half
            const washByHalf = {{first: 0, second: 0}};
            const wiscByHalf = {{first: 0, second: 0}};
            team1.plays.forEach(p => {{
                const qtr = p.period || 0;
                if (qtr <= 2) washByHalf.first++;
                else if (qtr >= 3) washByHalf.second++;
            }});
            team2.plays.forEach(p => {{
                const qtr = p.period || 0;
                if (qtr <= 2) wiscByHalf.first++;
                else if (qtr >= 3) wiscByHalf.second++;
            }});
            
            const ctxByHalf = document.getElementById('penaltyByHalfChart').getContext('2d');
            if (charts.penaltyByHalf) charts.penaltyByHalf.destroy();
            charts.penaltyByHalf = new Chart(ctxByHalf, {{
                type: 'bar',
                data: {{
                    labels: ['First Half', 'Second Half'],
                    datasets: [
                        {{ label: team1Name, data: [washByHalf.first, washByHalf.second], backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: [wiscByHalf.first, wiscByHalf.second], backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: 'Penalties by Half', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }}
                    }},
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
            
            // Tables - separate for each team
            // Sort chronologically
            const washSorted = sortPlaysChronologically(team1.plays);
            const washTableData = washSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.penalty_type || '', p.penalty_decision || '', 
                p.penalty_yards || (p.penalty_decision === 'accepted' ? Math.abs(p.yards_gained || 0) : 0),
                p.play_text || '',
                p.offense || ''  // Store offense for row class
            ]);
            const wiscSorted = sortPlaysChronologically(team2.plays);
            const wiscTableData = wiscSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.penalty_type || '', p.penalty_decision || '',
                p.penalty_yards || (p.penalty_decision === 'accepted' ? Math.abs(p.yards_gained || 0) : 0),
                p.play_text || '',
                p.offense || ''  // Store offense for row class
            ]);
            
            const washPenaltyConfig = {{
                data: washTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }}, {{ title: 'Clock' }},
                    {{ title: 'Penalty Type' }}, {{ title: 'Decision' }}, {{ title: 'Yards Lost' }}, {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for offense check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const offense = data[8]; // Last column (hidden, index 8 now)
                    if (offense && offense.toLowerCase() !== team1Name.toLowerCase()) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#penaltyTableWash', washTableData, washPenaltyConfig);
            
            const wiscPenaltyConfig = {{
                data: wiscTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }}, {{ title: 'Clock' }},
                    {{ title: 'Penalty Type' }}, {{ title: 'Decision' }}, {{ title: 'Yards Lost' }}, {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for offense check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const offense = data[8]; // Last column (hidden, index 8 now)
                    if (offense && offense.toLowerCase() !== team2Name.toLowerCase()) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#penaltyTableWisc', wiscTableData, wiscPenaltyConfig);
        }}
        
        function populate4thDowns() {{
            const team1 = allData[team1Key]['4thdowns'];
            const team2 = allData[team2Key]['4thdowns'];
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section {team1_key}">
                        <h3>{team_name1}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Attempts</h3><div class="value">${{team1.total_attempts}}</div></div>
                            <div class="summary-card"><h3>Conversions</h3><div class="value">${{team1.total_conversions}}</div></div>
                            <div class="summary-card"><h3>Rate</h3><div class="value">${{team1.conversion_rate.toFixed(1)}}%</div></div>
                            <div class="summary-card"><h3>Last 3 Attempts</h3><div class="value">${{team1.last_3_games.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Conversions</h3><div class="value">${{team1.last_3_games.conversions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Rate</h3><div class="value">${{team1.last_3_games.conversion_rate.toFixed(1)}}%</div></div>
                        </div>
                    </div>
                    <div class="team-section {team2_key}">
                        <h3>{team_name2}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Attempts</h3><div class="value">${{team2.total_attempts}}</div></div>
                            <div class="summary-card"><h3>Conversions</h3><div class="value">${{team2.total_conversions}}</div></div>
                            <div class="summary-card"><h3>Rate</h3><div class="value">${{team2.conversion_rate.toFixed(1)}}%</div></div>
                            <div class="summary-card"><h3>Last 3 Attempts</h3><div class="value">${{team2.last_3_games.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Conversions</h3><div class="value">${{team2.last_3_games.conversions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Rate</h3><div class="value">${{team2.last_3_games.conversion_rate.toFixed(1)}}%</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('fourthDownSummary').innerHTML = summaryHtml;
            
            const ctx = document.getElementById('fourthDownChart').getContext('2d');
            if (charts.fourthDown) charts.fourthDown.destroy();
            charts.fourthDown = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Attempts', 'Conversions', 'Rate %'],
                    datasets: [
                        {{ label: team1Name, data: [team1.total_attempts, team1.total_conversions, team1.conversion_rate], backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: [team2.total_attempts, team2.total_conversions, team2.conversion_rate], backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Trend chart - use filtered plays if available
            const team1PlaysForTrend = typeof allData[team1Key]['4thdowns']._filtered_plays !== 'undefined' ? 
                allData[team1Key]['4thdowns']._filtered_plays : team1Plays;
            const team2PlaysForTrend = typeof allData[team2Key]['4thdowns']._filtered_plays !== 'undefined' ? 
                allData[team2Key]['4thdowns']._filtered_plays : team2Plays;
            const team1Trends = calculate4thDownTrends(team1PlaysForTrend, team1Name);
            const team2Trends = calculate4thDownTrends(team2PlaysForTrend, team2Name);
            
            // Trend functions already return data for all weeks (1 to maxWeek), including BYE weeks with 0
            const allWeeks = team1Trends.weeks;
            const team1ConversionsAllWeeks = team1Trends.conversions;
            const team2ConversionsAllWeeks = team2Trends.conversions;
            
            const ctxTrend = document.getElementById('fourthDownTrendChart').getContext('2d');
            if (charts.fourthDownTrend) charts.fourthDownTrend.destroy();
            charts.fourthDownTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ 
                            label: team1Name + ' Conversions', 
                            data: team1ConversionsAllWeeks, 
                            borderColor: 'rgba(139, 0, 0, 1)', 
                            backgroundColor: 'rgba(139, 0, 0, 0.1)', 
                            fill: true 
                        }},
                        {{ 
                            label: team2Name + ' Conversions', 
                            data: team2ConversionsAllWeeks, 
                            borderColor: 'rgba(220, 20, 60, 1)', 
                            backgroundColor: 'rgba(220, 20, 60, 0.1)', 
                            fill: true 
                        }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    scales: {{ y: {{ beginAtZero: true }} }}, 
                    plugins: {{ 
                        title: {{ display: true, text: '4th Down Conversions by Week' }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const datasetIndex = context.datasetIndex;
                                    const dataIndex = context.dataIndex;
                                    const weekLabel = allWeeks[dataIndex];
                                    const weekNum = dataIndex + 1;
                                    const conversions = context.parsed.y;
                                    
                                    // Find the original week index in the team's trends
                                    const teamTrends = datasetIndex === 0 ? team1Trends : team2Trends;
                                    const weekIndex = teamTrends.weeks.indexOf(weekLabel);
                                    
                                    const teamName = datasetIndex === 0 ? team1Name : team2Name;
                                    const opponent = datasetIndex === 0 ? 
                                        (masterWeekMapping.team1WeekToOpponent[weekNum] || 'BYE') : 
                                        (masterWeekMapping.team2WeekToOpponent[weekNum] || 'BYE');
                                    const opponentText = opponent === 'BYE' ? ' (BYE)' : ' vs ' + opponent;
                                    
                                    if (weekIndex >= 0) {{
                                        const attempts = teamTrends.attempts[weekIndex];
                                        const rate = teamTrends.rates[weekIndex];
                                        return `${{teamName}}: ${{conversions}}/${{attempts}} (${{rate.toFixed(1)}}%)${{opponentText}}`;
                                    }} else {{
                                        // Week with no attempts
                                        return `${{teamName}}: 0/0 (0.0%)${{opponentText}}`;
                                    }}
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Tables - separate for each team
            // Sort chronologically
            const washSorted = sortPlaysChronologically(team1.plays);
            const washTableData = washSorted.map(p => [
                p.game_week || '', p.opponent || '', p.yard_line || '', p.distance || '',
                p.play_type || '', p.converted ? 'Yes' : 'No', p.yards_gained || 0, p.ppa ? p.ppa.toFixed(2) : '',
                p.play_text || '',
                p.converted || false  // Hidden column for conversion status
            ]);
            const wiscSorted = sortPlaysChronologically(team2.plays);
            const wiscTableData = wiscSorted.map(p => [
                p.game_week || '', p.opponent || '', p.yard_line || '', p.distance || '',
                p.play_type || '', p.converted ? 'Yes' : 'No', p.yards_gained || 0, p.ppa ? p.ppa.toFixed(2) : '',
                p.play_text || '',
                p.converted || false  // Hidden column for conversion status
            ]);
            
            const wash4thDownConfig = {{
                data: washTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Yard Line' }}, {{ title: 'Distance' }},
                    {{ title: 'Play Type' }}, {{ title: 'Converted' }}, {{ title: 'Yards' }}, {{ title: 'PPA' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for conversion status
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const converted = data[9]; // Last column (hidden, index 9)
                    if (converted === true) {{
                        $(row).addClass('converted-success');
                    }} else {{
                        $(row).addClass('converted-failed');
                    }}
                }}
            }};
            safeUpdateDataTable('#fourthDownTableWash', washTableData, wash4thDownConfig);
            
            const wisc4thDownConfig = {{
                data: wiscTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Yard Line' }}, {{ title: 'Distance' }},
                    {{ title: 'Play Type' }}, {{ title: 'Converted' }}, {{ title: 'Yards' }}, {{ title: 'PPA' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for conversion status
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const converted = data[9]; // Last column (hidden, index 9)
                    if (converted === true) {{
                        $(row).addClass('converted-success');
                    }} else {{
                        $(row).addClass('converted-failed');
                    }}
                }}
            }};
            safeUpdateDataTable('#fourthDownTableWisc', wiscTableData, wisc4thDownConfig);
        }}
        
        function populatePostTurnover() {{
            const team1 = allData[team1Key].turnover;
            const team2 = allData[team2Key].turnover;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section {team1_key}">
                        <h3>{team_name1}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Opponent Turnovers</h3><div class="value">${{team1.opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Scored After</h3><div class="value">${{team1.points_scored_after_opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>${{team1Name}} Turnovers</h3><div class="value">${{team1.our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Allowed After</h3><div class="value">${{team1.points_allowed_after_our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Net Points</h3><div class="value">${{team1.net_points_after_turnovers}}</div></div>
                            <div class="summary-card"><h3>Last 3 Net Points</h3><div class="value">${{team1.last_3_games?.net_points || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section {team2_key}">
                        <h3>{team_name2}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Opponent Turnovers</h3><div class="value">${{team2.opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Scored After</h3><div class="value">${{team2.points_scored_after_opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>${{team2Name}} Turnovers</h3><div class="value">${{team2.our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Allowed After</h3><div class="value">${{team2.points_allowed_after_our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Net Points</h3><div class="value">${{team2.net_points_after_turnovers}}</div></div>
                            <div class="summary-card"><h3>Last 3 Net Points</h3><div class="value">${{team2.last_3_games?.net_points || 0}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('postTurnoverSummary').innerHTML = summaryHtml;
            
            const ctx = document.getElementById('postTurnoverChart').getContext('2d');
            if (charts.postTurnover) charts.postTurnover.destroy();
            charts.postTurnover = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Team TO', 'Opp TO', 'Pts Scored Off TO', 'Pts Allowed Off TO'],
                    datasets: [
                        {{ label: team1Name, data: [team1.our_turnovers, team1.opponent_turnovers, team1.points_scored_after_opponent_turnovers, -team1.points_allowed_after_our_turnovers], backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: [team2.our_turnovers, team2.opponent_turnovers, team2.points_scored_after_opponent_turnovers, -team2.points_allowed_after_our_turnovers], backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            ticks: {{
                                callback: function(value) {{
                                    return Math.abs(value);
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed.y;
                                    const label = context.label || '';
                                    if (value < 0) {{
                                        return context.dataset.label + ': -' + Math.abs(value);
                                    }}
                                    return context.dataset.label + ': ' + value;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Trend chart - net points by week - use filtered plays if available
            const team1PlaysForTrend = typeof allData[team1Key].turnover._filtered_plays !== 'undefined' ? 
                allData[team1Key].turnover._filtered_plays : team1Plays;
            const team2PlaysForTrend = typeof allData[team2Key].turnover._filtered_plays !== 'undefined' ? 
                allData[team2Key].turnover._filtered_plays : team2Plays;
            const team1NetPoints = calculateNetPointsByWeek(team1PlaysForTrend, team1Name);
            const team2NetPoints = calculateNetPointsByWeek(team2PlaysForTrend, team2Name);
            
            // Trend functions already return data for all weeks (1 to maxWeek), including BYE weeks with 0
            const allWeeks = team1NetPoints.weeks;
            const team1NetPointsAllWeeks = team1NetPoints.netPoints;
            const team2NetPointsAllWeeks = team2NetPoints.netPoints;
            
            const ctxTrend = document.getElementById('postTurnoverTrendChart').getContext('2d');
            if (charts.postTurnoverTrend) charts.postTurnoverTrend.destroy();
            charts.postTurnoverTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ label: team1Name + ' Net Points', data: team1NetPointsAllWeeks, borderColor: 'rgba(139, 0, 0, 1)', backgroundColor: 'rgba(139, 0, 0, 0.1)', fill: true }},
                        {{ label: team2Name + ' Net Points', data: team2NetPointsAllWeeks, borderColor: 'rgba(220, 20, 60, 1)', backgroundColor: 'rgba(220, 20, 60, 0.1)', fill: true }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    scales: {{ 
                        y: {{ 
                            beginAtZero: false,
                            ticks: {{
                                callback: function(value) {{
                                    return value;
                                }}
                            }}
                        }} 
                    }}, 
                    plugins: {{ 
                        title: {{ display: true, text: 'Net Points After Turnovers by Week' }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    const week = context[0].dataIndex + 1;
                                    const datasetIndex = context[0].datasetIndex;
                                    const opponent = datasetIndex === 0 ? 
                                        (masterWeekMapping.team1WeekToOpponent[week] || 'BYE') : 
                                        (masterWeekMapping.team2WeekToOpponent[week] || 'BYE');
                                    return 'Week ' + week + (opponent === 'BYE' ? ' (BYE)' : ' vs ' + opponent);
                                }},
                                label: function(context) {{
                                    const value = context.parsed.y;
                                    const sign = value >= 0 ? '+' : '';
                                    return context.dataset.label + ': ' + sign + value;
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Tables - separate for each team
            // Sort chronologically (turnover_analysis items may not have period/clock, so sort by week only)
            const washTurnoverSorted = team1.turnover_analysis.slice().sort((a, b) => (a.game_week || 0) - (b.game_week || 0));
            const washTableData = washTurnoverSorted.map(t => [
                t.game_week || '', t.opponent || '', t.turnover_type || '',
                t.is_our_turnover ? team1Name : 'Opponent', t.drive_result || '', 
                (t.points_scored || 0) + (t.points_allowed || 0), // Total points from turnover
                t.play_text || '',
                t.is_our_turnover ? false : true  // Store isOpponent for row class
            ]);
            const wiscTurnoverSorted = team2.turnover_analysis.slice().sort((a, b) => (a.game_week || 0) - (b.game_week || 0));
            const wiscTableData = wiscTurnoverSorted.map(t => [
                t.game_week || '', t.opponent || '', t.turnover_type || '',
                t.is_our_turnover ? team2Name : 'Opponent', t.drive_result || '', 
                (t.points_scored || 0) + (t.points_allowed || 0), // Total points from turnover
                t.play_text || '',
                t.is_our_turnover ? false : true  // Store isOpponent for row class
            ]);
            
            const washTurnoverConfig = {{
                data: washTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Turnover Type' }},
                    {{ title: 'Offense' }}, {{ title: 'Drive Result' }}, {{ title: 'Points' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for isOpponent check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const isOpponent = data[7]; // Last column (hidden)
                    if (isOpponent) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#postTurnoverTableWash', washTableData, washTurnoverConfig);
            
            const wiscTurnoverConfig = {{
                data: wiscTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Turnover Type' }},
                    {{ title: 'Offense' }}, {{ title: 'Drive Result' }}, {{ title: 'Points' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for isOpponent check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const isOpponent = data[7]; // Last column (hidden)
                    if (isOpponent) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#postTurnoverTableWisc', wiscTableData, wiscTurnoverConfig);
        }}
        
        function populateSpecialTeams() {{
            const team1 = allData[team1Key].specialteams;
            const team2 = allData[team2Key].specialteams;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section {team1_key}">
                        <h3>{team_name1}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Explosive</h3><div class="value">${{team1.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Explosive Allowed</h3><div class="value">${{team1.explosive_returns_allowed}}</div></div>
                            <div class="summary-card"><h3>TD's Scored</h3><div class="value">${{team1.tds_scored || 0}}</div></div>
                            <div class="summary-card"><h3>TD's Allowed</h3><div class="value">${{team1.tds_allowed || 0}}</div></div>
                            <div class="summary-card"><h3>Punt Blocks</h3><div class="value">${{team1.punt_blocks || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section {team2_key}">
                        <h3>{team_name2}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Explosive</h3><div class="value">${{team2.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Explosive Allowed</h3><div class="value">${{team2.explosive_returns_allowed}}</div></div>
                            <div class="summary-card"><h3>TD's Scored</h3><div class="value">${{team2.tds_scored || 0}}</div></div>
                            <div class="summary-card"><h3>TD's Allowed</h3><div class="value">${{team2.tds_allowed || 0}}</div></div>
                            <div class="summary-card"><h3>Punt Blocks</h3><div class="value">${{team2.punt_blocks || 0}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('specialTeamsSummary').innerHTML = summaryHtml;
            
            // Trend chart for special teams explosive plays - use filtered plays if available
            const team1PlaysForTrend = typeof allData[team1Key].specialteams._filtered_plays !== 'undefined' ? 
                allData[team1Key].specialteams._filtered_plays : team1Plays;
            const team2PlaysForTrend = typeof allData[team2Key].specialteams._filtered_plays !== 'undefined' ? 
                allData[team2Key].specialteams._filtered_plays : team2Plays;
            const team1Trends = calculateSpecialTeamsExplosiveTrends(team1PlaysForTrend, team1Name);
            const team2Trends = calculateSpecialTeamsExplosiveTrends(team2PlaysForTrend, team2Name);
            const ctxTrend = document.getElementById('specialTeamsTrendChart').getContext('2d');
            if (charts.specialTeamsTrend) charts.specialTeamsTrend.destroy();
            charts.specialTeamsTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: team1Trends.weeks,
                    datasets: [
                        {{ label: team1Name + ' Explosive ST Plays', data: team1Trends.ours, borderColor: 'rgba(139, 0, 0, 1)', backgroundColor: 'rgba(139, 0, 0, 0.1)', fill: true }},
                        {{ label: team1Name + ' Allowed', data: team1Trends.allowed.map(v => -v), borderColor: 'rgba(139, 0, 0, 0.5)', backgroundColor: 'rgba(139, 0, 0, 0.05)', fill: true }},
                        {{ label: team2Name + ' Explosive ST Plays', data: team2Trends.ours, borderColor: 'rgba(220, 20, 60, 1)', backgroundColor: 'rgba(220, 20, 60, 0.1)', fill: true }},
                        {{ label: team2Name + ' Allowed', data: team2Trends.allowed.map(v => -v), borderColor: 'rgba(220, 20, 60, 0.5)', backgroundColor: 'rgba(220, 20, 60, 0.05)', fill: true }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    scales: {{ 
                        y: {{ 
                            beginAtZero: false,
                            ticks: {{
                                callback: function(value) {{
                                    return Math.abs(value);
                                }}
                            }}
                        }} 
                    }}, 
                    plugins: {{ 
                        title: {{ display: true, text: 'Explosive Special Teams Plays by Week (Allowed shown as negative)' }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{
                                        label += ': ';
                                    }}
                                    if (context.parsed.y < 0) {{
                                        label += Math.abs(context.parsed.y);
                                    }} else {{
                                        label += context.parsed.y;
                                    }}
                                    const week = context.dataIndex + 1;
                                    const teamName = context.dataset.label.includes(team1Name) ? team1Name : team2Name;
                                    const opponent = teamName === team1Name ? 
                                        (masterWeekMapping.team1WeekToOpponent[week] || 'BYE') : 
                                        (masterWeekMapping.team2WeekToOpponent[week] || 'BYE');
                                    return label + (opponent === 'BYE' ? ' (BYE)' : ' vs ' + opponent);
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Tables - separate for each team
            // Sort chronologically
            const washSTSorted = sortPlaysChronologically(team1.plays);
            const washTableData = washSTSorted.map(p => [
                p.game_week || '', p.opponent || '', p.play_type || '',
                p.is_our ? team1Name : 'Opponent', p.yards_gained || 0,
                p.explosive ? 'Yes' : 'No',
                p.play_text || '',
                !p.is_our  // Store isOpponent for row class
            ]);
            const wiscSTSorted = sortPlaysChronologically(team2.plays);
            const wiscTableData = wiscSTSorted.map(p => [
                p.game_week || '', p.opponent || '', p.play_type || '',
                p.is_our ? team2Name : 'Opponent', p.yards_gained || 0,
                p.explosive ? 'Yes' : 'No',
                p.play_text || '',
                !p.is_our  // Store isOpponent for row class
            ]);
            
            const washSpecialTeamsConfig = {{
                data: washTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Play Type' }},
                    {{ title: 'Result' }}, {{ title: 'Yards' }}, {{ title: 'Explosive' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for isOpponent check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const isOpponent = data[7]; // Last column (hidden)
                    if (isOpponent) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#specialTeamsTableWash', washTableData, washSpecialTeamsConfig);
            
            const wiscSpecialTeamsConfig = {{
                data: wiscTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Play Type' }},
                    {{ title: 'Result' }}, {{ title: 'Yards' }}, {{ title: 'Explosive' }},
                    {{ title: 'Play Description' }},
                    {{ title: '', visible: false }}  // Hidden column for isOpponent check
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                    const isOpponent = data[7]; // Last column (hidden)
                    if (isOpponent) {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }};
            safeUpdateDataTable('#specialTeamsTableWisc', wiscTableData, wiscSpecialTeamsConfig);
        }}
        
        function populateRedZone() {{
            const team1 = allData[team1Key].redzone;
            const team2 = allData[team2Key].redzone;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section {team1_key}">
                        <h3>{team_name1}</h3>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #388e3c; margin-bottom: 10px;">Green Zone (30 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{team1.green_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{team1.green_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{team1.green_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{team1.green_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{team1.green_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{team1.green_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #d32f2f; margin-bottom: 10px;">Red Zone (20 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{team1.red_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{team1.red_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{team1.red_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{team1.red_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{team1.red_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{team1.red_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                        <div>
                            <h4 style="color: #b71c1c; margin-bottom: 10px;">Tight Red Zone (10 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{team1.tight_red_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{team1.tight_red_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{team1.tight_red_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{team1.tight_red_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{team1.tight_red_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{team1.tight_red_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                    </div>
                    <div class="team-section {team2_key}">
                        <h3>{team_name2}</h3>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #388e3c; margin-bottom: 10px;">Green Zone (30 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{team2.green_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{team2.green_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{team2.green_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{team2.green_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{team2.green_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{team2.green_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #d32f2f; margin-bottom: 10px;">Red Zone (20 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{team2.red_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{team2.red_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{team2.red_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{team2.red_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{team2.red_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{team2.red_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                        <div>
                            <h4 style="color: #b71c1c; margin-bottom: 10px;">Tight Red Zone (10 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{team2.tight_red_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{team2.tight_red_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{team2.tight_red_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{team2.tight_red_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{team2.tight_red_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{team2.tight_red_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('redZoneSummary').innerHTML = summaryHtml;
            
            // Bar chart comparing Tight Red Zone, Red Zone and Green Zone scoring rates
            const ctx = document.getElementById('redZoneChart').getContext('2d');
            if (charts.redZone) charts.redZone.destroy();
            charts.redZone = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Tight Red Zone TD %', 'Red Zone TD %', 'Green Zone TD %'],
                    datasets: [
                        {{ label: team1Name, data: [team1.tight_red_zone.td_scoring_rate, team1.red_zone.td_scoring_rate, team1.green_zone.td_scoring_rate], backgroundColor: 'rgba(139, 0, 0, 0.6)' }},
                        {{ label: team2Name, data: [team2.tight_red_zone.td_scoring_rate, team2.red_zone.td_scoring_rate, team2.green_zone.td_scoring_rate], backgroundColor: 'rgba(220, 20, 60, 0.6)' }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Tables - Tight Red Zone and Green Zone
            // Sort chronologically
            const washTightRedSorted = sortPlaysChronologically(team1.tight_red_zone.plays);
            const washTightRedTableData = washTightRedSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.down || '', p.distance || '', p.yards_to_goal || '',
                p.play_type || '', p.yards_gained || 0, p.scoring ? 'Yes' : 'No',
                p.explosive ? 'Yes' : 'No', p.ppa ? p.ppa.toFixed(3) : '', p.play_text || ''
            ]);
            
            const wiscTightRedSorted = sortPlaysChronologically(team2.tight_red_zone.plays);
            const wiscTightRedTableData = wiscTightRedSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.down || '', p.distance || '', p.yards_to_goal || '',
                p.play_type || '', p.yards_gained || 0, p.scoring ? 'Yes' : 'No',
                p.explosive ? 'Yes' : 'No', p.ppa ? p.ppa.toFixed(3) : '', p.play_text || ''
            ]);
            
            const washGreenSorted = sortPlaysChronologically(team1.green_zone.plays);
            const washGreenTableData = washGreenSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.down || '', p.distance || '', p.yards_to_goal || '',
                p.play_type || '', p.yards_gained || 0, p.scoring ? 'Yes' : 'No',
                p.explosive ? 'Yes' : 'No', p.ppa ? p.ppa.toFixed(3) : '', p.play_text || ''
            ]);
            
            const wiscGreenSorted = sortPlaysChronologically(team2.green_zone.plays);
            const wiscGreenTableData = wiscGreenSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.down || '', p.distance || '', p.yards_to_goal || '',
                p.play_type || '', p.yards_gained || 0, p.scoring ? 'Yes' : 'No',
                p.explosive ? 'Yes' : 'No', p.ppa ? p.ppa.toFixed(3) : '', p.play_text || ''
            ]);
            
            // Tight Red Zone tables
            const washTightRedZoneConfig = {{
                data: washTightRedTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }}, {{ title: 'Clock' }},
                    {{ title: 'Down' }}, {{ title: 'Dist' }}, {{ title: 'YTG' }},
                    {{ title: 'Play Type' }}, {{ title: 'Yards' }}, {{ title: 'Scoring' }},
                    {{ title: 'Explosive' }}, {{ title: 'PPA' }}, {{ title: 'Play Description' }}
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                }}
            }};
            safeUpdateDataTable('#tightRedZoneTableWash', washTightRedTableData, washTightRedZoneConfig);
            
            const wiscTightRedZoneConfig = {{
                data: wiscTightRedTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }}, {{ title: 'Clock' }},
                    {{ title: 'Down' }}, {{ title: 'Dist' }}, {{ title: 'YTG' }},
                    {{ title: 'Play Type' }}, {{ title: 'Yards' }}, {{ title: 'Scoring' }},
                    {{ title: 'Explosive' }}, {{ title: 'PPA' }}, {{ title: 'Play Description' }}
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                }}
            }};
            safeUpdateDataTable('#tightRedZoneTableWisc', wiscTightRedTableData, wiscTightRedZoneConfig);
            
            const washGreenZoneConfig = {{
                data: washGreenTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }}, {{ title: 'Clock' }},
                    {{ title: 'Down' }}, {{ title: 'Dist' }}, {{ title: 'YTG' }},
                    {{ title: 'Play Type' }}, {{ title: 'Yards' }}, {{ title: 'Scoring' }},
                    {{ title: 'Explosive' }}, {{ title: 'PPA' }}, {{ title: 'Play Description' }}
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                }}
            }};
            safeUpdateDataTable('#greenZoneTableWash', washGreenTableData, washGreenZoneConfig);
            
            const wiscGreenZoneConfig = {{
                data: wiscGreenTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Period' }}, {{ title: 'Clock' }},
                    {{ title: 'Down' }}, {{ title: 'Dist' }}, {{ title: 'YTG' }},
                    {{ title: 'Play Type' }}, {{ title: 'Yards' }}, {{ title: 'Scoring' }},
                    {{ title: 'Explosive' }}, {{ title: 'PPA' }}, {{ title: 'Play Description' }}
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                }}
            }};
            safeUpdateDataTable('#greenZoneTableWisc', wiscGreenTableData, wiscGreenZoneConfig);
        }}
        
        function filterSituationalReceiving(situationalData, filters) {{
            // Filter SIS situational receiving data based on filters
            // Returns filtered copy of the data structure
            if (!situationalData) return null;
            
            // Check if any filters are actually applied
            const hasFilters = filters.conference_only || filters.non_conference_only || 
                              filters.power4_only || filters.last_3_games;
            
            // If no filters, return original data (no need to recalculate)
            if (!hasFilters) {{
                return situationalData;
            }}
            
            // Check if data has enrichment fields (is_conference, is_power4_opponent, game_id)
            // If not, we can't filter properly, so return original data with a warning
            let hasEnrichment = false;
            for (const situation of Object.values(situationalData)) {{
                if (situation && situation.by_week) {{
                    for (const weekData of Object.values(situation.by_week)) {{
                        if (weekData.hasOwnProperty('is_conference') || weekData.hasOwnProperty('is_power4_opponent') || weekData.hasOwnProperty('game_id')) {{
                            hasEnrichment = true;
                            break;
                        }}
                    }}
                    if (hasEnrichment) break;
                }}
            }}
            
            if (!hasEnrichment) {{
                console.warn('Situational receiving data does not have enrichment fields (is_conference, is_power4_opponent, game_id). Cannot apply filters. Returning unfiltered data.');
                return situationalData;
            }}
            
            const filtered = JSON.parse(JSON.stringify(situationalData)); // Deep copy
            
            // Helper function to filter a situation (3rd_down or redzone)
            function filterSituation(situation) {{
                if (!situation || !situation.by_week) return situation;
                
                const filteredByWeek = {{}};
                let filteredTotal = {{ targets: 0, receptions: 0, yards: 0, first_downs: 0, touchdowns: 0 }};
                const filteredPlayers = {{}};
                const filteredLast3Weeks = [];
                
                // Get last 3 game IDs if needed
                let last3GameIds = [];
                if (filters.last_3_games) {{
                    // Get all unique game_ids from by_week, sorted by week
                    const allWeeks = Object.keys(situation.by_week)
                        .map(w => ({{
                            week: parseInt(w),
                            game_id: situation.by_week[w].game_id,
                            week_str: w
                        }}))
                        .filter(w => w.game_id)
                        .sort((a, b) => a.week - b.week);
                    last3GameIds = allWeeks.slice(-3).map(w => w.game_id);
                }}
                
                // Filter by_week entries
                for (const [weekStr, weekData] of Object.entries(situation.by_week)) {{
                    let include = true;
                    
                    // Filter by conference/non-conference/power4
                    // Only apply filters if enrichment fields are present
                    if (filters.conference_only) {{
                        if (weekData.hasOwnProperty('is_conference')) {{
                            include = include && weekData.is_conference === true;
                        }} else {{
                            // If enrichment field is missing, exclude to be safe
                            include = false;
                        }}
                    }} else if (filters.non_conference_only) {{
                        if (weekData.hasOwnProperty('is_conference')) {{
                            include = include && weekData.is_conference === false;
                        }} else {{
                            include = false;
                        }}
                    }} else if (filters.power4_only) {{
                        if (weekData.hasOwnProperty('is_power4_opponent')) {{
                            include = include && weekData.is_power4_opponent === true;
                        }} else {{
                            include = false;
                        }}
                    }}
                    
                    // Filter by last 3 games
                    if (filters.last_3_games) {{
                        if (weekData.game_id && last3GameIds.length > 0) {{
                            include = include && last3GameIds.includes(weekData.game_id);
                        }} else if (last3GameIds.length > 0) {{
                            // If game_id is missing but we need to filter by last 3, exclude
                            include = false;
                        }}
                    }}
                    
                    if (include) {{
                        filteredByWeek[weekStr] = weekData;
                        filteredLast3Weeks.push(parseInt(weekStr));
                        
                        // Aggregate totals
                        const stats = weekData.stats || {{}};
                        filteredTotal.targets += stats.targets || 0;
                        filteredTotal.receptions += stats.receptions || 0;
                        filteredTotal.yards += stats.yards || 0;
                        if (situation === filtered['3rd_down']) {{
                            filteredTotal.first_downs += stats.first_downs || 0;
                            // Also add touchdowns from stats (may not be in player-level data)
                            filteredTotal.touchdowns += stats.touchdowns || 0;
                        }} else {{
                            // For redzone, also add touchdowns from stats
                            filteredTotal.touchdowns += stats.touchdowns || 0;
                        }}
                        
                        // Aggregate player stats
                        for (const player of weekData.players || []) {{
                            const playerId = player.playerId;
                            if (!filteredPlayers[playerId]) {{
                                filteredPlayers[playerId] = {{
                                    playerId: playerId,
                                    player: player.player,
                                    targets: 0,
                                    receptions: 0,
                                    yards: 0,
                                    first_downs: 0,
                                    touchdowns: 0,
                                    big_ten_rank: player.big_ten_rank,
                                    is_top_25: player.is_top_25
                                }};
                            }}
                            filteredPlayers[playerId].targets += player.targets || 0;
                            filteredPlayers[playerId].receptions += player.receptions || 0;
                            filteredPlayers[playerId].yards += player.yards || 0;
                            if (situation === filtered['3rd_down']) {{
                                filteredPlayers[playerId].first_downs += player.first_downs || 0;
                            }}
                            filteredPlayers[playerId].touchdowns += player.touchdowns || 0;
                        }}
                    }}
                }}
                
                // Calculate last 3 games stats
                filteredLast3Weeks.sort((a, b) => a - b);
                const last3 = filteredLast3Weeks.slice(-3);
                const last3Targets = last3.reduce((sum, w) => sum + (filteredByWeek[w.toString()]?.stats?.targets || 0), 0);
                const last3Receptions = last3.reduce((sum, w) => sum + (filteredByWeek[w.toString()]?.stats?.receptions || 0), 0);
                const last3Yards = last3.reduce((sum, w) => sum + (filteredByWeek[w.toString()]?.stats?.yards || 0), 0);
                
                let last3Extra = {{}};
                if (situation === filtered['3rd_down']) {{
                    const last3FirstDowns = last3.reduce((sum, w) => sum + (filteredByWeek[w.toString()]?.stats?.first_downs || 0), 0);
                    const last3Touchdowns = last3.reduce((sum, w) => 
                        sum + (filteredByWeek[w.toString()]?.players || []).reduce((pSum, p) => pSum + (p.touchdowns || 0), 0), 0);
                    last3Extra = {{ first_downs: last3FirstDowns, touchdowns: last3Touchdowns }};
                }} else {{
                    const last3Touchdowns = last3.reduce((sum, w) => 
                        sum + (filteredByWeek[w.toString()]?.players || []).reduce((pSum, p) => pSum + (p.touchdowns || 0), 0), 0);
                    last3Extra = {{ touchdowns: last3Touchdowns }};
                }}
                
                // Sum player first downs for total (use player-level aggregation for accuracy)
                if (situation === filtered['3rd_down']) {{
                    filteredTotal.first_downs = Object.values(filteredPlayers).reduce((sum, p) => sum + p.first_downs, 0);
                }}
                // For touchdowns: 
                // 1. First try stats.touchdowns sum (already calculated above)
                // 2. If that's 0, try player-level sum
                // 3. If both are 0 but original total had TDs, the weekly breakdown may be missing
                //    In that case, we keep the stats sum (0) as it's the filtered subset
                const playerTdSum = Object.values(filteredPlayers).reduce((sum, p) => sum + p.touchdowns, 0);
                // Only use player-level sum if stats sum is 0 and player sum is > 0
                if (filteredTotal.touchdowns === 0 && playerTdSum > 0) {{
                    filteredTotal.touchdowns = playerTdSum;
                }}
                // Note: If both are 0, it means the filtered weeks genuinely have 0 TDs
                // (even if the original total had TDs, those TDs were in weeks not included in the filter)
                
                return {{
                    total: filteredTotal,
                    by_week: filteredByWeek,
                    last_3_games: {{
                        targets: last3Targets,
                        receptions: last3Receptions,
                        yards: last3Yards,
                        ...last3Extra
                    }},
                    players: Object.values(filteredPlayers).sort((a, b) => b.targets - a.targets)
                }};
            }}
            
            // Filter both situations
            if (filtered['3rd_down']) {{
                filtered['3rd_down'] = filterSituation(filtered['3rd_down']);
            }}
            if (filtered.redzone) {{
                filtered.redzone = filterSituation(filtered.redzone);
            }}
            
            return filtered;
        }}
        
        function populateSituationalReceiving() {{
            // Use filtered data if available, otherwise use original
            const team1 = allData[team1Key].situational_filtered || allData[team1Key].situational;
            const team2 = allData[team2Key].situational_filtered || allData[team2Key].situational;
            
            if (!team1 || !team2) {{
                console.warn('Situational receiving data not available');
                return;
            }}
            
            // 3rd Down Summary
            const team13rd = team1['3rd_down'];
            const team23rd = team2['3rd_down'];
            const thirdDownSummary = `
                <div class="team-comparison">
                    <div class="team-section ">
                        <h3></h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total Targets</h3><div class="value">${{team13rd.total.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Receptions</h3><div class="value">${{team13rd.total.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Reception %</h3><div class="value">${{team13rd.total.targets > 0 ? (team13rd.total.receptions / team13rd.total.targets * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>First Downs</h3><div class="value">${{team13rd.total.first_downs || 0}}</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{team13rd.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Targets</h3><div class="value">${{team13rd.last_3_games.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Receptions</h3><div class="value">${{team13rd.last_3_games.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 First Downs</h3><div class="value">${{team13rd.last_3_games.first_downs || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section ">
                        <h3></h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total Targets</h3><div class="value">${{team23rd.total.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Receptions</h3><div class="value">${{team23rd.total.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Reception %</h3><div class="value">${{team23rd.total.targets > 0 ? (team23rd.total.receptions / team23rd.total.targets * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>First Downs</h3><div class="value">${{team23rd.total.first_downs || 0}}</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{team23rd.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Targets</h3><div class="value">${{team23rd.last_3_games.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Receptions</h3><div class="value">${{team23rd.last_3_games.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 First Downs</h3><div class="value">${{team23rd.last_3_games.first_downs || 0}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('thirdDownSummary').innerHTML = thirdDownSummary;
            
            // 3rd Down Pie Charts - Target Distribution by Player
            // Aggregate player targets across all games, including rankings
            const washPlayerTargets = {{}};
            const wiscPlayerTargets = {{}};
            
            // Also aggregate from players list to get rankings
            const washPlayerRankings = {{}};
            const wiscPlayerRankings = {{}};
            for (const player of team13rd.players || []) {{
                const name = player.player || 'Unknown';
                washPlayerRankings[name] = player.big_ten_rank;
            }}
            for (const player of team23rd.players || []) {{
                const name = player.player || 'Unknown';
                wiscPlayerRankings[name] = player.big_ten_rank;
            }}
            
            for (const weekData of Object.values(team13rd.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const name = player.player || 'Unknown';
                    if (!washPlayerTargets[name]) {{
                        washPlayerTargets[name] = {{ targets: 0, rank: washPlayerRankings[name] || null }};
                    }}
                    washPlayerTargets[name].targets += (player.targets || 0);
                }}
            }}
            
            for (const weekData of Object.values(team23rd.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const name = player.player || 'Unknown';
                    if (!wiscPlayerTargets[name]) {{
                        wiscPlayerTargets[name] = {{ targets: 0, rank: wiscPlayerRankings[name] || null }};
                    }}
                    wiscPlayerTargets[name].targets += (player.targets || 0);
                }}
            }}
            
            // Sort by targets and take top players (limit to top 8 for readability)
            const washTopPlayers = Object.entries(washPlayerTargets)
                .map(([name, data]) => [name, data.targets, data.rank])
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8);
            const wiscTopPlayers = Object.entries(wiscPlayerTargets)
                .map(([name, data]) => [name, data.targets, data.rank])
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8);
            
            // Team 1 pie chart
            const ctx3rdWash = document.getElementById('thirdDownChartWash').getContext('2d');
            if (charts.thirdDownWash) charts.thirdDownWash.destroy();
            
            const washColors = [
                'rgba(139, 0, 0, 0.8)', 'rgba(139, 0, 0, 0.6)', 'rgba(139, 0, 0, 0.4)',
                'rgba(34, 139, 34, 0.8)', 'rgba(34, 139, 34, 0.6)', 'rgba(34, 139, 34, 0.4)',
                'rgba(0, 100, 0, 0.8)', 'rgba(0, 100, 0, 0.6)'
            ];
            
            charts.thirdDownWash = new Chart(ctx3rdWash, {{
                type: 'pie',
                data: {{
                    labels: washTopPlayers.map(p => p[0]),
                    datasets: [{{
                        data: washTopPlayers.map(p => p[1]),
                        backgroundColor: washColors.slice(0, washTopPlayers.length),
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team1Name + ' - 3rd Down Target Distribution', font: {{ size: 14 }} }},
                        legend: {{ 
                            display: true,
                            position: 'right',
                            labels: {{
                                font: {{ size: 11 }},
                                padding: 12,
                                generateLabels: function(chart) {{
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {{
                                        return data.labels.map((label, i) => {{
                                            const value = data.datasets[0].data[i];
                                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            const rank = washTopPlayers[i][2];
                                            const rankText = rank ? ` (Rank #${{rank}})` : '';
                                            return {{
                                                text: `${{label}}: ${{value}} (${{percentage}}%)${{rankText}}`,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                strokeStyle: data.datasets[0].borderColor,
                                                lineWidth: data.datasets[0].borderWidth,
                                                hidden: false,
                                                index: i
                                            }};
                                        }});
                                    }}
                                    return [];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} targets (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Team 2 pie chart
            const ctx3rdWisc = document.getElementById('thirdDownChartWisc').getContext('2d');
            if (charts.thirdDownWisc) charts.thirdDownWisc.destroy();
            
            const wiscColors = [
                'rgba(220, 20, 60, 0.8)', 'rgba(220, 20, 60, 0.6)', 'rgba(220, 20, 60, 0.4)',
                'rgba(139, 0, 0, 0.8)', 'rgba(139, 0, 0, 0.6)', 'rgba(139, 0, 0, 0.4)',
                'rgba(165, 42, 42, 0.8)', 'rgba(165, 42, 42, 0.6)'
            ];
            
            charts.thirdDownWisc = new Chart(ctx3rdWisc, {{
                type: 'pie',
                data: {{
                    labels: wiscTopPlayers.map(p => p[0]),
                    datasets: [{{
                        data: wiscTopPlayers.map(p => p[1]),
                        backgroundColor: wiscColors.slice(0, wiscTopPlayers.length),
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team2Name + ' - 3rd Down Target Distribution', font: {{ size: 14 }} }},
                        legend: {{ 
                            display: true,
                            position: 'right',
                            labels: {{
                                font: {{ size: 11 }},
                                padding: 12,
                                generateLabels: function(chart) {{
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {{
                                        return data.labels.map((label, i) => {{
                                            const value = data.datasets[0].data[i];
                                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            const rank = wiscTopPlayers[i][2];
                                            const rankText = rank ? ` (Rank #${{rank}})` : '';
                                            return {{
                                                text: `${{label}}: ${{value}} (${{percentage}}%)${{rankText}}`,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                strokeStyle: data.datasets[0].borderColor,
                                                lineWidth: data.datasets[0].borderWidth,
                                                hidden: false,
                                                index: i
                                            }};
                                        }});
                                    }}
                                    return [];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} targets (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Create player ranking lookup from aggregated players
            const wash3rdPlayerRankings = {{}};
            for (const player of team13rd.players || []) {{
                wash3rdPlayerRankings[player.player || 'Unknown'] = {{ rank: player.big_ten_rank, isTop25: player.is_top_25 }};
            }}
            const wisc3rdPlayerRankings = {{}};
            for (const player of team23rd.players || []) {{
                wisc3rdPlayerRankings[player.player || 'Unknown'] = {{ rank: player.big_ten_rank, isTop25: player.is_top_25 }};
            }}
            
            // 3rd Down Tables
            const wash3rdTableData = [];
            for (const [weekStr, weekData] of Object.entries(team13rd.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const recPct = player.targets > 0 ? (player.receptions / player.targets * 100).toFixed(1) : '0.0';
                    const playerName = player.player || 'Unknown';
                    const rankInfo = wash3rdPlayerRankings[playerName] || {{ rank: null, isTop25: false }};
                    wash3rdTableData.push([
                        parseInt(weekStr), weekData.opponent || '', playerName,
                        player.targets || 0, player.receptions || 0, recPct + '%',
                        player.first_downs || 0, player.touchdowns || 0, player.yards || 0,
                        rankInfo.rank || ''
                    ]);
                }}
            }}
            wash3rdTableData.sort((a, b) => {{
                if (a[0] !== b[0]) return a[0] - b[0];
                return (b[3] || 0) - (a[3] || 0); // Sort by targets descending within week
            }});
            
            const wisc3rdTableData = [];
            for (const [weekStr, weekData] of Object.entries(team23rd.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const recPct = player.targets > 0 ? (player.receptions / player.targets * 100).toFixed(1) : '0.0';
                    const playerName = player.player || 'Unknown';
                    const rankInfo = wisc3rdPlayerRankings[playerName] || {{ rank: null, isTop25: false }};
                    wisc3rdTableData.push([
                        parseInt(weekStr), weekData.opponent || '', playerName,
                        player.targets || 0, player.receptions || 0, recPct + '%',
                        player.first_downs || 0, player.touchdowns || 0, player.yards || 0,
                        rankInfo.rank || ''
                    ]);
                }}
            }}
            wisc3rdTableData.sort((a, b) => {{
                if (a[0] !== b[0]) return a[0] - b[0];
                return (b[3] || 0) - (a[3] || 0);
            }});
            
            // Get top 25 players for banner
            const washTop25_3rd = team13rd.players.filter(p => p.is_top_25).map(p => p.player).join(', ');
            const wiscTop25_3rd = team23rd.players.filter(p => p.is_top_25).map(p => p.player).join(', ');
            
            const wash3rdDownConfig = {{
                data: wash3rdTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Player' }},
                    {{ title: 'Targets' }}, {{ title: 'Receptions' }}, {{ title: 'Reception %' }},
                    {{ title: 'First Downs' }}, {{ title: 'TDs' }}, {{ title: 'Yards' }},
                    {{ title: 'Big Ten Rank' }}
                ]
            }};
            safeUpdateDataTable('#thirdDownTableWash', wash3rdTableData, wash3rdDownConfig);
            
            const wisc3rdDownConfig = {{
                data: wisc3rdTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Player' }},
                    {{ title: 'Targets' }}, {{ title: 'Receptions' }}, {{ title: 'Reception %' }},
                    {{ title: 'First Downs' }}, {{ title: 'TDs' }}, {{ title: 'Yards' }},
                    {{ title: 'Big Ten Rank' }}
                ]
            }};
            safeUpdateDataTable('#thirdDownTableWisc', wisc3rdTableData, wisc3rdDownConfig);
            
            // Add top 25 banner for 3rd down
            if (washTop25_3rd || wiscTop25_3rd) {{
                let bannerHTML = '<div class="notice-banner" style="margin-bottom: 20px;"><strong>Top 25 Big Ten Rankings:</strong> ';
                const parts = [];
                if (washTop25_3rd) parts.push(`Washington: ${{washTop25_3rd}}`);
                if (wiscTop25_3rd) parts.push(`Wisconsin: ${{wiscTop25_3rd}}`);
                bannerHTML += parts.join(' | ') + '</div>';
                document.getElementById('thirdDownSummary').insertAdjacentHTML('afterend', bannerHTML);
            }}
            
            // Red Zone Summary
            const washRZ = team1.redzone;
            const wiscRZ = team2.redzone;
            const redZoneSummary = `
                <div class="team-comparison">
                    <div class="team-section ">
                        <h3></h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total Targets</h3><div class="value">${{washRZ.total.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Receptions</h3><div class="value">${{washRZ.total.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Reception %</h3><div class="value">${{washRZ.total.targets > 0 ? (washRZ.total.receptions / washRZ.total.targets * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{washRZ.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Targets</h3><div class="value">${{washRZ.last_3_games.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Receptions</h3><div class="value">${{washRZ.last_3_games.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 TDs</h3><div class="value">${{washRZ.last_3_games.touchdowns || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section ">
                        <h3></h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total Targets</h3><div class="value">${{wiscRZ.total.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Receptions</h3><div class="value">${{wiscRZ.total.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Reception %</h3><div class="value">${{wiscRZ.total.targets > 0 ? (wiscRZ.total.receptions / wiscRZ.total.targets * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{wiscRZ.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Targets</h3><div class="value">${{wiscRZ.last_3_games.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Receptions</h3><div class="value">${{wiscRZ.last_3_games.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 TDs</h3><div class="value">${{wiscRZ.last_3_games.touchdowns || 0}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('redZoneReceivingSummary').innerHTML = redZoneSummary;
            
            // Red Zone Pie Charts - Target Distribution by Player
            // Aggregate player targets across all games, including rankings
            const washRZPlayerTargets = {{}};
            const wiscRZPlayerTargets = {{}};
            
            // Also aggregate from players list to get rankings
            const washRZPlayerRankings = {{}};
            const wiscRZPlayerRankings = {{}};
            for (const player of washRZ.players || []) {{
                const name = player.player || 'Unknown';
                washRZPlayerRankings[name] = player.big_ten_rank;
            }}
            for (const player of wiscRZ.players || []) {{
                const name = player.player || 'Unknown';
                wiscRZPlayerRankings[name] = player.big_ten_rank;
            }}
            
            for (const weekData of Object.values(washRZ.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const name = player.player || 'Unknown';
                    if (!washRZPlayerTargets[name]) {{
                        washRZPlayerTargets[name] = {{ targets: 0, rank: washRZPlayerRankings[name] || null }};
                    }}
                    washRZPlayerTargets[name].targets += (player.targets || 0);
                }}
            }}
            
            for (const weekData of Object.values(wiscRZ.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const name = player.player || 'Unknown';
                    if (!wiscRZPlayerTargets[name]) {{
                        wiscRZPlayerTargets[name] = {{ targets: 0, rank: wiscRZPlayerRankings[name] || null }};
                    }}
                    wiscRZPlayerTargets[name].targets += (player.targets || 0);
                }}
            }}
            
            // Sort by targets and take top players
            const washRZTopPlayers = Object.entries(washRZPlayerTargets)
                .map(([name, data]) => [name, data.targets, data.rank])
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8);
            const wiscRZTopPlayers = Object.entries(wiscRZPlayerTargets)
                .map(([name, data]) => [name, data.targets, data.rank])
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8);
            
            // Team 1 Red Zone pie chart
            const ctxRZWash = document.getElementById('redZoneReceivingChartWash').getContext('2d');
            if (charts.redZoneReceivingWash) charts.redZoneReceivingWash.destroy();
            
            charts.redZoneReceivingWash = new Chart(ctxRZWash, {{
                type: 'pie',
                data: {{
                    labels: washRZTopPlayers.map(p => p[0]),
                    datasets: [{{
                        data: washRZTopPlayers.map(p => p[1]),
                        backgroundColor: washColors.slice(0, washRZTopPlayers.length),
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team1Name + ' - Red Zone Target Distribution', font: {{ size: 14 }} }},
                        legend: {{ 
                            display: true,
                            position: 'right',
                            labels: {{
                                font: {{ size: 11 }},
                                padding: 12,
                                generateLabels: function(chart) {{
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {{
                                        return data.labels.map((label, i) => {{
                                            const value = data.datasets[0].data[i];
                                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            const rank = washRZTopPlayers[i][2];
                                            const rankText = rank ? ` (Rank #${{rank}})` : '';
                                            return {{
                                                text: `${{label}}: ${{value}} (${{percentage}}%)${{rankText}}`,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                strokeStyle: data.datasets[0].borderColor,
                                                lineWidth: data.datasets[0].borderWidth,
                                                hidden: false,
                                                index: i
                                            }};
                                        }});
                                    }}
                                    return [];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} targets (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Team 2 Red Zone pie chart
            const ctxRZWisc = document.getElementById('redZoneReceivingChartWisc').getContext('2d');
            if (charts.redZoneReceivingWisc) charts.redZoneReceivingWisc.destroy();
            
            charts.redZoneReceivingWisc = new Chart(ctxRZWisc, {{
                type: 'pie',
                data: {{
                    labels: wiscRZTopPlayers.map(p => p[0]),
                    datasets: [{{
                        data: wiscRZTopPlayers.map(p => p[1]),
                        backgroundColor: wiscColors.slice(0, wiscRZTopPlayers.length),
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team2Name + ' - Red Zone Target Distribution', font: {{ size: 14 }} }},
                        legend: {{ 
                            display: true,
                            position: 'right',
                            labels: {{
                                font: {{ size: 11 }},
                                padding: 12,
                                generateLabels: function(chart) {{
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {{
                                        return data.labels.map((label, i) => {{
                                            const value = data.datasets[0].data[i];
                                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            const rank = wiscRZTopPlayers[i][2];
                                            const rankText = rank ? ` (Rank #${{rank}})` : '';
                                            return {{
                                                text: `${{label}}: ${{value}} (${{percentage}}%)${{rankText}}`,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                strokeStyle: data.datasets[0].borderColor,
                                                lineWidth: data.datasets[0].borderWidth,
                                                hidden: false,
                                                index: i
                                            }};
                                        }});
                                    }}
                                    return [];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} targets (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Create player ranking lookup from aggregated players for Red Zone
            const washRZPlayerRankingsTable = {{}};
            for (const player of washRZ.players || []) {{
                washRZPlayerRankingsTable[player.player || 'Unknown'] = {{ rank: player.big_ten_rank, isTop25: player.is_top_25 }};
            }}
            const wiscRZPlayerRankingsTable = {{}};
            for (const player of wiscRZ.players || []) {{
                wiscRZPlayerRankingsTable[player.player || 'Unknown'] = {{ rank: player.big_ten_rank, isTop25: player.is_top_25 }};
            }}
            
            // Red Zone Tables
            const washRZTableData = [];
            for (const [weekStr, weekData] of Object.entries(washRZ.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const recPct = player.targets > 0 ? (player.receptions / player.targets * 100).toFixed(1) : '0.0';
                    const playerName = player.player || 'Unknown';
                    const rankInfo = washRZPlayerRankingsTable[playerName] || {{ rank: null, isTop25: false }};
                    washRZTableData.push([
                        parseInt(weekStr), weekData.opponent || '', playerName,
                        player.targets || 0, player.receptions || 0, recPct + '%',
                        player.touchdowns || 0, player.yards || 0,
                        rankInfo.rank || ''
                    ]);
                }}
            }}
            washRZTableData.sort((a, b) => {{
                if (a[0] !== b[0]) return a[0] - b[0];
                return (b[3] || 0) - (a[3] || 0);
            }});
            
            const wiscRZTableData = [];
            for (const [weekStr, weekData] of Object.entries(wiscRZ.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const recPct = player.targets > 0 ? (player.receptions / player.targets * 100).toFixed(1) : '0.0';
                    const playerName = player.player || 'Unknown';
                    const rankInfo = wiscRZPlayerRankingsTable[playerName] || {{ rank: null, isTop25: false }};
                    wiscRZTableData.push([
                        parseInt(weekStr), weekData.opponent || '', playerName,
                        player.targets || 0, player.receptions || 0, recPct + '%',
                        player.touchdowns || 0, player.yards || 0,
                        rankInfo.rank || ''
                    ]);
                }}
            }}
            wiscRZTableData.sort((a, b) => {{
                if (a[0] !== b[0]) return a[0] - b[0];
                return (b[3] || 0) - (a[3] || 0);
            }});
            
            // Get top 25 players for banner
            const washTop25_RZ = washRZ.players.filter(p => p.is_top_25).map(p => p.player).join(', ');
            const wiscTop25_RZ = wiscRZ.players.filter(p => p.is_top_25).map(p => p.player).join(', ');
            
            const washRZConfig = {{
                data: washRZTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Player' }},
                    {{ title: 'Targets' }}, {{ title: 'Receptions' }}, {{ title: 'Reception %' }},
                    {{ title: 'TDs' }}, {{ title: 'Yards' }},
                    {{ title: 'Big Ten Rank' }}
                ]
            }};
            safeUpdateDataTable('#redZoneReceivingTableWash', washRZTableData, washRZConfig);
            
            const wiscRZConfig = {{
                data: wiscRZTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Player' }},
                    {{ title: 'Targets' }}, {{ title: 'Receptions' }}, {{ title: 'Reception %' }},
                    {{ title: 'TDs' }}, {{ title: 'Yards' }},
                    {{ title: 'Big Ten Rank' }}
                ]
            }};
            safeUpdateDataTable('#redZoneReceivingTableWisc', wiscRZTableData, wiscRZConfig);
            
            // Add top 25 banner for red zone
            if (washTop25_RZ || wiscTop25_RZ) {{
                let bannerHTML = '<div class="notice-banner" style="margin-bottom: 20px;"><strong>Top 25 Big Ten Rankings:</strong> ';
                const parts = [];
                if (washTop25_RZ) parts.push(`Washington: ${{washTop25_RZ}}`);
                if (wiscTop25_RZ) parts.push(`Wisconsin: ${{wiscTop25_RZ}}`);
                bannerHTML += parts.join(' | ') + '</div>';
                document.getElementById('redZoneReceivingSummary').insertAdjacentHTML('afterend', bannerHTML);
            }}
        }}
        
        function filterDeepTargets(deepTargetData, filters) {{
            // Filter deep target data based on filters
            // Returns filtered copy of the data structure
            if (!deepTargetData) return null;
            
            // Check if any filters are actually applied
            const hasFilters = filters.conference_only || filters.non_conference_only || 
                              filters.power4_only || filters.last_3_games;
            
            // If no filters, return original data
            if (!hasFilters) {{
                return deepTargetData;
            }}
            
            // Check if receiving data has enrichment fields
            // If not, we can't filter properly, so return original data with a warning
            let hasEnrichment = false;
            if (deepTargetData.receiving && deepTargetData.receiving.by_game) {{
                for (const gameData of Object.values(deepTargetData.receiving.by_game)) {{
                    if (gameData.hasOwnProperty('is_conference') || gameData.hasOwnProperty('is_power4_opponent') || gameData.hasOwnProperty('game_id')) {{
                        hasEnrichment = true;
                        break;
                    }}
                }}
            }}
            
            if (!hasEnrichment) {{
                console.warn('Deep target data does not have enrichment fields (is_conference, is_power4_opponent, game_id). Cannot apply filters. Returning unfiltered data.');
                return deepTargetData;
            }}
            
            const filtered = JSON.parse(JSON.stringify(deepTargetData)); // Deep copy
            
            // Helper function to filter by_game data
            // For passing data, we need to match it to receiving data to get enrichment fields
            function filterByGame(byGame, isPassing, receivingByGame) {{
                if (!byGame) return byGame;
                
                const filteredByGame = {{}};
                let filteredTotal = isPassing ? 
                    {{ attempts: 0, completions: 0, yards: 0, touchdowns: 0, interceptions: 0 }} :
                    {{ targets: 0, receptions: 0, yards: 0, touchdowns: 0 }};
                const filteredLast3Games = [];
                
                // Get last 3 game IDs if needed (use receiving data which has game_id)
                let last3GameIds = [];
                if (filters.last_3_games && receivingByGame) {{
                    const allGames = Object.entries(receivingByGame)
                        .map(([key, data]) => ({{
                            week: data.week || parseInt(key.replace('Week', '').split('_')[0]) || 0,
                            game_id: data.game_id,
                            key: key
                        }}))
                        .filter(g => g.game_id)
                        .sort((a, b) => a.week - b.week);
                    last3GameIds = allGames.slice(-3).map(g => g.game_id);
                }}
                
                // Filter games
                for (const [gameKey, gameData] of Object.entries(byGame)) {{
                    let include = true;
                    
                    // For passing data, get enrichment fields from matching receiving game
                    let enrichmentData = null;
                    if (isPassing && receivingByGame && receivingByGame[gameKey]) {{
                        enrichmentData = receivingByGame[gameKey];
                    }} else if (!isPassing) {{
                        enrichmentData = gameData; // Receiving data has enrichment fields
                    }}
                    
                    // Filter by conference/non-conference/power4
                    // Only apply filters if we have enrichment data, otherwise include the game
                    if (enrichmentData) {{
                        if (filters.conference_only) {{
                            include = include && enrichmentData.is_conference === true;
                        }} else if (filters.non_conference_only) {{
                            include = include && enrichmentData.is_conference === false;
                        }} else if (filters.power4_only) {{
                            include = include && enrichmentData.is_power4_opponent === true;
                        }}
                        
                        // Filter by last 3 games
                        if (filters.last_3_games) {{
                            include = include && last3GameIds.includes(enrichmentData.game_id);
                        }}
                    }}
                    // If no enrichment data but filters are active, we can't determine if it should be included
                    // For now, exclude it to be safe (this shouldn't happen if data is properly enriched)
                    
                    if (include) {{
                        filteredByGame[gameKey] = gameData;
                        filteredLast3Games.push(gameData);
                        
                        // Aggregate totals
                        if (isPassing) {{
                            filteredTotal.attempts += gameData.attempts || 0;
                            filteredTotal.completions += gameData.completions || 0;
                            filteredTotal.yards += gameData.yards || 0;
                            filteredTotal.touchdowns += gameData.touchdowns || 0;
                            filteredTotal.interceptions += gameData.interceptions || 0;
                        }} else {{
                            filteredTotal.targets += gameData.targets || 0;
                            filteredTotal.receptions += gameData.receptions || 0;
                            filteredTotal.yards += gameData.yards || 0;
                            filteredTotal.touchdowns += gameData.touchdowns || 0;
                        }}
                    }}
                }}
                
                // Calculate last 3 games stats
                filteredLast3Games.sort((a, b) => (a.week || 0) - (b.week || 0));
                const last3 = filteredLast3Games.slice(-3);
                
                const last3Stats = isPassing ? 
                    {{
                        attempts: last3.reduce((sum, g) => sum + (g.attempts || 0), 0),
                        completions: last3.reduce((sum, g) => sum + (g.completions || 0), 0),
                        yards: last3.reduce((sum, g) => sum + (g.yards || 0), 0),
                        touchdowns: last3.reduce((sum, g) => sum + (g.touchdowns || 0), 0),
                        interceptions: last3.reduce((sum, g) => sum + (g.interceptions || 0), 0)
                    }} :
                    {{
                        targets: last3.reduce((sum, g) => sum + (g.targets || 0), 0),
                        receptions: last3.reduce((sum, g) => sum + (g.receptions || 0), 0),
                        yards: last3.reduce((sum, g) => sum + (g.yards || 0), 0),
                        touchdowns: last3.reduce((sum, g) => 
                            sum + (g.players || []).reduce((pSum, p) => pSum + (p.touchdowns || 0), 0), 0)
                    }};
                
                return {{
                    total: filteredTotal,
                    by_game: filteredByGame,
                    last_3_games: last3Stats,
                    big_ten_rank: isPassing ? (deepTargetData.passing?.big_ten_rank || null) : undefined, // Preserve rank if passing
                    players: isPassing ? undefined : aggregateReceivingPlayers(filteredByGame)
                }};
            }}
            
            // Helper to aggregate receiving players across filtered games
            function aggregateReceivingPlayers(byGame) {{
                const playerStats = {{}};
                for (const gameData of Object.values(byGame)) {{
                    for (const player of gameData.players || []) {{
                        const name = player.player || 'Unknown';
                        if (!playerStats[name]) {{
                            playerStats[name] = {{
                                player: name,
                                targets: 0,
                                receptions: 0,
                                yards: 0,
                                touchdowns: 0,
                                air_yards: 0
                            }};
                        }}
                        playerStats[name].targets += player.targets || 0;
                        playerStats[name].receptions += player.receptions || 0;
                        playerStats[name].yards += player.yards || 0;
                        playerStats[name].touchdowns += player.touchdowns || 0;
                        playerStats[name].air_yards += player.air_yards || 0;
                    }}
                }}
                return Object.values(playerStats).sort((a, b) => b.targets - a.targets);
            }}
            
            // Filter passing and receiving
            // Pass receiving by_game to filterByGame so passing can use enrichment fields
            if (filtered.passing && filtered.receiving) {{
                filtered.passing = filterByGame(filtered.passing.by_game, true, filtered.receiving.by_game);
            }}
            if (filtered.receiving) {{
                filtered.receiving = filterByGame(filtered.receiving.by_game, false, null);
            }}
            
            return filtered;
        }}
        
        function populateDeepTargets() {{
            // Use filtered data if available, otherwise use original
            const team1 = allData[team1Key].deep_targets_filtered || allData[team1Key].deep_targets;
            const team2 = allData[team2Key].deep_targets_filtered || allData[team2Key].deep_targets;
            
            if (!team1 || !team2) {{
                console.warn('Deep target data not available');
                return;
            }}
            
            // Combined Summary (unique cards only)
            const team1Passing = team1.passing;
            const team2Passing = team2.passing;
            const team1Receiving = team1.receiving;
            const team2Receiving = team2.receiving;
            const combinedSummary = `
                <div class="team-comparison">
                    <div class="team-section ">
                        <h3>${{team1Name}}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Pass Attempts</h3><div class="value">${{team1Passing.total.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Completions</h3><div class="value">${{team1Passing.total.completions || 0}}</div></div>
                            <div class="summary-card"><h3>Completion %</h3><div class="value">${{team1Passing.total.attempts > 0 ? (team1Passing.total.completions / team1Passing.total.attempts * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>Yards</h3><div class="value">${{team1Passing.total.yards || 0}}</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{team1Passing.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>INTs</h3><div class="value">${{team1Passing.total.interceptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Attempts</h3><div class="value">${{team1Passing.last_3_games.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Completions</h3><div class="value">${{team1Passing.last_3_games.completions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 TDs</h3><div class="value">${{team1Receiving.last_3_games.touchdowns || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section ">
                        <h3>${{team2Name}}</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Pass Attempts</h3><div class="value">${{team2Passing.total.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Completions</h3><div class="value">${{team2Passing.total.completions || 0}}</div></div>
                            <div class="summary-card"><h3>Completion %</h3><div class="value">${{team2Passing.total.attempts > 0 ? (team2Passing.total.completions / team2Passing.total.attempts * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>Yards</h3><div class="value">${{team2Passing.total.yards || 0}}</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{team2Passing.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>INTs</h3><div class="value">${{team2Passing.total.interceptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Attempts</h3><div class="value">${{team2Passing.last_3_games.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Completions</h3><div class="value">${{team2Passing.last_3_games.completions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 TDs</h3><div class="value">${{team2Receiving.last_3_games.touchdowns || 0}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('deepTargetSummary').innerHTML = combinedSummary;
            
            // Passing Charts - Attempts by Week (sorted by week)
            const washPassingGames = Object.entries(team1Passing.by_game || {{}})
                .map(([key, data]) => ({{
                    week: data.week || parseInt(key.replace('Week', '').split('_')[0]) || 0,
                    opponent: data.opponent || key.replace('Week', '').split('_').slice(1).join(' ').replace(/_/g, ' ') || '',
                    attempts: data.attempts || 0,
                    completions: data.completions || 0
                }}))
                .sort((a, b) => a.week - b.week);
            
            const washPassingWeeks = washPassingGames.map(g => `Week ${{g.week}}`);
            const washPassingAttempts = washPassingGames.map(g => g.attempts);
            const washPassingCompletions = washPassingGames.map(g => g.completions);
            const washPassingOpponents = washPassingGames.map(g => g.opponent);
            
            const wiscPassingGames = Object.entries(team2Passing.by_game || {{}})
                .map(([key, data]) => ({{
                    week: data.week || parseInt(key.replace('Week', '').split('_')[0]) || 0,
                    opponent: data.opponent || key.replace('Week', '').split('_').slice(1).join(' ').replace(/_/g, ' ') || '',
                    attempts: data.attempts || 0,
                    completions: data.completions || 0
                }}))
                .sort((a, b) => a.week - b.week);
            
            const wiscPassingWeeks = wiscPassingGames.map(g => `Week ${{g.week}}`);
            const wiscPassingAttempts = wiscPassingGames.map(g => g.attempts);
            const wiscPassingCompletions = wiscPassingGames.map(g => g.completions);
            const wiscPassingOpponents = wiscPassingGames.map(g => g.opponent);
            
            // Team 1 passing chart
            const ctxPassWash = document.getElementById('deepPassingChartWash').getContext('2d');
            if (charts.deepPassingWash) charts.deepPassingWash.destroy();
            charts.deepPassingWash = new Chart(ctxPassWash, {{
                type: 'bar',
                data: {{
                    labels: washPassingWeeks,
                    datasets: [{{
                        label: 'Attempts',
                        data: washPassingAttempts,
                        backgroundColor: 'rgba(139, 0, 0, 0.6)',
                        borderColor: 'rgba(139, 0, 0, 1)',
                        borderWidth: 1
                    }}, {{
                        label: 'Completions',
                        data: washPassingCompletions,
                        backgroundColor: 'rgba(34, 139, 34, 0.6)',
                        borderColor: 'rgba(34, 139, 34, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team1Name + ' - Deep Ball Attempts by Week', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    const index = context[0].dataIndex;
                                    const opponent = washPassingOpponents[index] || '';
                                    return `Week ${{washPassingGames[index].week}}${{opponent ? ' vs ' + opponent : ''}}`;
                                }},
                                label: function(context) {{
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y || 0;
                                    return `${{label}}: ${{value}}`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                    }}
                }}
            }});
            
            // Team 2 passing chart
            const ctxPassWisc = document.getElementById('deepPassingChartWisc').getContext('2d');
            if (charts.deepPassingWisc) charts.deepPassingWisc.destroy();
            charts.deepPassingWisc = new Chart(ctxPassWisc, {{
                type: 'bar',
                data: {{
                    labels: wiscPassingWeeks,
                    datasets: [{{
                        label: 'Attempts',
                        data: wiscPassingAttempts,
                        backgroundColor: 'rgba(220, 20, 60, 0.6)',
                        borderColor: 'rgba(220, 20, 60, 1)',
                        borderWidth: 1
                    }}, {{
                        label: 'Completions',
                        data: wiscPassingCompletions,
                        backgroundColor: 'rgba(139, 0, 0, 0.6)',
                        borderColor: 'rgba(139, 0, 0, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team2Name + ' - Deep Ball Attempts by Week', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'top' }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    const index = context[0].dataIndex;
                                    const opponent = wiscPassingOpponents[index] || '';
                                    return `Week ${{wiscPassingGames[index].week}}${{opponent ? ' vs ' + opponent : ''}}`;
                                }},
                                label: function(context) {{
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y || 0;
                                    return `${{label}}: ${{value}}`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                    }}
                }}
            }});
            
            
            // Receiving Charts - Target Distribution by Player
            const washPlayerTargets = {{}};
            const wiscPlayerTargets = {{}};
            
            for (const player of team1Receiving.players || []) {{
                const name = player.player || 'Unknown';
                washPlayerTargets[name] = (washPlayerTargets[name] || 0) + (player.targets || 0);
            }}
            
            for (const player of team2Receiving.players || []) {{
                const name = player.player || 'Unknown';
                wiscPlayerTargets[name] = (wiscPlayerTargets[name] || 0) + (player.targets || 0);
            }}
            
            const washTopPlayers = Object.entries(washPlayerTargets)
                .map(([name, targets]) => [name, targets])
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8);
            const wiscTopPlayers = Object.entries(wiscPlayerTargets)
                .map(([name, targets]) => [name, targets])
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8);
            
            // Team 1 receiving pie chart
            const ctxRecWash = document.getElementById('deepReceivingChartWash').getContext('2d');
            if (charts.deepReceivingWash) charts.deepReceivingWash.destroy();
            const washColors = [
                'rgba(139, 0, 0, 0.8)', 'rgba(139, 0, 0, 0.6)', 'rgba(139, 0, 0, 0.4)',
                'rgba(34, 139, 34, 0.8)', 'rgba(34, 139, 34, 0.6)', 'rgba(34, 139, 34, 0.4)',
                'rgba(0, 100, 0, 0.8)', 'rgba(0, 100, 0, 0.6)'
            ];
            charts.deepReceivingWash = new Chart(ctxRecWash, {{
                type: 'pie',
                data: {{
                    labels: washTopPlayers.map(p => p[0] + ' (' + p[1] + ')'),
                    datasets: [{{
                        data: washTopPlayers.map(p => p[1]),
                        backgroundColor: washColors.slice(0, washTopPlayers.length),
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team1Name + ' - Deep Target Distribution', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'right' }}
                    }}
                }}
            }});
            
            // Team 2 receiving pie chart
            const ctxRecWisc = document.getElementById('deepReceivingChartWisc').getContext('2d');
            if (charts.deepReceivingWisc) charts.deepReceivingWisc.destroy();
            const wiscColors = [
                'rgba(220, 20, 60, 0.8)', 'rgba(220, 20, 60, 0.6)', 'rgba(220, 20, 60, 0.4)',
                'rgba(139, 0, 0, 0.8)', 'rgba(139, 0, 0, 0.6)', 'rgba(139, 0, 0, 0.4)',
                'rgba(165, 42, 42, 0.8)', 'rgba(165, 42, 42, 0.6)'
            ];
            charts.deepReceivingWisc = new Chart(ctxRecWisc, {{
                type: 'pie',
                data: {{
                    labels: wiscTopPlayers.map(p => p[0] + ' (' + p[1] + ')'),
                    datasets: [{{
                        data: wiscTopPlayers.map(p => p[1]),
                        backgroundColor: wiscColors.slice(0, wiscTopPlayers.length),
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{ display: true, text: team2Name + ' - Deep Target Distribution', font: {{ size: 14 }} }},
                        legend: {{ display: true, position: 'right' }}
                    }}
                }}
            }});
            
            // Receiving Tables
            const washRecTableData = [];
            for (const [gameKey, gameData] of Object.entries(team1Receiving.by_game || {{}})) {{
                for (const player of gameData.players || []) {{
                    const recPct = player.targets > 0 ? (player.receptions / player.targets * 100).toFixed(1) : '0.0';
                    washRecTableData.push([
                        gameData.week || '', gameData.opponent || '', player.player || 'Unknown',
                        player.targets || 0, player.receptions || 0, recPct + '%',
                        player.yards || 0, player.air_yards || 0, player.touchdowns || 0
                    ]);
                }}
            }}
            washRecTableData.sort((a, b) => {{
                if (a[0] !== b[0]) return (a[0] || 0) - (b[0] || 0);
                return (b[3] || 0) - (a[3] || 0);
            }});
            
            const wiscRecTableData = [];
            for (const [gameKey, gameData] of Object.entries(team2Receiving.by_game || {{}})) {{
                for (const player of gameData.players || []) {{
                    const recPct = player.targets > 0 ? (player.receptions / player.targets * 100).toFixed(1) : '0.0';
                    wiscRecTableData.push([
                        gameData.week || '', gameData.opponent || '', player.player || 'Unknown',
                        player.targets || 0, player.receptions || 0, recPct + '%',
                        player.yards || 0, player.air_yards || 0, player.touchdowns || 0
                    ]);
                }}
            }}
            wiscRecTableData.sort((a, b) => {{
                if (a[0] !== b[0]) return (a[0] || 0) - (b[0] || 0);
                return (b[3] || 0) - (a[3] || 0);
            }});
            
            const washRecConfig = {{
                data: washRecTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Player' }},
                    {{ title: 'Targets' }}, {{ title: 'Receptions' }}, {{ title: 'Reception %' }},
                    {{ title: 'Yards' }}, {{ title: 'Air Yards' }}, {{ title: 'TDs' }}
                ]
            }};
            safeUpdateDataTable('#deepReceivingTableWash', washRecTableData, washRecConfig);
            
            const wiscRecConfig = {{
                data: wiscRecTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Player' }},
                    {{ title: 'Targets' }}, {{ title: 'Receptions' }}, {{ title: 'Reception %' }},
                    {{ title: 'Yards' }}, {{ title: 'Air Yards' }}, {{ title: 'TDs' }}
                ]
            }};
            safeUpdateDataTable('#deepReceivingTableWisc', wiscRecTableData, wiscRecConfig);
        }}
        
        function populateAllSections() {{
            populateMiddleEight();
            populateExplosivePlays();
            populatePenalties();
            populate4thDowns();
            populatePostTurnover();
            populateSpecialTeams();
            populateRedZone();
            populateSituationalReceiving();
            populateDeepTargets();
            populateAllPlaysBrowser();
        }}
        
        function populateAllPlaysBrowser() {{
            const container = document.getElementById('allPlaysContainer');
            if (!container) return;
            
            let html = '<div class="plays-browser">';
            
            // Process both teams
            const teams = [
                {{ name: team1Name, plays: team1Plays, color: team1Key }},
                {{ name: team2Name, plays: team2Plays, color: team2Key }}
            ];
            
            teams.forEach((team, teamIdx) => {{
                // Group plays by game, then quarter, then drive
                const gameMap = new Map();
                
                team.plays.forEach(play => {{
                    const gameId = play.game_id;
                    if (!gameMap.has(gameId)) {{
                        gameMap.set(gameId, {{
                            game_id: gameId,
                            week: play.game_week || 0,
                            opponent: play.opponent || 'Unknown',
                            quarters: new Map()
                        }});
                    }}
                    
                    const game = gameMap.get(gameId);
                    const period = play.period || 1;
                    const driveId = play.drive_id || 'unknown';
                    
                    if (!game.quarters.has(period)) {{
                        game.quarters.set(period, new Map());
                    }}
                    
                    const quarter = game.quarters.get(period);
                    if (!quarter.has(driveId)) {{
                        quarter.set(driveId, {{
                            drive_id: driveId,
                            drive_number: play.drive_number || 0,
                            plays: []
                        }});
                    }}
                    
                    quarter.get(driveId).plays.push(play);
                }});
                
                // Sort games by week
                const sortedGames = Array.from(gameMap.values()).sort((a, b) => a.week - b.week);
                
                // Team header
                const teamId = `team-${{teamIdx}}`;
                html += `<div class="team-section-browser">`;
                html += `<div class="team-header-browser ${{team.color}}" onclick="toggleCollapsible('${{teamId}}')">`;
                html += `<span class="expand-icon">▶</span> ${{team.name}}`;
                html += `</div>`;
                html += `<div id="${{teamId}}" class="collapsible-content">`;
                
                // Games
                sortedGames.forEach((game, gameIdx) => {{
                    const gameId = `game-${{teamIdx}}-${{gameIdx}}`;
                    html += `<div class="game-section-browser">`;
                    html += `<div class="game-header-browser" onclick="toggleCollapsible('${{gameId}}')">`;
                    html += `<span class="expand-icon">▶</span> Week ${{game.week}}: vs ${{game.opponent}}`;
                    html += `</div>`;
                    html += `<div id="${{gameId}}" class="collapsible-content">`;
                    
                    // Quarters (sorted)
                    const sortedQuarters = Array.from(game.quarters.entries()).sort((a, b) => a[0] - b[0]);
                    
                    sortedQuarters.forEach(([period, drivesMap]) => {{
                        const quarterId = `quarter-${{teamIdx}}-${{gameIdx}}-${{period}}`;
                        html += `<div class="quarter-section-browser">`;
                        html += `<div class="quarter-header-browser" onclick="toggleCollapsible('${{quarterId}}')">`;
                        html += `<span class="expand-icon">▶</span> ${{getQuarterName(period)}} Quarter`;
                        html += `</div>`;
                        html += `<div id="${{quarterId}}" class="collapsible-content">`;
                        
                        // Drives (sorted by drive number)
                        const sortedDrives = Array.from(drivesMap.values()).sort((a, b) => a.drive_number - b.drive_number);
                        
                        sortedDrives.forEach((drive, driveIdx) => {{
                            const driveId = `drive-${{teamIdx}}-${{gameIdx}}-${{period}}-${{driveIdx}}`;
                            html += `<div class="drive-section-browser">`;
                            html += `<div class="drive-header-browser" onclick="toggleCollapsible('${{driveId}}')">`;
                            html += `<span class="expand-icon">▶</span> Drive ${{drive.drive_number}} (${{drive.plays.length}} plays)`;
                            html += `</div>`;
                            html += `<div id="${{driveId}}" class="collapsible-content">`;
                            
                            // Plays table
                            html += `<table class="plays-table-browser">`;
                            html += `<thead><tr>`;
                            html += `<th>Play</th><th>Clock</th><th>Down</th><th>Dist</th><th>Yard Line</th><th>Play Type</th><th>Yards</th><th>Description</th>`;
                            html += `</tr></thead><tbody>`;
                            
                            drive.plays.sort((a, b) => (a.play_number || 0) - (b.play_number || 0)).forEach(play => {{
                                html += `<tr>`;
                                html += `<td>${{play.play_number || ''}}</td>`;
                                html += `<td>${{formatClock(play.clock || '')}}</td>`;
                                html += `<td>${{play.down || ''}}</td>`;
                                html += `<td>${{play.distance || ''}}</td>`;
                                html += `<td>${{play.yard_line || ''}}</td>`;
                                html += `<td>${{play.play_type || ''}}</td>`;
                                html += `<td>${{play.yards_gained || 0}}</td>`;
                                html += `<td>${{escapeHtml((play.play_text || '').substring(0, 100))}}</td>`;
                                html += `</tr>`;
                            }});
                            
                            html += `</tbody></table>`;
                            html += `</div></div>`; // drive
                        }});
                        
                        html += `</div></div>`; // quarter
                    }});
                    
                    html += `</div></div>`; // game
                }});
                
                html += `</div></div>`; // team
            }});
            
            html += '</div>';
            container.innerHTML = html;
        }}
        
        function toggleCollapsible(id) {{
            const element = document.getElementById(id);
            if (!element) return;
            
            const isExpanded = element.classList.contains('expanded');
            if (isExpanded) {{
                element.classList.remove('expanded');
                // Hide all child collapsibles
                element.querySelectorAll('.collapsible-content').forEach(child => {{
                    child.classList.remove('expanded');
                }});
            }} else {{
                element.classList.add('expanded');
            }}
            
            // Update icon
            const header = element.previousElementSibling;
            if (header) {{
                const icon = header.querySelector('.expand-icon');
                if (icon) {{
                    icon.classList.toggle('expanded', !isExpanded);
                }}
            }}
        }}
        
        function getQuarterName(period) {{
            const quarters = ['', '1st', '2nd', '3rd', '4th', 'OT'];
            return quarters[period] || period;
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Analysis functions in JavaScript (simplified versions)
        function analyzeMiddleEight(plays, teamName) {{
            const middle8Plays = plays.filter(p => p.middle_eight === true);
            let pointsScored = 0;
            let pointsAllowed = 0;
            const scoringDrives = [];
            const gameStats = {{}};
            
            middle8Plays.forEach(play => {{
                const gameId = play.game_id;
                if (!gameStats[gameId]) {{
                    gameStats[gameId] = {{ pointsScored: 0, pointsAllowed: 0 }};
                }}
                
                const isOffense = play.offense?.toLowerCase() === teamName.toLowerCase();
                if (play.scoring === true) {{
                    let points = 0;
                    if (play.play_type?.includes('Touchdown')) {{
                        points = 7;
                    }} else if (play.play_type?.includes('Field Goal')) {{
                        points = 3;
                    }}
                    
                    if (isOffense) {{
                        pointsScored += points;
                        gameStats[gameId].pointsScored += points;
                    }} else {{
                        pointsAllowed += points;
                        gameStats[gameId].pointsAllowed += points;
                    }}
                    
                    // Determine actual opponent - if our team is on offense, opponent is defense, and vice versa
                    let actualOpponent = play.opponent || '';
                    if (!actualOpponent || actualOpponent.toLowerCase() === teamName.toLowerCase()) {{
                        actualOpponent = play.defense || '';
                    }}
                    
                    scoringDrives.push({{
                        game_week: play.game_week,
                        opponent: actualOpponent,
                        scoring_team: play.offense || '',
                        drive_number: play.drive_number,
                        period: play.period,
                        clock: play.clock,
                        play_type: play.play_type,
                        points: points,  // Always positive
                        is_offense: isOffense,
                        play_text: play.play_text?.substring(0, 100) || ''
                    }});
                }}
            }});
            
            const uniqueGames = new Set(middle8Plays.map(p => p.game_id)).size;
            
            // Calculate last 3 games
            const sortedGames = Object.keys(gameStats).sort((a, b) => {{
                const weekA = middle8Plays.find(p => p.game_id == a)?.game_week || 0;
                const weekB = middle8Plays.find(p => p.game_id == b)?.game_week || 0;
                return weekA - weekB;
            }});
            const last3Games = sortedGames.slice(-3);
            
            const last3PointsScored = last3Games.reduce((sum, gid) => sum + (gameStats[gid]?.pointsScored || 0), 0);
            const last3PointsAllowed = last3Games.reduce((sum, gid) => sum + (gameStats[gid]?.pointsAllowed || 0), 0);
            const last3Net = last3PointsScored - last3PointsAllowed;
            
            return {{
                total_points_scored: pointsScored,
                total_points_allowed: pointsAllowed,
                total_net_points: pointsScored - pointsAllowed,
                avg_net_per_game: uniqueGames > 0 ? (pointsScored - pointsAllowed) / uniqueGames : 0,
                last_3_games: {{
                    points_scored: last3PointsScored,
                    points_allowed: last3PointsAllowed,
                    net_points: last3Net
                }},
                scoring_drives: scoringDrives
            }};
        }}
        
        function isRunPlay(playType) {{
            if (!playType) return false;
            const pt = playType.toLowerCase();
            return pt.includes('rush') || pt.includes('run') || pt === 'sack';
        }}
        
        function isPassPlay(playType) {{
            if (!playType) return false;
            const pt = playType.toLowerCase();
            return pt.includes('pass') || pt.includes('reception') || pt.includes('incompletion') || pt.includes('interception');
        }}
        
        function analyzeExplosivePlays(plays, teamName) {{
            const explosivePlays = plays.filter(p => 
                p.explosive_play === true && 
                p.offense?.toLowerCase() === teamName.toLowerCase() &&
                p.play_classification !== 'special_teams'
            );
            const uniqueGames = new Set(explosivePlays.map(p => p.game_id)).size;
            
            // Categorize runs vs passes
            const runs = explosivePlays.filter(p => isRunPlay(p.play_type));
            const passes = explosivePlays.filter(p => isPassPlay(p.play_type));
            
            // Calculate last 3 games stats
            const gameStats = {{}};
            const gameStatsRuns = {{}};
            const gameStatsPasses = {{}};
            explosivePlays.forEach(p => {{
                const gameId = p.game_id;
                if (!gameStats[gameId]) {{
                    gameStats[gameId] = {{
                        game_id: gameId,
                        game_week: p.game_week || 0,
                        count: 0
                    }};
                    gameStatsRuns[gameId] = {{ count: 0 }};
                    gameStatsPasses[gameId] = {{ count: 0 }};
                }}
                gameStats[gameId].count++;
                if (isRunPlay(p.play_type)) {{
                    gameStatsRuns[gameId].count++;
                }} else if (isPassPlay(p.play_type)) {{
                    gameStatsPasses[gameId].count++;
                }}
            }});
            
            // Sort games by week and get last 3
            const sortedGames = Object.values(gameStats).sort((a, b) => a.game_week - b.game_week);
            const last3Games = sortedGames.slice(-3);
            const last3GameIds = new Set(last3Games.map(g => g.game_id));
            const last3Count = last3Games.reduce((sum, g) => sum + g.count, 0);
            const last3Runs = last3Games.reduce((sum, g) => sum + (gameStatsRuns[g.game_id]?.count || 0), 0);
            const last3Passes = last3Games.reduce((sum, g) => sum + (gameStatsPasses[g.game_id]?.count || 0), 0);
            const last3Avg = last3Games.length > 0 ? last3Count / last3Games.length : 0;
            
            return {{
                total_explosive_plays: explosivePlays.length,
                total_runs: runs.length,
                total_passes: passes.length,
                avg_per_game: uniqueGames > 0 ? explosivePlays.length / uniqueGames : 0,
                avg_runs_per_game: uniqueGames > 0 ? runs.length / uniqueGames : 0,
                avg_passes_per_game: uniqueGames > 0 ? passes.length / uniqueGames : 0,
                last_3_games: {{
                    total: last3Count,
                    runs: last3Runs,
                    passes: last3Passes,
                    avg_per_game: last3Avg,
                    games: last3Games.map(g => g.game_id)
                }},
                plays: explosivePlays.map(p => ({{
                    game_week: p.game_week,
                    opponent: p.opponent,
                    period: p.period,
                    clock: p.clock,
                    down: p.down,
                    distance: p.distance,
                    play_type: p.play_type,
                    yards_gained: p.yards_gained,
                    ppa: p.ppa,
                    play_text: p.play_text?.substring(0, 150) || ''
                }}))
            }};
        }}
        
        function analyzePenalties(plays, teamName) {{
            const penaltyPlays = plays.filter(p => 
                p.penalty_type != null && 
                (p.offense?.toLowerCase() === teamName.toLowerCase() || 
                 p.defense?.toLowerCase() === teamName.toLowerCase())
            );
            const accepted = penaltyPlays.filter(p => p.penalty_decision === 'accepted').length;
            const declined = penaltyPlays.filter(p => p.penalty_decision === 'declined').length;
            
            // Use yards_gained field directly for accepted penalties
            let totalYards = 0;
            penaltyPlays.forEach(p => {{
                if (p.penalty_decision === 'accepted') {{
                    const yardsGained = p.yards_gained || 0;
                    // Use absolute value since yards_gained might be negative
                    // Penalties are always negative yardage, so we want the absolute value
                    totalYards += Math.abs(yardsGained);
                }}
            }});
            
            const uniqueGames = new Set(penaltyPlays.map(p => p.game_id)).size;
            return {{
                total_penalties: penaltyPlays.length,
                accepted: accepted,
                declined: declined,
                total_penalty_yards: totalYards,
                avg_per_game: uniqueGames > 0 ? penaltyPlays.length / uniqueGames : 0,
                plays: penaltyPlays.map(p => {{
                    // Use penalty_category for holding penalties, otherwise use penalty_type
                    // This breaks out holding into: offensive_holding, defensive_holding, special_teams_holding
                    let displayPenaltyType = p.penalty_type;
                    if (p.penalty_category && ['offensive_holding', 'defensive_holding', 'special_teams_holding'].includes(p.penalty_category)) {{
                        // Convert snake_case to Title Case: "Offensive Holding", "Defensive Holding", "Special Teams Holding"
                        displayPenaltyType = p.penalty_category.replace(/_/g, ' ').replace(/\\b\\w/g, function(l) {{ return l.toUpperCase(); }});
                    }}
                    return {{
                        game_week: p.game_week,
                        opponent: p.opponent,
                        period: p.period,
                        clock: p.clock,
                        penalty_type: displayPenaltyType,
                        penalty_decision: p.penalty_decision,
                        down: p.down || 0,
                        play_text: p.play_text?.substring(0, 200) || ''
                    }};
                }})
            }};
        }}
        
        function analyze4thDowns(plays, teamName) {{
            const fourthDowns = plays.filter(p => 
                p.down === 4 && 
                p.offense?.toLowerCase() === teamName.toLowerCase() &&
                !p.play_type?.toLowerCase().includes('punt') &&
                !p.play_type?.toLowerCase().includes('field goal') &&
                !p.play_type?.toLowerCase().includes('timeout')
            );
            
            let conversions = 0;
            const playData = fourthDowns.map(p => {{
                const playText = p.play_text?.toLowerCase() || '';
                const converted = playText.includes('1st down') || 
                                playText.includes('first down') || 
                                playText.includes('touchdown') ||
                                (p.yards_gained >= p.distance);
                if (converted) conversions++;
                return {{
                    game_id: p.game_id,
                    game_week: p.game_week,
                    opponent: p.opponent,
                    yard_line: p.yard_line,
                    distance: p.distance,
                    play_type: p.play_type,
                    converted: converted,
                    yards_gained: p.yards_gained,
                    ppa: p.ppa,
                    play_text: p.play_text?.substring(0, 200) || ''
                }};
            }});
            
            // Calculate last 3 games stats
            const gameStats = {{}};
            playData.forEach(p => {{
                const gameId = p.game_id;
                if (!gameStats[gameId]) {{
                    gameStats[gameId] = {{ attempts: 0, conversions: 0, week: p.game_week }};
                }}
                gameStats[gameId].attempts++;
                if (p.converted) gameStats[gameId].conversions++;
            }});
            
            // Sort games by week and get last 3
            const sortedGames = Object.entries(gameStats)
                .map(([id, stats]) => ({{ id: parseInt(id), week: stats.week }}))
                .sort((a, b) => a.week - b.week);
            const last3GameIds = sortedGames.slice(-3).map(g => g.id);
            
            const last3Attempts = playData.filter(p => last3GameIds.includes(p.game_id)).length;
            const last3Conversions = playData.filter(p => last3GameIds.includes(p.game_id) && p.converted).length;
            const last3Rate = last3Attempts > 0 ? (last3Conversions / last3Attempts * 100) : 0;
            
            return {{
                total_attempts: fourthDowns.length,
                total_conversions: conversions,
                conversion_rate: fourthDowns.length > 0 ? (conversions / fourthDowns.length * 100) : 0,
                last_3_games: {{
                    attempts: last3Attempts,
                    conversions: last3Conversions,
                    conversion_rate: last3Rate
                }},
                plays: playData
            }};
        }}
        
        function analyzePostTurnover(plays, teamName) {{
            const turnovers = plays.filter(p => p.turnover === true);
            const postTurnoverPlays = plays.filter(p => p.drive_started_after_turnover === true);
            
            // Group by drive_id to get unique drives that started after turnovers
            const postTurnoverDrives = {{}};
            postTurnoverPlays.forEach(play => {{
                const driveId = play.drive_id;
                if (!postTurnoverDrives[driveId]) {{
                    postTurnoverDrives[driveId] = {{
                        game_id: play.game_id,
                        drive_number: play.drive_number || 0,
                        plays: []
                    }};
                }}
                postTurnoverDrives[driveId].plays.push(play);
            }});
            
            let ourTurnovers = 0;
            let opponentTurnovers = 0;
            let pointsScoredAfterOpponentTO = 0;
            let pointsAllowedAfterOurTO = 0;
            const turnoverAnalysis = [];
            
            // For each drive that started after a turnover, find the turnover that caused it
            Object.keys(postTurnoverDrives).forEach(driveId => {{
                const driveInfo = postTurnoverDrives[driveId];
                const gameId = driveInfo.game_id;
                const driveNumber = driveInfo.drive_number;
                const drivePlays = driveInfo.plays;
                
                // Find the turnover in the previous drive (or same drive if turnover ended the drive)
                let matchingTurnover = null;
                turnovers.forEach(turnover => {{
                    if (turnover.game_id === gameId && 
                        (turnover.drive_number === driveNumber - 1 || 
                         turnover.drive_number === driveNumber)) {{
                        // Prefer the previous drive, but accept same drive if no previous drive turnover
                        if (turnover.drive_number === driveNumber - 1) {{
                            matchingTurnover = turnover;
                            return;
                        }} else if (!matchingTurnover) {{
                            matchingTurnover = turnover;
                        }}
                    }}
                }});
                
                if (!matchingTurnover) return; // Skip if we can't find the matching turnover
                
                const isOurTurnover = matchingTurnover.offense?.toLowerCase() === teamName.toLowerCase();
                if (isOurTurnover) ourTurnovers++;
                else opponentTurnovers++;
                
                // Determine turnover type
                // If it's an interception or fumble, use that; otherwise it's a turnover on downs
                const playType = matchingTurnover.play_type || 'Unknown';
                let turnoverType;
                if (playType.includes('Interception')) {{
                    turnoverType = 'Interception';
                }} else if (playType.includes('Fumble')) {{
                    turnoverType = 'Fumble';
                }} else {{
                    turnoverType = 'Turnover on Downs';
                }}
                
                // Check if the turnover play itself resulted in points (e.g., pick-6, fumble return TD)
                let drivePoints = 0;
                let driveResult = 'No Score';
                let scoringPlayText = '';
                
                if (matchingTurnover.scoring === true) {{
                    if (matchingTurnover.play_type?.includes('Touchdown')) {{
                        drivePoints = 7;
                        driveResult = 'Touchdown';
                        scoringPlayText = matchingTurnover.play_text?.substring(0, 150) || '';
                    }} else if (matchingTurnover.play_type?.includes('Field Goal')) {{
                        drivePoints = 3;
                        driveResult = 'Field Goal';
                        scoringPlayText = matchingTurnover.play_text?.substring(0, 150) || '';
                    }}
                }}
                
                // If turnover didn't score, check the subsequent drive for scoring plays
                if (drivePoints === 0) {{
                    drivePlays.forEach(p => {{
                        if (p.scoring === true) {{
                            if (p.play_type?.includes('Touchdown')) {{
                                drivePoints = 7;
                                driveResult = 'Touchdown';
                                scoringPlayText = p.play_text?.substring(0, 150) || '';
                                return; // Touchdown is highest priority
                            }} else if (p.play_type?.includes('Field Goal') && driveResult === 'No Score') {{
                                drivePoints = 3;
                                driveResult = 'Field Goal';
                                scoringPlayText = p.play_text?.substring(0, 150) || '';
                            }}
                        }}
                    }});
                }}
                
                if (isOurTurnover) {{
                    pointsAllowedAfterOurTO += drivePoints;
                }} else {{
                    pointsScoredAfterOpponentTO += drivePoints;
                }}
                
                // Combine turnover play and scoring play text
                const turnoverText = matchingTurnover.play_text?.substring(0, 150) || '';
                const playDescription = scoringPlayText 
                    ? `TO: ${{turnoverText}} | Score: ${{scoringPlayText}}`
                    : `TO: ${{turnoverText}}`;
                
                turnoverAnalysis.push({{
                    game_week: matchingTurnover.game_week,
                    opponent: matchingTurnover.opponent,
                    turnover_type: turnoverType,
                    is_our_turnover: isOurTurnover,
                    drive_result: driveResult,
                    points_scored: isOurTurnover ? 0 : drivePoints,
                    points_allowed: isOurTurnover ? drivePoints : 0,
                    play_text: playDescription
                }});
            }});
            
            const netPoints = pointsScoredAfterOpponentTO - pointsAllowedAfterOurTO;
            
            // Calculate last 3 games
            const sortedWeeks = [...new Set(turnoverAnalysis.map(t => t.game_week || 0))].sort((a, b) => a - b);
            const last3Weeks = sortedWeeks.slice(-3);
            const last3Turnovers = turnoverAnalysis.filter(t => last3Weeks.includes(t.game_week || 0));
            
            const last3PointsScored = last3Turnovers
                .filter(t => !t.is_our_turnover)
                .reduce((sum, t) => sum + (t.points_scored || 0), 0);
            const last3PointsAllowed = last3Turnovers
                .filter(t => t.is_our_turnover)
                .reduce((sum, t) => sum + (t.points_allowed || 0), 0);
            const last3NetPoints = last3PointsScored - last3PointsAllowed;
            
            return {{
                total_turnovers: turnovers.length,
                our_turnovers: ourTurnovers,
                opponent_turnovers: opponentTurnovers,
                points_scored_after_opponent_turnovers: pointsScoredAfterOpponentTO,
                points_allowed_after_our_turnovers: pointsAllowedAfterOurTO,
                net_points_after_turnovers: netPoints,
                last_3_games: {{
                    points_scored: last3PointsScored,
                    points_allowed: last3PointsAllowed,
                    net_points: last3NetPoints
                }},
                turnover_analysis: turnoverAnalysis
            }};
        }}
        
        function analyzeRedZone(plays, teamName) {{
            // Filter to ONLY the primary team's offensive plays (but include field goals even though they're special teams)
            // This ensures we only analyze the primary team's performance, not opponent plays
            let offensivePlays = plays.filter(p => 
                p.offense?.toLowerCase() === teamName.toLowerCase() &&
                (p.play_classification !== 'special_teams' ||
                 (p.play_type || '').toLowerCase().includes('field goal'))
            );
            
            // Double-check: ensure no opponent plays slip through
            offensivePlays = offensivePlays.filter(p => p.offense?.toLowerCase() === teamName.toLowerCase());
            
            const tightRedZonePlays = offensivePlays.filter(p => (p.yards_to_goal || 100) <= 10);
            const redZonePlays = offensivePlays.filter(p => (p.yards_to_goal || 100) <= 20);
            const greenZonePlays = offensivePlays.filter(p => (p.yards_to_goal || 100) <= 30);
            
            function analyzeZone(zonePlays) {{
                if (zonePlays.length === 0) {{
                    return {{
                        total_plays: 0,
                        touchdowns: 0,
                        td_scoring_rate: 0,
                        turnovers: 0,
                        avg_ppa: 0,
                        conversions_3rd: {{ attempts: 0, conversions: 0, rate: 0 }},
                        plays: []
                    }};
                }}
                
                const touchdowns = zonePlays.filter(p => p.play_type?.toLowerCase().includes('touchdown')).length;
                const tdScoringRate = zonePlays.length > 0 ? (touchdowns / zonePlays.length * 100) : 0;
                
                // Count turnovers in the zone
                const turnovers = zonePlays.filter(p => p.turnover === true).length;
                
                const ppas = zonePlays.filter(p => p.ppa != null).map(p => parseFloat(p.ppa));
                const avgPpa = ppas.length > 0 ? (ppas.reduce((a, b) => a + b, 0) / ppas.length) : 0;
                
                const thirdDowns = zonePlays.filter(p => p.down === 3);
                const thirdConversions = thirdDowns.filter(p => {{
                    const pt = (p.play_text || '').toLowerCase();
                    return pt.includes('1st down') || pt.includes('first down') || (p.yards_gained || 0) >= (p.distance || 0);
                }}).length;
                
                return {{
                    total_plays: zonePlays.length,
                    touchdowns: touchdowns,
                    td_scoring_rate: tdScoringRate,
                    turnovers: turnovers,
                    avg_ppa: avgPpa,
                    conversions_3rd: {{
                        attempts: thirdDowns.length,
                        conversions: thirdConversions,
                        rate: thirdDowns.length > 0 ? (thirdConversions / thirdDowns.length * 100) : 0
                    }},
                    plays: zonePlays.map(p => ({{
                        game_week: p.game_week,
                        opponent: p.opponent,
                        period: p.period,
                        clock: p.clock,
                        down: p.down,
                        distance: p.distance,
                        yards_to_goal: p.yards_to_goal,
                        play_type: p.play_type,
                        yards_gained: p.yards_gained,
                        scoring: p.scoring || false,
                        explosive: p.explosive_play || false,
                        ppa: p.ppa,
                        play_text: p.play_text?.substring(0, 200) || ''
                    }}))
                }};
            }}
            
            return {{
                tight_red_zone: analyzeZone(tightRedZonePlays),
                red_zone: analyzeZone(redZonePlays),
                green_zone: analyzeZone(greenZonePlays)
            }};
        }}
        
        function analyzeSpecialTeams(plays, teamName) {{
            const stPlays = plays.filter(p => p.play_classification === 'special_teams');
            
            // Separate by offense (our special teams) vs defense (opponent special teams)
            // For returns, the returning team is on "defense", not "offense"
            const ourSTPlays = [];
            const opponentSTPlays = [];
            
            stPlays.forEach(p => {{
                const playType = (p.play_type || '').toLowerCase();
                const playText = (p.play_text || '').toLowerCase();
                
                // Check if it's a return play (kickoff return or punt return)
                const isReturn = (
                    (playType.includes('return') || playText.includes('return')) &&
                    (playType.includes('kickoff') || playText.includes('kickoff') ||
                     playType.includes('punt') || playText.includes('punt'))
                );
                
                if (isReturn) {{
                    // For returns, check defense field (returning team)
                    if (p.defense?.toLowerCase() === teamName.toLowerCase()) {{
                        ourSTPlays.push(p);
                    }} else {{
                        opponentSTPlays.push(p);
                    }}
                }} else {{
                    // For other ST plays (kicks, punts), check offense field
                    if (p.offense?.toLowerCase() === teamName.toLowerCase()) {{
                        ourSTPlays.push(p);
                    }} else {{
                        opponentSTPlays.push(p);
                    }}
                }}
            }});
            
            // Check if special teams play is explosive: 35+ kick return, 20+ punt return
            function isSpecialTeamsExplosive(play) {{
                const pt = (play.play_type || '').toLowerCase();
                const ptxt = (play.play_text || '').toLowerCase();
                
                // For returns, we need to parse the return yards from the play text
                // because yards_gained might include the kick/punt distance
                function parseReturnYards(playText) {{
                    if (!playText) return 0;
                    
                    // Look for patterns like "returns for X yds" or "returns for no gain"
                    const returnMatch = playText.match(/return[s]? for (?:no gain|(\d+) (?:yd|yard))/i);
                    if (returnMatch) {{
                        if (returnMatch[1]) {{
                            return parseInt(returnMatch[1], 10);
                        }} else {{
                            return 0; // "no gain"
                        }}
                    }}
                    
                    // Fallback: if we can't parse, return 0 to be safe
                    return 0;
                }}
                
                // Kick return: 35+ yards
                if ((pt.includes('kickoff') || ptxt.includes('kickoff')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    const returnYards = parseReturnYards(play.play_text);
                    return returnYards >= 35;
                }}
                
                // Punt return: 20+ yards
                if ((pt.includes('punt') || ptxt.includes('punt')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    const returnYards = parseReturnYards(play.play_text);
                    return returnYards >= 20;
                }}
                
                return false;
            }}
            
            const explosivePlays = ourSTPlays.filter(p => isSpecialTeamsExplosive(p));
            const explosiveReturnsAllowed = opponentSTPlays.filter(p => isSpecialTeamsExplosive(p));
            
            // Count touchdowns on special teams
            // Important: For return TDs, the "offense" field is the team that punted/kicked,
            // not the team that scored. We need to check all ST plays and determine who scored.
            const tdsScored = stPlays.filter(p => {{
                const scoring = p.scoring === true;
                if (!scoring) return false;
                
                const playType = (p.play_type || '').toLowerCase();
                const playText = (p.play_text || '').toLowerCase();
                const hasTD = playType.includes('touchdown') || playText.includes('touchdown') || playText.includes(' for a td');
                
                if (!hasTD) return false;
                
                // Check if this is a return TD (punt return or kickoff return)
                const isReturnTD = (playType.includes('return') || playText.includes('return')) &&
                                  (playType.includes('kickoff') || playText.includes('kickoff') ||
                                   playType.includes('punt') || playText.includes('punt'));
                
                if (isReturnTD) {{
                    // For return TDs: if opponent is on offense (they punted/kicked), 
                    // then Washington scored on the return
                    const isOpponentOffense = p.offense?.toLowerCase() !== teamName.toLowerCase();
                    return isOpponentOffense;  // Opponent kicked, Washington returned for TD
                }} else {{
                    // For non-return TDs (like blocked punts run back), Washington on offense = their TD
                    return p.offense?.toLowerCase() === teamName.toLowerCase();
                }}
            }}).length;
            
            const tdsAllowed = stPlays.filter(p => {{
                const scoring = p.scoring === true;
                if (!scoring) return false;
                
                const playType = (p.play_type || '').toLowerCase();
                const playText = (p.play_text || '').toLowerCase();
                const hasTD = playType.includes('touchdown') || playText.includes('touchdown') || playText.includes(' for a td');
                
                if (!hasTD) return false;
                
                // Check if this is a return TD
                const isReturnTD = (playType.includes('return') || playText.includes('return')) &&
                                  (playType.includes('kickoff') || playText.includes('kickoff') ||
                                   playType.includes('punt') || playText.includes('punt'));
                
                if (isReturnTD) {{
                    // For return TDs: if Washington is on offense (they punted/kicked),
                    // then opponent scored on the return (Washington allowed it)
                    return p.offense?.toLowerCase() === teamName.toLowerCase();
                }} else {{
                    // For non-return TDs, opponent on offense = their TD
                    return p.offense?.toLowerCase() !== teamName.toLowerCase();
                }}
            }}).length;
            
            return {{
                total_explosive_plays: explosivePlays.length,
                explosive_returns_allowed: explosiveReturnsAllowed.length,
                tds_scored: tdsScored,
                tds_allowed: tdsAllowed,
                plays: stPlays.map(p => {{
                    const explosive = isSpecialTeamsExplosive(p);
                    const isOur = p.offense?.toLowerCase() === teamName.toLowerCase();
                    return {{
                        game_week: p.game_week,
                        opponent: p.opponent,
                        play_type: p.play_type,
                        is_our: isOur,
                        explosive: explosive,
                        turnover: p.turnover || false,
                        yards_gained: p.yards_gained,
                        play_text: p.play_text?.substring(0, 200) || ''
                    }};
                }})
            }};
        }}
        
        function applyFilters() {{
            const filters = getFilters();
            
            // Filter raw plays for both teams
            const team1Filtered = filterPlays(team1Plays, filters);
            const team2Filtered = filterPlays(team2Plays, filters);
            
            // Debug: Log filtering results
            if (filters.conference_only || filters.power4_only) {{
                console.log('Filter applied:', filters);
                console.log('Team1 plays before filter:', team1Plays.length);
                console.log('Team1 plays after filter:', team1Filtered.length);
                console.log('Team2 plays before filter:', team2Plays.length);
                console.log('Team2 plays after filter:', team2Filtered.length);
                if (team1Filtered.length > 0) {{
                    console.log('Sample Team1 play:', team1Filtered[0]);
                }}
                if (team2Filtered.length > 0) {{
                    console.log('Sample Team2 play:', team2Filtered[0]);
                }}
            }}
            
            // Re-analyze with filtered data
            const team1FilteredData = {{
                middle8: analyzeMiddleEight(team1Filtered, team1Name),
                explosive: analyzeExplosivePlays(team1Filtered, team1Name),
                penalties: analyzePenalties(team1Filtered, team1Name),
                '4thdowns': analyze4thDowns(team1Filtered, team1Name),
                turnover: analyzePostTurnover(team1Filtered, team1Name),
                specialteams: analyzeSpecialTeams(team1Filtered, team1Name),
                redzone: analyzeRedZone(team1Filtered, team1Name)
            }};
            
            const team2FilteredData = {{
                middle8: analyzeMiddleEight(team2Filtered, team2Name),
                explosive: analyzeExplosivePlays(team2Filtered, team2Name),
                penalties: analyzePenalties(team2Filtered, team2Name),
                '4thdowns': analyze4thDowns(team2Filtered, team2Name),
                turnover: analyzePostTurnover(team2Filtered, team2Name),
                specialteams: analyzeSpecialTeams(team2Filtered, team2Name),
                redzone: analyzeRedZone(team2Filtered, team2Name)
            }};
            
            // Debug: Log analysis results
            if (filters.conference_only || filters.power4_only) {{
                console.log('Team1 Middle8 result:', team1FilteredData.middle8);
                console.log('Team1 Explosive result:', team1FilteredData.explosive);
                console.log('Team2 Middle8 result:', team2FilteredData.middle8);
                console.log('Team2 Explosive result:', team2FilteredData.explosive);
            }}
            
            // Store filtered plays for trend calculations
            team1FilteredData.middle8._filtered_plays = team1Filtered;
            team1FilteredData.explosive._filtered_plays = team1Filtered;
            team1FilteredData.penalties._filtered_plays = team1Filtered;
            team1FilteredData['4thdowns']._filtered_plays = team1Filtered;
            team1FilteredData.turnover._filtered_plays = team1Filtered;
            team1FilteredData.specialteams._filtered_plays = team1Filtered;
            team1FilteredData.redzone._filtered_plays = team1Filtered;
            
            team2FilteredData.middle8._filtered_plays = team2Filtered;
            team2FilteredData.explosive._filtered_plays = team2Filtered;
            team2FilteredData.penalties._filtered_plays = team2Filtered;
            team2FilteredData['4thdowns']._filtered_plays = team2Filtered;
            team2FilteredData.turnover._filtered_plays = team2Filtered;
            team2FilteredData.specialteams._filtered_plays = team2Filtered;
            team2FilteredData.redzone._filtered_plays = team2Filtered;
            
            // Filter SIS situational receiving data (always use original data)
            const team1SituationalFiltered = filterSituationalReceiving(originalAllData[team1Key].situational, filters);
            const team2SituationalFiltered = filterSituationalReceiving(originalAllData[team2Key].situational, filters);
            
            // Filter SIS deep target data (always use original data)
            const team1DeepTargetsFiltered = filterDeepTargets(originalAllData[team1Key].deep_targets, filters);
            const team2DeepTargetsFiltered = filterDeepTargets(originalAllData[team2Key].deep_targets, filters);
            
            // Temporarily replace allData with filtered data
            allData[team1Key] = team1FilteredData;
            allData[team2Key] = team2FilteredData;
            
            // Add filtered SIS data
            if (team1SituationalFiltered) {{
                allData[team1Key].situational_filtered = team1SituationalFiltered;
            }}
            if (team2SituationalFiltered) {{
                allData[team2Key].situational_filtered = team2SituationalFiltered;
            }}
            if (team1DeepTargetsFiltered) {{
                allData[team1Key].deep_targets_filtered = team1DeepTargetsFiltered;
            }}
            if (team2DeepTargetsFiltered) {{
                allData[team2Key].deep_targets_filtered = team2DeepTargetsFiltered;
            }}
            
            // Re-populate all sections with filtered data
            populateAllSections();
            
            // Restore original data (for future filter changes)
            allData[team1Key] = JSON.parse(JSON.stringify(originalAllData[team1Key]));
            allData[team2Key] = JSON.parse(JSON.stringify(originalAllData[team2Key]));
        }}
        
        function resetFilters() {{
            // Reset filter dropdowns
            document.getElementById('conferenceFilter').selectedIndex = 0;
            document.getElementById('timePeriodFilter').selectedIndex = 0;
            
            // Restore original data
            allData[team1Key] = JSON.parse(JSON.stringify(originalAllData[team1Key]));
            allData[team2Key] = JSON.parse(JSON.stringify(originalAllData[team2Key]));
            
            // Re-populate with original (unfiltered) data
            populateAllSections();
        }}
        
        // Update active navigation link on scroll
        function updateActiveNavLink() {{
            const sections = document.querySelectorAll('.section[id]');
            const navLinks = document.querySelectorAll('.nav-links a');
            
            let currentSection = '';
            const scrollPosition = window.scrollY + 100;
            
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                
                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {{
                    currentSection = section.getAttribute('id');
                }}
            }});
            
            navLinks.forEach(link => {{
                link.classList.remove('active');
                const href = link.getAttribute('href');
                if (href === `#${{currentSection}}`) {{
                    link.classList.add('active');
                }}
            }});
        }}
        
        // Initialize on load
        window.addEventListener('DOMContentLoaded', function() {{
            initializeFilters();
            populateAllSections();
            updateActiveNavLink();
            
            // Smooth scroll for navigation links
            document.querySelectorAll('.nav-links a').forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {{
                        const offset = 80;
                        const targetPosition = targetElement.offsetTop - offset;
                        window.scrollTo({{
                            top: targetPosition,
                            behavior: 'smooth'
                        }});
                    }}
                }});
            }});
            
            // Update active link on scroll
            window.addEventListener('scroll', updateActiveNavLink);
        }});
    </script>
            </div> <!-- End container -->
        </div> <!-- End content-area -->
    </div> <!-- End main-wrapper -->
</body>
</html>"""
    
    # Write to file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML app generated: {output_path.absolute()}")
    print(f"  - Middle 8 Analysis: Complete")
    print(f"  - Explosive Plays: Complete")
    print(f"  - Penalties: Complete")
    print(f"  - 4th Downs: Complete")
    print(f"  - Post Turnover: Complete")
    print(f"  - Special Teams: Complete")
    print(f"  - Red Zone / Green Zone: Complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate advanced team analysis HTML app')
    parser.add_argument('--team1', type=str, default='Washington', 
                       help='Name of first team (default: Washington)')
    parser.add_argument('--team2', type=str, default='Wisconsin',
                       help='Name of second team (default: Wisconsin)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output HTML file path (default: auto-generated from team names)')
    parser.add_argument('--data-dir', type=str, default='advanced_reports_yogi',
                       help='Directory containing play-by-play data (default: advanced_reports_yogi)')
    parser.add_argument('--sis-file', type=str, default=None,
                       help='Path to SIS data JSON file (default: auto-generated from team names)')
    parser.add_argument('--year', type=int, default=2025,
                       help='Season year for SIS data file naming (default: 2025)')
    
    args = parser.parse_args()
    
    generate_html_app(
        team_name1=args.team1,
        team_name2=args.team2,
        output_file=args.output,
        data_dir=args.data_dir,
        sis_data_file=args.sis_file,
        year=args.year
    )

