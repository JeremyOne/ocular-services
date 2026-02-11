"""Unit tests for WHOIS service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from whois_service import whois_lookup
from service_response import ServiceResponse


class TestWhoisService(unittest.TestCase):
    """Test cases for WHOIS service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_whois_missing_domain(self):
        """Test WHOIS with missing domain parameter"""
        response = self.loop.run_until_complete(whois_lookup("", "", "", 30))
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "whois")
        self.assertIn("domain parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_whois_invalid_timeout(self):
        """Test WHOIS with invalid timeout"""
        response = self.loop.run_until_complete(whois_lookup("example.com", "", "", 0))
        
        self.assertIn("timeout must be at least 1 second", response.raw_error)
        
        response = self.loop.run_until_complete(whois_lookup("example.com", "", "", 200))
        self.assertIn("timeout cannot exceed 120 seconds", response.raw_error)
    
    def test_whois_domain_cleaning(self):
        """Test WHOIS domain input cleaning"""
        # Test with protocol in URL
        response = self.loop.run_until_complete(whois_lookup("https://example.com/path", "", "", 30))
        
        self.assertEqual(response.target, "example.com")
    
    def test_whois_response_structure(self):
        """Test WHOIS response structure"""
        response = self.loop.run_until_complete(whois_lookup("example.com", "", "", 30))
        
        self.assertEqual(response.service, "whois")
        self.assertIn("domain", response.arguments)
        self.assertIsNotNone(response.process_time_ms)
    
    def test_whois_response_json_serializable(self):
        """Test that WHOIS response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(whois_lookup("example.com", "", "", 30))
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
