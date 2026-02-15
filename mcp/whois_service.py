from typing import Optional
import subprocess
from service_response import ServiceResponse
from fastmcp import Context
from utility import execute_command

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

async def whois_lookup(domain: str, options: str = "", server: str = "", timeout: int = 30,
                       ctx: Context = None) -> ServiceResponse:
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

    # Clean domain input - remove protocol and path if present
    cleaned_domain = domain.replace("https://", "").replace("http://", "").split("/")[0].strip() if domain else ""
    
    # Initialize ServiceResponse
    response = ServiceResponse(
        service="whois",
        target=cleaned_domain,
        arguments={
            "domain": cleaned_domain,
            "options": options,
            "server": server,
            "timeout": timeout
        }
    )
    
    try:
        
        # Validate parameters
        if not domain:
            response.add_error("domain parameter is required")
            return response
        
        # Validate timeout
        if timeout < 1:
            response.add_error("timeout must be at least 1 second")
            return response
        if timeout > 120:  # 2 minutes max
            response.add_error("timeout cannot exceed 120 seconds")
            return response
        
        # Build command
        cmd_parts = ["whois"]
        
        # Add options if provided
        if options:
            cmd_parts.append(options)
        
        # Add server if provided
        if server:
            cmd_parts.extend(["-h", server])
        
        # Add domain
        cmd_parts.append(cleaned_domain)
        
        cmd = " ".join(cmd_parts)
        
        # Execute command with real-time output processing
        return await execute_command(
            cmd=cmd,
            response=response,
            ctx=ctx,
            timeout=timeout,
            expected_lines=100
        )
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()
        return response
