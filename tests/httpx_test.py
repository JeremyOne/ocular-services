#!/usr/bin/env python3
# filepath: /home/jp/Documents/ocular_agents/tests/test_httpx.py

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..tools.httpx_tool import httpx_scan, HttpxOptions

def main():
    """Test the httpx tool."""
    if len(sys.argv) < 2:
        target = "example.com"
    else:
        target = sys.argv[1]
    
    option = HttpxOptions.BASIC_PROBE
    
    print(f"Testing httpx on {target} with options {option.name}")
    result = httpx_scan(target, option)
    print(result)

if __name__ == "__main__":
    main()