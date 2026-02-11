"""Unit tests for nikto service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from nikto_service import nikto_scan
from service_response import ServiceResponse


class TestNiktoService(unittest.TestCase):
    """Test cases for nikto service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_nikto_missing_target(self):
        """Test nikto with missing target parameter"""
        response = self.loop.run_until_complete(
            nikto_scan("", "basic", "", False, 10, "", "", "")
        )
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "nikto")
        self.assertIn("target parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_nikto_invalid_timeout(self):
        """Test nikto with invalid timeout"""
        response = self.loop.run_until_complete(
            nikto_scan("https://example.com", "basic", "", False, 3, "", "", "")
        )
        
        self.assertIn("timeout must be at least 5 seconds", response.raw_error)
        
        response = self.loop.run_until_complete(
            nikto_scan("https://example.com", "basic", "", False, 400, "", "", "")
        )
        self.assertIn("timeout cannot exceed 300 seconds", response.raw_error)
    
    def test_nikto_scan_types(self):
        """Test nikto scan type options"""
        scan_types = ["basic", "ssl", "cgi", "files", "misconfig", "disclosure", "comprehensive", "fast"]
        
        for scan_type in scan_types:
            response = self.loop.run_until_complete(
                nikto_scan("https://example.com", scan_type, "", False, 10, "", "", "")
            )
            
            self.assertEqual(response.service, "nikto")
            self.assertIn("nikto", response.raw_command)
    
    def test_nikto_ssl_auto_detect(self):
        """Test nikto SSL auto-detection from URL"""
        response = self.loop.run_until_complete(
            nikto_scan("https://example.com", "basic", "", False, 10, "", "", "")
        )
        
        self.assertTrue(response.arguments["ssl"])
        
        response = self.loop.run_until_complete(
            nikto_scan("http://example.com", "basic", "", False, 10, "", "", "")
        )
        
        self.assertFalse(response.arguments["ssl"])
    
    def test_nikto_port_ssl_detect(self):
        """Test nikto SSL auto-detection from port 443"""
        response = self.loop.run_until_complete(
            nikto_scan("example.com", "basic", "443", False, 10, "", "", "")
        )
        
        self.assertTrue(response.arguments["ssl"])
    
    def test_nikto_custom_port(self):
        """Test nikto with custom port"""
        response = self.loop.run_until_complete(
            nikto_scan("example.com", "basic", "8080", False, 10, "", "", "")
        )
        
        self.assertEqual(response.arguments["port"], "8080")
        if response.raw_command:
            self.assertIn("-port 8080", response.raw_command)
    
    def test_nikto_custom_tuning(self):
        """Test nikto with custom tuning options"""
        response = self.loop.run_until_complete(
            nikto_scan("https://example.com", "basic", "", False, 10, "1,2,3", "", "")
        )
        
        self.assertEqual(response.arguments["tuning"], "1,2,3")
        if response.raw_command:
            self.assertIn("-Tuning 1,2,3", response.raw_command)
    
    def test_nikto_custom_plugins(self):
        """Test nikto with custom plugins"""
        response = self.loop.run_until_complete(
            nikto_scan("https://example.com", "basic", "", False, 10, "", "headers,robots", "")
        )
        
        self.assertEqual(response.arguments["plugins"], "headers,robots")
        if response.raw_command:
            self.assertIn("-Plugins", response.raw_command)
    
    def test_nikto_vhost(self):
        """Test nikto with virtual host header"""
        response = self.loop.run_until_complete(
            nikto_scan("https://example.com", "basic", "", False, 10, "", "", "www.example.com")
        )
        
        self.assertEqual(response.arguments["vhost"], "www.example.com")
        if response.raw_command:
            self.assertIn("-vhost www.example.com", response.raw_command)
    
    def test_nikto_response_json_serializable(self):
        """Test that nikto response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(
            nikto_scan("https://example.com", "basic", "", False, 10, "", "", "")
        )
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
