from typing import Optional
import subprocess
import os
import tempfile
from service_response import ServiceResponse
from fastmcp import Context
from utility import execute_command

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
                      force: bool = False, random_user_agent: bool = False,
                      ctx: Context = None) -> ServiceResponse:
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
        
        # Build command
        cmd_parts = ["wpscan", "--url", url]
        
        # Add scan options
        if options_str:
            cmd_parts.append(options_str)
        
        # Add API token if provided
        if api_token:
            cmd_parts.extend(["--api-token", api_token])
        
        # Add additional flags
        if force:
            cmd_parts.append("--force")
        
        if random_user_agent:
            cmd_parts.append("--random-user-agent")
        
        # Add no-banner flag
        cmd_parts.append("--no-banner")
        
        cmd = " ".join(cmd_parts)
        
        # Execute command with real-time output processing
        return await execute_command(
            cmd=cmd,
            response=response,
            ctx=ctx,
            timeout=timeout,
            expected_lines=200
        )
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()
        return response
        
        return response

if __name__ == "__main__":
    pass
