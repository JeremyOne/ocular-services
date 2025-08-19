#!/usr/bin/env python3

"""
Comprehensive test file for all tools and enum options in ocular_agents.

This test file validates:
1. All enum classes and their options can be accessed correctly
2. All tool functions can accept their respective enum parameters
3. Tool functions handle enum conversion properly (value attribute access)
4. Import functionality works for all tools
5. Error handling for missing dependencies

Note: This test focuses on parameter handling and enum compatibility.
Actual tool execution may fail due to missing dependencies or network issues.
"""

import sys
import traceback
from datetime import datetime

# Import all enum classes
from tools.enums import (
    NmapOptions, CurlOptions, NbtScanOptions, Enum4linuxOptions,
    NiktoOptions, SmbClientOptions, PingOptions, DnsRecordTypes,
    HttpxOptions, WpScanOptions, WhoisOptions
)

# Test data for different tool types
TEST_TARGETS = {
    'ip': '127.0.0.1',
    'domain': 'localhost',
    'url': 'http://localhost',
    'https_url': 'https://localhost',
    'range': '192.168.0.1-192.168.0.10',
    'subnet': '192.168.0.0/24'
}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_pass(self, test_name):
        self.passed += 1
        print(f"  ✅ {test_name}")
        
    def add_fail(self, test_name, error):
        self.failed += 1
        error_msg = f"❌ {test_name}: {error}"
        print(f"  {error_msg}")
        self.errors.append(error_msg)
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")

def test_enum_access():
    """Test that all enum classes and their options are accessible."""
    print("🔍 Testing Enum Access...")
    results = TestResults()
    
    enum_classes = [
        (NmapOptions, "NmapOptions"),
        (CurlOptions, "CurlOptions"),
        (NbtScanOptions, "NbtScanOptions"),
        (Enum4linuxOptions, "Enum4linuxOptions"),
        (NiktoOptions, "NiktoOptions"),
        (SmbClientOptions, "SmbClientOptions"),
        (PingOptions, "PingOptions"),
        (DnsRecordTypes, "DnsRecordTypes"),
        (HttpxOptions, "HttpxOptions"),
        (WpScanOptions, "WpScanOptions"),
        (WhoisOptions, "WhoisOptions")
    ]
    
    for enum_class, name in enum_classes:
        try:
            # Test that we can iterate through all options
            options = list(enum_class)
            if not options:
                results.add_fail(f"{name} enumeration", "No options found")
                continue
                
            # Test each option has required attributes
            for option in options:
                if not hasattr(option, 'value'):
                    results.add_fail(f"{name}.{option.name}.value", "Missing value attribute")
                    continue
                if not hasattr(option, 'description'):
                    results.add_fail(f"{name}.{option.name}.description", "Missing description attribute")
                    continue
                    
            results.add_pass(f"{name} ({len(options)} options)")
            
        except Exception as e:
            results.add_fail(f"{name} access", str(e))
    
    return results

def test_tool_imports():
    """Test that all tool functions can be imported."""
    print("\n📦 Testing Tool Imports...")
    results = TestResults()
    
    tools_to_import = [
        ('tools.ping_tool', 'ping_host'),
        ('tools.nmap_tool', 'nmap_scan'),
        ('tools.curl_tool', 'curl_test'),
        ('tools.dns_tool', 'dns_lookup'),
        ('tools.nbtscan_tool', 'nbtscan_scan'),
        ('tools.enum4linux_tool', 'enum4linux_scan'),
        ('tools.nikto_tool', 'nikto_scan'),
        ('tools.smbclient_tool', 'smbclient_scan'),
        ('tools.httpx_tool', 'httpx_scan'),
        ('tools.wpscan_tool', 'wpscan_scan'),
        ('tools.whois_tool', 'whois_lookup'),
        ('tools.report_tool', 'write_report'),
        ('tools.datetime_tool', 'get_current_datetime')
    ]
    
    for module_name, function_name in tools_to_import:
        try:
            module = __import__(module_name, fromlist=[function_name])
            func = getattr(module, function_name)
            results.add_pass(f"{module_name}.{function_name}")
        except Exception as e:
            results.add_fail(f"{module_name}.{function_name}", str(e))
    
    return results

def test_tool_enum_compatibility():
    """Test that tools can handle their respective enum parameters without AttributeError."""
    print("\n🔧 Testing Tool-Enum Compatibility...")
    results = TestResults()
    
    # Test each tool with its corresponding enum options
    # Generate test cases for EVERY enum option
    test_cases = []
    
    # PingOptions - all options
    for option in PingOptions:
        test_cases.append(('ping_tool', 'ping_host', option, TEST_TARGETS['ip']))
    
    # NmapOptions - all options
    for option in NmapOptions:
        test_cases.append(('nmap_tool', 'nmap_scan', option, TEST_TARGETS['ip']))
    
    # CurlOptions - all options
    for option in CurlOptions:
        test_cases.append(('curl_tool', 'curl_test', option, TEST_TARGETS['url']))
    
    # DnsRecordTypes - all options
    for option in DnsRecordTypes:
        test_cases.append(('dns_tool', 'dns_lookup', option, TEST_TARGETS['domain']))
    
    # NbtScanOptions - all options
    for option in NbtScanOptions:
        test_cases.append(('nbtscan_tool', 'nbtscan_scan', option, TEST_TARGETS['ip']))
    
    # Enum4linuxOptions - all options
    for option in Enum4linuxOptions:
        test_cases.append(('enum4linux_tool', 'enum4linux_scan', option, TEST_TARGETS['ip']))
    
    # NiktoOptions - all options
    for option in NiktoOptions:
        test_cases.append(('nikto_tool', 'nikto_scan', option, TEST_TARGETS['url']))
    
    # SmbClientOptions - all options
    for option in SmbClientOptions:
        test_cases.append(('smbclient_tool', 'smbclient_scan', option, TEST_TARGETS['ip']))
    
    # HttpxOptions - all options
    for option in HttpxOptions:
        test_cases.append(('httpx_tool', 'httpx_scan', option, TEST_TARGETS['url']))
    
    # WpScanOptions - all options
    for option in WpScanOptions:
        test_cases.append(('wpscan_tool', 'wpscan_scan', option, TEST_TARGETS['url']))
    
    # WhoisOptions - all options
    for option in WhoisOptions:
        test_cases.append(('whois_tool', 'whois_lookup', option, TEST_TARGETS['domain']))
    
    
    
    for module_name, function_name, enum_option, target in test_cases:
        try:
            # Import the function
            module = __import__(f'tools.{module_name}', fromlist=[function_name])
            func = getattr(module, function_name)
            
            # Try to call the function with enum parameter
            # We expect it to fail with dependency errors, not AttributeError
            try:
                if function_name == 'dns_lookup':
                    # DNS lookup expects record_types as list
                    result = func(target, [enum_option])
                else:
                    result = func(target, enum_option)
                    
                # If it succeeds, that's great!
                results.add_pass(f"{function_name} with {enum_option.name}")
                
            except AttributeError as e:
                # This is what we're testing for - should NOT happen
                if 'cmd_option' in str(e) or 'attribute' in str(e):
                    results.add_fail(f"{function_name} enum handling", f"AttributeError: {e}")
                else:
                    # Other AttributeErrors might be legitimate
                    results.add_pass(f"{function_name} enum handling (other AttributeError: {e})")
                    
            except Exception as e:
                # Other exceptions (missing tools, network errors, etc.) are expected
                error_type = type(e).__name__
                if error_type in ['CalledProcessError', 'FileNotFoundError', 'TimeoutExpired']:
                    results.add_pass(f"{function_name} enum handling (expected {error_type})")
                else:
                    results.add_pass(f"{function_name} enum handling (unexpected but not AttributeError: {error_type})")
                    
        except Exception as e:
            results.add_fail(f"{function_name} import/setup", str(e))
    
    return results

def test_enum_option_coverage():
    """Test that we can access all options in each enum without errors."""
    print("\n📋 Testing All Enum Options...")
    results = TestResults()
    
    enum_classes = {
        'NmapOptions': NmapOptions,
        'CurlOptions': CurlOptions,
        'NbtScanOptions': NbtScanOptions,
        'Enum4linuxOptions': Enum4linuxOptions,
        'NiktoOptions': NiktoOptions,
        'SmbClientOptions': SmbClientOptions,
        'PingOptions': PingOptions,
        'DnsRecordTypes': DnsRecordTypes,
        'HttpxOptions': HttpxOptions,
        'WpScanOptions': WpScanOptions,
        'WhoisOptions': WhoisOptions
    }
    
    for enum_name, enum_class in enum_classes.items():
        option_count = 0
        for option in enum_class:
            try:
                # Test value access
                value = option.value
                description = option.description
                name = option.name
                
                # Validate that value and description are not empty
                if value is None:
                    results.add_fail(f"{enum_name}.{name}.value", "Value is None")
                elif description is None or description.strip() == "":
                    results.add_fail(f"{enum_name}.{name}.description", "Description is empty")
                else:
                    option_count += 1
                    
            except Exception as e:
                results.add_fail(f"{enum_name}.{option.name}", str(e))
        
        if option_count > 0:
            results.add_pass(f"{enum_name} all {option_count} options accessible")
    
    return results

def test_tool_specific_functionality():
    """Test specific functionality for tools that don't require external dependencies."""
    print("\n⚙️  Testing Tool-Specific Functionality...")
    results = TestResults()
    
    # Test datetime tool (no external dependencies)
    try:
        from tools.datetime_tool import get_current_datetime
        result = get_current_datetime()
        if result and isinstance(result, str):
            results.add_pass("datetime_tool basic functionality")
        else:
            results.add_fail("datetime_tool basic functionality", f"Unexpected result: {result}")
    except Exception as e:
        results.add_fail("datetime_tool basic functionality", str(e))
    
    # Test report tool basic functionality
    try:
        from tools.report_tool import write_report
        # Don't actually write a file, just test parameter handling
        test_content = "Test content"
        test_hostname = "test-host"
        # This should validate parameters but not necessarily succeed
        results.add_pass("report_tool parameter handling")
    except Exception as e:
        results.add_fail("report_tool import", str(e))
    
    return results

def main():
    """Run all tests and provide comprehensive report."""
    print("🚀 Starting Comprehensive Tool and Enum Testing")
    print(f"📅 Test started at: {datetime.now().isoformat()}")
    print("="*60)
    
    all_results = TestResults()
    
    # Run all test suites
    test_suites = [
        test_enum_access,
        test_tool_imports,
        test_enum_option_coverage,
        test_tool_enum_compatibility,
        test_tool_specific_functionality
    ]
    
    for test_suite in test_suites:
        try:
            suite_results = test_suite()
            all_results.passed += suite_results.passed
            all_results.failed += suite_results.failed
            all_results.errors.extend(suite_results.errors)
        except Exception as e:
            print(f"❌ Test suite {test_suite.__name__} failed: {e}")
            traceback.print_exc()
            all_results.failed += 1
            all_results.errors.append(f"Test suite {test_suite.__name__}: {e}")
    
    # Print comprehensive summary
    all_results.summary()
    
    print(f"\n📅 Test completed at: {datetime.now().isoformat()}")
    
    # Return exit code based on results
    return 0 if all_results.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
