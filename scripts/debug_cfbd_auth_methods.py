#!/usr/bin/env python3
"""
Debug CFBD authentication methods
"""

import json
import cfbd

def debug_cfbd_auth_methods():
    """Try different authentication methods"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    print("🔍 Debugging CFBD authentication methods...")
    print("=" * 60)
    
    print(f"API Key: {api_key}")
    
    # Method 1: Bearer in key
    print("\n🧪 Method 1: Bearer in key")
    try:
        configuration = cfbd.Configuration()
        configuration.api_key['Authorization'] = f"Bearer {api_key}"
        configuration.api_key_prefix['Authorization'] = ''
        
        api_client = cfbd.ApiClient(configuration)
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=2025, week=8, team='Michigan')
        print(f"✅ Method 1 works! Got {len(games)} games")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Separate Bearer prefix
    print("\n🧪 Method 2: Separate Bearer prefix")
    try:
        configuration = cfbd.Configuration()
        configuration.api_key['Authorization'] = api_key
        configuration.api_key_prefix['Authorization'] = 'Bearer'
        
        api_client = cfbd.ApiClient(configuration)
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=2025, week=8, team='Michigan')
        print(f"✅ Method 2 works! Got {len(games)} games")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Different header name
    print("\n🧪 Method 3: Different header name")
    try:
        configuration = cfbd.Configuration()
        configuration.api_key['X-API-Key'] = api_key
        configuration.api_key_prefix['X-API-Key'] = ''
        
        api_client = cfbd.ApiClient(configuration)
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=2025, week=8, team='Michigan')
        print(f"✅ Method 3 works! Got {len(games)} games")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Method 4: Query parameter
    print("\n🧪 Method 4: Query parameter")
    try:
        configuration = cfbd.Configuration()
        configuration.api_key['api_key'] = api_key
        configuration.api_key_prefix['api_key'] = ''
        
        api_client = cfbd.ApiClient(configuration)
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=2025, week=8, team='Michigan')
        print(f"✅ Method 4 works! Got {len(games)} games")
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
    
    # Method 5: Check what the library is actually sending
    print("\n🧪 Method 5: Check actual request")
    try:
        configuration = cfbd.Configuration()
        configuration.api_key['Authorization'] = f"Bearer {api_key}"
        configuration.api_key_prefix['Authorization'] = ''
        
        # Enable debug logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        api_client = cfbd.ApiClient(configuration)
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=2025, week=8, team='Michigan')
        print(f"✅ Method 5 works! Got {len(games)} games")
    except Exception as e:
        print(f"❌ Method 5 failed: {e}")
        print(f"Error details: {e}")

if __name__ == "__main__":
    debug_cfbd_auth_methods()
