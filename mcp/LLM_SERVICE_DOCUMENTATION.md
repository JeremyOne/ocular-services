# Ocular Agents MCP Service Documentation

## Overview

This document provides comprehensive documentation for all services available through the Ocular Agents MCP (Model Context Protocol) server. These services are designed for penetration testing, network discovery, and security auditing tasks.

**Server Name:** `Ocular Services`  
**Protocol:** MCP (Model Context Protocol) via FastMCP  
**Purpose:** Penetration testing and network discovery tools

---

## Common Response Format

All services return a standardized `ServiceResponse` object with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| `service` | string | Name of the service that generated the response |
| `target` | string | The target IP, domain, or resource that was scanned |
| `process_start_time` | datetime | UTC timestamp when processing started |
| `process_time_ms` | integer | Processing time in milliseconds |
| `process_end_time` | datetime | UTC timestamp when processing ended |
| `arguments` | object | Dictionary of arguments passed to the service |
| `raw_command` | string | The actual command executed |
| `return_code` | integer | Exit code from service execution (0 = success) |
| `raw_output` | string | Raw stdout from the service |
| `raw_error` | string | Raw stderr from the service |

**Common Parameter:** All services support an `AsJson` parameter (boolean, default: false) that returns the response as a JSON string instead of a string representation.

---

## Services

### 1. Ping Service

**Tool Name:** `ping`  
**Description:** Network connectivity testing using ICMP ping.  
**Use Cases:** Test network reachability, measure latency, verify host availability.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `host` | string | ✅ Yes | - | Valid hostname or IP | Target hostname or IP address to ping |
| `count` | integer | No | 5 | 1-99 | Number of ping packets to send |
| `interval` | float | No | 1.0 | 0.01-5.0 seconds | Interval between packets in seconds |
| `packet_size` | integer | No | 56 | 1-65524 bytes | Size of data bytes to send |
| `timeout` | integer | No | 60 | 1+ seconds | Command timeout in seconds |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Example Usage
```
ping(host="192.168.1.1", count=10, interval=0.5, packet_size=64, AsJson=true)
```

#### Expected Output
Returns ICMP echo reply statistics including packet loss percentage, round-trip times (min/avg/max/mdev).

---

### 2. Time Service

**Tool Name:** `time`  
**Description:** Get the current date and time from the server.  
**Use Cases:** Synchronize timestamps, verify server time, log time-based operations.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `InUTC` | boolean | ✅ Yes | - | Return time in UTC timezone if true, local time if false |
| `AsJson` | boolean | ✅ Yes | - | Return response as JSON object with "datetime" key |

#### Example Usage
```
time(InUTC=true, AsJson=true)
```

#### Expected Output
ISO 8601 formatted datetime string (e.g., `2026-01-28T14:30:00.000000+00:00`)

---

### 3. cURL Service

**Tool Name:** `curl`  
**Description:** Make HTTP requests using curl for penetration testing and discovery.  
**Use Cases:** Web application testing, API probing, header analysis, SSL/TLS testing.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `url` | string | ✅ Yes | - | Valid URL | Target URL to request |
| `method` | string | No | "GET" | HTTP methods | HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS) |
| `headers` | string | No | "" | Semicolon-separated | Custom headers to send (e.g., "Accept: application/json;X-Custom: value") |
| `data` | string | No | "" | - | POST/PUT/PATCH data to send |
| `follow_redirects` | boolean | No | false | - | Follow HTTP redirects (curl -L) |
| `verbose` | boolean | No | false | - | Enable verbose output (curl -v) |
| `insecure` | boolean | No | false | - | Allow insecure SSL connections (curl -k) |
| `user_agent` | string | No | "" | - | Custom User-Agent header |
| `headers_only` | boolean | No | false | - | Get headers only, no body (curl -I) |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Example Usage
```
curl(url="https://example.com/api", method="POST", headers="Content-Type: application/json;Authorization: Bearer token", data='{"key":"value"}', follow_redirects=true, AsJson=true)
```

#### Expected Output
HTTP response including status code, headers, and body content.

---

### 4. DNS Service

**Tool Name:** `dns`  
**Description:** Perform DNS lookups for various record types.  
**Use Cases:** DNS enumeration, mail server discovery, domain reconnaissance, subdomain analysis.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `host` | string | ✅ Yes | - | Valid hostname | Target hostname or domain to look up |
| `record_types` | string | No | "A,TXT" | Comma-separated | DNS record types to query |
| `timeout` | float | No | 5.0 | 1-30 seconds | DNS query timeout in seconds |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Supported Record Types

| Type | Description |
|------|-------------|
| `A` | IPv4 address records |
| `AAAA` | IPv6 address records |
| `MX` | Mail exchange records |
| `TXT` | Text records (SPF, DKIM, etc.) |
| `CNAME` | Canonical name records |
| `NS` | Name server records |
| `PTR` | Pointer records (reverse DNS) |
| `SOA` | Start of Authority records |
| `SRV` | Service records |

#### Example Usage
```
dns(host="example.com", record_types="A,MX,TXT,NS", timeout=10.0, AsJson=true)
```

#### Expected Output
DNS records organized by type with associated values.

---

### 5. WHOIS Service

**Tool Name:** `whois`  
**Description:** WHOIS domain registration information lookup.  
**Use Cases:** Domain ownership research, registrar identification, registration date analysis.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `domain` | string | ✅ Yes | - | Valid domain | Domain name to lookup (e.g., example.com) |
| `options` | string | No | "" | WHOIS flags | WHOIS options (-R, -a, -t, -H) |
| `server` | string | No | "" | Hostname | Specific WHOIS server to query |
| `timeout` | integer | No | 30 | 1-120 seconds | Command timeout in seconds |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Available Options

| Option | Description |
|--------|-------------|
| `-R` | Show registrar information only |
| `-a` | Show administrative contact information |
| `-t` | Show technical contact information |
| `-H` | Hide legal disclaimers, show full details |

#### Example Usage
```
whois(domain="example.com", options="-H", timeout=60, AsJson=true)
```

#### Expected Output
Domain registration information including registrar, creation date, expiration date, name servers, and contact information.

---

### 6. WPScan Service

**Tool Name:** `wpscan`  
**Description:** WordPress security scanner using WPScan.  
**Use Cases:** WordPress vulnerability assessment, plugin/theme enumeration, user discovery.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `url` | string | ✅ Yes | - | Valid URL | Target WordPress URL (include http:// or https://) |
| `options` | string | No | "basic" | Scan type | Scan type preset (see below) |
| `api_token` | string | No | "" | - | WordPress Vulnerability Database API token |
| `timeout` | integer | No | 300 | 60-1800 seconds | Command timeout in seconds |
| `force` | boolean | No | false | - | Force scan even if WordPress not detected |
| `random_user_agent` | boolean | No | false | - | Use random user agent |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Scan Type Options

| Option | Description | Detection Mode |
|--------|-------------|----------------|
| `basic` | Basic scan for plugins, themes, users | Mixed |
| `plugins` | Aggressive plugin enumeration | Aggressive |
| `themes` | Aggressive theme enumeration | Aggressive |
| `users` | User enumeration only | - |
| `vulns` | Scan for vulnerable plugins and themes | Aggressive |
| `full` | Full comprehensive scan (slow) | Aggressive |
| `passive` | Passive scan (less detectable) | Passive |

#### Example Usage
```
wpscan(url="https://wordpress-site.com", options="vulns", api_token="your-token", force=true, AsJson=true)
```

#### Expected Output
WordPress version, detected plugins/themes, enumerated users, identified vulnerabilities.

---

### 7. HTTPX Service

**Tool Name:** `httpx`  
**Description:** Fast HTTP/HTTPS service discovery and analysis using ProjectDiscovery's httpx.  
**Use Cases:** Web service discovery, technology detection, bulk URL probing.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `targets` | string | ✅ Yes | - | Comma-separated | Target hosts/URLs to probe |
| `options` | string | No | "basic" | Scan type | Scan type preset (see below) |
| `ports` | string | No | "80,443,8080,8443" | Comma-separated | Ports to probe |
| `paths` | string | No | "" | Comma-separated | Paths to test |
| `method` | string | No | "GET" | HTTP method | HTTP method to use |
| `timeout` | integer | No | 10 | 5-120 seconds | Request timeout per target |
| `threads` | integer | No | 50 | 1-100 | Number of concurrent threads |
| `rate_limit` | integer | No | 150 | 1-1000 | Maximum requests per second |
| `retries` | integer | No | 2 | 0-5 | Number of retry attempts |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Scan Type Options

| Option | Description |
|--------|-------------|
| `basic` | Status code, content length, page title |
| `detailed` | Basic + technology detection, web server, response time |
| `headers` | Basic + response headers |
| `hashes` | Basic + MD5, SHA256, SimHash of response |
| `comprehensive` | All options combined including JARM fingerprint |

#### Example Usage
```
httpx(targets="example.com,test.com", options="detailed", ports="80,443,8080", threads=25, AsJson=true)
```

#### Expected Output
HTTP response details including status codes, content length, titles, technologies, and server information.

---

### 8. NBTScan Service

**Tool Name:** `nbtscan`  
**Description:** NetBIOS name scanner for Windows network discovery.  
**Use Cases:** Windows network enumeration, NetBIOS name resolution, workgroup discovery.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `target` | string | ✅ Yes | - | IP/range/subnet | IP address, range, or subnet to scan |
| `options` | string | No | "basic" | Scan type | Scan options preset (see below) |
| `timeout` | integer | No | 1000 | 100-30000 ms | Response timeout in milliseconds |
| `verbose` | boolean | No | false | - | Enable verbose output |
| `retransmits` | integer | No | 0 | 0-10 | Number of retransmits |
| `use_local_port` | boolean | No | false | - | Use local port 137 (requires root) |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Scan Options

| Option | Description |
|--------|-------------|
| `basic` | Standard NetBIOS name scan |
| `verbose` | Verbose output with all names |
| `script` | Script-friendly output format |
| `hosts` | Output in /etc/hosts format |
| `lmhosts` | Output in lmhosts format |

#### Target Formats

| Format | Example | Description |
|--------|---------|-------------|
| Single IP | `192.168.1.1` | Scan single host |
| IP Range | `192.168.1.1-254` | Scan range of IPs |
| CIDR | `192.168.1.0/24` | Scan entire subnet |

#### Example Usage
```
nbtscan(target="192.168.1.0/24", options="verbose", timeout=2000, AsJson=true)
```

#### Expected Output
Discovered hosts with NetBIOS names, computer names, domains/workgroups, and services.

---

### 9. Nmap Service

**Tool Name:** `nmap`  
**Description:** Network Mapper for network discovery and security auditing.  
**Use Cases:** Port scanning, service detection, OS fingerprinting, vulnerability scanning.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `target` | string | ✅ Yes | - | IP/hostname/range | Target host, IP, or network range to scan |
| `scan_type` | string | No | "fast" | Scan type | Type of scan preset (see below) |
| `timeout` | integer | No | 240 | 30-1800 seconds | Command timeout in seconds |
| `ports` | string | No | "" | Port specification | Specific ports to scan (overrides scan_type) |
| `scripts` | string | No | "" | NSE scripts | Additional nmap scripts to run |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Scan Type Options

| Option | Nmap Flags | Description |
|--------|------------|-------------|
| `fast` | `-F -Pn -T4` | Fast scan of top 100 ports with faster timing |
| `service` | `-sV --top-ports 20 -Pn` | Service version detection on top 20 ports |
| `stealth` | `-sS -Pn` | Stealth SYN scan without pinging |
| `rdp` | `-p 3389 --script rdp-vuln-ms12-020,rdp-enum-encryption -Pn` | RDP vulnerability scan with specific scripts |
| `aggressive` | `-A -T4 -Pn` | Aggressive scan with OS detection |
| `vuln` | `-sV --script vuln -Pn` | CVE vulnerability scanning with service detection |

#### Target Formats

| Format | Example | Description |
|--------|---------|-------------|
| Single IP | `192.168.1.1` | Scan single host |
| Hostname | `example.com` | Scan by hostname |
| IP Range | `192.168.1.1-254` | Scan range |
| CIDR | `192.168.1.0/24` | Scan subnet |
| Multiple | `192.168.1.1 192.168.1.2` | Space-separated targets |

#### Example Usage
```
nmap(target="192.168.1.0/24", scan_type="service", ports="22,80,443,3389", scripts="http-title,ssh-auth-methods", AsJson=true)
```

#### Expected Output
Port states, service versions, OS detection results, script output.

---

### 10. Nikto Service

**Tool Name:** `nikto`  
**Description:** Web vulnerability scanner for comprehensive security testing.  
**Use Cases:** Web server vulnerability assessment, misconfigurations, information disclosure.

#### Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `target` | string | ✅ Yes | - | URL/hostname | Target URL or hostname to scan |
| `scan_type` | string | No | "basic" | Scan type | Type of scan preset (see below) |
| `port` | string | No | "" | Port number | Port to scan (auto-detected if not specified) |
| `ssl` | boolean | No | false | - | Force SSL mode (auto-detected from URL) |
| `timeout` | integer | No | 10 | 5-300 seconds | Request timeout in seconds |
| `tuning` | string | No | "" | 1-9 | Nikto tuning options (comma-separated) |
| `plugins` | string | No | "" | Plugin names | Specific plugins to run |
| `vhost` | string | No | "" | Hostname | Virtual host header |
| `AsJson` | boolean | No | false | - | Return response as JSON string |

#### Scan Type Options

| Option | Description |
|--------|-------------|
| `basic` | Standard host scan |
| `ssl` | Force SSL scan |
| `cgi` | Check all CGI directories |
| `files` | Look for interesting files (tuning 1) |
| `misconfig` | Look for misconfigurations (tuning 2) |
| `disclosure` | Look for information disclosure (tuning 3) |
| `comprehensive` | All tuning options (1-9) |
| `fast` | Quick scan with reduced timeouts |

#### Tuning Options

| Tuning | Description |
|--------|-------------|
| `1` | Interesting files/Seen in logs |
| `2` | Misconfiguration/Default files |
| `3` | Information Disclosure |
| `4` | Injection (XSS/Script/HTML) |
| `5` | Remote File Retrieval - Inside Web Root |
| `6` | Denial of Service |
| `7` | Remote File Retrieval - Server Wide |
| `8` | Command Execution/Remote Shell |
| `9` | SQL Injection |

#### Example Usage
```
nikto(target="https://example.com", scan_type="comprehensive", timeout=30, vhost="www.example.com", AsJson=true)
```

#### Expected Output
Identified vulnerabilities, misconfigurations, server information, interesting files.

---

## Error Handling

All services handle errors consistently:

1. **Parameter Validation Errors:** Returned immediately with descriptive error messages in `raw_error`
2. **Tool Not Installed:** Returns error message with installation instructions
3. **Timeout Errors:** Returns partial results with timeout indication
4. **Network Errors:** Captured in `raw_error` field

### Checking for Errors

```python
# In response:
if response.return_code != 0 or response.raw_error:
    # Handle error
    print(f"Error: {response.raw_error}")
```

---

## Best Practices for LLM Clients

1. **Always check `return_code`:** A value of 0 indicates success
2. **Use `AsJson=true`:** For structured parsing of responses
3. **Respect timeouts:** Long-running scans (nmap, wpscan, nikto) may need extended timeouts
4. **Handle rate limits:** Use appropriate `rate_limit` and `threads` values for httpx
5. **Validate targets:** Ensure targets are properly formatted before calling services
6. **Chain services logically:** Use DNS → Ping → Port scan → Service scan workflow
7. **Store raw output:** Keep `raw_output` for detailed analysis when needed

---

## Quick Reference

| Service | Primary Use | Key Parameters |
|---------|-------------|----------------|
| `ping` | Connectivity test | host, count |
| `time` | Server time | InUTC, AsJson |
| `curl` | HTTP requests | url, method, headers |
| `dns` | DNS enumeration | host, record_types |
| `whois` | Domain info | domain |
| `wpscan` | WordPress security | url, options |
| `httpx` | HTTP discovery | targets, options |
| `nbtscan` | NetBIOS scan | target |
| `nmap` | Port/service scan | target, scan_type |
| `nikto` | Web vulnerabilities | target, scan_type |

---

## Version Information

- **Documentation Version:** 0.3.2
- **Last Updated:** February 16, 2026
- **Compatible MCP Version:** FastMCP
