#!/usr/bin/env python3
"""
Test API key with direct HTTP request
"""

import json
import requests

def test_api_key_direct():
    """Test API key with direct HTTP request"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    
    print("🔍 Testing API key with direct HTTP request...")
    print("=" * 60)
    
    print(f"API Key: {api_key}")
    
    # Test with direct HTTP request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    url = 'https://api.collegefootballdata.com/games'
    params = {
        'year': 2025,
        'week': 8,
        'team': 'Michigan'
    }
    
    print(f"\n🧪 Testing direct HTTP request...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"\n📋 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {len(data)} games")
            if data:
                print(f"First game: {data[0]}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_key_direct()
