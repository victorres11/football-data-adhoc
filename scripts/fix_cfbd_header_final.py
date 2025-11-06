#!/usr/bin/env python3
"""
Fix CFBD header to show CFBD WPA
"""

import re

def fix_cfbd_header_final():
    """Fix CFBD header to show CFBD WPA"""
    
    print("🔍 Fixing CFBD header to show CFBD WPA...")
    
    # Load HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'r') as f:
        html_content = f.read()
    
    # Fix the CFBD table header (the second occurrence)
    # Look for the pattern in the CFBD table section
    cfbd_header_pattern = r'<th>Raw Data</th><th>ESPN WPA</th>'
    new_cfbd_header = r'<th>Raw Data</th><th>CFBD WPA</th>'
    
    # Replace only the second occurrence (CFBD table)
    matches = list(re.finditer(cfbd_header_pattern, html_content))
    if len(matches) >= 2:
        # Replace the second occurrence (CFBD table)
        second_match = matches[1]
        html_content = html_content[:second_match.start()] + new_cfbd_header + html_content[second_match.end():]
        print("✅ Fixed CFBD header to show CFBD WPA")
    else:
        print("❌ Could not find second occurrence of Raw Data header")
    
    # Save updated HTML
    with open('espn_cfbd_side_by_side_401752873_SORTED.html', 'w') as f:
        f.write(html_content)
    
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
    fix_cfbd_header_final()
