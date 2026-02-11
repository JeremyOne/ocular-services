"""Unit tests for httpx service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from httpx_service import httpx_scan
from service_response import ServiceResponse


class TestHttpxService(unittest.TestCase):
    """Test cases for httpx service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_httpx_missing_targets(self):
        """Test httpx with missing targets parameter"""
        response = self.loop.run_until_complete(
            httpx_scan("", "basic", "80,443", "", "GET", 10, 50, 150, 2)
        )
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "httpx")
        self.assertIn("targets parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_httpx_invalid_timeout(self):
        """Test httpx with invalid timeout"""
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 3, 50, 150, 2)
        )
        
        self.assertIn("timeout must be at least 5 seconds", response.raw_error)
        
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 200, 50, 150, 2)
        )
        self.assertIn("timeout cannot exceed 120 seconds", response.raw_error)
    
    def test_httpx_invalid_threads(self):
        """Test httpx with invalid threads count"""
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 10, 0, 150, 2)
        )
        
        self.assertIn("threads must be at least 1", response.raw_error)
        
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 10, 200, 150, 2)
        )
        self.assertIn("threads cannot exceed 100", response.raw_error)
    
    def test_httpx_invalid_rate_limit(self):
        """Test httpx with invalid rate limit"""
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 10, 50, 0, 2)
        )
        
        self.assertIn("rate_limit must be at least 1", response.raw_error)
        
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 10, 50, 2000, 2)
        )
        self.assertIn("rate_limit cannot exceed 1000", response.raw_error)
    
    def test_httpx_invalid_retries(self):
        """Test httpx with invalid retries"""
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 10, 50, 150, -1)
        )
        
        self.assertIn("retries cannot be negative", response.raw_error)
        
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 10, 50, 150, 10)
        )
        self.assertIn("retries cannot exceed 5", response.raw_error)
    
    def test_httpx_scan_types(self):
        """Test httpx scan type options"""
        scan_types = ["basic", "detailed", "headers", "hashes", "comprehensive"]
        
        for scan_type in scan_types:
            response = self.loop.run_until_complete(
                httpx_scan("example.com", scan_type, "80,443", "", "GET", 10, 50, 150, 2)
            )
            
            self.assertEqual(response.service, "httpx")
            # Should have httpx command built
            if response.raw_command:
                self.assertIn("httpx", response.raw_command.lower())
    
    def test_httpx_multiple_targets(self):
        """Test httpx with multiple comma-separated targets"""
        response = self.loop.run_until_complete(
            httpx_scan("example.com,test.com", "basic", "80,443", "", "GET", 10, 50, 150, 2)
        )
        
        self.assertEqual(response.service, "httpx")
        self.assertEqual(response.target, "example.com,test.com")
    
    def test_httpx_custom_ports(self):
        """Test httpx with custom port specification"""
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "8080,8443,9000", "", "GET", 10, 50, 150, 2)
        )
        
        self.assertIn("8080,8443,9000", response.arguments["ports"])
    
    def test_httpx_response_json_serializable(self):
        """Test that httpx response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(
            httpx_scan("example.com", "basic", "80,443", "", "GET", 10, 50, 150, 2)
        )
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
