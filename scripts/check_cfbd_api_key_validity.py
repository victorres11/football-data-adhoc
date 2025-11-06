#!/usr/bin/env python3
"""
Check CFBD API key validity and try different authentication methods
"""

import json
import requests

def check_cfbd_api_key_validity():
    """Check CFBD API key validity"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    print("🔍 Checking CFBD API key validity...")
    print("=" * 60)
    
    print(f"API Key: {api_key[:10]}...")
    print(f"Base URL: {base_url}")
    
    # Try different authentication methods with direct HTTP requests
    auth_methods = [
        {
            'name': 'Bearer Token in Header',
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        },
        {
            'name': 'API Key in Header',
            'headers': {
                'Authorization': api_key,
                'Content-Type': 'application/json'
            }
        },
        {
            'name': 'X-API-Key Header',
            'headers': {
                'X-API-Key': api_key,
                'Content-Type': 'application/json'
            }
        },
        {
            'name': 'API Key as Query Parameter',
            'headers': {
                'Content-Type': 'application/json'
            },
            'params': {
                'key': api_key
            }
        }
    ]
    
    for method in auth_methods:
        print(f"\n🧪 Testing: {method['name']}")
        
        try:
            # Test with a simple endpoint
            response = requests.get(f"{base_url}/games", headers=method['headers'], params=method.get('params', {}))
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Success! API key works with this method")
                data = response.json()
                print(f"Got {len(data)} games")
                
                # Now try win probability endpoint
                print(f"\n🧪 Testing win probability endpoint...")
                wp_response = requests.get(f"{base_url}/winprobability", headers=method['headers'], params={
                    'gameId': 401752873,
                    **method.get('params', {})
                })
                
                print(f"Win Probability Status: {wp_response.status_code}")
                
                if wp_response.status_code == 200:
                    try:
                        wp_data = wp_response.json()
                        print(f"✅ Win probability data retrieved!")
                        print(f"Data type: {type(wp_data)}")
                        print(f"Data length: {len(wp_data) if isinstance(wp_data, list) else 'N/A'}")
                        
                        if wp_data:
                            print(f"Sample data: {wp_data[0] if isinstance(wp_data, list) else wp_data}")
                            return wp_data
                    except json.JSONDecodeError:
                        print(f"❌ Win probability response is not JSON: {wp_response.text[:200]}...")
                else:
                    print(f"❌ Win probability failed: {wp_response.text[:200]}...")
                
                return data
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📋 Summary:")
    print(f"  API key may be invalid or expired")
    print(f"  CFBD may require a new API key")
    print(f"  Win probability endpoint may not be available")
    
    return None

if __name__ == "__main__":
    check_cfbd_api_key_validity()
