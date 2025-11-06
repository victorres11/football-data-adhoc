#!/usr/bin/env python3
"""
Get CFBD win probability data for game 401752873
"""

import json
import cfbd

def get_cfbd_win_probability():
    """Get CFBD win probability data for game 401752873"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    print("🔍 Getting CFBD win probability data for game 401752873...")
    
    try:
        # Configure CFBD with access_token method
        configuration = cfbd.Configuration(access_token=api_key)
        
        with cfbd.ApiClient(configuration) as api_client:
            # Get win probability data
            metrics_api = cfbd.MetricsApi(api_client)
            win_prob_data = metrics_api.get_win_probability(game_id=401752873)
            
            print(f"✅ Success! Got {len(win_prob_data)} win probability entries")
            
            # Convert to JSON-serializable format
            win_prob_json = []
            for entry in win_prob_data:
                win_prob_json.append({
                    'game_id': entry.game_id,
                    'play_id': entry.play_id,
                    'play_text': entry.play_text,
                    'home_id': entry.home_id,
                    'home': entry.home,
                    'away_id': entry.away_id,
                    'away': entry.away,
                    'spread': entry.spread,
                    'home_ball': entry.home_ball,
                    'home_score': entry.home_score,
                    'away_score': entry.away_score,
                    'yard_line': entry.yard_line,
                    'down': entry.down,
                    'distance': entry.distance,
                    'home_win_probability': entry.home_win_probability,
                    'play_number': entry.play_number
                })
            
            # Save to file
            with open('cfbd_win_probability_401752873.json', 'w') as f:
                json.dump(win_prob_json, f, indent=2)
            
            print(f"💾 Saved win probability data to cfbd_win_probability_401752873.json")
            
            return win_prob_json
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

if __name__ == "__main__":
    get_cfbd_win_probability()
