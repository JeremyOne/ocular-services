from typing import Optional
import subprocess
import re
import json
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# Usage
#   curl [options] <URL>
# 
# Common Options:
#   -I, --head              Show document info only
#   -L, --location          Follow redirects
#   -v, --verbose           Make the operation more talkative
#   --http2                 Use HTTP/2
#   --trace-ascii           Detailed trace output to file
#   -H, --header            Pass custom header to server
#   -X, --request           Specify request command to use
#   -d, --data              HTTP POST data
#   -u, --user              Server user and password
#   -k, --insecure          Allow insecure server connections
#   -s, --silent            Silent mode
#   -o, --output            Write to file instead of stdout
#   -w, --write-out         Use output format after completion

# Create FastMCP server
mcp = FastMCP("Curl Service")

def get_service_info() -> dict:
    return {
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

def get_option_descriptions() -> list: [
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

def parse_curl_output(output: str, stderr: str, options_used: str) -> dict:
    """Parse curl output into structured JSON format"""
    result = {
        "response_headers": {},
        "response_body": "",
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "server": None,
        "location": None,
        "timing": {},
        "ssl_info": {},
        "verbose_info": []
    }
    
    lines = output.strip().split('\n')
    stderr_lines = stderr.strip().split('\n') if stderr else []
    
    # Parse HTTP status from verbose output or response
    status_pattern = r'HTTP/[\d.]+\s+(\d+)'
    for line in lines + stderr_lines:
        match = re.search(status_pattern, line)
        if match:
            result["http_status"] = int(match.group(1))
            break
    
    # Parse headers (from -I option or verbose output)
    header_section = False
    body_section = False
    
    for line in lines:
        line = line.strip()
        
        # Detect header section
        if line.startswith('HTTP/'):
            header_section = True
            body_section = False
            continue
        elif line == '' and header_section:
            header_section = False
            body_section = True
            continue
        
        # Parse headers
        if header_section and ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            result["response_headers"][key] = value
            
            # Extract common headers
            if key == 'content-type':
                result["content_type"] = value
            elif key == 'content-length':
                result["content_length"] = int(value) if value.isdigit() else value
            elif key == 'server':
                result["server"] = value
            elif key == 'location':
                result["location"] = value
        
        # Collect body (if not headers-only request)
        elif body_section:
            result["response_body"] += line + '\n'
    
    # Parse verbose information from stderr
    for line in stderr_lines:
        line = line.strip()
        if line.startswith('*') or line.startswith('>') or line.startswith('<'):
            result["verbose_info"].append(line)
        
        # Parse SSL/TLS information
        if 'SSL' in line or 'TLS' in line:
            if 'SSL connection using' in line:
                ssl_match = re.search(r'SSL connection using (.+)', line)
                if ssl_match:
                    result["ssl_info"]["cipher"] = ssl_match.group(1)
            elif 'Server certificate:' in line:
                result["ssl_info"]["has_certificate"] = True
    
    # Clean up response body
    result["response_body"] = result["response_body"].strip()
    
    return result

@mcp.custom_route("/curl", methods=["GET", "POST"])
async def curl_request(request: Request) -> JSONResponse:
    """Make HTTP requests using curl for penetration testing and discovery.
        url: The target URL to request
        method: HTTP method (GET, POST, etc.)
        headers: Additional headers to send
        data: POST data to send
        follow_redirects: Whether to follow redirects
        verbose: Enable verbose output
        insecure: Allow insecure SSL connections
        user_agent: Custom User-Agent header
    Returns:
        JSON response matching schema.json format
    """
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            url = request.query_params.get("url")
            method = request.query_params.get("method", "GET")
            headers = request.query_params.get("headers", "")
            data = request.query_params.get("data", "")
            follow_redirects = request.query_params.get("follow_redirects", "false").lower() == "true"
            verbose = request.query_params.get("verbose", "false").lower() == "true"
            insecure = request.query_params.get("insecure", "false").lower() == "true"
            user_agent = request.query_params.get("user_agent", "")
            headers_only = request.query_params.get("headers_only", "false").lower() == "true"
        else:  # POST
            body = await request.json()
            url = body.get("url")
            method = body.get("method", "GET")
            headers = body.get("headers", "")
            data = body.get("data", "")
            follow_redirects = body.get("follow_redirects", False)
            verbose = body.get("verbose", False)
            insecure = body.get("insecure", False)
            user_agent = body.get("user_agent", "")
            headers_only = body.get("headers_only", False)
        
        if not url:
            return JSONResponse(
                {"error": "url parameter is required"}, 
                status_code=400
            )
        
        # Build curl command
        cmd = ["curl"]
        
        # Add options based on parameters
        if headers_only:
            cmd.append("-I")  # Headers only
        if follow_redirects:
            cmd.append("-L")  # Follow redirects
        if verbose:
            cmd.append("-v")  # Verbose output
        if insecure:
            cmd.append("-k")  # Allow insecure connections
        
        # Set HTTP method
        if method != "GET":
            cmd.extend(["-X", method])
        
        # Add custom headers
        if headers:
            for header in headers.split(';'):
                if header.strip():
                    cmd.extend(["-H", header.strip()])
        
        # Add User-Agent if specified
        if user_agent:
            cmd.extend(["-H", f"User-Agent: {user_agent}"])
        
        # Add POST data
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            cmd.extend(["-d", data])
        
        # Add URL
        cmd.append(url)
        
        # Execute curl command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        raw_output = result.stdout if result.stdout else ""
        raw_error = result.stderr if result.stderr else ""
        
        # Parse the curl output into structured format
        options_used = " ".join(cmd[1:-1])  # All options except 'curl' and URL
        structured_output = parse_curl_output(raw_output, raw_error, options_used)
        
        # Format response according to schema.json
        response = {
            "service": "curl",
            "process_time_ms": process_time_ms,
            "target": url,
            "arguments": {
                "method": method,
                "headers": headers,
                "data": data,
                "follow_redirects": follow_redirects,
                "verbose": verbose,
                "insecure": insecure,
                "user_agent": user_agent,
                "headers_only": headers_only,
                "options_used": options_used
            },
            "return_code": result.returncode,
            "raw_output": raw_output,
            "raw_error": raw_error,
            "structured_output": structured_output
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "curl",
            "process_time_ms": process_time_ms,
            "target": url if 'url' in locals() else "unknown",
            "arguments": {
                "method": method if 'method' in locals() else "GET",
                "headers": headers if 'headers' in locals() else "",
                "data": data if 'data' in locals() else "",
                "follow_redirects": follow_redirects if 'follow_redirects' in locals() else False,
                "verbose": verbose if 'verbose' in locals() else False,
                "insecure": insecure if 'insecure' in locals() else False,
                "user_agent": user_agent if 'user_agent' in locals() else "",
                "headers_only": headers_only if 'headers_only' in locals() else False,
                "options_used": ""
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
    # mcp.run() # stdio
    mcp.run(transport="http", host="0.0.0.0", port=9001)
