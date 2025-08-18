#!/usr/bin/env python3

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.whois_tool import whois_lookup, WhoisOptions

def main():
    """Test the whois tool."""
    if len(sys.argv) < 2:
        print("Usage: python test_whois.py <domain>")
        print("Example: python test_whois.py example.com")
        sys.exit(1)
    
    domain = sys.argv[1]
    option = WhoisOptions.BASIC_WHOIS  # Use basic whois for testing
    
    print(f"Testing whois lookup on domain: {domain}")
    print(f"Using option: {option.name}")
    print("=" * 50)
    result = whois_lookup(domain, option)
    print(result)

if __name__ == "__main__":
    main()
