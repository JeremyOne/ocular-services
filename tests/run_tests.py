"""Test runner for all unit tests"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test modules
from tests import (
    test_service_response,
    test_ping_service,
    test_dns_service,
    test_whois_service,
    test_curl_service,
    test_nmap_service,
    test_httpx_service,
    test_nbtscan_service,
    test_nikto_service,
    test_wpscan_service
)


def run_all_tests():
    """Run all unit tests and display results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test modules
    suite.addTests(loader.loadTestsFromModule(test_service_response))
    suite.addTests(loader.loadTestsFromModule(test_ping_service))
    suite.addTests(loader.loadTestsFromModule(test_dns_service))
    suite.addTests(loader.loadTestsFromModule(test_whois_service))
    suite.addTests(loader.loadTestsFromModule(test_curl_service))
    suite.addTests(loader.loadTestsFromModule(test_nmap_service))
    suite.addTests(loader.loadTestsFromModule(test_httpx_service))
    suite.addTests(loader.loadTestsFromModule(test_nbtscan_service))
    suite.addTests(loader.loadTestsFromModule(test_nikto_service))
    suite.addTests(loader.loadTestsFromModule(test_wpscan_service))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
