#!/usr/bin/env python3
"""
Test CFBD MetricsApi get_win_probability function with correct authentication
"""

import json
import cfbd

def test_cfbd_metrics_win_probability():
    """Test CFBD MetricsApi get_win_probability function"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    # Configure CFBD library with correct authentication
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = api_key
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    configuration.host = base_url
    
    print("🔍 Testing CFBD MetricsApi get_win_probability function...")
    print("=" * 60)
    
    # Create MetricsApi instance
    api_instance = cfbd.MetricsApi(cfbd.ApiClient(configuration))
    
    try:
        print("🧪 Testing get_win_probability with correct parameters...")
        
        # Try the get_win_probability function with correct parameters
        # Based on the error, it needs game_id parameter
        try:
            result = api_instance.get_win_probability(game_id=401752873)
            
            print(f"✅ Success! Got win probability data")
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
            
            if result:
                print(f"\n📋 Win Probability Data:")
                if isinstance(result, list):
                    print(f"Number of entries: {len(result)}")
                    for i, entry in enumerate(result[:5]):  # Show first 5 entries
                        print(f"  {i+1}. {entry}")
                else:
                    print(f"Result: {result}")
                
                return result
            else:
                print(f"❌ Empty result")
                
        except Exception as e:
            print(f"❌ Error with get_win_probability: {e}")
            print(f"Error type: {type(e)}")
        
        # Try pregame win probabilities
        print(f"\n🧪 Testing get_pregame_win_probabilities...")
        
        try:
            result = api_instance.get_pregame_win_probabilities(year=2025, week=8)
            
            print(f"✅ Success! Got pregame win probability data")
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
            
            if result:
                print(f"\n📋 Pregame Win Probability Data:")
                if isinstance(result, list):
                    print(f"Number of entries: {len(result)}")
                    for i, entry in enumerate(result[:5]):  # Show first 5 entries
                        print(f"  {i+1}. {entry}")
                else:
                    print(f"Result: {result}")
                
                return result
            else:
                print(f"❌ Empty result")
                
        except Exception as e:
            print(f"❌ Error with get_pregame_win_probabilities: {e}")
            print(f"Error type: {type(e)}")
        
        # Check what parameters the methods actually accept
        print(f"\n🔍 Checking method signatures...")
        
        import inspect
        
        try:
            sig = inspect.signature(api_instance.get_win_probability)
            print(f"get_win_probability signature: {sig}")
        except Exception as e:
            print(f"Error getting signature: {e}")
        
        try:
            sig = inspect.signature(api_instance.get_pregame_win_probabilities)
            print(f"get_pregame_win_probabilities signature: {sig}")
        except Exception as e:
            print(f"Error getting signature: {e}")
        
    except Exception as e:
        print(f"❌ Error creating MetricsApi instance: {e}")
        print(f"Error type: {type(e)}")
    
    print(f"\n📋 Summary:")
    print(f"  CFBD MetricsApi get_win_probability function tested")
    print(f"  Check results above for actual data structure")
    
    return None

if __name__ == "__main__":
    test_cfbd_metrics_win_probability()
