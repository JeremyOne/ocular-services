"""Unit tests for nmap service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from nmap_service import nmap_scan
from service_response import ServiceResponse


class TestNmapService(unittest.TestCase):
    """Test cases for nmap service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_nmap_missing_target(self):
        """Test nmap with missing target parameter"""
        response = self.loop.run_until_complete(nmap_scan("", "fast", 240, "", ""))
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "nmap")
        self.assertIn("target parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_nmap_invalid_timeout(self):
        """Test nmap with invalid timeout"""
        response = self.loop.run_until_complete(nmap_scan("localhost", "fast", 10, "", ""))
        
        self.assertIn("timeout must be at least 30 seconds", response.raw_error)
        
        response = self.loop.run_until_complete(nmap_scan("localhost", "fast", 2000, "", ""))
        self.assertIn("timeout cannot exceed 1800 seconds", response.raw_error)
    
    def test_nmap_scan_types(self):
        """Test nmap scan type mapping"""
        scan_types = ["fast", "service", "stealth", "rdp", "aggressive", "vuln"]
        
        for scan_type in scan_types:
            response = self.loop.run_until_complete(
                nmap_scan("localhost", scan_type, 240, "", "")
            )
            
            self.assertEqual(response.service, "nmap")
            self.assertIn("nmap", response.raw_command)
            # Should have scan type specific flags
            self.assertTrue(len(response.raw_command) > len("nmap localhost"))
    
    def test_nmap_custom_ports(self):
        """Test nmap with custom port specification"""
        response = self.loop.run_until_complete(
            nmap_scan("localhost", "fast", 240, "80,443,8080", "")
        )
        
        self.assertIn("-p 80,443,8080", response.raw_command)
    
    def test_nmap_custom_scripts(self):
        """Test nmap with custom NSE scripts"""
        response = self.loop.run_until_complete(
            nmap_scan("localhost", "fast", 240, "", "http-title,ssh-auth-methods")
        )
        
        self.assertIn("--script", response.raw_command)
        self.assertIn("http-title,ssh-auth-methods", response.raw_command)
    
    def test_nmap_response_json_serializable(self):
        """Test that nmap response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(nmap_scan("localhost", "fast", 240, "", ""))
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
