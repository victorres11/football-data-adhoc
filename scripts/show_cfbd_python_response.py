#!/usr/bin/env python3
"""
Show the exact response from CFBD Python client
"""

import json
import cfbd

def show_cfbd_python_response():
    """Show exact CFBD Python client response"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    print("🔍 Showing exact CFBD Python client response...")
    print("=" * 60)
    
    print(f"API Key: {api_key}")
    
    # Configure CFBD library
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = f"Bearer {api_key}"
    configuration.api_key_prefix['Authorization'] = ''
    
    # Create API client
    api_client = cfbd.ApiClient(configuration)
    
    # Test with basic endpoint first
    print("\n🧪 Testing basic endpoint (games)...")
    try:
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=2025, week=8, team='Michigan')
        print(f"✅ Basic endpoint works! Got {len(games)} games")
    except Exception as e:
        print(f"❌ Basic endpoint failed: {e}")
        print(f"Error type: {type(e)}")
        if hasattr(e, 'status'):
            print(f"HTTP Status: {e.status}")
        if hasattr(e, 'reason'):
            print(f"Reason: {e.reason}")
        if hasattr(e, 'body'):
            print(f"Response Body: {e.body}")
        if hasattr(e, 'headers'):
            print(f"Response Headers: {e.headers}")
        return
    
    # Now test win probability
    print("\n🧪 Testing win probability endpoint...")
    try:
        metrics_api = cfbd.MetricsApi(api_client)
        result = metrics_api.get_win_probability(game_id=401752873)
        
        print(f"✅ Success! Got win probability data")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        
        if result:
            print(f"\n📋 Win Probability Data:")
            print(f"Number of entries: {len(result)}")
            
            # Show first entry in detail
            if result:
                first_entry = result[0]
                print(f"\n📋 First Entry:")
                print(f"Type: {type(first_entry)}")
                
                if hasattr(first_entry, '__dict__'):
                    print(f"Attributes: {list(first_entry.__dict__.keys())}")
                    for attr, value in first_entry.__dict__.items():
                        print(f"  {attr}: {value}")
                else:
                    print(f"Value: {first_entry}")
        
    except Exception as e:
        print(f"❌ Win probability failed: {e}")
        print(f"Error type: {type(e)}")
        
        # Show full error details
        if hasattr(e, 'status'):
            print(f"HTTP Status: {e.status}")
        if hasattr(e, 'reason'):
            print(f"Reason: {e.reason}")
        if hasattr(e, 'body'):
            print(f"Response Body: {e.body}")
        if hasattr(e, 'headers'):
            print(f"Response Headers: {e.headers}")
        
        # Try to get the raw response
        if hasattr(e, 'response'):
            print(f"Raw Response: {e.response}")
        
        # Show the full exception details
        print(f"\n📋 Full Exception Details:")
        print(f"Exception: {e}")
        print(f"Exception type: {type(e)}")
        print(f"Exception args: {e.args}")
        
        # Try to get more details about the HTTP response
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response Text: {e.response.text}")
        if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            print(f"Response Status Code: {e.response.status_code}")
        if hasattr(e, 'response') and hasattr(e.response, 'headers'):
            print(f"Response Headers: {e.response.headers}")

if __name__ == "__main__":
    show_cfbd_python_response()
