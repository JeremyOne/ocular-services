fastmcp run mcp/ping.py:mcp


fastmcp run mcp/curl.py:mcp
http://localhost:9001/curl?url=http://google.com
/**
 * cURL Service
 * 
 * A service class that provides HTTP request functionality using cURL.
 * This service handles GET, POST, PUT, DELETE and other HTTP methods
 * with support for various options like headers, authentication, timeouts,
 * and SSL verification.
 * 
 * Features:
 * - Multiple HTTP methods support
 * - Custom headers configuration
 * - Authentication support (Basic, Bearer, etc.)
 * - Request/response timeout handling
 * - SSL certificate verification options
 * - Error handling and response parsing
 * - Support for JSON and form data payloads
 * 
 * @example
 * ```php
 * $curl = new CurlService();
 * $response = $curl->get('https://api.example.com/users');
 * $data = $curl->post('https://api.example.com/users', ['name' => 'John']);
 * ```
 */

## Datetime service
DateTime MCP Service (datetime.py)
Features:
Port: 9003 (individual service)
Endpoint: /datetime
Methods: GET and POST
Schema Compliant: Follows the same JSON response format as ping and curl
Parameters:
timezone: Optional timezone specification
format: Custom strftime format string
utc: Boolean flag to return UTC time
Structured Output Includes:
iso_format: ISO 8601 format
timestamp: Unix timestamp
human_readable: Human-friendly format
date_only: Date portion only
time_only: Time portion only
timezone: Timezone information
weekday: Day of the week
month: Month name
year, month_num, day: Date components
hour, minute, second, microsecond: Time components
day_of_year: Day number in year
week_number: ISO week number
custom_format: Result of custom format (if provided)

## DNS MCP Service (dns.py)
Features:
Port: 9004 (individual service)
Endpoint: /dns
Methods: GET and POST
Schema Compliant: Follows the same JSON response format as other services
Parameters:
host (required): Hostname or domain to look up
record_types: Comma-separated DNS record types (default: "A,TXT")
timeout: DNS query timeout in seconds (1-30, default: 5)
Supported Record Types:
A: IPv4 addresses
TXT: Text records (including SPF detection)
MX: Mail exchange records
CNAME: Canonical name records
NS: Name server records
PTR: Reverse DNS records
Any other standard DNS record type
Structured Output Includes:
host: Target hostname
records: Object with each record type as keys
summary: Overview with counts and flags:
total_record_types: Number of record types queried
successful_queries: Number of successful queries
failed_queries: Number of failed queries
has_ip_addresses: Boolean flag for A records
has_mail_records: Boolean flag for MX/SPF records
has_txt_records: Boolean flag for TXT records
Legacy Compatibility:
Maintains backward compatibility with original dns_tool.py
Includes ip_addresses and email_host fields
Automatic SPF parsing from TXT records
Integration with AllServices
The DNS service is now available in the combined server at:

URL: http://localhost:8999/dns
Service Discovery: Listed in /services endpoint
Documentation: Available at root / endpoint
Usage Examples:
Basic DNS lookup (A and TXT records):
curl "http://localhost:8999/dns?host=google.com"

Multiple record types:
curl "http://localhost:8999/dns?host=google.com&record_types=A,MX,NS,TXT"

With custom timeout:
curl "http://localhost:8999/dns?host=example.com&record_types=A,CNAME&timeout=10"

POST request:
curl -X POST http://localhost:8999/dns \
  -H "Content-Type: application/json" \
  -d '{"host": "google.com", "record_types": ["A", "MX", "TXT"], "timeout": 5}'

Example Response:
```{
  "service": "dns",
  "process_time_ms": 45,
  "target": "google.com",
  "arguments": {
    "record_types": ["A", "TXT"],
    "timeout": 5
  },
  "return_code": 0,
  "raw_output": "A records for google.com:\n  172.217.12.142\nTXT records for google.com:\n  v=spf1 include:_spf.google.com ~all",
  "raw_error": "",
  "structured_output": {
    "host": "google.com",
    "records": {
      "A": ["172.217.12.142"],
      "TXT": ["v=spf1 include:_spf.google.com ~all"]
    },
    "summary": {
      "total_record_types": 2,
      "successful_queries": 2,
      "failed_queries": 0,
      "has_ip_addresses": true,
      "has_mail_records": true,
      "has_txt_records": true
    }
  }
}```


The DNS service is now fully integrated and provides comprehensive DNS analysis capabilities for penetration testing and reconnaissance workflows!

https://gofastmcp.com/servers/server#running-the-server

pkill -f "python3 allservices.py"

cd /home/jp/Documents/ocular_agents && source .venv/bin/activate && cd mcp && python3 allservices.py &


cd /home/jp/Documents/ocular_agents && source .venv/bin/activate && cd mcp && python3 allservices.py &
cd /home/jp/Documents/ocular_agents && source .venv/bin/activate && cd mcp && python3 allservices.py &

sleep 3 && curl -s "http://localhost:8999/services" | jq '.services[] | select(.name=="wpscan")'
ps aux | grep allservices
curl -s "http://localhost:8999/services" | jq '.services[6]'

## testing nmap
curl -s -X POST "http://localhost:8999/nmap" -H "Content-Type: application/json" -d '{"target": "127.0.0.1", "scan_type": "fast"}' | jq '.service, .return_code, .process_time_ms, .structured_output.scan_stats'