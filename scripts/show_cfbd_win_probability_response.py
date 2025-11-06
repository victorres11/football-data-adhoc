#!/usr/bin/env python3
"""
Show actual CFBD win probability endpoint response
"""

import json
import requests

def show_cfbd_win_probability_response():
    """Show actual CFBD win probability response"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Getting actual CFBD win probability response...")
    print("=" * 60)
    
    # Try the win probability endpoint
    try:
        response = requests.get(f"{base_url}/winprobability", headers=headers, params={
            'gameId': 401752873
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print()
        
        print("Raw Response (first 1000 characters):")
        print("-" * 40)
        print(response.text[:1000])
        print("-" * 40)
        
        if response.status_code == 200:
            # Try to parse as JSON
            try:
                data = response.json()
                print(f"\n✅ Successfully parsed as JSON!")
                print(f"Data type: {type(data)}")
                print(f"Data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON decode error: {e}")
                print(f"This suggests the endpoint returns HTML instead of JSON")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🔍 Trying with different parameters...")
    
    # Try with year parameter
    try:
        response = requests.get(f"{base_url}/winprobability", headers=headers, params={
            'year': 2025,
            'week': 8
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response (first 500 chars): {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ Found win probability data!")
                print(f"Number of entries: {len(data) if isinstance(data, list) else 'Not a list'}")
                if isinstance(data, list) and data:
                    print(f"Sample entry: {json.dumps(data[0], indent=2)}")
                return data
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🔍 Trying to find any working win probability endpoint...")
    
    # Try different endpoint variations
    endpoints = [
        f"{base_url}/winprobability",
        f"{base_url}/win-probability", 
        f"{base_url}/games/winprobability",
        f"{base_url}/plays/winprobability"
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Trying: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, params={'year': 2025})
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON response!")
                    print(f"Type: {type(data)}")
                    if isinstance(data, list):
                        print(f"Entries: {len(data)}")
                        if data:
                            print(f"Sample: {json.dumps(data[0], indent=2)}")
                    else:
                        print(f"Data: {json.dumps(data, indent=2)}")
                    return data
                except:
                    print(f"❌ Not JSON: {response.text[:200]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📋 Summary:")
    print(f"  CFBD win probability endpoint may not exist")
    print(f"  Or it may require different parameters")
    print(f"  ESPN has working win probability endpoint")
    print(f"  CFBD focuses on PPA and advanced metrics")
    
    return None

if __name__ == "__main__":
    show_cfbd_win_probability_response()
