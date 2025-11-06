#!/usr/bin/env python3
"""
Test CFBD win probability with access_token method
"""

import json
import cfbd

def test_cfbd_win_probability_access_token():
    """Test CFBD win probability with access_token method"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    print("🔍 Testing CFBD win probability with access_token method...")
    print("=" * 60)
    
    print(f"API Key: {api_key}")
    
    try:
        # Test the access_token method
        configuration = cfbd.Configuration(
            access_token = api_key
        )
        
        with cfbd.ApiClient(configuration) as api_client:
            # Test win probability endpoint
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
                        
                # Show a few more entries
                print(f"\n📋 Sample Entries:")
                for i, entry in enumerate(result[:3]):
                    print(f"Entry {i+1}: {entry}")
                    
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
    test_cfbd_win_probability_access_token()
