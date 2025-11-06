#!/usr/bin/env python3
"""
Create aligned WPA chart with 159 plays each
"""

import json

def create_aligned_wpa_chart():
    """Create aligned WPA chart with 159 plays each"""
    
    print("🔍 Creating aligned WPA chart with 159 plays each...")
    
    # Load reconstructed ESPN data (160 plays)
    with open('espn_reconstructed_plays_401752873.json', 'r') as f:
        espn_data = json.load(f)
    
    # Load CFBD data
    with open('cfbd_pbp_with_wpa_401752873.json', 'r') as f:
        cfbd_data = json.load(f)
    
    print(f"📊 ESPN plays (original): {len(espn_data)}")
    print(f"📊 CFBD plays: {len(cfbd_data)}")
    
    # Remove first play from ESPN data to align with CFBD
    espn_data_aligned = espn_data[1:]  # Skip first play
    print(f"📊 ESPN plays (aligned): {len(espn_data_aligned)}")
    
    # Prepare ESPN WPA data (aligned)
    espn_wpa_data = []
    for i, play in enumerate(espn_data_aligned):
        if 'wpa' in play and play['wpa']['wpa_percentage'] is not None:
            espn_wpa_data.append(play['wpa']['wpa_percentage'])
    
    # Prepare CFBD WPA data
    cfbd_wpa_data = []
    for i, play in enumerate(cfbd_data):
        if 'cfbd_wpa' in play and play['cfbd_wpa']['wpa_percentage'] is not None:
            cfbd_wpa_data.append(play['cfbd_wpa']['wpa_percentage'])
    
    print(f"📈 ESPN WPA data points: {len(espn_wpa_data)}")
    print(f"📈 CFBD WPA data points: {len(cfbd_wpa_data)}")
    
    # Create HTML with Chart.js
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WPA Comparison: ESPN vs CFBD - Game 401752873 (Aligned)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin-top: 0;
            color: #333;
        }}
        .stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }}
        .stat-item {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .stat-label {{
            font-weight: bold;
            color: #666;
        }}
        .stat-value {{
            font-size: 1.2em;
            color: #333;
        }}
        .note {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #4caf50;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 WPA Comparison: ESPN vs CFBD (Aligned)</h1>
        <h2>Michigan vs Washington - Game ID: 401752873</h2>
        <p>Win Probability Added (WPA) comparison between ESPN and CFBD data sources</p>
    </div>
    
    <div class="note">
        <strong>✅ Aligned Data:</strong> Both datasets now have exactly 159 plays for direct comparison. 
        ESPN data has been aligned by removing the first play to match CFBD's play count.
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>📺 ESPN WPA Summary (Aligned)</h3>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-label">Total Plays</div>
                    <div class="stat-value">{len(espn_data_aligned)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">WPA Data Points</div>
                    <div class="stat-value">{len(espn_wpa_data)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Max WPA</div>
                    <div class="stat-value">{max(espn_wpa_data):+.1f}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Min WPA</div>
                    <div class="stat-value">{min(espn_wpa_data):+.1f}%</div>
                </div>
            </div>
        </div>
        
        <div class="summary-card">
            <h3>📊 CFBD WPA Summary</h3>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-label">Total Plays</div>
                    <div class="stat-value">{len(cfbd_data)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">WPA Data Points</div>
                    <div class="stat-value">{len(cfbd_wpa_data)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Max WPA</div>
                    <div class="stat-value">{max(cfbd_wpa_data):+.1f}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Min WPA</div>
                    <div class="stat-value">{min(cfbd_wpa_data):+.1f}%</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="chart-container">
        <h3>WPA Comparison Chart (Aligned - 159 Plays Each)</h3>
        <canvas id="wpaChart" width="800" height="400"></canvas>
    </div>
    
    <script>
        // Prepare data for chart
        const espnWpaData = {espn_wpa_data};
        const cfbdWpaData = {cfbd_wpa_data};
        
        // Create labels for x-axis (play numbers)
        const labels = [];
        for (let i = 0; i < 159; i++) {{
            labels.push(`Play ${{i + 1}}`);
        }}
        
        // Create chart
        const ctx = document.getElementById('wpaChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'ESPN WPA (%)',
                    data: espnWpaData,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.1,
                    fill: false
                }}, {{
                    label: 'CFBD WPA (%)',
                    data: cfbdWpaData,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.1,
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Win Probability Added (WPA) Comparison: ESPN vs CFBD (Aligned - 159 Plays Each)'
                    }},
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    tooltip: {{
                        callbacks: {{
                            afterLabel: function(context) {{
                                const datasetLabel = context.dataset.label;
                                const value = context.parsed.y;
                                return `${{datasetLabel}}: ${{value.toFixed(1)}}%`;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'Play Number'
                        }},
                        grid: {{
                            display: true
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'WPA (%)'
                        }},
                        grid: {{
                            display: true
                        }},
                        min: Math.min(...espnWpaData, ...cfbdWpaData) - 1,
                        max: Math.max(...espnWpaData, ...cfbdWpaData) + 1
                    }}
                }},
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    with open('wpa_comparison_chart_aligned_401752873.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created aligned WPA chart with 159 plays each")
    print("📄 File: wpa_comparison_chart_aligned_401752873.html")
    
    # Show data summary
    print(f"\n📊 Aligned Data Summary:")
    print(f"  ESPN WPA range: {min(espn_wpa_data):.1f}% to {max(espn_wpa_data):.1f}%")
    print(f"  CFBD WPA range: {min(cfbd_wpa_data):.1f}% to {max(cfbd_wpa_data):.1f}%")
    print(f"  ESPN data points: {len(espn_wpa_data)}")
    print(f"  CFBD data points: {len(cfbd_wpa_data)}")
    print(f"  ✅ Both datasets now have exactly 159 plays for direct comparison")

if __name__ == "__main__":
    create_aligned_wpa_chart()
