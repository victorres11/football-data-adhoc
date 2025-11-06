#!/usr/bin/env python3
"""
Fix ESPN WPA column header
"""

import re

def fix_espn_wpa_header():
    """Fix ESPN WPA column header"""
    
    print("🔍 Fixing ESPN WPA column header...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Fix the duplicate WPA header in ESPN table
    # Look for the pattern: <th>Raw Data</th><th>WPA</th><th>WPA</th>
    espn_duplicate_pattern = r'<th>Raw Data</th><th>WPA</th><th>WPA</th>'
    espn_fixed = r'<th>Raw Data</th><th>WPA</th>'
    html_content = re.sub(espn_duplicate_pattern, espn_fixed, html_content)
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Fixed ESPN WPA column header")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Verify the fix
    print(f"\n📊 Verifying ESPN WPA header...")
    
    # Check for WPA headers
    wpa_headers = re.findall(r'<th>WPA</th>', html_content)
    print(f"Found {len(wpa_headers)} WPA headers")
    
    # Check for duplicate WPA headers
    duplicate_pattern = r'<th>WPA</th><th>WPA</th>'
    duplicates = re.findall(duplicate_pattern, html_content)
    print(f"Found {len(duplicates)} duplicate WPA headers")
    
    if len(duplicates) == 0:
        print("✅ No duplicate WPA headers found")
    else:
        print("❌ Still have duplicate WPA headers")

if __name__ == "__main__":
    fix_espn_wpa_header()
