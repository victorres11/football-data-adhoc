#!/usr/bin/env python3
"""
Test CFBD with access_token method
"""

import json
import cfbd

def test_cfbd_access_token():
    """Test CFBD with access_token method"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    print("🔍 Testing CFBD with access_token method...")
    print("=" * 60)
    
    print(f"API Key: {api_key}")
    
    try:
        # Test the access_token method
        configuration = cfbd.Configuration(
            access_token = api_key
        )
        
        with cfbd.ApiClient(configuration) as api_client:
            api_instance = cfbd.GamesApi(api_client)
            games = api_instance.get_games(year=2025)
            
            print(f"✅ Success! Got {len(games)} games")
            if games:
                print(f"First game: {games[0]}")
                
    except Exception as e:
        print(f"❌ Failed: {e}")
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

if __name__ == "__main__":
    test_cfbd_access_token()
