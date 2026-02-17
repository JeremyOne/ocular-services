from typing import Optional
import subprocess
from service_response import ServiceResponse
from fastmcp import Context
from utility import execute_command

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


async def curl_request(url: str, method: str = "GET", headers: str = "", data: str = "", 
                       follow_redirects: bool = False, verbose: bool = False, insecure: bool = False, 
                       user_agent: str = "", headers_only: bool = False, timeout: int = 30,
                       ctx: Context = None) -> ServiceResponse:
    
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

    # Initialize ServiceResponse
    response = ServiceResponse(
        service="curl",
        target=url,
        arguments={
            "url": url,
            "method": method,
            "headers": headers,
            "data": data,
            "follow_redirects": follow_redirects,
            "verbose": verbose,
            "insecure": insecure,
            "user_agent": user_agent,
            "headers_only": headers_only,
            "timeout": timeout
        }
    )
        
    try:
        
        # Validate parameters
        if not url:
            response.add_error("url parameter is required")
            return response
        
        # Build command
        cmd_parts = ["curl"]
        
        # Add options based on parameters
        if headers_only:
            cmd_parts.append("-I")  # Headers only
        if follow_redirects:
            cmd_parts.append("-L")  # Follow redirects
        if verbose:
            cmd_parts.append("-v")  # Verbose output
        if insecure:
            cmd_parts.append("-k")  # Allow insecure connections
        
        # Set HTTP method
        if method != "GET":
            cmd_parts.extend(["-X", method])
        
        # Add custom headers
        if headers:
            for header in headers.split(';'):
                if header.strip():
                    cmd_parts.extend(["-H", header.strip()])
        
        # Add User-Agent if specified
        if user_agent:
            cmd_parts.extend(["-H", f"User-Agent: {user_agent}"])
        
        # Add POST data
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            cmd_parts.extend(["-d", data])
        
        # Add URL
        cmd_parts.append(url)
        
        cmd = " ".join(cmd_parts)
        
        # Execute command with real-time output processing
        return await execute_command(
            cmd=cmd,
            response=response,
            ctx=ctx,
            timeout=timeout,
            expected_lines=50
        )
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()       
        return response