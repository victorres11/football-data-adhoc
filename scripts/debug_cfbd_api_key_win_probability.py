#!/usr/bin/env python3
"""
Debug CFBD API key and win probability endpoint access
"""

import json
import cfbd

def debug_cfbd_api_key_win_probability():
    """Debug CFBD API key and win probability access"""
    
    # Load API key
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    print("🔍 Debugging CFBD API key and win probability access...")
    print("=" * 60)
    
    print(f"API Key: {api_key[:10]}...")
    print(f"Base URL: {base_url}")
    
    # Configure CFBD library
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = api_key
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    configuration.host = base_url
    
    # Test with a simple endpoint first
    print(f"\n🧪 Testing API key with simple endpoint (games)...")
    
    try:
        games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))
        games = games_api.get_games(year=2025, week=8, team='Michigan')
        
        print(f"✅ API key works! Got {len(games)} games")
        
        # Find our target game
        target_game = None
        for game in games:
            if game.id == 401752873:
                target_game = game
                break
        
        if target_game:
            print(f"✅ Found target game: {target_game.away_team} @ {target_game.home_team}")
        else:
            print(f"❌ Target game not found")
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        print(f"This suggests the API key might be invalid or expired")
        return
    
    # Now test win probability with working API key
    print(f"\n🧪 Testing win probability with working API key...")
    
    try:
        metrics_api = cfbd.MetricsApi(cfbd.ApiClient(configuration))
        
        # Try get_win_probability
        try:
            result = metrics_api.get_win_probability(game_id=401752873)
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
            
            # Check if it's a specific error about the game
            if "not found" in str(e).lower() or "invalid" in str(e).lower():
                print(f"  This might mean the game doesn't have win probability data")
            elif "unauthorized" in str(e).lower():
                print(f"  This suggests win probability endpoint requires different permissions")
            elif "forbidden" in str(e).lower():
                print(f"  This suggests win probability endpoint is restricted")
            
            # Try pregame win probabilities as fallback
            try:
                result = metrics_api.get_pregame_win_probabilities(year=2025, week=8)
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
                print(f"Error type: {type(e2)}")
                
    except Exception as e:
        print(f"❌ Error creating MetricsApi: {e}")
    
    print(f"\n📋 Summary:")
    print(f"  API key works for basic endpoints")
    print(f"  Win probability endpoint may require special permissions")
    print(f"  Or the game may not have win probability data available")
    
    return None

if __name__ == "__main__":
    debug_cfbd_api_key_win_probability()
