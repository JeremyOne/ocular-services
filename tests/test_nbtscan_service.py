"""Unit tests for nbtscan service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from nbtscan_service import nbtscan_scan
from service_response import ServiceResponse


class TestNbtscanService(unittest.TestCase):
    """Test cases for nbtscan service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_nbtscan_missing_target(self):
        """Test nbtscan with missing target parameter"""
        response = self.loop.run_until_complete(
            nbtscan_scan("", "basic", 1000, False, 0, False)
        )
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "nbtscan")
        self.assertIn("target parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_nbtscan_invalid_timeout(self):
        """Test nbtscan with invalid timeout"""
        response = self.loop.run_until_complete(
            nbtscan_scan("192.168.1.1", "basic", 50, False, 0, False)
        )
        
        self.assertIn("timeout must be at least 100 milliseconds", response.raw_error)
        
        response = self.loop.run_until_complete(
            nbtscan_scan("192.168.1.1", "basic", 40000, False, 0, False)
        )
        self.assertIn("timeout cannot exceed 30000 milliseconds", response.raw_error)
    
    def test_nbtscan_invalid_retransmits(self):
        """Test nbtscan with invalid retransmits"""
        response = self.loop.run_until_complete(
            nbtscan_scan("192.168.1.1", "basic", 1000, False, -1, False)
        )
        
        self.assertIn("retransmits cannot be negative", response.raw_error)
        
        response = self.loop.run_until_complete(
            nbtscan_scan("192.168.1.1", "basic", 1000, False, 15, False)
        )
        self.assertIn("retransmits cannot exceed 10", response.raw_error)
    
    def test_nbtscan_scan_options(self):
        """Test nbtscan scan option types"""
        scan_options = ["basic", "verbose", "script", "hosts", "lmhosts"]
        
        for option in scan_options:
            response = self.loop.run_until_complete(
                nbtscan_scan("192.168.1.1", option, 1000, False, 0, False)
            )
            
            self.assertEqual(response.service, "nbtscan")
            self.assertIn("nbtscan", response.raw_command)
    
    def test_nbtscan_target_formats(self):
        """Test nbtscan with different target formats"""
        targets = [
            "192.168.1.1",           # Single IP
            "192.168.1.1-10",        # IP range
            "192.168.1.0/24"         # CIDR subnet
        ]
        
        for target in targets:
            response = self.loop.run_until_complete(
                nbtscan_scan(target, "basic", 1000, False, 0, False)
            )
            
            self.assertEqual(response.service, "nbtscan")
            self.assertEqual(response.target, target)
    
    def test_nbtscan_verbose_flag(self):
        """Test nbtscan with verbose flag"""
        response = self.loop.run_until_complete(
            nbtscan_scan("192.168.1.1", "basic", 1000, True, 0, False)
        )
        
        self.assertTrue(response.arguments["verbose"])
    
    def test_nbtscan_use_local_port(self):
        """Test nbtscan with use_local_port flag"""
        response = self.loop.run_until_complete(
            nbtscan_scan("192.168.1.1", "basic", 1000, False, 0, True)
        )
        
        self.assertTrue(response.arguments["use_local_port"])
        # Should have -r flag
        if response.raw_command:
            self.assertIn("-r", response.raw_command)
    
    def test_nbtscan_response_json_serializable(self):
        """Test that nbtscan response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(
            nbtscan_scan("192.168.1.1", "basic", 1000, False, 0, False)
        )
        
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
