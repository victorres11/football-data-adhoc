#!/usr/bin/env python3
"""
Fix CFBD authentication and test win probability with correct API key format
"""

import json
import cfbd

def fix_cfbd_authentication_win_probability():
    """Fix CFBD authentication and test win probability"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    print("🔍 Fixing CFBD authentication for win probability...")
    print("=" * 60)
    
    print(f"API Key: {api_key[:10]}...")
    print(f"Base URL: {base_url}")
    
    # Try different authentication methods
    auth_methods = [
        {
            'name': 'Method 1: Bearer prefix in key',
            'api_key': f'Bearer {api_key}',
            'prefix': 'Bearer'
        },
        {
            'name': 'Method 2: Bearer prefix in configuration',
            'api_key': api_key,
            'prefix': 'Bearer'
        },
        {
            'name': 'Method 3: No prefix',
            'api_key': api_key,
            'prefix': None
        }
    ]
    
    for method in auth_methods:
        print(f"\n🧪 Testing: {method['name']}")
        
        try:
            # Configure CFBD library
            configuration = cfbd.Configuration()
            configuration.api_key['Authorization'] = method['api_key']
            if method['prefix']:
                configuration.api_key_prefix['Authorization'] = method['prefix']
            configuration.host = base_url
            
            # Create MetricsApi instance
            api_instance = cfbd.MetricsApi(cfbd.ApiClient(configuration))
            
            # Test get_win_probability
            try:
                result = api_instance.get_win_probability(game_id=401752873)
                
                print(f"✅ Success! Got win probability data")
                print(f"Result type: {type(result)}")
                print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
                
                if result:
                    print(f"\n📋 Win Probability Data:")
                    if isinstance(result, list):
                        print(f"Number of entries: {len(result)}")
                        for i, entry in enumerate(result[:3]):  # Show first 3 entries
                            print(f"  {i+1}. {entry}")
                            
                        # Show the structure of the first entry
                        if result:
                            first_entry = result[0]
                            print(f"\n📋 First entry structure:")
                            print(f"  Type: {type(first_entry)}")
                            if hasattr(first_entry, '__dict__'):
                                print(f"  Attributes: {list(first_entry.__dict__.keys())}")
                                for attr, value in first_entry.__dict__.items():
                                    print(f"    {attr}: {value}")
                            else:
                                print(f"  Value: {first_entry}")
                    
                    return result
                else:
                    print(f"❌ Empty result")
                    
            except Exception as e:
                print(f"❌ Error with get_win_probability: {e}")
                print(f"Error type: {type(e)}")
                
                # Try pregame win probabilities as fallback
                try:
                    result = api_instance.get_pregame_win_probabilities(year=2025, week=8)
                    print(f"✅ Fallback success with pregame win probabilities!")
                    print(f"Result type: {type(result)}")
                    print(f"Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
                    
                    if result:
                        print(f"\n📋 Pregame Win Probability Data:")
                        if isinstance(result, list):
                            print(f"Number of entries: {len(result)}")
                            for i, entry in enumerate(result[:3]):  # Show first 3 entries
                                print(f"  {i+1}. {entry}")
                        return result
                    
                except Exception as e2:
                    print(f"❌ Fallback also failed: {e2}")
                    
        except Exception as e:
            print(f"❌ Error with authentication method: {e}")
    
    print(f"\n📋 Summary:")
    print(f"  CFBD authentication methods tested")
    print(f"  Check results above for successful authentication")
    
    return None

if __name__ == "__main__":
    fix_cfbd_authentication_win_probability()
