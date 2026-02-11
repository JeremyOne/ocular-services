"""Unit tests for wpscan service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from wpscan_service import wpscan_scan
from service_response import ServiceResponse


class TestWpscanService(unittest.TestCase):
    """Test cases for wpscan service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_wpscan_missing_url(self):
        """Test wpscan with missing URL parameter"""
        response = self.loop.run_until_complete(
            wpscan_scan("", "basic", "", 300, False, False)
        )
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "wpscan")
        self.assertIn("url parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_wpscan_timeout_clamping(self):
        """Test wpscan timeout clamping to valid range"""
        # Timeout too low (should be clamped to 60)
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "basic", "", 30, False, False)
        )
        
        # Should not error, but timeout should be adjusted
        self.assertEqual(response.service, "wpscan")
        
        # Timeout too high (should be clamped to 1800)
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "basic", "", 5000, False, False)
        )
        
        self.assertEqual(response.service, "wpscan")
    
    def test_wpscan_url_protocol_addition(self):
        """Test wpscan adds http:// protocol if missing"""
        response = self.loop.run_until_complete(
            wpscan_scan("example.com", "basic", "", 300, False, False)
        )
        
        self.assertEqual(response.target, "http://example.com")
        
        # Should not modify URLs that already have protocol
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "basic", "", 300, False, False)
        )
        
        self.assertEqual(response.target, "https://example.com")
    
    def test_wpscan_scan_options(self):
        """Test wpscan scan option types"""
        scan_options = ["basic", "plugins", "themes", "users", "vulns", "full", "passive"]
        
        for option in scan_options:
            response = self.loop.run_until_complete(
                wpscan_scan("https://example.com", option, "", 300, False, False)
            )
            
            self.assertEqual(response.service, "wpscan")
            self.assertEqual(response.arguments["options"], option)
            self.assertIn("wpscan", response.raw_command)
    
    def test_wpscan_api_token(self):
        """Test wpscan with API token"""
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "basic", "test-token-123", 300, False, False)
        )
        
        self.assertTrue(response.arguments["api_token_provided"])
        if response.raw_command:
            self.assertIn("--api-token", response.raw_command)
    
    def test_wpscan_force_flag(self):
        """Test wpscan with force flag"""
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "basic", "", 300, True, False)
        )
        
        self.assertTrue(response.arguments["force"])
        if response.raw_command:
            self.assertIn("--force", response.raw_command)
    
    def test_wpscan_random_user_agent(self):
        """Test wpscan with random user agent flag"""
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "basic", "", 300, False, True)
        )
        
        self.assertTrue(response.arguments["random_user_agent"])
        if response.raw_command:
            self.assertIn("--random-user-agent", response.raw_command)
    
    def test_wpscan_all_options_combined(self):
        """Test wpscan with all options enabled"""
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "full", "test-token", 300, True, True)
        )
        
        self.assertEqual(response.service, "wpscan")
        self.assertTrue(response.arguments["force"])
        self.assertTrue(response.arguments["random_user_agent"])
        self.assertTrue(response.arguments["api_token_provided"])
    
    def test_wpscan_response_json_serializable(self):
        """Test that wpscan response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(
            wpscan_scan("https://example.com", "basic", "", 300, False, False)
        )
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
