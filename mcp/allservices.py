from typing import Optional
import subprocess
import re
import json
import time
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from ping_service import ping_host
from curl_service import curl_request
from datetime_service import get_datetime
from dns_service import dns_lookup_service
from enum4linux_service import enum4linux_scan
from whois_service import whois_lookup
from wpscan_service import wpscan_scan
from httpx_service import httpx_scan
from nbtscan_service import nbtscan_scan

# Combined MCP server for all ocular_agents services
# This server provides access to multiple penetration testing tools
# Currently includes: ping, curl, datetime, dns, enum4linux, whois, wpscan, httpx, nbtscan

# Create FastMCP server
mcp = FastMCP("Ocular Agents - All Services")


# Ping Service Endpoint
@mcp.custom_route("/ping", methods=["GET", "POST"])
async def ping_service(request: Request) -> JSONResponse:
    return await ping_host(request)

@mcp.custom_route("/curl", methods=["GET", "POST"])
async def curl_service(request: Request) -> JSONResponse:
    return await curl_request(request)

@mcp.custom_route("/datetime", methods=["GET", "POST"])
async def datetime_service(request: Request) -> JSONResponse:
    return await get_datetime(request)

@mcp.custom_route("/dns", methods=["GET", "POST"])
async def dns_service(request: Request) -> JSONResponse:
    return await dns_lookup_service(request)

@mcp.custom_route("/enum4linux", methods=["GET", "POST"])
async def enum4linux_service(request: Request) -> JSONResponse:
    return await enum4linux_scan(request)

@mcp.custom_route("/whois", methods=["GET", "POST"])
async def whois_service(request: Request) -> JSONResponse:
    return await whois_lookup(request)

@mcp.custom_route("/wpscan", methods=["GET", "POST"])
async def wpscan_service(request: Request) -> JSONResponse:
    return await wpscan_scan(request)

@mcp.custom_route("/httpx", methods=["GET", "POST"])
async def httpx_service(request: Request) -> JSONResponse:
    return await httpx_scan(request)

@mcp.custom_route("/nbtscan", methods=["GET", "POST"])
async def nbtscan_service(request: Request) -> JSONResponse:
    return await nbtscan_scan(request)

# Service Discovery Endpoint
@mcp.custom_route("/services", methods=["GET"])
async def list_services(request: Request) -> JSONResponse:
    """List all available services in this MCP server."""
    services = {
        "server": "Ocular Agents - All Services",
        "version": "1.0",
        "services": [
            {
                "name": "ping",
                "endpoint": "/ping",
                "description": "Network connectivity testing using ICMP ping",
                "methods": ["GET", "POST"],
                "parameters": {
                    "host": "Target hostname or IP address (required)",
                    "count": "Number of ping packets (1-99, default: 5)",
                    "interval": "Interval between packets (0.01-5.0, default: 1.0)",
                    "packet_size": "Size of data bytes (1-65524, default: 56)"
                }
            },
            {
                "name": "curl",
                "endpoint": "/curl",
                "description": "HTTP requests for web application testing",
                "methods": ["GET", "POST"],
                "parameters": {
                    "url": "Target URL (required)",
                    "method": "HTTP method (default: GET)",
                    "headers": "Custom headers (semicolon-separated)",
                    "data": "POST data",
                    "follow_redirects": "Follow HTTP redirects (boolean)",
                    "verbose": "Enable verbose output (boolean)",
                    "insecure": "Allow insecure SSL (boolean)",
                    "user_agent": "Custom User-Agent string",
                    "headers_only": "Get headers only (boolean)"
                }
            },
            {
                "name": "datetime",
                "endpoint": "/datetime", 
                "description": "Get current date and time with various formats",
                "methods": ["GET", "POST"],
                "parameters": {
                    "timezone": "Timezone to convert to (optional)",
                    "format": "Custom strftime format string (optional)",
                    "utc": "Return UTC time (boolean, default: false)"
                }
            },
            {
                "name": "dns",
                "endpoint": "/dns",
                "description": "DNS record lookups and domain analysis",
                "methods": ["GET", "POST"],
                "parameters": {
                    "host": "Hostname or domain to look up (required)",
                    "record_types": "Comma-separated DNS record types (default: A,TXT)",
                    "timeout": "DNS query timeout in seconds (1-30, default: 5)"
                }
            },
            {
                "name": "enum4linux",
                "endpoint": "/enum4linux",
                "description": "SMB/CIFS enumeration using enum4linux tool",
                "methods": ["GET", "POST"],
                "parameters": {
                    "target": "Target hostname or IP address (required)",
                    "options": "Enumeration options (default: -a for all)",
                    "username": "Username for authentication (optional)",
                    "password": "Password for authentication (optional)",
                    "timeout": "Command timeout in seconds (30-600, default: 120)"
                }
            },
            {
                "name": "whois",
                "endpoint": "/whois",
                "description": "WHOIS domain registration information lookup",
                "methods": ["GET", "POST"],
                "parameters": {
                    "domain": "Domain name to lookup (required, e.g., example.com)",
                    "options": "WHOIS options (optional, e.g., -R, -a, -t, -H)",
                    "server": "Specific WHOIS server to query (optional)",
                    "timeout": "Command timeout in seconds (10-120, default: 30)"
                }
            },
            {
                "name": "wpscan",
                "endpoint": "/wpscan",
                "description": "WordPress security scanner using WPScan",
                "methods": ["GET", "POST"],
                "parameters": {
                    "url": "Target WordPress URL (required, include http:// or https://)",
                    "options": "Scan type: basic, plugins, themes, users, vulns, full, passive (default: basic)",
                    "api_token": "WordPress vulnerability database API token (optional)",
                    "timeout": "Command timeout in seconds (60-1800, default: 300)",
                    "force": "Force scan even if WordPress not detected (boolean)",
                    "random_user_agent": "Use random user agent (boolean)"
                }
            },
            {
                "name": "httpx",
                "endpoint": "/httpx",
                "description": "Fast HTTP/HTTPS service discovery and analysis",
                "methods": ["GET", "POST"],
                "parameters": {
                    "targets": "Target hosts/URLs to probe (required, comma-separated for multiple)",
                    "options": "Scan type: basic, detailed, headers, hashes, comprehensive (default: basic)",
                    "ports": "Ports to probe (comma-separated, default: 80,443,8080,8443)",
                    "paths": "Paths to test (comma-separated, optional)",
                    "method": "HTTP method to use (default: GET)",
                    "timeout": "Request timeout in seconds (5-120, default: 10)",
                    "threads": "Number of threads (1-100, default: 50)",
                    "rate_limit": "Requests per second limit (1-1000, default: 150)",
                    "retries": "Number of retries (0-5, default: 2)"
                }
            },
            {
                "name": "nbtscan",
                "endpoint": "/nbtscan",
                "description": "NetBIOS name scanner for Windows network discovery",
                "methods": ["GET", "POST"],
                "parameters": {
                    "target": "IP address, range, or subnet to scan (required)",
                    "options": "Scan options: basic, verbose, script, hosts, lmhosts (default: basic)",
                    "timeout": "Response timeout in milliseconds (100-30000, default: 1000)",
                    "verbose": "Enable verbose output (boolean)",
                    "retransmits": "Number of retransmits (0-10, default: 0)",
                    "use_local_port": "Use local port 137 for scans (boolean, requires root)"
                }
            }
        ]
    }
    return JSONResponse(services)

# Health Check Endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

# Root Endpoint
@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    """Root endpoint with basic server information."""
    info = {
        "server": "Ocular Agents - All Services",
        "description": "MCP server providing penetration testing and network discovery tools",
        "version": "1.0",
        "endpoints": {
            "/": "This information page",
            "/services": "List all available services",
            "/ping": "Network connectivity testing",
            "/curl": "HTTP request testing",
            "/datetime": "Date and time information",
            "/dns": "DNS record lookups",
            "/enum4linux": "SMB/CIFS enumeration",
            "/whois": "Domain registration information",
            "/wpscan": "WordPress security scanning",
            "/httpx": "HTTP/HTTPS service discovery",
            "/nbtscan": "NetBIOS name scanning",
            "/health": "Health check"
        },
        "documentation": "See /services for detailed parameter information"
    }
    return JSONResponse(info)

if __name__ == "__main__":
    # Run combined server on port 8999
    mcp.run(transport="http", host="0.0.0.0", port=8999)
