from typing import Optional
import subprocess
import re
import datetime
from service_response import ServiceResponse

# whois - WHOIS domain lookup tool
# Usage: whois [options] domain
# 
# Options:
#   -R    Show registrar information only
#   -a    Show administrative contact information  
#   -t    Show technical contact information
#   -H    Hide legal disclaimers, show full details
#   -h host  Connect to server HOST
#   -p port  Connect to PORT
#   -I    Show IANA whois server and exit
#   -v    Verbose debug output


def get_service_info() -> dict:
    return {
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
    }

async def whois_lookup(domain: str, options: str = "", server: str = "", timeout: int = 30) -> dict:
    """Perform WHOIS lookup on a domain to get registration information.
    
    Parameters:
        domain: Domain name to lookup (required, e.g., example.com)
        options: WHOIS options (optional, default: basic lookup)
        server: Specific WHOIS server to query (optional)
        timeout: Command timeout in seconds (default: 30)
        
    Available options:
        "": Basic WHOIS lookup (default)
        -R: Show registrar information only
        -a: Show administrative contact information
        -t: Show technical contact information
        -H: Hide legal disclaimers, show full details
        
    Returns:
        JSON response matching schema.json format
    """
    import time
    start_time = time.time()
    
    try:
        if not domain:
            return {"error": "domain parameter is required"}
        
        # Clean domain input - remove protocol and path if present
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0].strip()
        
        # Validate timeout
        if timeout < 1:
            return {"error": "timeout must be at least 1 second"}
        if timeout > 120:  # 2 minutes max
            return {"error": "timeout cannot exceed 120 seconds"}
        
        # Check if whois is installed
        try:
            subprocess.run(["which", "whois"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            response = ServiceResponse(
                service="whois",
                process_time_ms=process_time_ms,
                target=domain,
                arguments={
                    "options": options,
                    "server": server,
                    "timeout": timeout
                },
                return_code=-1,
                raw_output="",
                raw_error="whois is not installed. Please install it with 'sudo apt-get install whois'"
            )
            
            return response
        
        # Build command
        cmd = ["whois"]
        
        # Add options if provided
        if options:
            option_parts = [opt.strip() for opt in options.split() if opt.strip()]
            cmd.extend(option_parts)
        
        # Add server if provided
        if server:
            cmd.extend(["-h", server])
        
        # Add domain
        cmd.append(domain)
        
        # Execute command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        raw_output = result.stdout if result.stdout else ""
        raw_error = result.stderr if result.stderr else ""
        
        # Format response according to schema.json
        response = ServiceResponse(
            service="whois",
            process_time_ms=process_time_ms,
            target=domain,
            arguments={
                "options": options,
                "server": server,
                "timeout": timeout
            },
            return_code=result.returncode,
            raw_output=raw_output,
            raw_error=raw_error
        )
        
        return response
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="whois",
            process_time_ms=process_time_ms,
            target=domain if 'domain' in locals() else "unknown",
            arguments={
                "options": options if 'options' in locals() else "",
                "server": server if 'server' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 30
            },
            return_code=-1,
            raw_output="",
            raw_error=f"Command timed out after {timeout} seconds"
        )
        
        return response
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="whois",
            process_time_ms=process_time_ms,
            target=domain if 'domain' in locals() else "unknown",
            arguments={
                "options": options if 'options' in locals() else "",
                "server": server if 'server' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 30
            },
            return_code=-1,
            raw_output="",
            raw_error=str(e)
        )
        
        return response
