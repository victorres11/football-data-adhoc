# ESPN College Football API Guide

## Overview

This guide documents the two different ESPN API endpoints used for college football game data and explains why we prefer the internal endpoint for future development.

## API Endpoints

### 1. Public API (`site.api.espn.com`) - Legacy
**Endpoint**: `http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}`

**Data Structure**:
```json
{
  "drives": {
    "previous": [
      {
        "id": "4017528662",
        "description": "6 plays, 15 yards, 2:29",
        "plays": [
          {
            "id": "401752866101849902",
            "text": "Gabriel Nwosu kickoff for 65 yds for a touchback",
            "clock": {"displayValue": "15:00"},
            "wallclock": "2025-10-11T19:38:10Z"
          }
        ]
      }
    ],
    "current": []
  }
}
```

**Characteristics**:
- ✅ Complete game data (144 plays for Northwestern)
- ❌ Complex nested structure (plays embedded in drives)
- ❌ Requires complex extraction logic
- ❌ Inconsistent data organization
- ❌ Harder to maintain

### 2. Internal API (`sports.core.api.espn.com`) - Preferred
**Endpoint**: `https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays`

**Data Structure**:
```json
{
  "count": 147,
  "pageIndex": 1,
  "pageSize": 25,
  "pageCount": 6,
  "items": [
    {
      "id": "401752866101849901",
      "text": "PSU wins the toss and chooses endzone...",
      "clock": {"value": 900.0, "displayValue": "15:00"},
      "wallclock": "2025-10-11T19:38:10Z"
    }
  ]
}
```

**Characteristics**:
- ✅ Complete game data (147 plays for Northwestern - includes pre/post game)
- ✅ Simple flat structure (direct access to plays)
- ✅ Consistent with Michigan data structure
- ✅ Better timestamp format (`clock.value` + `displayValue`)
- ✅ Pagination support for large datasets
- ✅ Easier to maintain and debug

## Why We Prefer the Internal API

### 1. **Unified Data Structure**
Both Northwestern and Michigan games use the same `plays.items[]` structure when fetched from the internal API, eliminating the need for different extraction logic.

### 2. **Better Data Quality**
- More complete data (includes pre-game and post-game events)
- Better timestamp format with both `value` (seconds) and `displayValue` (MM:SS)
- Consistent field names across all games

### 3. **Simpler Code**
```python
# Internal API - Simple extraction
def extract_plays_internal(game_data):
    return game_data.get('plays', {}).get('items', [])

# Public API - Complex extraction
def extract_plays_public(game_data):
    plays = []
    drives = game_data.get('drives', {})
    for drive_list in [drives.get('previous', []), drives.get('current', [])]:
        for drive in drive_list:
            plays.extend(drive.get('plays', []))
    return plays
```

### 4. **Future-Proof**
The internal API is more likely to be maintained and updated by ESPN, while the public API may be deprecated.

## Data Structure Comparison

| Aspect | Public API | Internal API |
|--------|------------|--------------|
| **Plays Access** | `drives.previous[].plays[]` | `plays.items[]` |
| **Extraction** | Complex nested loops | Direct access |
| **Consistency** | Varies by game | Consistent across games |
| **Completeness** | Game plays only | Game + pre/post events |
| **Timestamps** | `clock.displayValue` only | `clock.value` + `displayValue` |
| **Maintenance** | High complexity | Low complexity |

## Implementation Guide

### For Future Development

1. **Always use the internal API** for new games:
   ```python
   def fetch_game_data(game_id):
       url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays"
       response = requests.get(url)
       return response.json()
   ```

2. **Handle pagination** for complete data:
   ```python
   def fetch_all_plays(game_id):
       all_plays = []
       page = 1
       while True:
           url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/events/{game_id}/competitions/{game_id}/plays?page={page}&pageSize=50"
           response = requests.get(url)
           data = response.json()
           
           if 'items' not in data:
               break
               
           all_plays.extend(data['items'])
           
           if page >= data.get('pageCount', 1):
               break
               
           page += 1
           
       return all_plays
   ```

3. **Use unified extraction logic**:
   ```python
   def extract_plays_unified(game_data):
       """Extract plays from either data structure"""
       # Check if it's the internal API structure
       if 'plays' in game_data and 'items' in game_data.get('plays', {}):
           return game_data['plays']['items']
       
       # Check if it's the public API structure (legacy support)
       elif 'drives' in game_data:
           plays = []
           drives = game_data.get('drives', {})
           for drive_list in [drives.get('previous', []), drives.get('current', [])]:
               for drive in drive_list:
                   plays.extend(drive.get('plays', []))
           return plays
       
       return []
   ```

## Migration Strategy

### For Existing Games
1. **Northwestern (401752866)**: Currently uses public API - consider migrating to internal API
2. **Michigan (401752873)**: Already uses internal API - keep as is
3. **Future games**: Always use internal API

### Backward Compatibility
Maintain support for both data structures in extraction functions to handle existing data files.

## Common Pitfalls to Avoid

1. **Don't assume all games use the same structure** - always check the data structure first
2. **Don't hardcode extraction logic** - use the unified extraction function
3. **Don't ignore pagination** - the internal API uses pagination for large datasets
4. **Don't mix data sources** - stick to one API endpoint per game for consistency

## File Naming Convention

- **Internal API data**: `{game_id}_internal_plays.json`
- **Public API data**: `{game_id}_public_data.json`
- **Unified extraction**: `extract_plays_unified.py`

## Testing

Always test with both data structures to ensure compatibility:

```python
def test_extraction():
    # Test with internal API structure
    internal_data = {"plays": {"items": [{"id": "1", "text": "Test play"}]}}
    assert len(extract_plays_unified(internal_data)) == 1
    
    # Test with public API structure
    public_data = {"drives": {"previous": [{"plays": [{"id": "1", "text": "Test play"}]}]}}
    assert len(extract_plays_unified(public_data)) == 1
```

## Conclusion

The internal API (`sports.core.api.espn.com`) is the preferred choice for future development due to its:
- Unified data structure across all games
- Better data quality and completeness
- Simpler extraction logic
- Future-proof design

Always use the internal API for new games and maintain backward compatibility for existing data.
