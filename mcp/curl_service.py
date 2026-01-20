from typing import Optional
import subprocess
from service_response import ServiceResponse

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

async def curl_request(url: str, method: str = "GET", headers: str = "", data: str = "", 
                       follow_redirects: bool = False, verbose: bool = False, insecure: bool = False, 
                       user_agent: str = "", headers_only: bool = False) -> dict:
    
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

        
        if not url:
            return {"error": "url parameter is required"}
        
        
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

        options_used = " ".join(cmd[1:-1])  # All options except 'curl' and URL

        
        # Format response according to schema.json
        response = ServiceResponse(
            service="curl",
            process_time_ms=process_time_ms,
            target=url,
            arguments={
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
            return_code=result.returncode,
            raw_output=raw_output,
            raw_error=raw_error
        )
        
        return response
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="curl",
            process_time_ms=process_time_ms,
            target=url if 'url' in locals() else "unknown",
            arguments={
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
            return_code=-1,
            raw_output="",
            raw_error=str(e)
        )
        
        return response

