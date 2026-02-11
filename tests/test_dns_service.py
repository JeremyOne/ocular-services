"""Unit tests for DNS service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from dns_service import dns_lookup
from service_response import ServiceResponse


class TestDNSService(unittest.TestCase):
    """Test cases for DNS service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_dns_missing_host(self):
        """Test DNS lookup with missing host parameter"""
        response = self.loop.run_until_complete(dns_lookup("", "A", 5.0))
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "dns")
        self.assertIn("host parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_dns_invalid_timeout(self):
        """Test DNS with invalid timeout"""
        response = self.loop.run_until_complete(dns_lookup("google.com", "A", 0))
        
        self.assertIn("timeout must be at least 1 second", response.raw_error)
        
        response = self.loop.run_until_complete(dns_lookup("google.com", "A", 100))
        self.assertIn("timeout cannot exceed 30 seconds", response.raw_error)
    
    def test_dns_a_record_lookup(self):
        """Test DNS A record lookup for a known domain"""
        response = self.loop.run_until_complete(dns_lookup("google.com", "A", 5.0))
        
        self.assertEqual(response.service, "dns")
        self.assertEqual(response.target, "google.com")
        self.assertEqual(response.return_code, 0)
        self.assertIn("A records", response.raw_output)
    
    def test_dns_multiple_record_types(self):
        """Test DNS lookup with multiple record types"""
        response = self.loop.run_until_complete(dns_lookup("google.com", "A,MX,TXT", 5.0))
        
        self.assertEqual(response.return_code, 0)
        output = response.raw_output
        self.assertIn("A records", output)
        self.assertIn("MX records", output)
        self.assertIn("TXT records", output)
    
    def test_dns_response_json_serializable(self):
        """Test that DNS response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(dns_lookup("google.com", "A", 5.0))
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
