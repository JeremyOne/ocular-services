from typing import Optional
import subprocess
import json
import os
import tempfile
import shutil
from service_response import ServiceResponse

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

async def httpx_scan(targets: str, options: str = "basic", ports: str = "80,443,8080,8443", paths: str = "", 
                     method: str = "GET", timeout: int = 10, threads: int = 50, rate_limit: int = 150, retries: int = 2) -> dict:


    import time
    start_time = time.time()
    
    try:
        if not targets:
            return {"error": "targets parameter is required"}
        
        # Validate parameters
        if timeout < 5:
            return {"error": "timeout must be at least 5 seconds"}
        if timeout > 120:
            return {"error": "timeout cannot exceed 120 seconds"}
        if threads < 1:
            return {"error": "threads must be at least 1"}
        if threads > 100:
            return {"error": "threads cannot exceed 100"}
        if rate_limit < 1:
            return {"error": "rate_limit must be at least 1"}
        if rate_limit > 1000:
            return {"error": "rate_limit cannot exceed 1000"}
        if retries < 0:
            return {"error": "retries cannot be negative"}
        if retries > 5:
            return {"error": "retries cannot exceed 5"}
        
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
            
            response = ServiceResponse(
                service="httpx",
                process_time_ms=process_time_ms,
                target=targets,
                arguments={
                    "options": options,
                    "ports": ports,
                    "method": method,
                    "timeout": timeout,
                    "threads": threads
                },
                return_code=-1,
                raw_output="",
                raw_error="httpx is not installed. Install it and ensure it's on PATH (e.g., ProjectDiscovery httpx binary)."
            )
            
            return response
        
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
            
            # Format response according to schema.json
            response = ServiceResponse(
                service="httpx",
                process_time_ms=process_time_ms,
                target=targets,
                arguments={
                    "options": options,
                    "ports": ports,
                    "paths": paths,
                    "method": method,
                    "timeout": timeout,
                    "threads": threads,
                    "rate_limit": rate_limit,
                    "retries": retries
                },
                return_code=result.returncode,
                raw_output=raw_output,
                raw_error=raw_error
            )
            
            return response
            
        finally:
            # Clean up temporary target file if it was created
            if 'targets_file_path' in locals() and os.path.exists(targets_file_path):
                os.remove(targets_file_path)
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="httpx",
            process_time_ms=process_time_ms,
            target=targets if 'targets' in locals() else "unknown",
            arguments={
                "options": options if 'options' in locals() else "",
                "ports": ports if 'ports' in locals() else "",
                "method": method if 'method' in locals() else "GET",
                "timeout": timeout if 'timeout' in locals() else 10,
                "threads": threads if 'threads' in locals() else 50
            },
            return_code=-1,
            raw_output="",
            raw_error="Command timed out after 5 minutes"
        )
        
        return response
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="httpx",
            process_time_ms=process_time_ms,
            target=targets if 'targets' in locals() else "unknown",
            arguments={
                "options": options if 'options' in locals() else "",
                "ports": ports if 'ports' in locals() else "",
                "method": method if 'method' in locals() else "GET",
                "timeout": timeout if 'timeout' in locals() else 10,
                "threads": threads if 'threads' in locals() else 50
            },
            return_code=-1,
            raw_output="",
            raw_error=str(e)
        )
        
        return response