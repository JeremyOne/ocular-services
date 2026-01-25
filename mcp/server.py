from typing import Optional
import asyncio
import subprocess
import re
import json
import time
import requests
import logging
from fastmcp import FastMCP
from fastmcp.client.logging import LogMessage
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse


import ping_service as ping_service_module
import curl_service as curl_service_module  
import dns_service as dns_service_module
## import enum4linux_service as enum4linux_service_module
import whois_service as whois_service_module
import wpscan_service as wpscan_service_module
import httpx_service as httpx_service_module
import nbtscan_service as nbtscan_service_module
import nmap_service as nmap_service_module
import nikto_service as nikto_service_module

from ping_service import ping_host
from datetime import datetime, timezone
from curl_service import curl_request
from dns_service import dns_lookup
##from enum4linux_service import enum4linux_scan
from whois_service import whois_lookup
from wpscan_service import wpscan_scan
from httpx_service import httpx_scan
from nbtscan_service import nbtscan_scan
from nmap_service import nmap_scan
from nikto_service import nikto_scan

# Custom log handler to provide detailed logging to console
async def detailed_log_handler(message: LogMessage):
    msg = message.data.get('msg')
    extra = message.data.get('extra')

    if message.level == "error":
        print(f"ERROR: {msg} | Details: {extra}")
    elif message.level == "warning":
        print(f"WARNING: {msg} | Details: {extra}")
    else:
        print(f"{message.level.upper()}: {msg}")


# Combined MCP server for all ocular_agents services
# This server provides access to multiple penetration testing tools
mcp = FastMCP(
    name="Ocular Agents",
    instructions="This MCP server provides access to multiple penetration testing and network discovery tools."
    )

# Ping Service Endpoint
@mcp.tool(
        name="ping",
        description="Network connectivity testing using ICMP ping."
    )
async def ping_service(host: str, count: int = 5, interval: float = 1.0, packet_size: int = 56, AsJson: bool = False) -> str:
    result = await ping_host(host, count, interval, packet_size)
    
    if AsJson:
        return json.dumps(result)
    else:
        return result.__repr__()

@mcp.tool(
        name="time",
        description="Get the current date and time from the server."
    )
async def time_service(InUTC: bool, AsJson: bool) -> str:
    if AsJson:
        if InUTC:
            return json.dumps({"datetime": datetime.now(timezone.utc).isoformat()})
        else:
            return json.dumps({"datetime": datetime.now().isoformat()})
    else:
        if InUTC:
            return datetime.now(timezone.utc).isoformat()
        else:
            return datetime.now().isoformat()


@mcp.tool(
        name="curl",
        description="Make HTTP requests using curl for penetration testing and discovery."
    )
async def curl_service(url: str, method: str = "GET", headers: str = "", data: str = "", 
                       follow_redirects: bool = False, verbose: bool = False, insecure: bool = False, 
                       user_agent: str = "", headers_only: bool = False, AsJson: bool = False) -> str:
    
    result = await curl_request(url, method, headers, data, follow_redirects, verbose, insecure, user_agent, headers_only)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()


@mcp.tool(
        name="dns",
        description="Perform DNS lookups for various record types."
    )
async def dns_service(host: str, record_types: str = "A,TXT", timeout: float = 5.0, AsJson: bool = False) -> str:
    result = await dns_lookup(host, record_types, timeout)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()


@mcp.tool(
        name="whois",
        description="WHOIS domain registration information lookup."
    )
async def whois_service(domain: str, options: str = "", server: str = "", timeout: int = 30, AsJson: bool = False) -> str:
    result = await whois_lookup(domain, options, server, timeout)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()


@mcp.tool(
        name="wpscan",
        description="WordPress security scanner using WPScan."
    )
async def wpscan_service(url: str, options: str = "basic", api_token: str = "", timeout: int = 300, 
                         force: bool = False, random_user_agent: bool = False, AsJson: bool = False) -> str:
    result = await wpscan_scan(url, options, api_token, timeout, force, random_user_agent)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()


@mcp.tool(
        name="httpx",
        description="Fast HTTP/HTTPS service discovery and analysis."
    )
async def httpx_service(targets: str, options: str = "basic", ports: str = "80,443,8080,8443", paths: str = "", 
                        method: str = "GET", timeout: int = 10, threads: int = 50, rate_limit: int = 150, 
                        retries: int = 2, AsJson: bool = False) -> str:
    result = await httpx_scan(targets, options, ports, paths, method, timeout, threads, rate_limit, retries)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()


@mcp.tool(
        name="nbtscan",
        description="NetBIOS name scanner for Windows network discovery."
    )
async def nbtscan_service(target: str, options: str = "basic", timeout: int = 1000, verbose: bool = False,
                          retransmits: int = 0, use_local_port: bool = False, AsJson: bool = False) -> str:
    result = await nbtscan_scan(target, options, timeout, verbose, retransmits, use_local_port)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()


@mcp.tool(
        name="nmap",
        description="Network Mapper for network discovery and security auditing."
    )
async def nmap_service(target: str, scan_type: str = "fast", timeout: int = 240, 
                       ports: str = "", scripts: str = "", AsJson: bool = False) -> str:
    result = await nmap_scan(target, scan_type, timeout, ports, scripts)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()


@mcp.tool(
        name="nikto",
        description="Web vulnerability scanner for comprehensive security testing."
    )
async def nikto_service(target: str, scan_type: str = "basic", port: str = "", ssl: bool = False, 
                        timeout: int = 10, tuning: str = "", plugins: str = "", vhost: str = "", 
                        AsJson: bool = False) -> str:
    result = await nikto_scan(target, scan_type, port, ssl, timeout, tuning, plugins, vhost)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()



# Service Discovery Endpoint
#@mcp.custom_route("/services", methods=["GET"])
#
#async def list_services(request: Request) -> JSONResponse:
#    #List all available services in this MCP server."""
#
#    all_service_info = [
#        ping_service_module.get_service_info(),
#        curl_service_module.get_service_info(),
#        dns_service_module.get_service_info(),
#        ## enum4linux_service_module.get_service_info(),
#        whois_service_module.get_service_info(),
#        wpscan_service_module.get_service_info(),
#        httpx_service_module.get_service_info(),
#        nbtscan_service_module.get_service_info(),
#        nmap_service_module.get_service_info(),
#        nikto_service_module.get_service_info()
#    ]
#
#    services = {
#        "server": "Ocular Agents",
#        "version": "1.0",
#        "services": all_service_info
#    }
#    return JSONResponse(services)


# Health Check Endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

# Root Endpoint
#@mcp.custom_route("/", methods=["GET"])
#async def root(request: Request) -> JSONResponse:
#    """Root endpoint with basic server information."""
#    info = {
#        "server": "Ocular Agents - All Services",
#        "description": "MCP server providing penetration testing and network discovery tools",
#        "version": "1.0",
#        "endpoints": {
#            "/": "This information page",
#            "/services": "List all available services",
#            "/ping": "Network connectivity testing",
#            "/curl": "HTTP request testing",
#            "/datetime": "Date and time information",
#            "/dns": "DNS record lookups",
#            "/enum4linux": "SMB/CIFS enumeration",
#            "/whois": "Domain registration information",
#            "/wpscan": "WordPress security scanning",
#            "/httpx": "HTTP/HTTPS service discovery",
#            "/nbtscan": "NetBIOS name scanning",
#            "/nmap": "Network mapping and port scanning",
#            "/health": "Health check"
#        },
#        "documentation": "See /services for detailed parameter information"
#    }
#    return JSONResponse(info)


#@mcp.custom_route("/test", methods=["GET"])
#async def test_all_services(request: Request) -> JSONResponse:
#    """Exercise each service endpoint once.
#
#    This endpoint is intended as a lightweight smoke test for the unified server.
#    It makes HTTP requests to the server itself (localhost:8999) and returns a
#    per-service summary of whether each call succeeded.
#    """
#
#    base_url = "http://127.0.0.1:8999"
#
#    tests = [
#        ("ping", "/ping", "GET", {"host": "127.0.0.1", "count": "1"}),
#        ("curl", "/curl", "GET", {"url": "http://example.com", "headers_only": "true"}),
#        ("datetime", "/datetime", "GET", {}),
#        ("dns", "/dns", "GET", {"host": "example.com", "record_types": "A"}),
#        ("whois", "/whois", "GET", {"domain": "example.com"}),
#        ("httpx", "/httpx", "GET", {"targets": "example.com", "options": "basic"}),
#        ("nbtscan", "/nbtscan", "GET", {"target": "127.0.0.1", "options": "basic"}),
#        ("nmap", "/nmap", "GET", {"target": "127.0.0.1", "scan_type": "fast", "timeout": "60"}),
#        ("nikto", "/nikto", "GET", {"target": "http://example.com", "scan_type": "fast"}),
#        ("wpscan", "/wpscan", "GET", {"url": "http://example.com", "options": "passive", "timeout": "120"}),
#    ]
#
#    def _do_request(name: str, path: str, method: str, params: dict) -> dict:
#        start = time.time()
#        try:
#            resp = requests.request(method, f"{base_url}{path}", params=params, timeout=30)
#            elapsed_ms = int((time.time() - start) * 1000)
#            try:
#                body = resp.json()
#            except Exception:
#                body = resp.text[:500]
#
#            return {
#                "service": name,
#                "endpoint": path,
#                "method": method,
#                "ok": resp.ok,
#                "status_code": resp.status_code,
#                "elapsed_ms": elapsed_ms,
#                "response": body,
#            }
#        except Exception as e:
#            elapsed_ms = int((time.time() - start) * 1000)
#            return {
#                "service": name,
#                "endpoint": path,
#                "method": method,
#                "ok": False,
#                "status_code": None,
#                "elapsed_ms": elapsed_ms,
#                "error": str(e),
#            }
#
#    results = await asyncio.gather(
#        *[asyncio.to_thread(_do_request, name, path, method, params) for (name, path, method, params) in tests]
#    )
#
#    summary = {
#        "total": len(results),
#        "ok": sum(1 for r in results if r.get("ok")),
#        "failed": sum(1 for r in results if not r.get("ok")),
#    }
#
#    return JSONResponse({"summary": summary, "results": results})

if __name__ == "__main__":
    #mcp.add_log_handler(detailed_log_handler)
    mcp.run(transport="http", host="0.0.0.0", port=8999, log_level="DEBUG") 
