#!/usr/bin/env python3

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.wpscan_tool import wpscan_scan, WpScanOptions

def main():
    """Test the wpscan tool."""
    if len(sys.argv) < 2:
        print("Usage: python test_wpscan.py <wordpress_url>")
        print("Example: python test_wpscan.py https://example.com")
        sys.exit(1)
    
    target = sys.argv[1]
    option = WpScanOptions.BASIC_SCAN  # Use basic scan for testing
    
    print(f"Testing wpscan on {target} with options {option.name}")
    result = wpscan_scan(target, option)
    print(result)

if __name__ == "__main__":
    main()
