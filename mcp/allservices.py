from typing import Optional
import subprocess
import re
import json
import time
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

import ping_service
import curl_service  
import datetime_service
import dns_service
import enum4linux_service
import whois_service
import wpscan_service
import httpx_service
import nbtscan_service
import nmap_service
import nikto_service

from ping_service import ping_host
from curl_service import curl_request
from datetime_service import get_datetime
from dns_service import dns_lookup_service
from enum4linux_service import enum4linux_scan
from whois_service import whois_lookup
from wpscan_service import wpscan_scan
from httpx_service import httpx_scan
from nbtscan_service import nbtscan_scan
from nmap_service import nmap_scan
from nikto_service import nikto_scan

# Combined MCP server for all ocular_agents services
# This server provides access to multiple penetration testing tools
# Currently includes: ping, curl, datetime, dns, enum4linux, whois, wpscan, httpx, nbtscan, nmap, nikto
# Currently includes: ping, curl, datetime, dns, enum4linux, whois, wpscan, httpx, nbtscan, nmap

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

@mcp.custom_route("/nmap", methods=["GET", "POST"])
async def nmap_service(request: Request) -> JSONResponse:
    return await nmap_scan(request)

@mcp.custom_route("/nikto", methods=["GET", "POST"])
async def nikto_service(request: Request) -> JSONResponse:
    return await nikto_scan(request)

# Service Discovery Endpoint
@mcp.custom_route("/services", methods=["GET"])

async def list_services(request: Request) -> JSONResponse:
    """List all available services in this MCP server."""

    all_service_info = [
        ping_service.get_service_info(),
        curl_service.get_service_info(),
        datetime_service.get_service_info(),
        dns_service.get_service_info(),
        enum4linux_service.get_service_info(),
        whois_service.get_service_info(),
        wpscan_service.get_service_info(),
        httpx_service.get_service_info(),
        nbtscan_service.get_service_info(),
        nmap_service.get_service_info(),
        nikto_service.get_service_info()
    ]

    services = {
        "server": "Ocular Agents - All Services",
        "version": "1.0",
        "services": all_service_info
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
            "/nmap": "Network mapping and port scanning",
            "/health": "Health check"
        },
        "documentation": "See /services for detailed parameter information"
    }
    return JSONResponse(info)

if __name__ == "__main__":
    # Run combined server on port 8999
    mcp.run(transport="http", host="0.0.0.0", port=8999)
