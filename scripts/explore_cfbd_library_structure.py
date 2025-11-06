#!/usr/bin/env python3
"""
Explore CFBD library structure to find win probability functionality
"""

import json
import cfbd

def explore_cfbd_library_structure():
    """Explore CFBD library structure"""
    
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
    
    print("🔍 Exploring CFBD library structure...")
    print("=" * 60)
    
    # Get all available API classes
    print("📋 Available CFBD API classes:")
    api_classes = [attr for attr in dir(cfbd) if not attr.startswith('_') and 'Api' in attr]
    for api_class in api_classes:
        print(f"  {api_class}")
    
    print(f"\n🔍 Checking each API class for win probability methods...")
    
    # Check each API class
    for api_class_name in api_classes:
        print(f"\n📋 {api_class_name}:")
        
        try:
            # Get the API class
            api_class = getattr(cfbd, api_class_name)
            api_instance = api_class(cfbd.ApiClient(configuration))
            
            # Get all methods
            methods = [method for method in dir(api_instance) if not method.startswith('_')]
            
            # Look for win probability related methods
            wp_methods = [method for method in methods if 'win' in method.lower() or 'prob' in method.lower()]
            
            if wp_methods:
                print(f"  ✅ Win probability methods: {wp_methods}")
                
                # Try to call the method
                for method_name in wp_methods:
                    print(f"\n  🧪 Testing {method_name}...")
                    try:
                        method = getattr(api_instance, method_name)
                        
                        # Try different parameter combinations
                        test_params = [
                            {'game_id': 401752873},
                            {'gameId': 401752873},
                            {'game_id': 401752873, 'year': 2025},
                            {'gameId': 401752873, 'year': 2025},
                            {'game_id': 401752873, 'year': 2025, 'week': 8},
                            {'gameId': 401752873, 'year': 2025, 'week': 8}
                        ]
                        
                        for params in test_params:
                            try:
                                result = method(**params)
                                print(f"    ✅ Success with {params}!")
                                print(f"    Result type: {type(result)}")
                                print(f"    Result: {result}")
                                return result
                            except Exception as e:
                                print(f"    ❌ Failed with {params}: {e}")
                                
                    except Exception as e:
                        print(f"    ❌ Error calling {method_name}: {e}")
            else:
                print(f"  ❌ No win probability methods found")
                
        except Exception as e:
            print(f"  ❌ Error with {api_class_name}: {e}")
    
    # Check if there's a separate win probability module
    print(f"\n🔍 Checking for separate win probability module...")
    
    try:
        # Check if there's a win probability specific module
        if hasattr(cfbd, 'WinProbabilityApi'):
            print(f"  ✅ Found WinProbabilityApi!")
            wp_api = cfbd.WinProbabilityApi(cfbd.ApiClient(configuration))
            methods = [method for method in dir(wp_api) if not method.startswith('_')]
            print(f"  Methods: {methods}")
        else:
            print(f"  ❌ No WinProbabilityApi found")
    except Exception as e:
        print(f"  ❌ Error checking WinProbabilityApi: {e}")
    
    # Check the main cfbd module for win probability functions
    print(f"\n🔍 Checking main cfbd module for win probability functions...")
    
    try:
        all_attributes = [attr for attr in dir(cfbd) if not attr.startswith('_')]
        wp_attributes = [attr for attr in all_attributes if 'win' in attr.lower() or 'prob' in attr.lower()]
        
        if wp_attributes:
            print(f"  ✅ Found win probability attributes: {wp_attributes}")
        else:
            print(f"  ❌ No win probability attributes found")
            
        print(f"  All attributes: {all_attributes}")
        
    except Exception as e:
        print(f"  ❌ Error checking main module: {e}")
    
    print(f"\n📋 Summary:")
    print(f"  CFBD library structure explored")
    print(f"  Check results above for win probability functionality")
    
    return None

if __name__ == "__main__":
    explore_cfbd_library_structure()
