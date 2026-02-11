"""Unit tests for cURL service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from curl_service import curl_request
from service_response import ServiceResponse


class TestCurlService(unittest.TestCase):
    """Test cases for cURL service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_curl_missing_url(self):
        """Test cURL with missing URL parameter"""
        response = self.loop.run_until_complete(
            curl_request("", "GET", "", "", False, False, False, "", False)
        )
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "curl")
        self.assertIn("url parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_curl_command_building(self):
        """Test cURL command construction"""
        response = self.loop.run_until_complete(
            curl_request("https://example.com", "POST", "Content-Type: application/json", 
                        '{"key":"value"}', True, True, True, "CustomAgent", False)
        )
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertIn("curl", response.raw_command)
        self.assertIn("-L", response.raw_command)  # follow_redirects
        self.assertIn("-v", response.raw_command)  # verbose
        self.assertIn("-k", response.raw_command)  # insecure
        self.assertIn("-X POST", response.raw_command)  # method
    
    def test_curl_headers_only(self):
        """Test cURL with headers_only flag"""
        response = self.loop.run_until_complete(
            curl_request("https://example.com", "GET", "", "", False, False, False, "", True)
        )
        
        self.assertIn("-I", response.raw_command)  # headers only flag
    
    def test_curl_response_json_serializable(self):
        """Test that cURL response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(
            curl_request("https://example.com", "GET", "", "", False, False, False, "", False)
        )
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
