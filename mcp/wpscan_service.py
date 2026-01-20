from typing import Optional
import subprocess
import os
import tempfile
from service_response import ServiceResponse

# wpscan - WordPress Security Scanner
# Usage: wpscan --url URL [options]
# 
# Key Options:
#   --enumerate p,t,u    Enumerate plugins, themes, users
#   --plugins-detection  Detection mode: mixed, passive, aggressive
#   --themes-detection   Theme detection mode
#   --api-token         WordPress vulnerability database API token
#   --force             Forces WPScan to not check if target is running WordPress
#   --wp-content-dir    WP content directory if custom
#   --wp-plugins-dir    WP plugins directory if custom
#   --random-user-agent Use random user agent
#   --detection-mode    Mixed, passive, aggressive
#   --threads           Number of threads to use
#   --throttle          Milliseconds to wait between requests

def get_service_info() -> dict:
    return {
        "name": "wpscan",
        "endpoint": "/wpscan",
        "description": "WordPress security scanner using WPScan",
        "methods": ["GET", "POST"],
        "parameters": {
            "url": "Target WordPress URL (required, include http:// or https://)",
            "options": "Scan type: basic, plugins, themes, users, vulns, full, passive (default: basic)",
            "api_token": "WordPress vulnerability database API token (optional)",
            "timeout": "Command timeout in seconds (60-1800, default: 300)",
            "force": "Force scan even if WordPress not detected (boolean)",
            "random_user_agent": "Use random user agent (boolean)"
        }
    }

async def wpscan_scan(url: str, options: str = "basic", api_token: str = "", timeout: int = 300, 
                      force: bool = False, random_user_agent: bool = False) -> ServiceResponse:
    """Perform WordPress security scan using WPScan.
    
    Parameters:
        url: Target WordPress URL (required, include http:// or https://)
        options: Scan options (default: basic scan)
        api_token: WordPress vulnerability database API token (optional)
        timeout: Command timeout in seconds (default: 300)
        force: Force scan even if WordPress not detected (boolean)
        random_user_agent: Use random user agent (boolean)
        
    Available scan options:
        "basic": Basic scan for plugins, themes, users (default)
        "plugins": Aggressive plugin enumeration  
        "themes": Aggressive theme enumeration
        "users": User enumeration only
        "vulns": Scan for vulnerable plugins and themes
        "full": Full comprehensive scan (slow but thorough)
        "passive": Passive scan (less detectable)
        
    Returns:
        JSON response matching schema.json format
    """

    # Ensure URL has protocol
    if url and not url.startswith(('http://', 'https://')):
        url = f"http://{url}"
    
    # Initialize ServiceResponse
    response = ServiceResponse(
        service="wpscan",
        target=url,
        arguments={
            "url": url,
            "options": options,
            "timeout": timeout,
            "force": force,
            "random_user_agent": random_user_agent,
            "api_token_provided": bool(api_token)
        }
    )
    
    try:
        
        # Validate parameters
        if not url:
            response.add_error("url parameter is required")
            return response
        
        # Validate timeout
        if timeout < 60:
            timeout = 60
        if timeout > 1800:  # 30 minutes max
            timeout = 1800
        
        # Check if wpscan is installed
        try:
            subprocess.run(["which", "wpscan"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            response.add_error("wpscan is not installed. Please install it with 'gem install wpscan'")
            response.return_code = -1
            response.end_process_timer()
            return response
        
        # Map friendly option names to actual wpscan parameters
        option_mapping = {
            "basic": "--enumerate p,t,u --plugins-detection mixed",
            "plugins": "--enumerate p --plugins-detection aggressive",
            "themes": "--enumerate t --themes-detection aggressive", 
            "users": "--enumerate u",
            "vulns": "--enumerate vp,vt --plugins-detection aggressive",
            "full": "--enumerate ap,at,tt,cb,dbe,u,m --plugins-detection aggressive",
            "passive": "--enumerate p,t,u --plugins-detection passive"
        }
        
        # Get the actual options string
        if options in option_mapping:
            options_str = option_mapping[options]
        else:
            options_str = options  # Use as-is if not in mapping
        
        # Create temporary file for JSON output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            output_file = temp_file.name
        
        try:
            # Build command
            cmd = ["wpscan", "--url", url]
            
            # Add scan options
            if options_str:
                cmd.extend(options_str.split())
            
            # Add API token if provided
            if api_token:
                cmd.extend(["--api-token", api_token])
            
            # Add additional flags
            if force:
                cmd.append("--force")
            
            if random_user_agent:
                cmd.append("--random-user-agent")
            
            # Add output format and file
            cmd.extend(["--format", "json", "--output", output_file, "--no-banner"])
            
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
            
        finally:
            # Clean up temporary file
            if os.path.exists(output_file):
                os.remove(output_file)
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()
        return response
        
        return response

if __name__ == "__main__":
    pass
