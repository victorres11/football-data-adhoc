#!/usr/bin/env python3
"""
Test CFBD win probability with fixed authentication
"""

import json
import cfbd

def test_cfbd_win_probability_fixed_auth():
    """Test CFBD win probability with fixed authentication"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    print("🔍 Testing CFBD win probability with fixed authentication...")
    print("=" * 60)
    
    print(f"API Key: {api_key[:10]}...")
    
    # Try different authentication configurations
    auth_configs = [
        {
            'name': 'Standard Bearer',
            'api_key': api_key,
            'prefix': 'Bearer'
        },
        {
            'name': 'Bearer in key',
            'api_key': f'Bearer {api_key}',
            'prefix': None
        },
        {
            'name': 'No prefix',
            'api_key': api_key,
            'prefix': None
        }
    ]
    
    for config_method in auth_configs:
        print(f"\n🧪 Testing: {config_method['name']}")
        
        try:
            # Configure CFBD library
            configuration = cfbd.Configuration()
            configuration.api_key['Authorization'] = config_method['api_key']
            if config_method['prefix']:
                configuration.api_key_prefix['Authorization'] = config_method['prefix']
            
            # Create API client
            api_client = cfbd.ApiClient(configuration)
            
            # Test with a simple endpoint first
            print(f"  Testing basic endpoint...")
            games_api = cfbd.GamesApi(api_client)
            games = games_api.get_games(year=2025, week=8, team='Michigan')
            print(f"  ✅ Basic endpoint works! Got {len(games)} games")
            
            # Now test win probability
            print(f"  Testing win probability...")
            metrics_api = cfbd.MetricsApi(api_client)
            result = metrics_api.get_win_probability(game_id=401752873)
            
            print(f"  ✅ Success! Got win probability data")
            print(f"  Result type: {type(result)}")
            print(f"  Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
            
            if result:
                print(f"\n📋 Win Probability Data:")
                if isinstance(result, list):
                    print(f"Number of entries: {len(result)}")
                    
                    # Show first few entries
                    for i, entry in enumerate(result[:3]):
                        print(f"\n  Entry {i+1}:")
                        print(f"    Type: {type(entry)}")
                        
                        if hasattr(entry, '__dict__'):
                            print(f"    Attributes: {list(entry.__dict__.keys())}")
                            for attr, value in entry.__dict__.items():
                                print(f"      {attr}: {value}")
                        else:
                            print(f"    Value: {entry}")
                    
                    # Show the structure of the first entry in detail
                    if result:
                        first_entry = result[0]
                        print(f"\n📋 First Entry Detailed Structure:")
                        print(f"  Type: {type(first_entry)}")
                        
                        if hasattr(first_entry, '__dict__'):
                            for attr, value in first_entry.__dict__.items():
                                print(f"    {attr}: {value} (type: {type(value)})")
                        
                        # Check if it has the expected win probability fields
                        if hasattr(first_entry, 'home_win_probability'):
                            print(f"\n✅ Found home_win_probability: {first_entry.home_win_probability}")
                        if hasattr(first_entry, 'away_win_probability'):
                            print(f"✅ Found away_win_probability: {first_entry.away_win_probability}")
                        if hasattr(first_entry, 'play_id'):
                            print(f"✅ Found play_id: {first_entry.play_id}")
                        if hasattr(first_entry, 'play_number'):
                            print(f"✅ Found play_number: {first_entry.play_number}")
                
                return result
            else:
                print(f"  ❌ Empty result")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print(f"  Error type: {type(e)}")
            
            # Try to get more details about the error
            if hasattr(e, 'status'):
                print(f"  HTTP Status: {e.status}")
            if hasattr(e, 'reason'):
                print(f"  Reason: {e.reason}")
            if hasattr(e, 'body'):
                print(f"  Response Body: {e.body}")
    
    print(f"\n📋 Summary:")
    print(f"  CFBD win probability tested with various authentication methods")
    print(f"  Check results above for successful data retrieval")
    
    return None

if __name__ == "__main__":
    test_cfbd_win_probability_fixed_auth()
