#!/usr/bin/env python3
"""
Test CFBD library get_win_probability function
"""

import json
import cfbd

def test_cfbd_library_win_probability():
    """Test CFBD library get_win_probability function"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    # Configure CFBD library
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = api_key
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    configuration.host = base_url
    
    print("🔍 Testing CFBD library get_win_probability function...")
    print("=" * 60)
    
    # Create API instance
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    
    try:
        print("🧪 Testing get_win_probability with game ID 401752873...")
        
        # Try different parameter combinations
        test_cases = [
            {
                'name': 'Game ID only',
                'game_id': 401752873
            },
            {
                'name': 'Game ID + year',
                'game_id': 401752873,
                'year': 2025
            },
            {
                'name': 'Game ID + year + week',
                'game_id': 401752873,
                'year': 2025,
                'week': 8
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            print(f"Parameters: {test_case}")
            
            try:
                # Call the get_win_probability function
                result = api_instance.get_win_probability(**test_case)
                
                print(f"✅ Success! Got win probability data")
                print(f"Result type: {type(result)}")
                print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
                
                if result:
                    print(f"Sample result: {result[0] if isinstance(result, list) else result}")
                    
                    # Show first few entries
                    if isinstance(result, list):
                        print(f"\n📋 First 5 win probability entries:")
                        for i, entry in enumerate(result[:5]):
                            print(f"  {i+1}. {entry}")
                    
                    return result
                else:
                    print(f"❌ Empty result")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                print(f"Error type: {type(e)}")
        
        # Try alternative approach - get win probability by team
        print(f"\n🧪 Testing get_win_probability by team...")
        
        try:
            result = api_instance.get_win_probability(team='Michigan', year=2025, week=8)
            print(f"✅ Success with team parameter!")
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
            
            if result:
                print(f"Sample result: {result[0] if isinstance(result, list) else result}")
                return result
                
        except Exception as e:
            print(f"❌ Error with team parameter: {e}")
        
        # Try to get all available methods
        print(f"\n🔍 Available methods in GamesApi:")
        methods = [method for method in dir(api_instance) if not method.startswith('_')]
        print(f"  {methods}")
        
        # Check if there are other win probability related methods
        wp_methods = [method for method in methods if 'win' in method.lower() or 'prob' in method.lower()]
        print(f"\n🔍 Win probability related methods: {wp_methods}")
        
    except Exception as e:
        print(f"❌ Error creating API instance: {e}")
        print(f"Error type: {type(e)}")
    
    print(f"\n📋 Summary:")
    print(f"  CFBD library get_win_probability function tested")
    print(f"  Check results above for actual data structure")
    
    return None

if __name__ == "__main__":
    test_cfbd_library_win_probability()
