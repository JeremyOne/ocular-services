"""Unit tests for ping service"""
import unittest
import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from ping_service import ping_host
from service_response import ServiceResponse


class TestPingService(unittest.TestCase):
    """Test cases for ping service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()
    
    def test_ping_missing_host(self):
        """Test ping with missing host parameter"""
        response = self.loop.run_until_complete(ping_host("", 5, 1.0, 56, 60))
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "ping")
        self.assertIn("host parameter is required", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_ping_invalid_count(self):
        """Test ping with invalid count parameter"""
        response = self.loop.run_until_complete(ping_host("localhost", 0, 1.0, 56, 60))
        
        self.assertIn("count must be between 1 and 99", response.raw_error)
        self.assertTrue(response.has_errors())
        
        response = self.loop.run_until_complete(ping_host("localhost", 100, 1.0, 56, 60))
        self.assertIn("count must be between 1 and 99", response.raw_error)
    
    def test_ping_invalid_interval(self):
        """Test ping with invalid interval parameter"""
        response = self.loop.run_until_complete(ping_host("localhost", 5, 0.001, 56, 60))
        
        self.assertIn("interval must be between 0.01 and 5", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_ping_invalid_packet_size(self):
        """Test ping with invalid packet_size parameter"""
        response = self.loop.run_until_complete(ping_host("localhost", 5, 1.0, 0, 60))
        
        self.assertIn("packet_size must be between 1 and 65524", response.raw_error)
        self.assertTrue(response.has_errors())
    
    def test_ping_localhost(self):
        """Test ping to localhost (should succeed)"""
        response = self.loop.run_until_complete(ping_host("localhost", 2, 1.0, 56, 60))
        
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.service, "ping")
        self.assertEqual(response.target, "localhost")
        self.assertIsNotNone(response.process_time_ms)
        self.assertGreater(response.process_time_ms, 0)
        # Command should be executed (may succeed or fail depending on system)
        self.assertIn("ping", response.raw_command)
    
    def test_ping_response_json_serializable(self):
        """Test that ping response can be converted to JSON"""
        import json
        
        response = self.loop.run_until_complete(ping_host("localhost", 1, 1.0, 56, 60))
        
        # This should not raise an exception
        try:
            result_dict = response.to_dict()
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"Response is not JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()
