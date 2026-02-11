"""Unit tests for ServiceResponse class"""
import unittest
import json
from datetime import datetime
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp'))

from service_response import ServiceResponse


class TestServiceResponse(unittest.TestCase):
    """Test cases for ServiceResponse class"""
    
    def test_initialization(self):
        """Test ServiceResponse initialization"""
        response = ServiceResponse(
            service="test_service",
            target="127.0.0.1"
        )
        
        self.assertEqual(response.service, "test_service")
        self.assertEqual(response.target, "127.0.0.1")
        self.assertEqual(response.return_code, 0)
        self.assertEqual(response.raw_output, "")
        self.assertEqual(response.raw_error, "")
        self.assertIsInstance(response.process_start_time, datetime)
        self.assertEqual(response.process_time_ms, 0)
        self.assertIsNone(response.process_end_time)
    
    def test_to_dict_serialization(self):
        """Test to_dict method returns JSON-serializable dict"""
        response = ServiceResponse(
            service="ping",
            target="google.com",
            arguments={"count": 5},
            return_code=0,
            raw_command="ping -c 5 google.com",
            raw_output="PING google.com: 5 packets transmitted",
            raw_error=""
        )
        
        result_dict = response.to_dict()
        
        # Verify all fields are present
        self.assertIn("service", result_dict)
        self.assertIn("target", result_dict)
        self.assertIn("process_start_time", result_dict)
        self.assertIn("process_end_time", result_dict)
        self.assertIn("process_time_ms", result_dict)
        self.assertIn("arguments", result_dict)
        self.assertIn("return_code", result_dict)
        self.assertIn("raw_command", result_dict)
        self.assertIn("raw_output", result_dict)
        self.assertIn("raw_error", result_dict)
        
        # Verify datetime is converted to string
        self.assertIsInstance(result_dict["process_start_time"], str)
        
        # Verify JSON serializable
        try:
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"to_dict() returned non-JSON-serializable dict: {e}")
    
    def test_is_successful(self):
        """Test is_successful method"""
        response = ServiceResponse(service="test", target="localhost")
        response.return_code = 0
        self.assertTrue(response.is_successful())
        
        response.return_code = 1
        self.assertFalse(response.is_successful())
    
    def test_has_errors(self):
        """Test has_errors method"""
        response = ServiceResponse(service="test", target="localhost")
        self.assertFalse(response.has_errors())
        
        response.raw_error = "Error occurred"
        self.assertTrue(response.has_errors())
        
        response.raw_error = ""
        response.return_code = 1
        self.assertTrue(response.has_errors())
    
    def test_end_process_timer(self):
        """Test end_process_timer calculates time correctly"""
        response = ServiceResponse(service="test", target="localhost")
        initial_start = response.process_start_time
        
        # Simulate some processing time
        import time
        time.sleep(0.01)  # 10ms
        
        response.end_process_timer()
        
        self.assertIsNotNone(response.process_end_time)
        self.assertGreater(response.process_time_ms, 0)
        self.assertEqual(response.process_start_time, initial_start)
    
    def test_add_error(self):
        """Test add_error method"""
        response = ServiceResponse(service="test", target="localhost")
        
        response.add_error("First error")
        self.assertEqual(response.raw_error, "First error")
        
        response.add_error("Second error", return_code=1)
        self.assertEqual(response.raw_error, "First error\nSecond error")
        self.assertEqual(response.return_code, 1)
        self.assertIsNotNone(response.process_end_time)
    
    def test_repr(self):
        """Test __repr__ method"""
        response = ServiceResponse(
            service="ping",
            target="localhost",
            return_code=0,
            raw_output="Success"
        )
        response.end_process_timer()
        
        repr_str = repr(response)
        
        self.assertIn("ping", repr_str)
        self.assertIn("localhost", repr_str)
        self.assertIn("Success", repr_str)
    
    def test_from_dict(self):
        """Test from_dict class method"""
        data = {
            "service": "nmap",
            "target": "192.168.1.1",
            "return_code": 0,
            "raw_command": "nmap 192.168.1.1",
            "raw_output": "Host is up",
            "raw_error": "",
            "arguments": {"scan_type": "fast"}
        }
        
        response = ServiceResponse.from_dict(data)
        
        self.assertEqual(response.service, "nmap")
        self.assertEqual(response.target, "192.168.1.1")
        self.assertEqual(response.return_code, 0)
        self.assertEqual(response.arguments["scan_type"], "fast")


if __name__ == '__main__':
    unittest.main()
