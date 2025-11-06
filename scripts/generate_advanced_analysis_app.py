#!/usr/bin/env python3
"""
Generate comprehensive HTML analysis app comparing Washington and Wisconsin
"""

import json
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


def generate_html_app(output_file: str = "advanced_analysis_app.html", data_dir: str = "advanced_reports_yogi"):
    """
    Generate the comprehensive HTML analysis app with all analyses pre-computed
    """
    
    # Load data for both teams
    print("Loading team data...")
    washington_data = load_team_data("Washington", data_dir)
    wisconsin_data = load_team_data("Wisconsin", data_dir)
    
    print("Running analyses for Washington...")
    wash_middle8 = analyze_middle_eight(washington_data['all_plays'], "Washington")
    wash_explosive = analyze_explosive_plays(washington_data['all_plays'], "Washington")
    wash_penalties = analyze_penalties(washington_data['all_plays'], "Washington")
    wash_4th = analyze_4th_downs(washington_data['all_plays'], "Washington")
    wash_turnover = analyze_post_turnover(washington_data['all_plays'], "Washington")
    wash_st = analyze_special_teams(washington_data['all_plays'], "Washington")
    wash_redzone = analyze_red_zone(washington_data['all_plays'], "Washington")
    
    print("Running analyses for Wisconsin...")
    wisc_middle8 = analyze_middle_eight(wisconsin_data['all_plays'], "Wisconsin")
    wisc_explosive = analyze_explosive_plays(wisconsin_data['all_plays'], "Wisconsin")
    wisc_penalties = analyze_penalties(wisconsin_data['all_plays'], "Wisconsin")
    wisc_4th = analyze_4th_downs(wisconsin_data['all_plays'], "Wisconsin")
    wisc_turnover = analyze_post_turnover(wisconsin_data['all_plays'], "Wisconsin")
    wisc_st = analyze_special_teams(wisconsin_data['all_plays'], "Wisconsin")
    wisc_redzone = analyze_red_zone(wisconsin_data['all_plays'], "Wisconsin")
    
    # Get game lists for filtering
    washington_games = get_game_list(washington_data)
    wisconsin_games = get_game_list(wisconsin_data)
    
    # Load SIS data and analyze situational receiving stats
    print("Loading SIS data...")
    try:
        sis_data = load_sis_data(f"{data_dir}/sis-data/washington_wisconsin_analysis_2025.json")
        wash_situational = analyze_situational_receiving(sis_data, "Washington", washington_games)
        wisc_situational = analyze_situational_receiving(sis_data, "Wisconsin", wisconsin_games)
        print("SIS situational receiving data loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load SIS data: {e}")
        wash_situational = {
            '3rd_down': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'redzone': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'game_mapping': {}
        }
        wisc_situational = {
            '3rd_down': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'redzone': {'total': {}, 'by_week': {}, 'last_3_games': {}, 'players': []},
            'game_mapping': {}
        }
    
    # Serialize all analysis data for JavaScript
    all_data_json = json.dumps({
        'washington': {
            'middle8': wash_middle8,
            'explosive': wash_explosive,
            'penalties': wash_penalties,
            '4thdowns': wash_4th,
            'turnover': wash_turnover,
            'specialteams': wash_st,
            'redzone': wash_redzone,
            'situational': wash_situational,
            'games': washington_games,
            'all_plays': washington_data['all_plays']
        },
        'wisconsin': {
            'middle8': wisc_middle8,
            'explosive': wisc_explosive,
            'penalties': wisc_penalties,
            '4thdowns': wisc_4th,
            'turnover': wisc_turnover,
            'specialteams': wisc_st,
            'redzone': wisc_redzone,
            'situational': wisc_situational,
            'games': wisconsin_games,
            'all_plays': wisconsin_data['all_plays']
        }
    })
    
    # Serialize for backwards compatibility
    washington_plays_json = json.dumps(washington_data['all_plays'])
    wisconsin_plays_json = json.dumps(wisconsin_data['all_plays'])
    washington_games_json = json.dumps(washington_games)
    wisconsin_games_json = json.dumps(wisconsin_games)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Team Analysis - Washington vs Wisconsin</title>
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
        
        .team-section.washington {{
            border-left-color: #4a90e2;
        }}
        
        .team-section.wisconsin {{
            border-left-color: #c41e3a;
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
        
        .team-header-browser.washington {{
            background: #4a90e2;
        }}
        
        .team-header-browser.wisconsin {{
            background: #c41e3a;
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
            min-height: 100vh;
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
        
        /* Content Area */
        .content-area {{
            margin-left: 240px;
            width: calc(100% - 240px);
            padding: 20px 40px;
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
                <li><a href="#allPlaysSection">All Plays Browser</a></li>
            </ul>
        </nav>
        
        <!-- Main Content Area -->
        <div class="content-area">
            <div class="container">
                <header>
                    <h1>Advanced Team Analysis</h1>
                    <p>Washington vs Wisconsin - Comprehensive Play-by-Play Analysis</p>
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
                    <li><strong>Performance Gap:</strong> Both teams show decreased performance during Middle 8. Washington drops from 0.363 PPA (regular) to 0.214 PPA (Middle 8), while Wisconsin drops from 0.074 PPA to -0.146 PPA (negative).</li>
                    <li><strong>Explosive Rate:</strong> Washington's explosive play rate drops from 9.6% (regular) to 5.2% (Middle 8), while Wisconsin maintains ~4% in both periods.</li>
                </ul>
            </div>
            <div id="middleEightSummary"></div>
            <div class="chart-container">
                <canvas id="middleEightChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="middleEightTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
            <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
                    <li><strong>Drive Conversion:</strong> Washington converts explosive plays into scores at 76.7% rate vs Wisconsin's 53.7% - a 23-point advantage showing superior finishing ability.</li>
                    <li><strong>Quarterly Distribution:</strong> Washington maintains more consistent explosive rates (6.6%-10.9% across quarters) while Wisconsin's Q2 drops to just 2.2% (lowest for either team).</li>
                    <li><strong>2nd & Long Efficiency:</strong> Washington excels on difficult 2nd downs - 0.805 PPA on 2nd & 9 vs Wisconsin's -0.481 PPA, a 1.29 PPA difference.</li>
                </ul>
            </div>
            <div id="explosivePlaysSummary"></div>
            <div class="chart-container">
                <canvas id="explosivePlaysChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="explosivePlaysTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
            <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
                    <li><strong>Penalty-Explosive Correlation:</strong> 53.1% of Washington's penalty drives also feature explosive plays (vs 31.6% for Wisconsin), suggesting Washington may be more aggressive/chaotic on penalty drives.</li>
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
            
            <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
            <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
                    <li><strong>4th & 1 Dominance:</strong> Washington shows exceptional efficiency on 4th & 1 with 1.865 PPA (6 plays) vs Wisconsin's 0.162 PPA (4 plays) - a massive 1.70 PPA advantage in critical short-yardage situations.</li>
                    <li><strong>Situational Efficiency:</strong> Washington performs significantly better across multiple down/distance situations, particularly on 3rd & short (0.901 PPA on 3rd & 4 vs Wisconsin's -0.277).</li>
                </ul>
            </div>
            <div id="fourthDownSummary"></div>
            <div class="chart-container">
                <canvas id="fourthDownChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="fourthDownTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
            <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
                    <li><strong>1st Quarter Turnover Problem:</strong> Wisconsin has a significant early-game issue - 10 turnovers in Q1 (34% of all turnovers) vs Washington's 1 Q1 turnover (5%). This suggests Wisconsin struggles with game-opening script execution.</li>
                    <li><strong>Field Position:</strong> Wisconsin turns the ball over more frequently in their own territory (19 of 29 turnovers) compared to Washington (12 of 22), indicating deeper protection issues.</li>
                </ul>
            </div>
            <div id="postTurnoverSummary"></div>
            <div class="chart-container">
                <canvas id="postTurnoverChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="postTurnoverTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
            <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
            <div class="notice-banner">
                Note: Add blocks
            </div>
            <div class="insight-box">
                <h4>Key Insights:</h4>
                <ul>
                    <li><strong>Red Zone Efficiency:</strong> Despite lower overall efficiency, Wisconsin shows better red zone performance (0.531 PPA on 30 plays) vs Washington (0.341 PPA on 46 plays), suggesting better play-calling in compressed space.</li>
                    <li><strong>Own Territory Struggles:</strong> Wisconsin struggles significantly in their own 21-40 yard line zone (-0.428 PPA on 79 plays) vs Washington's slight negative (-0.014 PPA on 115 plays).</li>
                </ul>
            </div>
            <div id="specialTeamsSummary"></div>
            <div class="chart-container">
                <canvas id="specialTeamsTrendChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
            <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
                <p><strong>Definition:</strong> The Red Zone (20 yards to goal and in) and Green Zone (30 yards to goal and in) are critical scoring areas. Success in these zones is measured by scoring rate (TDs and FGs), conversion rates on 3rd/4th down, and PPA. Teams that consistently score in the red zone win more games, while teams that struggle often settle for field goals or turn the ball over.</p>
            </div>
            <div id="redZoneSummary"></div>
            <div class="chart-container">
                <canvas id="redZoneChart"></canvas>
            </div>
            <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
            <h4 style="color: #4a90e2; margin-top: 20px;">Green Zone Plays</h4>
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
            <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
            <h4 style="color: #c41e3a; margin-top: 20px;">Green Zone Plays</h4>
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
                <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
                <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
                <h3 style="margin-top: 30px; color: #4a90e2;">Washington</h3>
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
                <h3 style="margin-top: 30px; color: #c41e3a;">Wisconsin</h3>
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
        const allData = {all_data_json};
        const washingtonPlays = {washington_plays_json};
        const wisconsinPlays = {wisconsin_plays_json};
        const washingtonGames = {washington_games_json};
        const wisconsinGames = {wisconsin_games_json};
        
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
        
        // Create master game mapping from ALL games (both teams) - ensures consistent Game 1-9
        const masterGameMapping = (function() {{
            const allGameIds = new Set();
            washingtonPlays.forEach(p => {{ if (p.game_id) allGameIds.add(p.game_id); }});
            wisconsinPlays.forEach(p => {{ if (p.game_id) allGameIds.add(p.game_id); }});
            
            // Get week for each game and sort by week
            const allGames = Array.from(allGameIds).map(gameId => {{
                const play = [...washingtonPlays, ...wisconsinPlays].find(p => p.game_id === gameId);
                return {{ gameId, week: play?.game_week || 0 }};
            }}).sort((a, b) => a.week - b.week);
            
            // Create mapping: gameId -> sequential game number (1-9)
            const gameIdToGameNum = {{}};
            const gameLabels = [];
            allGames.forEach((game, idx) => {{
                gameIdToGameNum[game.gameId] = idx + 1;
                gameLabels.push(`Game ${{idx + 1}}`);
            }});
            
            return {{ gameIdToGameNum, allGames, gameLabels }};
        }})();
        
        // Helper function to get master game mapping (for backward compatibility)
        function createGameIdToGameNumberMapping(plays) {{
            // Always return the master mapping, ignoring the plays parameter
            return masterGameMapping.gameIdToGameNum;
        }}
        
        // Helper function to calculate trends by game (sequential game numbers)
        // Always includes all games (1-9) even if they have 0 values
        function calculateTrendsByWeek(plays, teamName, metricFn) {{
            const byGame = {{}};
            plays.forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                if (!byGame[gameId]) {{
                    byGame[gameId] = {{ plays: [] }};
                }}
                byGame[gameId].plays.push(play);
            }});
            
            // Use master mapping to ensure all games are included
            const gameIdToGameNum = masterGameMapping.gameIdToGameNum;
            
            // Create array with all games (1-9), filling in 0 for games with no data
            const values = masterGameMapping.allGames.map(game => {{
                const gamePlays = byGame[game.gameId]?.plays || [];
                return metricFn(gamePlays, teamName);
            }});
            
            return {{ weeks: masterGameMapping.gameLabels, values: values }};
        }}
        
        function calculateTurnoverTrends(plays, teamName) {{
            const byGame = {{}};
            plays.forEach(play => {{
                if (play.turnover === true) {{
                    const gameId = play.game_id;
                    if (!gameId) return;
                    if (!byGame[gameId]) {{
                        byGame[gameId] = {{ ourTO: 0, oppTO: 0 }};
                    }}
                    const isOur = play.offense?.toLowerCase() === teamName.toLowerCase();
                    if (isOur) {{
                        byGame[gameId].ourTO++;
                    }} else {{
                        byGame[gameId].oppTO++;
                    }}
                }}
            }});
            
            // Use master mapping to ensure all games are included
            const ourTurnovers = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.ourTO || 0
            );
            const oppTurnovers = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.oppTO || 0
            );
            
            return {{
                weeks: masterGameMapping.gameLabels,
                ourTurnovers: ourTurnovers,
                oppTurnovers: oppTurnovers
            }};
        }}
        
        function calculateNetPointsByWeek(plays, teamName) {{
            const turnovers = plays.filter(p => p.turnover === true);
            const postTurnoverPlays = plays.filter(p => p.drive_started_after_turnover === true);
            
            const byGame = {{}};
            
            turnovers.forEach(turnover => {{
                const gameId = turnover.game_id;
                if (!gameId) return;
                if (!byGame[gameId]) {{
                    byGame[gameId] = {{ pointsScored: 0, pointsAllowed: 0 }};
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
                    byGame[gameId].pointsAllowed += drivePoints;
                }} else {{
                    byGame[gameId].pointsScored += drivePoints;
                }}
            }});
            
            // Use master mapping to ensure all games are included
            const netPoints = masterGameMapping.allGames.map(game => {{
                const gameData = byGame[game.gameId] || {{ pointsScored: 0, pointsAllowed: 0 }};
                return gameData.pointsScored - gameData.pointsAllowed;
            }});
            
            return {{
                weeks: masterGameMapping.gameLabels,
                netPoints: netPoints
            }};
        }}
        
        function calculateMiddle8Trends(plays, teamName) {{
            const byGame = {{}};
            plays.filter(p => p.middle_eight === true).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                if (!byGame[gameId]) {{
                    byGame[gameId] = {{ scored: 0, allowed: 0 }};
                }}
                if (play.scoring === true) {{
                    const points = play.play_type?.includes('Touchdown') ? 7 : (play.play_type?.includes('Field Goal') ? 3 : 0);
                    const isOur = play.offense?.toLowerCase() === teamName.toLowerCase();
                    if (isOur) {{
                        byGame[gameId].scored += points;
                    }} else {{
                        byGame[gameId].allowed += points;
                    }}
                }}
            }});
            
            // Use master mapping to ensure all games are included
            const scored = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.scored || 0
            );
            const allowed = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.allowed || 0
            );
            const net = masterGameMapping.allGames.map(game => {{
                const gameData = byGame[game.gameId] || {{ scored: 0, allowed: 0 }};
                return gameData.scored - gameData.allowed;
            }});
            
            return {{
                weeks: masterGameMapping.gameLabels,
                scored: scored,
                allowed: allowed,
                net: net
            }};
        }}
        
        function calculateExplosiveTrends(plays, teamName) {{
            const byGame = {{}};
            plays.filter(p => 
                p.explosive_play === true && 
                p.play_classification !== 'special_teams'
            ).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                if (!byGame[gameId]) {{
                    byGame[gameId] = {{ ours: 0, allowed: 0 }};
                }}
                const isOurs = play.offense?.toLowerCase() === teamName.toLowerCase();
                if (isOurs) {{
                    byGame[gameId].ours++;
                }} else {{
                    byGame[gameId].allowed++;
                }}
            }});
            
            // Use master mapping to ensure all games are included
            const ours = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.ours || 0
            );
            const allowed = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.allowed || 0
            );
            
            return {{
                weeks: masterGameMapping.gameLabels,
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
                const yards = play.yards_gained || 0;
                
                // Kick return: 35+ yards
                if ((pt.includes('kickoff') || ptxt.includes('kickoff')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    return yards >= 35;
                }}
                
                // Punt return: 20+ yards
                if ((pt.includes('punt') || ptxt.includes('punt')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    return yards >= 20;
                }}
                
                return false;
            }}
            
            const byGame = {{}};
            plays.filter(p => isSpecialTeamsExplosive(p)).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                if (!byGame[gameId]) {{
                    byGame[gameId] = {{ ours: 0, allowed: 0 }};
                }}
                const isOurs = play.offense?.toLowerCase() === teamName.toLowerCase();
                if (isOurs) {{
                    byGame[gameId].ours++;
                }} else {{
                    byGame[gameId].allowed++;
                }}
            }});
            
            // Use master mapping to ensure all games are included
            const ours = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.ours || 0
            );
            const allowed = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.allowed || 0
            );
            
            return {{
                weeks: masterGameMapping.gameLabels,
                ours: ours,
                allowed: allowed
            }};
        }}
        
        function calculatePenaltyTrends(plays, teamName) {{
            const byGame = {{}};
            plays.filter(p => p.penalty_type != null && (p.offense?.toLowerCase() === teamName.toLowerCase() || p.defense?.toLowerCase() === teamName.toLowerCase())).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                if (!byGame[gameId]) {{
                    byGame[gameId] = 0;
                }}
                byGame[gameId]++;
            }});
            
            // Use master mapping to ensure all games are included
            const values = masterGameMapping.allGames.map(game => 
                byGame[game.gameId] || 0
            );
            
            return {{
                weeks: masterGameMapping.gameLabels,
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
                
                const week = play.game_week || 0;
                const playText = (play.play_text || '').toLowerCase();
                
                // Extract penalty yards from text (not from yards_gained which includes return yards)
                const yards = extractPenaltyYards(play.play_text || '', play.penalty_type);
                
                // Determine which team committed the penalty by checking play text
                // Look for patterns like "Washington Penalty", "PENALTY WASH", "PENALTY CSU", etc.
                let teamCommittedPenalty = false;
                
                // Check for team name in penalty context - look for patterns:
                // "PENALTY WASH", "PENALTY Washington", "Washington Penalty", "WASH Penalty"
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
            
            // Get all unique weeks
            const allWeeks = new Set([...Object.keys(teamYardsByWeek), ...Object.keys(opponentYardsByWeek)]);
            const weeks = Array.from(allWeeks).map(w => parseInt(w)).sort((a, b) => a - b);
            
            // Calculate net (opponent yards - team yards, so positive is good for team)
            const netYards = weeks.map(week => {{
                const teamYards = teamYardsByWeek[week] || 0;
                const oppYards = opponentYardsByWeek[week] || 0;
                return oppYards - teamYards; // Positive = opponent had more (good), negative = team had more (bad)
            }});
            
            // Use master mapping to ensure all games are included
            const values = masterGameMapping.allGames.map(game => {{
                const teamYards = teamYardsByWeek[game.gameId] || 0;
                const oppYards = opponentYardsByWeek[game.gameId] || 0;
                return oppYards - teamYards; // Positive = opponent had more (good), negative = team had more (bad)
            }});
            
            return {{
                weeks: masterGameMapping.gameLabels,
                values: values
            }};
        }}
        
        function calculate4thDownTrends(plays, teamName) {{
            const byGame = {{}};
            plays.filter(p => p.down === 4 && p.offense?.toLowerCase() === teamName.toLowerCase() && !p.play_type?.toLowerCase().includes('punt') && !p.play_type?.toLowerCase().includes('field goal')).forEach(play => {{
                const gameId = play.game_id;
                if (!gameId) return;
                if (!byGame[gameId]) {{
                    byGame[gameId] = {{ attempts: 0, conversions: 0 }};
                }}
                byGame[gameId].attempts++;
                const playText = play.play_text?.toLowerCase() || '';
                if (playText.includes('1st down') || playText.includes('first down') || playText.includes('touchdown') || (play.yards_gained >= play.distance)) {{
                    byGame[gameId].conversions++;
                }}
            }});
            
            // Use master mapping to ensure all games are included
            const attempts = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.attempts || 0
            );
            const conversions = masterGameMapping.allGames.map(game => 
                byGame[game.gameId]?.conversions || 0
            );
            const rates = masterGameMapping.allGames.map(game => {{
                const gameData = byGame[game.gameId];
                const att = gameData?.attempts || 0;
                return att > 0 ? (gameData.conversions / att * 100) : 0;
            }});
            
            return {{
                weeks: masterGameMapping.gameLabels,
                attempts: attempts,
                conversions: conversions,
                rates: rates
            }};
        }}
        
        // Initialize filters (no longer needed - removed filter dropdowns)
        function initializeFilters() {{
            // Filters are now simple dropdowns that don't need population
        }}
        
        // Filter functions
        function getFilters() {{
            return {{
                conference_only: document.getElementById('conferenceFilter').value === 'conference',
                non_conference_only: document.getElementById('conferenceFilter').value === 'non-conference',
                last_3_games: document.getElementById('timePeriodFilter').value === 'last3'
            }};
        }}
        
        function filterPlays(plays, filters) {{
            let filtered = plays;
            
            // Filter by conference/non-conference
            if (filters.conference_only) {{
                filtered = filtered.filter(p => p.is_conference === true);
            }} else if (filters.non_conference_only) {{
                filtered = filtered.filter(p => p.is_conference === false);
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
            const wash = allData.washington.middle8;
            const wisc = allData.wisconsin.middle8;
            
            // Summary cards
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div class="summary-cards">
                            <div class="summary-card">
                                <h3>Points Scored</h3>
                                <div class="value">${{wash.total_points_scored}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Points Allowed</h3>
                                <div class="value">${{wash.total_points_allowed}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Net Points</h3>
                                <div class="value">${{wash.total_net_points}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Avg Net/Game</h3>
                                <div class="value">${{wash.avg_net_per_game.toFixed(1)}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Last 3 Net</h3>
                                <div class="value">${{wash.last_3_games?.net_points || 0}}</div>
                            </div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div class="summary-cards">
                            <div class="summary-card">
                                <h3>Points Scored</h3>
                                <div class="value">${{wisc.total_points_scored}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Points Allowed</h3>
                                <div class="value">${{wisc.total_points_allowed}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Net Points</h3>
                                <div class="value">${{wisc.total_net_points}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Avg Net/Game</h3>
                                <div class="value">${{wisc.avg_net_per_game.toFixed(1)}}</div>
                            </div>
                            <div class="summary-card">
                                <h3>Last 3 Net</h3>
                                <div class="value">${{wisc.last_3_games?.net_points || 0}}</div>
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
                            label: 'Washington',
                            data: [wash.total_points_scored, wash.total_points_allowed, wash.total_net_points],
                            backgroundColor: 'rgba(74, 144, 226, 0.6)'
                        }},
                        {{
                            label: 'Wisconsin',
                            data: [wisc.total_points_scored, wisc.total_points_allowed, wisc.total_net_points],
                            backgroundColor: 'rgba(196, 30, 58, 0.6)'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false
                }}
            }});
            
            // Trend chart - net points by week (use filtered plays if available)
            const washPlaysForTrend = typeof allData.washington.middle8._filtered_plays !== 'undefined' ? 
                allData.washington.middle8._filtered_plays : washingtonPlays;
            const wiscPlaysForTrend = typeof allData.wisconsin.middle8._filtered_plays !== 'undefined' ? 
                allData.wisconsin.middle8._filtered_plays : wisconsinPlays;
            const washTrends = calculateMiddle8Trends(washPlaysForTrend, 'Washington');
            const wiscTrends = calculateMiddle8Trends(wiscPlaysForTrend, 'Wisconsin');
            
            // Use master mapping to ensure all games (1-9) are included
            const allWeeks = masterGameMapping.gameLabels;
            
            // Map data using master game mapping
            const washNetPointsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = washTrends.weeks.indexOf(gameLabel);
                return index >= 0 ? washTrends.net[index] : 0;
            }});
            
            const wiscNetPointsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = wiscTrends.weeks.indexOf(gameLabel);
                return index >= 0 ? wiscTrends.net[index] : 0;
            }});
            
            const ctxTrend = document.getElementById('middleEightTrendChart').getContext('2d');
            if (charts.middleEightTrend) charts.middleEightTrend.destroy();
            charts.middleEightTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ label: 'Washington Net Points', data: washNetPointsAllWeeks, borderColor: 'rgba(74, 144, 226, 1)', backgroundColor: 'rgba(74, 144, 226, 0.1)', fill: true }},
                        {{ label: 'Wisconsin Net Points', data: wiscNetPointsAllWeeks, borderColor: 'rgba(196, 30, 58, 1)', backgroundColor: 'rgba(196, 30, 58, 0.1)', fill: true }}
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
                        title: {{ display: true, text: 'Middle 8 Net Points by Game' }},
                        tooltip: {{
                            callbacks: {{
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
            
            // Tables - separate for each team (sort chronologically)
            const washSorted = sortDrivesChronologically(wash.scoring_drives);
            const washTableData = washSorted.map(d => [
                d.game_week || '',
                d.opponent || '',
                d.scoring_team || (d.is_offense ? 'Washington' : (d.opponent || '')),
                d.drive_number || '',
                d.period || '',
                formatClock(d.clock || ''),
                d.play_type || '',
                d.points || 0,
                d.play_text || '',
                d.scoring_team || (d.is_offense ? 'Washington' : (d.opponent || ''))  // Store scoring team for row class
            ]);
            const wiscSorted = sortDrivesChronologically(wisc.scoring_drives);
            const wiscTableData = wiscSorted.map(d => [
                d.game_week || '',
                d.opponent || '',
                d.scoring_team || (d.is_offense ? 'Wisconsin' : (d.opponent || '')),
                d.drive_number || '',
                d.period || '',
                formatClock(d.clock || ''),
                d.play_type || '',
                d.points || 0,
                d.play_text || '',
                d.scoring_team || (d.is_offense ? 'Wisconsin' : (d.opponent || ''))  // Store scoring team for row class
            ]);
            
            if ($.fn.DataTable.isDataTable('#middleEightTableWash')) {{
                $('#middleEightTableWash').DataTable().destroy();
            }}
            $('#middleEightTableWash').DataTable({{
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
                    if (scoringTeam && scoringTeam.toLowerCase() !== 'washington') {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }});
            
            if ($.fn.DataTable.isDataTable('#middleEightTableWisc')) {{
                $('#middleEightTableWisc').DataTable().destroy();
            }}
            $('#middleEightTableWisc').DataTable({{
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
                    if (scoringTeam && scoringTeam.toLowerCase() !== 'wisconsin') {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }});
        }}
        
        function populateExplosivePlays() {{
            const wash = allData.washington.explosive;
            const wisc = allData.wisconsin.explosive;
            
            // Calculate allowed explosive plays stats
            const washPlaysForAllowed = typeof allData.washington.explosive._filtered_plays !== 'undefined' ? 
                allData.washington.explosive._filtered_plays : washingtonPlays;
            const wiscPlaysForAllowed = typeof allData.wisconsin.explosive._filtered_plays !== 'undefined' ? 
                allData.wisconsin.explosive._filtered_plays : wisconsinPlays;
            
            // Calculate allowed explosive plays (by opponent, excluding special teams)
            const washAllowedPlays = washPlaysForAllowed.filter(p => 
                p.explosive_play === true && 
                p.offense?.toLowerCase() !== 'washington' &&
                p.play_classification !== 'special_teams'
            );
            const wiscAllowedPlays = wiscPlaysForAllowed.filter(p => 
                p.explosive_play === true && 
                p.offense?.toLowerCase() !== 'wisconsin' &&
                p.play_classification !== 'special_teams'
            );
            
            // Calculate allowed stats
            const washAllowedTotal = washAllowedPlays.length;
            const washAllowedGames = new Set(washAllowedPlays.map(p => p.game_id)).size;
            const washAllowedPerGame = washAllowedGames > 0 ? washAllowedTotal / washAllowedGames : 0;
            
            // Last 3 games allowed
            const washGames = [...new Set(washAllowedPlays.map(p => p.game_id))].map(gid => ({{
                id: gid,
                week: washAllowedPlays.find(p => p.game_id === gid)?.game_week || 0
            }})).sort((a, b) => a.week - b.week);
            const washLast3GameIds = washGames.slice(-3).map(g => g.id);
            const washAllowedLast3 = washAllowedPlays.filter(p => washLast3GameIds.includes(p.game_id)).length;
            
            const wiscAllowedTotal = wiscAllowedPlays.length;
            const wiscAllowedGames = new Set(wiscAllowedPlays.map(p => p.game_id)).size;
            const wiscAllowedPerGame = wiscAllowedGames > 0 ? wiscAllowedTotal / wiscAllowedGames : 0;
            
            const wiscGames = [...new Set(wiscAllowedPlays.map(p => p.game_id))].map(gid => ({{
                id: gid,
                week: wiscAllowedPlays.find(p => p.game_id === gid)?.game_week || 0
            }})).sort((a, b) => a.week - b.week);
            const wiscLast3GameIds = wiscGames.slice(-3).map(g => g.id);
            const wiscAllowedLast3 = wiscAllowedPlays.filter(p => wiscLast3GameIds.includes(p.game_id)).length;
            
            // Summary
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{wash.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{wash.avg_per_game.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Last 3</h3><div class="value">${{wash.last_3_games.total}}</div></div>
                            <div class="summary-card"><h3>Allowed Total</h3><div class="value">${{washAllowedTotal}}</div></div>
                            <div class="summary-card"><h3>Allowed Per Game</h3><div class="value">${{washAllowedPerGame.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Allowed Last 3</h3><div class="value">${{washAllowedLast3}}</div></div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{wisc.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{wisc.avg_per_game.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Last 3</h3><div class="value">${{wisc.last_3_games.total}}</div></div>
                            <div class="summary-card"><h3>Allowed Total</h3><div class="value">${{wiscAllowedTotal}}</div></div>
                            <div class="summary-card"><h3>Allowed Per Game</h3><div class="value">${{wiscAllowedPerGame.toFixed(1)}}</div></div>
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
                            label: 'Washington',
                            data: [wash.total_explosive_plays, wash.avg_per_game, wash.last_3_games.total],
                            backgroundColor: 'rgba(74, 144, 226, 0.6)'
                        }},
                        {{
                            label: 'Wisconsin',
                            data: [wisc.total_explosive_plays, wisc.avg_per_game, wisc.last_3_games.total],
                            backgroundColor: 'rgba(196, 30, 58, 0.6)'
                        }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Trend chart - use filtered plays if available
            const washPlaysForTrend = typeof allData.washington.explosive._filtered_plays !== 'undefined' ? 
                allData.washington.explosive._filtered_plays : washingtonPlays;
            const wiscPlaysForTrend = typeof allData.wisconsin.explosive._filtered_plays !== 'undefined' ? 
                allData.wisconsin.explosive._filtered_plays : wisconsinPlays;
            const washTrends = calculateExplosiveTrends(washPlaysForTrend, 'Washington');
            const wiscTrends = calculateExplosiveTrends(wiscPlaysForTrend, 'Wisconsin');
            const ctxTrend = document.getElementById('explosivePlaysTrendChart').getContext('2d');
            if (charts.explosiveTrend) charts.explosiveTrend.destroy();
            charts.explosiveTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: washTrends.weeks,
                    datasets: [
                        {{ label: 'Washington', data: washTrends.ours, borderColor: 'rgba(74, 144, 226, 1)', backgroundColor: 'rgba(74, 144, 226, 0.1)', fill: true }},
                        {{ label: 'Washington Allowed', data: washTrends.allowed.map(v => -v), borderColor: 'rgba(74, 144, 226, 0.5)', backgroundColor: 'rgba(74, 144, 226, 0.05)', fill: true }},
                        {{ label: 'Wisconsin', data: wiscTrends.ours, borderColor: 'rgba(196, 30, 58, 1)', backgroundColor: 'rgba(196, 30, 58, 0.1)', fill: true }},
                        {{ label: 'Wisconsin Allowed', data: wiscTrends.allowed.map(v => -v), borderColor: 'rgba(196, 30, 58, 0.5)', backgroundColor: 'rgba(196, 30, 58, 0.05)', fill: true }}
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
                        title: {{ display: true, text: 'Explosive Plays by Game (Allowed shown as negative)' }},
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
                                    return label;
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Tables - separate for each team (sort chronologically)
            const washSorted = sortPlaysChronologically(wash.plays);
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
            const wiscSorted = sortPlaysChronologically(wisc.plays);
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
            
            if ($.fn.DataTable.isDataTable('#explosivePlaysTableWash')) {{
                $('#explosivePlaysTableWash').DataTable().destroy();
            }}
            $('#explosivePlaysTableWash').DataTable({{
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
                    if (offense && offense.toLowerCase() !== 'washington') {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }});
            
            if ($.fn.DataTable.isDataTable('#explosivePlaysTableWisc')) {{
                $('#explosivePlaysTableWisc').DataTable().destroy();
            }}
            $('#explosivePlaysTableWisc').DataTable({{
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
                    if (offense && offense.toLowerCase() !== 'wisconsin') {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }});
        }}
        
        function populatePenalties() {{
            const wash = allData.washington.penalties;
            const wisc = allData.wisconsin.penalties;
            
            // Calculate yards per game
            const washYardsPerGame = wash.total_games > 0 ? (wash.total_penalty_yards || 0) / wash.total_games : 0;
            const wiscYardsPerGame = wisc.total_games > 0 ? (wisc.total_penalty_yards || 0) / wisc.total_games : 0;
            
            // Calculate last 3 yards per game
            const washLast3Games = wash.last_3_games?.games?.length || 0;
            const washLast3YardsPerGame = washLast3Games > 0 ? (wash.last_3_games?.yards || 0) / washLast3Games : 0;
            const wiscLast3Games = wisc.last_3_games?.games?.length || 0;
            const wiscLast3YardsPerGame = wiscLast3Games > 0 ? (wisc.last_3_games?.yards || 0) / wiscLast3Games : 0;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{wash.total_penalties}}</div></div>
                            <div class="summary-card"><h3>Accepted</h3><div class="value">${{wash.accepted}}</div></div>
                            <div class="summary-card"><h3>Penalty Yards/G</h3><div class="value">${{washYardsPerGame.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{wash.avg_per_game.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Last 3 Yards/G</h3><div class="value">${{washLast3YardsPerGame.toFixed(1)}}</div></div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total</h3><div class="value">${{wisc.total_penalties}}</div></div>
                            <div class="summary-card"><h3>Accepted</h3><div class="value">${{wisc.accepted}}</div></div>
                            <div class="summary-card"><h3>Penalty Yards/G</h3><div class="value">${{wiscYardsPerGame.toFixed(1)}}</div></div>
                            <div class="summary-card"><h3>Per Game</h3><div class="value">${{wisc.avg_per_game.toFixed(1)}}</div></div>
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
                        {{ label: 'Washington', data: [wash.total_penalties, wash.accepted, washYardsPerGame], backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: [wisc.total_penalties, wisc.accepted, wiscYardsPerGame], backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Trend chart - net penalty yards per week
            const washPlaysForTrend = typeof allData.washington.penalties._filtered_plays !== 'undefined' ? 
                allData.washington.penalties._filtered_plays : washingtonPlays;
            const wiscPlaysForTrend = typeof allData.wisconsin.penalties._filtered_plays !== 'undefined' ? 
                allData.wisconsin.penalties._filtered_plays : wisconsinPlays;
            const washNetYards = calculateNetPenaltyYardsByWeek(washPlaysForTrend, 'Washington');
            const wiscNetYards = calculateNetPenaltyYardsByWeek(wiscPlaysForTrend, 'Wisconsin');
            
            // Use master mapping to ensure all games (1-9) are included
            const allWeeks = masterGameMapping.gameLabels;
            
            // Map data using master game mapping
            const washNetYardsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = washNetYards.weeks.indexOf(gameLabel);
                return index >= 0 ? washNetYards.values[index] : 0;
            }});
            
            const wiscNetYardsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = wiscNetYards.weeks.indexOf(gameLabel);
                return index >= 0 ? wiscNetYards.values[index] : 0;
            }});
            
            const ctxTrend = document.getElementById('penaltyTrendChart').getContext('2d');
            if (charts.penaltyTrend) charts.penaltyTrend.destroy();
            charts.penaltyTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ label: 'Washington Net Yards', data: washNetYardsAllWeeks, borderColor: 'rgba(74, 144, 226, 1)', backgroundColor: 'rgba(74, 144, 226, 0.1)', fill: true }},
                        {{ label: 'Wisconsin Net Yards', data: wiscNetYardsAllWeeks, borderColor: 'rgba(196, 30, 58, 1)', backgroundColor: 'rgba(196, 30, 58, 0.1)', fill: true }}
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
                                    return context.dataset.label + ': ' + sign + value + ' yards';
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Penalties by Quarter Chart
            const washByQuarter = {{1: 0, 2: 0, 3: 0, 4: 0}};
            const wiscByQuarter = {{1: 0, 2: 0, 3: 0, 4: 0}};
            wash.plays.forEach(p => {{
                const qtr = p.period || 0;
                if (qtr >= 1 && qtr <= 4) washByQuarter[qtr]++;
            }});
            wisc.plays.forEach(p => {{
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
                        {{ label: 'Washington', data: [washByQuarter[1], washByQuarter[2], washByQuarter[3], washByQuarter[4]], backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: [wiscByQuarter[1], wiscByQuarter[2], wiscByQuarter[3], wiscByQuarter[4]], backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
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
            const washPenaltyTypes = {{}};
            const wiscPenaltyTypes = {{}};
            wash.plays.forEach(p => {{
                const type = p.penalty_type || 'Unknown';
                washPenaltyTypes[type] = (washPenaltyTypes[type] || 0) + 1;
            }});
            wisc.plays.forEach(p => {{
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
                        {{ label: 'Washington', data: topTypes.map(t => washPenaltyTypes[t] || 0), backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: topTypes.map(t => wiscPenaltyTypes[t] || 0), backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
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
            wash.plays.forEach(p => {{
                const down = p.down || 0;
                if (down >= 1 && down <= 4) washByDown[down]++;
            }});
            wisc.plays.forEach(p => {{
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
                        {{ label: 'Washington', data: [washByDown[1], washByDown[2], washByDown[3], washByDown[4]], backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: [wiscByDown[1], wiscByDown[2], wiscByDown[3], wiscByDown[4]], backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
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
            wash.plays.forEach(p => {{
                const qtr = p.period || 0;
                if (qtr <= 2) washByHalf.first++;
                else if (qtr >= 3) washByHalf.second++;
            }});
            wisc.plays.forEach(p => {{
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
                        {{ label: 'Washington', data: [washByHalf.first, washByHalf.second], backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: [wiscByHalf.first, wiscByHalf.second], backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
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
            const washSorted = sortPlaysChronologically(wash.plays);
            const washTableData = washSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.penalty_type || '', p.penalty_decision || '', 
                p.penalty_yards || (p.penalty_decision === 'accepted' ? Math.abs(p.yards_gained || 0) : 0),
                p.play_text || '',
                p.offense || ''  // Store offense for row class
            ]);
            const wiscSorted = sortPlaysChronologically(wisc.plays);
            const wiscTableData = wiscSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.penalty_type || '', p.penalty_decision || '',
                p.penalty_yards || (p.penalty_decision === 'accepted' ? Math.abs(p.yards_gained || 0) : 0),
                p.play_text || '',
                p.offense || ''  // Store offense for row class
            ]);
            
            if ($.fn.DataTable.isDataTable('#penaltyTableWash')) $('#penaltyTableWash').DataTable().destroy();
            $('#penaltyTableWash').DataTable({{
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
                    if (offense && offense.toLowerCase() !== 'washington') {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }});
            
            if ($.fn.DataTable.isDataTable('#penaltyTableWisc')) $('#penaltyTableWisc').DataTable().destroy();
            $('#penaltyTableWisc').DataTable({{
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
                    if (offense && offense.toLowerCase() !== 'wisconsin') {{
                        $(row).addClass('opponent-row');
                    }} else {{
                        $(row).addClass('team-row');
                    }}
                }}
            }});
        }}
        
        function populate4thDowns() {{
            const wash = allData.washington['4thdowns'];
            const wisc = allData.wisconsin['4thdowns'];
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Attempts</h3><div class="value">${{wash.total_attempts}}</div></div>
                            <div class="summary-card"><h3>Conversions</h3><div class="value">${{wash.total_conversions}}</div></div>
                            <div class="summary-card"><h3>Rate</h3><div class="value">${{wash.conversion_rate.toFixed(1)}}%</div></div>
                            <div class="summary-card"><h3>Last 3 Attempts</h3><div class="value">${{wash.last_3_games.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Conversions</h3><div class="value">${{wash.last_3_games.conversions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Rate</h3><div class="value">${{wash.last_3_games.conversion_rate.toFixed(1)}}%</div></div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Attempts</h3><div class="value">${{wisc.total_attempts}}</div></div>
                            <div class="summary-card"><h3>Conversions</h3><div class="value">${{wisc.total_conversions}}</div></div>
                            <div class="summary-card"><h3>Rate</h3><div class="value">${{wisc.conversion_rate.toFixed(1)}}%</div></div>
                            <div class="summary-card"><h3>Last 3 Attempts</h3><div class="value">${{wisc.last_3_games.attempts || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Conversions</h3><div class="value">${{wisc.last_3_games.conversions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Rate</h3><div class="value">${{wisc.last_3_games.conversion_rate.toFixed(1)}}%</div></div>
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
                        {{ label: 'Washington', data: [wash.total_attempts, wash.total_conversions, wash.conversion_rate], backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: [wisc.total_attempts, wisc.total_conversions, wisc.conversion_rate], backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Trend chart - use filtered plays if available
            const washPlaysForTrend = typeof allData.washington['4thdowns']._filtered_plays !== 'undefined' ? 
                allData.washington['4thdowns']._filtered_plays : washingtonPlays;
            const wiscPlaysForTrend = typeof allData.wisconsin['4thdowns']._filtered_plays !== 'undefined' ? 
                allData.wisconsin['4thdowns']._filtered_plays : wisconsinPlays;
            const washTrends = calculate4thDownTrends(washPlaysForTrend, 'Washington');
            const wiscTrends = calculate4thDownTrends(wiscPlaysForTrend, 'Wisconsin');
            
            // Use master mapping to ensure all games (1-9) are included
            const allWeeks = masterGameMapping.gameLabels;
            
            // Map data using master game mapping
            const washConversionsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = washTrends.weeks.indexOf(gameLabel);
                return index >= 0 ? washTrends.conversions[index] : 0;
            }});
            
            const wiscConversionsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = wiscTrends.weeks.indexOf(gameLabel);
                return index >= 0 ? wiscTrends.conversions[index] : 0;
            }});
            
            const ctxTrend = document.getElementById('fourthDownTrendChart').getContext('2d');
            if (charts.fourthDownTrend) charts.fourthDownTrend.destroy();
            charts.fourthDownTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ 
                            label: 'Washington Conversions', 
                            data: washConversionsAllWeeks, 
                            borderColor: 'rgba(74, 144, 226, 1)', 
                            backgroundColor: 'rgba(74, 144, 226, 0.1)', 
                            fill: true 
                        }},
                        {{ 
                            label: 'Wisconsin Conversions', 
                            data: wiscConversionsAllWeeks, 
                            borderColor: 'rgba(196, 30, 58, 1)', 
                            backgroundColor: 'rgba(196, 30, 58, 0.1)', 
                            fill: true 
                        }}
                    ]
                }},
                options: {{ 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    scales: {{ y: {{ beginAtZero: true }} }}, 
                    plugins: {{ 
                        title: {{ display: true, text: '4th Down Conversions by Game' }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const datasetIndex = context.datasetIndex;
                                    const dataIndex = context.dataIndex;
                                    const week = allWeeks[dataIndex];
                                    const conversions = context.parsed.y;
                                    
                                    // Find the original week index in the team's trends
                                    const teamTrends = datasetIndex === 0 ? washTrends : wiscTrends;
                                    const weekIndex = teamTrends.weeks.indexOf(week);
                                    
                                    if (weekIndex >= 0) {{
                                        const attempts = teamTrends.attempts[weekIndex];
                                        const rate = teamTrends.rates[weekIndex];
                                        const teamName = datasetIndex === 0 ? 'Washington' : 'Wisconsin';
                                        return `${{teamName}}: ${{conversions}}/${{attempts}} (${{rate.toFixed(1)}}%)`;
                                    }} else {{
                                        // Week with no attempts
                                        const teamName = datasetIndex === 0 ? 'Washington' : 'Wisconsin';
                                        return `${{teamName}}: 0/0 (0.0%)`;
                                    }}
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Tables - separate for each team
            // Sort chronologically
            const washSorted = sortPlaysChronologically(wash.plays);
            const washTableData = washSorted.map(p => [
                p.game_week || '', p.opponent || '', p.yard_line || '', p.distance || '',
                p.play_type || '', p.converted ? 'Yes' : 'No', p.yards_gained || 0, p.ppa ? p.ppa.toFixed(2) : '',
                p.play_text || ''
            ]);
            const wiscSorted = sortPlaysChronologically(wisc.plays);
            const wiscTableData = wiscSorted.map(p => [
                p.game_week || '', p.opponent || '', p.yard_line || '', p.distance || '',
                p.play_type || '', p.converted ? 'Yes' : 'No', p.yards_gained || 0, p.ppa ? p.ppa.toFixed(2) : '',
                p.play_text || ''
            ]);
            
            if ($.fn.DataTable.isDataTable('#fourthDownTableWash')) $('#fourthDownTableWash').DataTable().destroy();
            $('#fourthDownTableWash').DataTable({{
                data: washTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Yard Line' }}, {{ title: 'Distance' }},
                    {{ title: 'Play Type' }}, {{ title: 'Converted' }}, {{ title: 'Yards' }}, {{ title: 'PPA' }},
                    {{ title: 'Play Description' }}
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                }}
            }});
            
            if ($.fn.DataTable.isDataTable('#fourthDownTableWisc')) $('#fourthDownTableWisc').DataTable().destroy();
            $('#fourthDownTableWisc').DataTable({{
                data: wiscTableData,
                paging: false,
                searching: false,
                scrollY: '400px',
                scrollCollapse: true,
                columns: [
                    {{ title: 'Week' }}, {{ title: 'Opponent' }}, {{ title: 'Yard Line' }}, {{ title: 'Distance' }},
                    {{ title: 'Play Type' }}, {{ title: 'Converted' }}, {{ title: 'Yards' }}, {{ title: 'PPA' }},
                    {{ title: 'Play Description' }}
                ],
                createdRow: function(row, data) {{
                    const weekValue = data[0]; // Week is first column
                    addWeekClass(row, weekValue);
                }}
            }});
        }}
        
        function populatePostTurnover() {{
            const wash = allData.washington.turnover;
            const wisc = allData.wisconsin.turnover;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Opponent Turnovers</h3><div class="value">${{wash.opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Scored After</h3><div class="value">${{wash.points_scored_after_opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>Net Points</h3><div class="value">${{wash.net_points_after_turnovers}}</div></div>
                            <div class="summary-card"><h3>Washington Turnovers</h3><div class="value">${{wash.our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Allowed After</h3><div class="value">${{wash.points_allowed_after_our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Last 3 Net Points</h3><div class="value">${{wash.last_3_games?.net_points || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Opponent Turnovers</h3><div class="value">${{wisc.opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Scored After</h3><div class="value">${{wisc.points_scored_after_opponent_turnovers}}</div></div>
                            <div class="summary-card"><h3>Net Points</h3><div class="value">${{wisc.net_points_after_turnovers}}</div></div>
                            <div class="summary-card"><h3>Wisconsin Turnovers</h3><div class="value">${{wisc.our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Points Allowed After</h3><div class="value">${{wisc.points_allowed_after_our_turnovers}}</div></div>
                            <div class="summary-card"><h3>Last 3 Net Points</h3><div class="value">${{wisc.last_3_games?.net_points || 0}}</div></div>
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
                        {{ label: 'Washington', data: [wash.our_turnovers, wash.opponent_turnovers, wash.points_scored_after_opponent_turnovers, -wash.points_allowed_after_our_turnovers], backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: [wisc.our_turnovers, wisc.opponent_turnovers, wisc.points_scored_after_opponent_turnovers, -wisc.points_allowed_after_our_turnovers], backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
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
            const washPlaysForTrend = typeof allData.washington.turnover._filtered_plays !== 'undefined' ? 
                allData.washington.turnover._filtered_plays : washingtonPlays;
            const wiscPlaysForTrend = typeof allData.wisconsin.turnover._filtered_plays !== 'undefined' ? 
                allData.wisconsin.turnover._filtered_plays : wisconsinPlays;
            const washNetPoints = calculateNetPointsByWeek(washPlaysForTrend, 'Washington');
            const wiscNetPoints = calculateNetPointsByWeek(wiscPlaysForTrend, 'Wisconsin');
            
            // Use master mapping to ensure all games (1-9) are included
            const allWeeks = masterGameMapping.gameLabels;
            
            // Map data using master game mapping
            const washNetPointsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = washNetPoints.weeks.indexOf(gameLabel);
                return index >= 0 ? washNetPoints.netPoints[index] : 0;
            }});
            
            const wiscNetPointsAllWeeks = masterGameMapping.allGames.map(game => {{
                const gameNum = masterGameMapping.gameIdToGameNum[game.gameId];
                const gameLabel = `Game ${{gameNum}}`;
                const index = wiscNetPoints.weeks.indexOf(gameLabel);
                return index >= 0 ? wiscNetPoints.netPoints[index] : 0;
            }});
            
            const ctxTrend = document.getElementById('postTurnoverTrendChart').getContext('2d');
            if (charts.postTurnoverTrend) charts.postTurnoverTrend.destroy();
            charts.postTurnoverTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: allWeeks,
                    datasets: [
                        {{ label: 'Washington Net Points', data: washNetPointsAllWeeks, borderColor: 'rgba(74, 144, 226, 1)', backgroundColor: 'rgba(74, 144, 226, 0.1)', fill: true }},
                        {{ label: 'Wisconsin Net Points', data: wiscNetPointsAllWeeks, borderColor: 'rgba(196, 30, 58, 1)', backgroundColor: 'rgba(196, 30, 58, 0.1)', fill: true }}
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
                        title: {{ display: true, text: 'Net Points After Turnovers by Game' }},
                        tooltip: {{
                            callbacks: {{
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
            const washTurnoverSorted = wash.turnover_analysis.slice().sort((a, b) => (a.game_week || 0) - (b.game_week || 0));
            const washTableData = washTurnoverSorted.map(t => [
                t.game_week || '', t.opponent || '', t.turnover_type || '',
                t.is_our_turnover ? 'Washington' : 'Opponent', t.drive_result || '', t.points_scored || 0,
                t.play_text || '',
                t.is_our_turnover ? false : true  // Store isOpponent for row class
            ]);
            const wiscTurnoverSorted = wisc.turnover_analysis.slice().sort((a, b) => (a.game_week || 0) - (b.game_week || 0));
            const wiscTableData = wiscTurnoverSorted.map(t => [
                t.game_week || '', t.opponent || '', t.turnover_type || '',
                t.is_our_turnover ? 'Wisconsin' : 'Opponent', t.drive_result || '', t.points_scored || 0,
                t.play_text || '',
                t.is_our_turnover ? false : true  // Store isOpponent for row class
            ]);
            
            if ($.fn.DataTable.isDataTable('#postTurnoverTableWash')) $('#postTurnoverTableWash').DataTable().destroy();
            $('#postTurnoverTableWash').DataTable({{
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
            }});
            
            if ($.fn.DataTable.isDataTable('#postTurnoverTableWisc')) $('#postTurnoverTableWisc').DataTable().destroy();
            $('#postTurnoverTableWisc').DataTable({{
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
            }});
        }}
        
        function populateSpecialTeams() {{
            const wash = allData.washington.specialteams;
            const wisc = allData.wisconsin.specialteams;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Explosive</h3><div class="value">${{wash.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Explosive Allowed</h3><div class="value">${{wash.explosive_returns_allowed}}</div></div>
                            <div class="summary-card"><h3>TD's Scored</h3><div class="value">${{wash.tds_scored || 0}}</div></div>
                            <div class="summary-card"><h3>TD's Allowed</h3><div class="value">${{wash.tds_allowed || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Explosive</h3><div class="value">${{wisc.total_explosive_plays}}</div></div>
                            <div class="summary-card"><h3>Explosive Allowed</h3><div class="value">${{wisc.explosive_returns_allowed}}</div></div>
                            <div class="summary-card"><h3>TD's Scored</h3><div class="value">${{wisc.tds_scored || 0}}</div></div>
                            <div class="summary-card"><h3>TD's Allowed</h3><div class="value">${{wisc.tds_allowed || 0}}</div></div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('specialTeamsSummary').innerHTML = summaryHtml;
            
            // Trend chart for special teams explosive plays - use filtered plays if available
            const washPlaysForTrend = typeof allData.washington.specialteams._filtered_plays !== 'undefined' ? 
                allData.washington.specialteams._filtered_plays : washingtonPlays;
            const wiscPlaysForTrend = typeof allData.wisconsin.specialteams._filtered_plays !== 'undefined' ? 
                allData.wisconsin.specialteams._filtered_plays : wisconsinPlays;
            const washTrends = calculateSpecialTeamsExplosiveTrends(washPlaysForTrend, 'Washington');
            const wiscTrends = calculateSpecialTeamsExplosiveTrends(wiscPlaysForTrend, 'Wisconsin');
            const ctxTrend = document.getElementById('specialTeamsTrendChart').getContext('2d');
            if (charts.specialTeamsTrend) charts.specialTeamsTrend.destroy();
            charts.specialTeamsTrend = new Chart(ctxTrend, {{
                type: 'line',
                data: {{
                    labels: washTrends.weeks,
                    datasets: [
                        {{ label: 'Washington Explosive ST Plays', data: washTrends.ours, borderColor: 'rgba(74, 144, 226, 1)', backgroundColor: 'rgba(74, 144, 226, 0.1)', fill: true }},
                        {{ label: 'Washington Allowed', data: washTrends.allowed.map(v => -v), borderColor: 'rgba(74, 144, 226, 0.5)', backgroundColor: 'rgba(74, 144, 226, 0.05)', fill: true }},
                        {{ label: 'Wisconsin Explosive ST Plays', data: wiscTrends.ours, borderColor: 'rgba(196, 30, 58, 1)', backgroundColor: 'rgba(196, 30, 58, 0.1)', fill: true }},
                        {{ label: 'Wisconsin Allowed', data: wiscTrends.allowed.map(v => -v), borderColor: 'rgba(196, 30, 58, 0.5)', backgroundColor: 'rgba(196, 30, 58, 0.05)', fill: true }}
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
                        title: {{ display: true, text: 'Explosive Special Teams Plays by Game (Allowed shown as negative)' }},
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
                                    return label;
                                }}
                            }}
                        }}
                    }} 
                }}
            }});
            
            // Tables - separate for each team
            // Sort chronologically
            const washSTSorted = sortPlaysChronologically(wash.plays);
            const washTableData = washSTSorted.map(p => [
                p.game_week || '', p.opponent || '', p.play_type || '',
                p.is_our ? 'Washington' : 'Opponent', p.yards_gained || 0,
                p.explosive ? 'Yes' : 'No',
                p.play_text || '',
                !p.is_our  // Store isOpponent for row class
            ]);
            const wiscSTSorted = sortPlaysChronologically(wisc.plays);
            const wiscTableData = wiscSTSorted.map(p => [
                p.game_week || '', p.opponent || '', p.play_type || '',
                p.is_our ? 'Wisconsin' : 'Opponent', p.yards_gained || 0,
                p.explosive ? 'Yes' : 'No',
                p.play_text || '',
                !p.is_our  // Store isOpponent for row class
            ]);
            
            if ($.fn.DataTable.isDataTable('#specialTeamsTableWash')) $('#specialTeamsTableWash').DataTable().destroy();
            $('#specialTeamsTableWash').DataTable({{
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
            }});
            
            if ($.fn.DataTable.isDataTable('#specialTeamsTableWisc')) $('#specialTeamsTableWisc').DataTable().destroy();
            $('#specialTeamsTableWisc').DataTable({{
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
            }});
        }}
        
        function populateRedZone() {{
            const wash = allData.washington.redzone;
            const wisc = allData.wisconsin.redzone;
            
            const summaryHtml = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #d32f2f; margin-bottom: 10px;">Red Zone (20 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{wash.red_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{wash.red_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{wash.red_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{wash.red_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{wash.red_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{wash.red_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                        <div>
                            <h4 style="color: #388e3c; margin-bottom: 10px;">Green Zone (30 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{wash.green_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{wash.green_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{wash.green_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{wash.green_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{wash.green_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{wash.green_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #d32f2f; margin-bottom: 10px;">Red Zone (20 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{wisc.red_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{wisc.red_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{wisc.red_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{wisc.red_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{wisc.red_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{wisc.red_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                        <div>
                            <h4 style="color: #388e3c; margin-bottom: 10px;">Green Zone (30 & In)</h4>
                            <div class="summary-cards">
                                <div class="summary-card"><h3>Plays</h3><div class="value">${{wisc.green_zone.total_plays}}</div></div>
                                <div class="summary-card"><h3>Touchdowns</h3><div class="value">${{wisc.green_zone.touchdowns}}</div></div>
                                <div class="summary-card"><h3>TD Scoring %</h3><div class="value">${{wisc.green_zone.td_scoring_rate.toFixed(1)}}%</div></div>
                                <div class="summary-card"><h3>Turnovers</h3><div class="value">${{wisc.green_zone.turnovers}}</div></div>
                                <div class="summary-card"><h3>Avg PPA</h3><div class="value">${{wisc.green_zone.avg_ppa.toFixed(3)}}</div></div>
                                <div class="summary-card"><h3>3rd Down Conv</h3><div class="value">${{wisc.green_zone.conversions_3rd.rate.toFixed(1)}}%</div></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('redZoneSummary').innerHTML = summaryHtml;
            
            // Bar chart comparing Red Zone and Green Zone scoring rates
            const ctx = document.getElementById('redZoneChart').getContext('2d');
            if (charts.redZone) charts.redZone.destroy();
            charts.redZone = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Red Zone TD %', 'Green Zone TD %', 'Red Zone PPA', 'Green Zone PPA'],
                    datasets: [
                        {{ label: 'Washington', data: [wash.red_zone.td_scoring_rate, wash.green_zone.td_scoring_rate, wash.red_zone.avg_ppa, wash.green_zone.avg_ppa], backgroundColor: 'rgba(74, 144, 226, 0.6)' }},
                        {{ label: 'Wisconsin', data: [wisc.red_zone.td_scoring_rate, wisc.green_zone.td_scoring_rate, wisc.red_zone.avg_ppa, wisc.green_zone.avg_ppa], backgroundColor: 'rgba(196, 30, 58, 0.6)' }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
            
            // Tables - only Green Zone
            // Sort chronologically
            const washGreenSorted = sortPlaysChronologically(wash.green_zone.plays);
            const washGreenTableData = washGreenSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.down || '', p.distance || '', p.yards_to_goal || '',
                p.play_type || '', p.yards_gained || 0, p.scoring ? 'Yes' : 'No',
                p.explosive ? 'Yes' : 'No', p.ppa ? p.ppa.toFixed(3) : '', p.play_text || ''
            ]);
            
            const wiscGreenSorted = sortPlaysChronologically(wisc.green_zone.plays);
            const wiscGreenTableData = wiscGreenSorted.map(p => [
                p.game_week || '', p.opponent || '', p.period || '', formatClock(p.clock || ''),
                p.down || '', p.distance || '', p.yards_to_goal || '',
                p.play_type || '', p.yards_gained || 0, p.scoring ? 'Yes' : 'No',
                p.explosive ? 'Yes' : 'No', p.ppa ? p.ppa.toFixed(3) : '', p.play_text || ''
            ]);
            
            if ($.fn.DataTable.isDataTable('#greenZoneTableWash')) $('#greenZoneTableWash').DataTable().destroy();
            $('#greenZoneTableWash').DataTable({{
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
            }});
            
            if ($.fn.DataTable.isDataTable('#greenZoneTableWisc')) $('#greenZoneTableWisc').DataTable().destroy();
            $('#greenZoneTableWisc').DataTable({{
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
            }});
        }}
        
        function populateSituationalReceiving() {{
            const wash = allData.washington.situational;
            const wisc = allData.wisconsin.situational;
            
            if (!wash || !wisc) {{
                console.warn('Situational receiving data not available');
                return;
            }}
            
            // 3rd Down Summary
            const wash3rd = wash['3rd_down'];
            const wisc3rd = wisc['3rd_down'];
            const thirdDownSummary = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total Targets</h3><div class="value">${{wash3rd.total.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Receptions</h3><div class="value">${{wash3rd.total.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Reception %</h3><div class="value">${{wash3rd.total.targets > 0 ? (wash3rd.total.receptions / wash3rd.total.targets * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>First Downs</h3><div class="value">${{wash3rd.total.first_downs || 0}}</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{wash3rd.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Targets</h3><div class="value">${{wash3rd.last_3_games.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Receptions</h3><div class="value">${{wash3rd.last_3_games.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 First Downs</h3><div class="value">${{wash3rd.last_3_games.first_downs || 0}}</div></div>
                        </div>
                    </div>
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
                        <div class="summary-cards">
                            <div class="summary-card"><h3>Total Targets</h3><div class="value">${{wisc3rd.total.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Receptions</h3><div class="value">${{wisc3rd.total.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Reception %</h3><div class="value">${{wisc3rd.total.targets > 0 ? (wisc3rd.total.receptions / wisc3rd.total.targets * 100).toFixed(1) : 0}}%</div></div>
                            <div class="summary-card"><h3>First Downs</h3><div class="value">${{wisc3rd.total.first_downs || 0}}</div></div>
                            <div class="summary-card"><h3>TDs</h3><div class="value">${{wisc3rd.total.touchdowns || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Targets</h3><div class="value">${{wisc3rd.last_3_games.targets || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 Receptions</h3><div class="value">${{wisc3rd.last_3_games.receptions || 0}}</div></div>
                            <div class="summary-card"><h3>Last 3 First Downs</h3><div class="value">${{wisc3rd.last_3_games.first_downs || 0}}</div></div>
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
            for (const player of wash3rd.players || []) {{
                const name = player.player || 'Unknown';
                washPlayerRankings[name] = player.big_ten_rank;
            }}
            for (const player of wisc3rd.players || []) {{
                const name = player.player || 'Unknown';
                wiscPlayerRankings[name] = player.big_ten_rank;
            }}
            
            for (const weekData of Object.values(wash3rd.by_week || {{}})) {{
                for (const player of weekData.players || []) {{
                    const name = player.player || 'Unknown';
                    if (!washPlayerTargets[name]) {{
                        washPlayerTargets[name] = {{ targets: 0, rank: washPlayerRankings[name] || null }};
                    }}
                    washPlayerTargets[name].targets += (player.targets || 0);
                }}
            }}
            
            for (const weekData of Object.values(wisc3rd.by_week || {{}})) {{
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
            
            // Washington pie chart
            const ctx3rdWash = document.getElementById('thirdDownChartWash').getContext('2d');
            if (charts.thirdDownWash) charts.thirdDownWash.destroy();
            
            const washColors = [
                'rgba(74, 144, 226, 0.8)', 'rgba(74, 144, 226, 0.6)', 'rgba(74, 144, 226, 0.4)',
                'rgba(54, 162, 235, 0.8)', 'rgba(54, 162, 235, 0.6)', 'rgba(54, 162, 235, 0.4)',
                'rgba(153, 102, 255, 0.8)', 'rgba(153, 102, 255, 0.6)'
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
                        title: {{ display: true, text: 'Washington - 3rd Down Target Distribution', font: {{ size: 14 }} }},
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
            
            // Wisconsin pie chart
            const ctx3rdWisc = document.getElementById('thirdDownChartWisc').getContext('2d');
            if (charts.thirdDownWisc) charts.thirdDownWisc.destroy();
            
            const wiscColors = [
                'rgba(196, 30, 58, 0.8)', 'rgba(196, 30, 58, 0.6)', 'rgba(196, 30, 58, 0.4)',
                'rgba(220, 53, 69, 0.8)', 'rgba(220, 53, 69, 0.6)', 'rgba(220, 53, 69, 0.4)',
                'rgba(255, 99, 132, 0.8)', 'rgba(255, 99, 132, 0.6)'
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
                        title: {{ display: true, text: 'Wisconsin - 3rd Down Target Distribution', font: {{ size: 14 }} }},
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
            for (const player of wash3rd.players || []) {{
                wash3rdPlayerRankings[player.player || 'Unknown'] = {{ rank: player.big_ten_rank, isTop25: player.is_top_25 }};
            }}
            const wisc3rdPlayerRankings = {{}};
            for (const player of wisc3rd.players || []) {{
                wisc3rdPlayerRankings[player.player || 'Unknown'] = {{ rank: player.big_ten_rank, isTop25: player.is_top_25 }};
            }}
            
            // 3rd Down Tables
            const wash3rdTableData = [];
            for (const [weekStr, weekData] of Object.entries(wash3rd.by_week || {{}})) {{
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
            for (const [weekStr, weekData] of Object.entries(wisc3rd.by_week || {{}})) {{
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
            const washTop25_3rd = wash3rd.players.filter(p => p.is_top_25).map(p => p.player).join(', ');
            const wiscTop25_3rd = wisc3rd.players.filter(p => p.is_top_25).map(p => p.player).join(', ');
            
            if ($('#thirdDownTableWash').length) {{
                if ($.fn.DataTable.isDataTable('#thirdDownTableWash')) $('#thirdDownTableWash').DataTable().destroy();
                $('#thirdDownTableWash').DataTable({{
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
                }});
            }}
            
            if ($('#thirdDownTableWisc').length) {{
                if ($.fn.DataTable.isDataTable('#thirdDownTableWisc')) $('#thirdDownTableWisc').DataTable().destroy();
                $('#thirdDownTableWisc').DataTable({{
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
                }});
            }}
            
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
            const washRZ = wash.redzone;
            const wiscRZ = wisc.redzone;
            const redZoneSummary = `
                <div class="team-comparison">
                    <div class="team-section washington">
                        <h3>Washington</h3>
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
                    <div class="team-section wisconsin">
                        <h3>Wisconsin</h3>
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
            
            // Washington Red Zone pie chart
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
                        title: {{ display: true, text: 'Washington - Red Zone Target Distribution', font: {{ size: 14 }} }},
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
            
            // Wisconsin Red Zone pie chart
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
                        title: {{ display: true, text: 'Wisconsin - Red Zone Target Distribution', font: {{ size: 14 }} }},
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
            
            if ($('#redZoneReceivingTableWash').length) {{
                if ($.fn.DataTable.isDataTable('#redZoneReceivingTableWash')) $('#redZoneReceivingTableWash').DataTable().destroy();
                $('#redZoneReceivingTableWash').DataTable({{
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
                }});
            }}
            
            if ($('#redZoneReceivingTableWisc').length) {{
                if ($.fn.DataTable.isDataTable('#redZoneReceivingTableWisc')) $('#redZoneReceivingTableWisc').DataTable().destroy();
                $('#redZoneReceivingTableWisc').DataTable({{
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
                }});
            }}
            
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
        
        function populateAllSections() {{
            populateMiddleEight();
            populateExplosivePlays();
            populatePenalties();
            populate4thDowns();
            populatePostTurnover();
            populateSpecialTeams();
            populateRedZone();
            populateSituationalReceiving();
            populateAllPlaysBrowser();
        }}
        
        function populateAllPlaysBrowser() {{
            const container = document.getElementById('allPlaysContainer');
            if (!container) return;
            
            let html = '<div class="plays-browser">';
            
            // Process both teams
            const teams = [
                {{ name: 'Washington', plays: washingtonPlays, color: 'washington' }},
                {{ name: 'Wisconsin', plays: wisconsinPlays, color: 'wisconsin' }}
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
        
        function analyzeExplosivePlays(plays, teamName) {{
            const explosivePlays = plays.filter(p => 
                p.explosive_play === true && 
                p.offense?.toLowerCase() === teamName.toLowerCase() &&
                p.play_classification !== 'special_teams'
            );
            const uniqueGames = new Set(explosivePlays.map(p => p.game_id)).size;
            return {{
                total_explosive_plays: explosivePlays.length,
                avg_per_game: uniqueGames > 0 ? explosivePlays.length / uniqueGames : 0,
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
                plays: penaltyPlays.map(p => ({{
                    game_week: p.game_week,
                    opponent: p.opponent,
                    period: p.period,
                    clock: p.clock,
                    penalty_type: p.penalty_type,
                    penalty_decision: p.penalty_decision,
                    play_text: p.play_text?.substring(0, 200) || ''
                }}))
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
            
            let ourTurnovers = 0;
            let opponentTurnovers = 0;
            let pointsScoredAfterOpponentTO = 0;
            let pointsAllowedAfterOurTO = 0;
            const turnoverAnalysis = [];
            
            turnovers.forEach(turnover => {{
                const isOurTurnover = turnover.offense?.toLowerCase() === teamName.toLowerCase();
                if (isOurTurnover) ourTurnovers++;
                else opponentTurnovers++;
                
                // Find subsequent drive
                const nextDrivePlays = postTurnoverPlays.filter(p => 
                    p.game_id === turnover.game_id && p.drive_id !== turnover.drive_id
                );
                
                let drivePoints = 0;
                let driveResult = 'No Score';
                nextDrivePlays.forEach(p => {{
                    if (p.scoring === true) {{
                        if (p.play_type?.includes('Touchdown')) {{
                            drivePoints = 7;
                            driveResult = 'Touchdown';
                        }} else if (p.play_type?.includes('Field Goal')) {{
                            drivePoints = 3;
                            driveResult = 'Field Goal';
                        }}
                    }}
                }});
                
                if (isOurTurnover) {{
                    pointsAllowedAfterOurTO += drivePoints;
                }} else {{
                    pointsScoredAfterOpponentTO += drivePoints;
                }}
                
                turnoverAnalysis.push({{
                    game_week: turnover.game_week,
                    opponent: turnover.opponent,
                    turnover_type: turnover.play_type,
                    is_our_turnover: isOurTurnover,
                    drive_result: driveResult,
                    points_scored: isOurTurnover ? 0 : drivePoints,
                    points_allowed: isOurTurnover ? drivePoints : 0,
                    play_text: turnover.play_text?.substring(0, 150) || ''
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
                red_zone: analyzeZone(redZonePlays),
                green_zone: analyzeZone(greenZonePlays)
            }};
        }}
        
        function analyzeSpecialTeams(plays, teamName) {{
            const stPlays = plays.filter(p => p.play_classification === 'special_teams');
            const ourSTPlays = stPlays.filter(p => p.offense?.toLowerCase() === teamName.toLowerCase());
            const opponentSTPlays = stPlays.filter(p => p.offense?.toLowerCase() !== teamName.toLowerCase());
            
            // Check if special teams play is explosive: 35+ kick return, 20+ punt return
            function isSpecialTeamsExplosive(play) {{
                const pt = (play.play_type || '').toLowerCase();
                const ptxt = (play.play_text || '').toLowerCase();
                const yards = play.yards_gained || 0;
                
                // Kick return: 35+ yards
                if ((pt.includes('kickoff') || ptxt.includes('kickoff')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    return yards >= 35;
                }}
                
                // Punt return: 20+ yards
                if ((pt.includes('punt') || ptxt.includes('punt')) && 
                    (pt.includes('return') || ptxt.includes('return'))) {{
                    return yards >= 20;
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
            const washFiltered = filterPlays(washingtonPlays, filters);
            const wiscFiltered = filterPlays(wisconsinPlays, filters);
            
            // Re-analyze with filtered data
            const washFilteredData = {{
                middle8: analyzeMiddleEight(washFiltered, 'Washington'),
                explosive: analyzeExplosivePlays(washFiltered, 'Washington'),
                penalties: analyzePenalties(washFiltered, 'Washington'),
                '4thdowns': analyze4thDowns(washFiltered, 'Washington'),
                turnover: analyzePostTurnover(washFiltered, 'Washington'),
                specialteams: analyzeSpecialTeams(washFiltered, 'Washington'),
                redzone: analyzeRedZone(washFiltered, 'Washington')
            }};
            
            const wiscFilteredData = {{
                middle8: analyzeMiddleEight(wiscFiltered, 'Wisconsin'),
                explosive: analyzeExplosivePlays(wiscFiltered, 'Wisconsin'),
                penalties: analyzePenalties(wiscFiltered, 'Wisconsin'),
                '4thdowns': analyze4thDowns(wiscFiltered, 'Wisconsin'),
                turnover: analyzePostTurnover(wiscFiltered, 'Wisconsin'),
                specialteams: analyzeSpecialTeams(wiscFiltered, 'Wisconsin'),
                redzone: analyzeRedZone(wiscFiltered, 'Wisconsin')
            }};
            
            // Store filtered plays for trend calculations
            washFilteredData.middle8._filtered_plays = washFiltered;
            washFilteredData.explosive._filtered_plays = washFiltered;
            washFilteredData.penalties._filtered_plays = washFiltered;
            washFilteredData['4thdowns']._filtered_plays = washFiltered;
            washFilteredData.turnover._filtered_plays = washFiltered;
            washFilteredData.specialteams._filtered_plays = washFiltered;
            washFilteredData.redzone._filtered_plays = washFiltered;
            
            wiscFilteredData.middle8._filtered_plays = wiscFiltered;
            wiscFilteredData.explosive._filtered_plays = wiscFiltered;
            wiscFilteredData.penalties._filtered_plays = wiscFiltered;
            wiscFilteredData['4thdowns']._filtered_plays = wiscFiltered;
            wiscFilteredData.turnover._filtered_plays = wiscFiltered;
            wiscFilteredData.specialteams._filtered_plays = wiscFiltered;
            wiscFilteredData.redzone._filtered_plays = wiscFiltered;
            
            // Temporarily replace allData with filtered data
            const originalAllData = allData;
            allData.washington = washFilteredData;
            allData.wisconsin = wiscFilteredData;
            
            // Re-populate all sections with filtered data
            populateAllSections();
            
            // Restore original data (for future filter changes)
            allData.washington = originalAllData.washington;
            allData.wisconsin = originalAllData.wisconsin;
        }}
        
        function resetFilters() {{
            // Reset filter dropdowns
            document.getElementById('conferenceFilter').selectedIndex = 0;
            document.getElementById('timePeriodFilter').selectedIndex = 0;
            
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
    generate_html_app()

