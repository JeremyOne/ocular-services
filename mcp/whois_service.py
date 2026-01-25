from typing import Optional
import subprocess
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

async def whois_lookup(domain: str, options: str = "", server: str = "", timeout: int = 30) -> ServiceResponse:
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
        
        # Check if whois is installed
        try:
            subprocess.run(["which", "whois"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            response.add_error("whois is not installed. Please install it with 'sudo apt-get install whois'")
            response.return_code = -1
            response.end_process_timer()
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
        cmd.append(cleaned_domain)
        
        response.raw_command = " ".join(cmd)
        
        # Execute command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        
        response.raw_output = result.stdout if result.stdout else ""
        response.raw_error = result.stderr if result.stderr else ""
        response.return_code = result.returncode
        response.end_process_timer()
        
        return response
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()
        return response
