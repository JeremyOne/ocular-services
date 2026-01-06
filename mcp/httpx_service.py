from typing import Optional
import subprocess
import json
import os
import tempfile
import shutil
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# httpx - Fast and multi-purpose HTTP toolkit by ProjectDiscovery
# Usage: httpx [flags]
# 
# Key Options:
#   -u, -target           Input target host(s) to probe
#   -l, -list             Input file containing list of hosts
#   -sc, -status-code     Display response status-code
#   -cl, -content-length  Display response content-length
#   -ct, -content-type    Display response content-type
#   -title                Display page title
#   -tech-detect          Display technology in use
#   -web-server           Display server name
#   -method               Request method (GET, POST, etc.)
#   -ports                Ports to probe (default: 80,443,8080,8443)
#   -path                 Request path or list of paths
#   -json                 Output in JSON format
#   -silent               Silent mode
#   -no-color             Disable colored output
#   -threads              Number of threads (default: 50)
#   -rate-limit           Maximum requests per second
#   -timeout              Request timeout duration
#   -retries              Number of retries

# Create FastMCP server
mcp = FastMCP("Httpx Service")

def get_service_info() -> dict:
    return {
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
    }

def parse_httpx_output(json_output: str) -> dict:
    """Parse httpx JSON output into structured JSON format matching schema.json"""
    result = {
        "discovered_hosts": [],
        "statistics": {
            "total_hosts": 0,
            "responsive_hosts": 0,
            "unique_status_codes": [],
            "technologies_found": [],
            "web_servers_found": []
        },
        "hosts_by_status": {},
        "errors": []
    }
    
    if not json_output.strip():
        result["errors"].append("Empty httpx output")
        return result
    
    lines = json_output.strip().split('\n')
    status_codes = set()
    technologies = set()
    web_servers = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        try:
            data = json.loads(line)
            
            # Extract host information
            host_info = {
                "url": data.get("url", ""),
                "host": data.get("host", ""),
                "port": data.get("port", ""),
                "scheme": data.get("scheme", ""),
                "path": data.get("path", "/"),
                "status_code": data.get("status_code", 0),
                "content_length": data.get("content_length", 0),
                "content_type": data.get("content_type", ""),
                "title": data.get("title", ""),
                "web_server": data.get("webserver", ""),
                "technologies": data.get("tech", []),
                "response_time": data.get("response_time", ""),
                "method": data.get("method", "GET"),
                "location": data.get("location", ""),
                "hash": {},
                "headers": data.get("headers", {}),
                "jarm": data.get("jarm", ""),
                "a_records": data.get("a", []),
                "cnames": data.get("cname", []),
                "cdn": data.get("cdn", "")
            }
            
            # Extract hash information
            if "hash" in data:
                hash_data = data["hash"]
                if isinstance(hash_data, dict):
                    host_info["hash"] = {
                        "body_md5": hash_data.get("body_md5", ""),
                        "body_sha256": hash_data.get("body_sha256", ""),
                        "body_simhash": hash_data.get("body_simhash", ""),
                        "header_md5": hash_data.get("header_md5", ""),
                        "header_sha256": hash_data.get("header_sha256", "")
                    }
            
            result["discovered_hosts"].append(host_info)
            result["statistics"]["responsive_hosts"] += 1
            
            # Collect statistics
            if host_info["status_code"]:
                status_codes.add(host_info["status_code"])
                
                # Group by status code
                status_str = str(host_info["status_code"])
                if status_str not in result["hosts_by_status"]:
                    result["hosts_by_status"][status_str] = []
                result["hosts_by_status"][status_str].append(host_info["url"])
            
            if host_info["technologies"]:
                technologies.update(host_info["technologies"])
            
            if host_info["web_server"]:
                web_servers.add(host_info["web_server"])
                
        except json.JSONDecodeError as e:
            result["errors"].append(f"JSON parsing error: {str(e)} for line: {line[:100]}")
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)} for line: {line[:100]}")
    
    # Update statistics
    result["statistics"]["total_hosts"] = len(result["discovered_hosts"])
    result["statistics"]["unique_status_codes"] = sorted(list(status_codes))
    result["statistics"]["technologies_found"] = sorted(list(technologies))
    result["statistics"]["web_servers_found"] = sorted(list(web_servers))
    
    return result

@mcp.custom_route("/httpx", methods=["GET", "POST"])
async def httpx_scan(request: Request) -> JSONResponse:
    """Perform HTTP/HTTPS service discovery and analysis using httpx.
    
    Parameters:
        targets: Target hosts/URLs to probe (required, comma-separated for multiple)
        options: Scan options (default: basic probing)
        ports: Ports to probe (comma-separated, default: 80,443,8080,8443)
        paths: Paths to test (comma-separated, optional)
        method: HTTP method to use (default: GET)
        timeout: Request timeout in seconds (default: 10)
        threads: Number of threads (1-100, default: 50)
        rate_limit: Requests per second limit (default: 150)
        retries: Number of retries per request (default: 2)
        
    Available scan options:
        "basic": Status code, content length, title (default)
        "detailed": Basic + tech detection, web server, response time
        "headers": Include response headers analysis
        "hashes": Include response body and header hashes
        "comprehensive": All available information
        
    Returns:
        JSON response matching schema.json format
    """
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            targets = request.query_params.get("targets")
            options = request.query_params.get("options", "basic")
            ports = request.query_params.get("ports", "80,443,8080,8443")
            paths = request.query_params.get("paths", "")
            method = request.query_params.get("method", "GET")
            timeout = int(request.query_params.get("timeout", 10))
            threads = int(request.query_params.get("threads", 50))
            rate_limit = int(request.query_params.get("rate_limit", 150))
            retries = int(request.query_params.get("retries", 2))
        else:  # POST
            body = await request.json()
            targets = body.get("targets")
            options = body.get("options", "basic")
            ports = body.get("ports", "80,443,8080,8443")
            paths = body.get("paths", "")
            method = body.get("method", "GET")
            timeout = body.get("timeout", 10)
            threads = body.get("threads", 50)
            rate_limit = body.get("rate_limit", 150)
            retries = body.get("retries", 2)
        
        if not targets:
            return JSONResponse(
                {"error": "targets parameter is required"}, 
                status_code=400
            )
        
        # Validate parameters
        if timeout < 5:
            timeout = 5
        if timeout > 120:
            timeout = 120
        if threads < 1:
            threads = 1
        if threads > 100:
            threads = 100
        if rate_limit < 1:
            rate_limit = 1
        if rate_limit > 1000:
            rate_limit = 1000
        if retries < 0:
            retries = 0
        if retries > 5:
            retries = 5
        
        # Check if httpx is installed
        # Prefer PATH resolution, but also support a few common absolute locations.
        httpx_path = shutil.which("httpx")
        if not httpx_path:
            for candidate in [
                "/usr/local/bin/httpx",
                "/usr/bin/httpx",
                "/root/go/bin/httpx",
                "/home/jp/go/bin/httpx",
            ]:
                if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                    httpx_path = candidate
                    break
        
        if not httpx_path:
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            response = {
                "service": "httpx",
                "process_time_ms": process_time_ms,
                "target": targets,
                "arguments": {
                    "options": options,
                    "ports": ports,
                    "method": method,
                    "timeout": timeout,
                    "threads": threads
                },
                "return_code": -1,
                "raw_output": "",
                "raw_error": "httpx is not installed. Install it and ensure it's on PATH (e.g., ProjectDiscovery httpx binary).",
                "structured_output": {}
            }
            
            return JSONResponse(response, status_code=500)
        
        # Map friendly option names to actual httpx parameters
        option_mapping = {
            "basic": "-status-code -content-length -title",
            "detailed": "-status-code -content-length -title -tech-detect -web-server -response-time",
            "headers": "-status-code -content-length -title -include-response-header",
            "hashes": "-status-code -content-length -title -hash md5,sha256,simhash",
            "comprehensive": "-status-code -content-length -title -tech-detect -web-server -response-time -hash md5,sha256,simhash -jarm -location -include-response-header"
        }
        
        # Get the actual options string
        if options in option_mapping:
            options_str = option_mapping[options]
        else:
            options_str = options  # Use as-is if not in mapping
        
        # Note: httpx will output JSON to stdout when -json flag is used
        
        try:
            # Build command
            cmd = [httpx_path]
            
            # Handle multiple targets
            if ',' in targets:
                # Create temporary file for target list
                with tempfile.NamedTemporaryFile(delete=False, mode='w') as targets_file:
                    targets_file.write('\n'.join(targets.split(',')))
                    targets_file_path = targets_file.name
                cmd.extend(["-list", targets_file_path])
            else:
                cmd.extend(["-target", targets])
            
            # Add scan options
            if options_str:
                cmd.extend(options_str.split())
            
            # Add other parameters
            if ports:
                cmd.extend(["-ports", ports])
            
            if paths:
                cmd.extend(["-path", paths])
            
            cmd.extend(["-method", method])
            cmd.extend(["-timeout", str(timeout)])
            cmd.extend(["-threads", str(threads)])
            cmd.extend(["-rate-limit", str(rate_limit)])
            cmd.extend(["-retries", str(retries)])
            
            # Add output format - JSON to stdout
            cmd.extend(["-j", "-silent", "-no-color"])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 minute max timeout
            )
            
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            raw_output = result.stdout if result.stdout else ""
            raw_error = result.stderr if result.stderr else ""
            
            # Parse JSON output from stdout
            structured_output = {}
            if raw_output.strip():
                structured_output = parse_httpx_output(raw_output)
            
            # Format response according to schema.json
            response = {
                "service": "httpx",
                "process_time_ms": process_time_ms,
                "target": targets,
                "arguments": {
                    "options": options,
                    "ports": ports,
                    "paths": paths,
                    "method": method,
                    "timeout": timeout,
                    "threads": threads,
                    "rate_limit": rate_limit,
                    "retries": retries
                },
                "return_code": result.returncode,
                "raw_output": raw_output,
                "raw_error": raw_error,
                "structured_output": structured_output
            }
            
            return JSONResponse(response)
            
        finally:
            # Clean up temporary target file if it was created
            if 'targets_file_path' in locals() and os.path.exists(targets_file_path):
                os.remove(targets_file_path)
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "httpx",
            "process_time_ms": process_time_ms,
            "target": targets if 'targets' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "ports": ports if 'ports' in locals() else "",
                "method": method if 'method' in locals() else "GET",
                "timeout": timeout if 'timeout' in locals() else 10,
                "threads": threads if 'threads' in locals() else 50
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": "Command timed out after 5 minutes",
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=408)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "httpx",
            "process_time_ms": process_time_ms,
            "target": targets if 'targets' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "ports": ports if 'ports' in locals() else "",
                "method": method if 'method' in locals() else "GET",
                "timeout": timeout if 'timeout' in locals() else 10,
                "threads": threads if 'threads' in locals() else 50
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": str(e),
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=500)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    #mcp.run() stdio
    mcp.run(transport="http", host="0.0.0.0", port=9004)
