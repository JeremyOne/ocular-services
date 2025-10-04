from typing import Optional
import subprocess
import re
import json
import time
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from ping import ping_host
from curl import curl_request

# Combined MCP server for all ocular_agents services
# This server provides access to multiple penetration testing tools
# Currently includes: ping, curl

# Create FastMCP server
mcp = FastMCP("Ocular Agents - All Services")


# Ping Service Endpoint
@mcp.custom_route("/ping", methods=["GET", "POST"])
async def ping_service(request: Request) -> JSONResponse:
    return await ping_host(request)

@mcp.custom_route("/curl", methods=["GET", "POST"])
async def curl_service(request: Request) -> JSONResponse:
    return await curl_request(request)

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
            "/health": "Health check"
        },
        "documentation": "See /services for detailed parameter information"
    }
    return JSONResponse(info)

if __name__ == "__main__":
    # Run combined server on port 8999
    mcp.run(transport="http", host="0.0.0.0", port=8999)
