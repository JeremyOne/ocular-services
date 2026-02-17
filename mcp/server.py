from typing import Optional
import asyncio
import subprocess
import re
import json
import time
import requests
import logging
import unittest
import sys
import os
import io

from fastmcp import Context, FastMCP
from docket import Timeout
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
from datetime import datetime, timedelta, timezone
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
    instructions="This MCP server provides access to multiple penetration testing and network discovery tools.",
    version="0.3.2"
    )

# Ping Service Endpoint
@mcp.tool(
        task=True,
        name="ping",
        description="Network connectivity testing using ICMP ping."
    )
async def ping_service(host: str, 
                       count: int = 5, 
                       interval: float = 1.0, 
                       packet_size: int = 56, 
                       AsJson: bool = False, 
                       timeout: int = 60,
                       ctx: Context = None) -> str:
    
    result = await ping_host(host, count, interval, packet_size, timeout, ctx)
    
    if AsJson:
        return json.dumps(result.to_dict())
    else:
        return result.__repr__()

@mcp.tool(
        name="time",
        description="Get the current date and time from the server."
    )
async def time_service(InUTC: bool = False, AsJson: bool = False) -> str:
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


# Health Check Endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    #mcp.add_log_handler(detailed_log_handler)
    mcp.run(transport="http", host="0.0.0.0", port=8999, log_level="DEBUG") 
