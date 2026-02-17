# Testing
Warning: the unit tests call actual commands and use networking including doing things like resolving dns, and curl on example.com and running nmap on localhost. 

Run unit tests:
```
python -m pytest tests/
```

Or run with unittest:
```
python tests/run_tests.py
```

Run specific test file:
```
python -m pytest tests/test_service_response.py
python -m pytest tests/test_ping_service.py -v
```

The test suite includes:
- `test_service_response.py` - ServiceResponse class tests
- `test_ping_service.py` - Ping service validation and execution tests
- `test_dns_service.py` - DNS lookup tests
- `test_whois_service.py` - WHOIS service tests
- `test_curl_service.py` - cURL service tests
- `test_nmap_service.py` - Nmap service tests
- `test_httpx_service.py` - HTTPX service tests
- `test_nbtscan_service.py` - NBTScan service tests
- `test_nikto_service.py` - Nikto service tests
- `test_wpscan_service.py` - WPScan service tests
- `test_dns_service.py` - DNS lookup tests
- `test_whois_service.py` - WHOIS service tests
- `test_curl_service.py` - cURL service tests
- `test_nmap_service.py` - Nmap service tests

All tests verify:
- Parameter validation
- Error handling
- JSON serialization (fixes for datetime objects)
- Command building
- Response structure