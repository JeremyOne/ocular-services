#!/usr/bin/env python3
"""
Comprehensive test script for all MCP services
Launches the unified MCP server and tests all endpoints
"""

import subprocess
import time
import requests
import json
import sys
import os
import signal
from typing import Dict, List, Any, Optional

class MCPTester:
    def __init__(self, server_host: str = "localhost", server_port: int = 8999):
        self.server_host = server_host
        self.server_port = server_port
        self.base_url = f"http://{server_host}:{server_port}"
        self.server_process = None
        self.test_results = {}
        
    def start_server(self) -> bool:
        """Start the unified MCP server"""
        print("🚀 Starting MCP server...")
        
        # Kill any existing processes
        try:
            subprocess.run(["pkill", "-f", "allservices.py"], 
                         capture_output=True, check=False)
            time.sleep(2)
        except:
            pass
        
        # Get the Python path
        python_path = "/home/jp/Documents/ocular_agents/.venv/bin/python"
        if not os.path.exists(python_path):
            python_path = "python3"
        
        # Start the server
        try:
            self.server_process = subprocess.Popen(
                [python_path, "allservices.py"],
                cwd="/home/jp/Documents/ocular_agents/mcp",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Wait for server to start
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully on port {self.server_port}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                
                # Check if process is still running
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    print(f"❌ Server failed to start:")
                    print(f"STDOUT: {stdout.decode()}")
                    print(f"STDERR: {stderr.decode()}")
                    return False
            
            print(f"❌ Server did not respond after {max_attempts} seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.server_process:
            print("🛑 Stopping MCP server...")
            try:
                # Kill the process group to ensure all child processes are terminated
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already terminated
            self.server_process = None
    
    def test_endpoint(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            result = {
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                "content_type": response.headers.get("content-type", ""),
            }
            
            # Try to parse JSON response
            try:
                result["response"] = response.json()
            except json.JSONDecodeError:
                result["response"] = response.text[:500]  # Truncate long text responses
            
            return result
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Connection error"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_info_endpoints(self):
        """Test informational endpoints"""
        print("\n📋 Testing informational endpoints...")
        
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"), 
            ("/services", "GET")
        ]
        
        for endpoint, method in endpoints:
            print(f"  Testing {method} {endpoint}...")
            result = self.test_endpoint(endpoint, method)
            self.test_results[f"{method} {endpoint}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_ping_service(self):
        """Test ping service"""
        print("\n🏓 Testing ping service...")
        
        test_cases = [
            # GET request
            {
                "method": "GET",
                "params": {"host": "127.0.0.1", "count": "3"},
                "description": "GET request to localhost"
            },
            # POST request
            {
                "method": "POST", 
                "data": {"host": "8.8.8.8", "count": 2, "interval": 1.0},
                "description": "POST request to Google DNS"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/ping", 
                test_case["method"],
                test_case.get("data"),
                test_case.get("params")
            )
            self.test_results[f"ping_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_curl_service(self):
        """Test curl service"""
        print("\n🌐 Testing curl service...")
        
        test_cases = [
            {
                "method": "POST",
                "data": {"url": "https://httpbin.org/get", "method": "GET"},
                "description": "Simple GET request"
            },
            {
                "method": "POST",
                "data": {
                    "url": "https://httpbin.org/headers",
                    "headers": "User-Agent: MCP-Test-Agent",
                    "headers_only": True
                },
                "description": "Headers only request"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/curl",
                test_case["method"],
                test_case.get("data")
            )
            self.test_results[f"curl_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_datetime_service(self):
        """Test datetime service"""
        print("\n🕐 Testing datetime service...")
        
        test_cases = [
            {
                "method": "GET",
                "description": "Simple datetime request"
            },
            {
                "method": "POST",
                "data": {"utc": True, "format": "%Y-%m-%d %H:%M:%S"},
                "description": "UTC with custom format"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/datetime",
                test_case["method"],
                test_case.get("data")
            )
            self.test_results[f"datetime_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_dns_service(self):
        """Test DNS service"""
        print("\n🔍 Testing DNS service...")
        
        test_cases = [
            {
                "method": "POST",
                "data": {"host": "google.com", "record_types": "A,MX"},
                "description": "DNS lookup for google.com"
            },
            {
                "method": "GET", 
                "params": {"host": "github.com", "record_types": "A,AAAA"},
                "description": "IPv4 and IPv6 lookup for github.com"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/dns",
                test_case["method"],
                test_case.get("data"),
                test_case.get("params")
            )
            self.test_results[f"dns_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_enum4linux_service(self):
        """Test enum4linux service"""
        print("\n🔐 Testing enum4linux service...")
        
        # Use a shorter timeout for enum4linux since it might take a while
        test_cases = [
            {
                "method": "POST",
                "data": {"target": "127.0.0.1", "options": "-U", "timeout": 30},
                "description": "User enumeration on localhost (quick test)"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/enum4linux",
                test_case["method"], 
                test_case.get("data")
            )
            self.test_results[f"enum4linux_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_whois_service(self):
        """Test whois service"""
        print("\n📝 Testing whois service...")
        
        test_cases = [
            {
                "method": "POST",
                "data": {"domain": "google.com"},
                "description": "WHOIS lookup for google.com"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/whois",
                test_case["method"],
                test_case.get("data")
            )
            self.test_results[f"whois_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_wpscan_service(self):
        """Test wpscan service"""
        print("\n🔍 Testing wpscan service...")
        
        test_cases = [
            {
                "method": "POST",
                "data": {
                    "url": "https://demo.testfire.net", 
                    "options": "passive",
                    "timeout": 60
                },
                "description": "Passive scan of test site"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/wpscan",
                test_case["method"],
                test_case.get("data")
            )
            self.test_results[f"wpscan_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_httpx_service(self):
        """Test httpx service"""
        print("\n⚡ Testing httpx service...")
        
        test_cases = [
            {
                "method": "POST",
                "data": {
                    "targets": "httpbin.org,google.com",
                    "options": "basic",
                    "ports": "80,443"
                },
                "description": "Basic HTTP discovery"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/httpx",
                test_case["method"],
                test_case.get("data")
            )
            self.test_results[f"httpx_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def test_nbtscan_service(self):
        """Test nbtscan service"""
        print("\n🖥️  Testing nbtscan service...")
        
        test_cases = [
            {
                "method": "POST",
                "data": {
                    "target": "127.0.0.1",
                    "options": "basic", 
                    "timeout": 2000
                },
                "description": "NetBIOS scan of localhost"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing {test_case['description']}...")
            result = self.test_endpoint(
                "/nbtscan",
                test_case["method"],
                test_case.get("data")
            )
            self.test_results[f"nbtscan_{test_case['description']}"] = result
            
            if result["success"]:
                print(f"    ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
                if isinstance(result["response"], dict):
                    print(f"    📊 Return code: {result['response'].get('return_code', 'N/A')}")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed tests:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"  - {test_name}: {result['error']}")
        
        # Show response times for successful tests
        response_times = [
            result["response_time_ms"] 
            for result in self.test_results.values() 
            if result["success"] and "response_time_ms" in result
        ]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"\n⏱️  Response times:")
            print(f"  Average: {avg_response_time:.0f}ms")
            print(f"  Min: {min_response_time}ms")
            print(f"  Max: {max_response_time}ms")
    
    def save_results(self, filename: str = "test_results.json"):
        """Save test results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"\n💾 Test results saved to {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 MCP Service Comprehensive Test Suite")
        print("="*60)
        
        try:
            # Start server
            if not self.start_server():
                print("❌ Cannot start server. Exiting.")
                return False
            
            # Run all tests
            self.test_info_endpoints()
            self.test_ping_service()
            self.test_curl_service()
            self.test_datetime_service()
            self.test_dns_service()
            self.test_enum4linux_service()
            self.test_whois_service()
            self.test_wpscan_service()
            self.test_httpx_service()
            self.test_nbtscan_service()
            
            # Print summary
            self.print_summary()
            
            # Save results
            self.save_results()
            
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False
        finally:
            # Always stop server
            self.stop_server()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test all MCP services")
    parser.add_argument("--host", default="localhost", 
                       help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8999,
                       help="Server port (default: 8999)")
    parser.add_argument("--output", default="test_results.json",
                       help="Output file for results (default: test_results.json)")
    
    args = parser.parse_args()
    
    tester = MCPTester(args.host, args.port)
    success = tester.run_all_tests()
    
    if args.output != "test_results.json":
        tester.save_results(args.output)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
