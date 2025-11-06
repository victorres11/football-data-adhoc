#!/usr/bin/env python3
"""
Create enhanced comparison with win probability chart
"""

import json
import re

def create_enhanced_comparison_with_chart():
    """Create enhanced comparison with win probability chart"""
    
    print("🔍 Creating enhanced comparison with win probability chart...")
    
    # Load win probability data
    with open('cfbd_win_probability_401752873.json', 'r') as f:
        win_prob_data = json.load(f)
    
    print(f"📊 Loaded {len(win_prob_data)} win probability entries")
    
    # Load existing HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Add Chart.js and win probability chart
    chart_section = """
    <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
        <h3>📊 Win Probability Chart</h3>
        <canvas id="winProbabilityChart" width="800" height="400"></canvas>
        
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Prepare win probability data
            const winProbData = """ + json.dumps(win_prob_data) + """;
            
            // Extract data for chart
            const playNumbers = winProbData.map(entry => entry.play_number);
            const homeWinProbs = winProbData.map(entry => entry.home_win_probability * 100);
            const playTexts = winProbData.map(entry => entry.play_text);
            
            // Create chart
            const ctx = document.getElementById('winProbabilityChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: playNumbers,
                    datasets: [{
                        label: 'Michigan Win Probability (%)',
                        data: homeWinProbs,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Michigan vs Washington - Win Probability Over Time'
                        },
                        tooltip: {
                            callbacks: {
                                afterLabel: function(context) {
                                    const index = context.dataIndex;
                                    return 'Play: ' + playTexts[index];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Play Number'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Win Probability (%)'
                            },
                            min: 0,
                            max: 100
                        }
                    }
                }
            });
        </script>
    </div>
    """
    
    # Insert the chart section before the closing body tag
    html_content = html_content.replace('</body>', chart_section + '</body>')
    
    # Save enhanced HTML
    with open('espn_cfbd_side_by_side_401752873_ENHANCED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created enhanced comparison with win probability chart")
    print("📄 File: espn_cfbd_side_by_side_401752873_ENHANCED.html")

if __name__ == "__main__":
    create_enhanced_comparison_with_chart()
