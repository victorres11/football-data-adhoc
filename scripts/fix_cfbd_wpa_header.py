#!/usr/bin/env python3
"""
Fix CFBD WPA header
"""

import re

def fix_cfbd_wpa_header():
    """Fix CFBD WPA header"""
    
    print("🔍 Fixing CFBD WPA header...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Find and fix CFBD WPA header
    # Look for the CFBD table header pattern
    cfbd_header_pattern = r'<th>Raw Data</th><th>WPA</th>'
    new_cfbd_header = r'<th>Raw Data</th><th>CFBD WPA</th>'
    html_content = re.sub(cfbd_header_pattern, new_cfbd_header, html_content)
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Fixed CFBD WPA header")
    print("📄 File: espn_cfbd_side_by_side_401752873_SORTED.html")
    
    # Verify the fix
    print(f"\n📊 Verifying headers...")
    
    # Check for both WPA headers
    espn_wpa_headers = re.findall(r'<th>ESPN WPA</th>', html_content)
    cfbd_wpa_headers = re.findall(r'<th>CFBD WPA</th>', html_content)
    
    print(f"Found {len(espn_wpa_headers)} ESPN WPA headers")
    print(f"Found {len(cfbd_wpa_headers)} CFBD WPA headers")
    
    if len(espn_wpa_headers) > 0 and len(cfbd_wpa_headers) > 0:
        print("✅ Both WPA headers are properly set")
    else:
        print("❌ WPA headers not properly set")

if __name__ == "__main__":
    fix_cfbd_wpa_header()
