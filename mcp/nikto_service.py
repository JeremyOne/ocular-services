from typing import Optional
import subprocess
from service_response import ServiceResponse

# nikto - Web Server Scanner version 2.1.5
# Web vulnerability scanner that performs comprehensive tests
# 
# Scan types available:
#   basic: Standard host scan (-h)
#   ssl: Force SSL scan (-ssl)
#   cgi: Check all CGI directories (-C all)
#   files: Look for interesting files (-Tuning 1)
#   misconfig: Look for misconfigurations (-Tuning 2) 
#   disclosure: Look for information disclosure (-Tuning 3)
#   comprehensive: All tuning options combined
#   fast: Quick scan with reduced checks

def get_service_info() -> dict:
    """Get service information for the unified server"""
    return {
        "name": "nikto",
        "endpoint": "/nikto",
        "description": "Web vulnerability scanner for comprehensive security testing",
        "methods": ["GET", "POST"],
        "parameters": {
            "target": "Target URL or hostname to scan (required)",
            "scan_type": "Type of scan: basic, ssl, cgi, files, misconfig, disclosure, comprehensive, fast (default: basic)",
            "port": "Port to scan (default: 80 for HTTP, 443 for HTTPS)",
            "ssl": "Force SSL mode (boolean, default: auto-detect)",
            "timeout": "Request timeout in seconds (5-300, default: 10)",
            "tuning": "Nikto tuning options (1-9, comma-separated)",
            "plugins": "Specific plugins to run (optional)",
            "vhost": "Virtual host header (optional)"
        }
    }

async def nikto_scan(target: str, scan_type: str = "basic", port: str = "", ssl: bool = False, 
                     timeout: int = 10, tuning: str = "", plugins: str = "", vhost: str = "") -> ServiceResponse:
    """Perform web vulnerability scan using nikto.
    
    Parameters:
        target: Target URL or hostname to scan (required)
        scan_type: Type of scan to perform (default: basic)
        port: Port to scan (default: 80 for HTTP, 443 for HTTPS)
        ssl: Force SSL mode (boolean, default: auto-detect)
        timeout: Request timeout in seconds (5-300, default: 10)
        tuning: Nikto tuning options (1-9, comma-separated)
        plugins: Specific plugins to run (optional)
        vhost: Virtual host header (optional)
        
    Available scan types:
        "basic": Standard host scan (default)
        "ssl": Force SSL scan
        "cgi": Check all CGI directories
        "files": Look for interesting files (tuning 1)
        "misconfig": Look for misconfigurations (tuning 2)
        "disclosure": Look for information disclosure (tuning 3)
        "comprehensive": All tuning options (1,2,3,4,5,6,7,8,9)
        "fast": Quick scan with reduced timeouts
        
    Returns:
        JSON response with scan results and structured output
    """

    # Auto-detect SSL if not specified
    if not ssl and target and (target.startswith("https://") or (port and int(port) == 443)):
        ssl = True
    
    # Initialize ServiceResponse
    response = ServiceResponse(
        service="nikto",
        target=target,
        arguments={
            "target": target,
            "scan_type": scan_type,
            "port": port,
            "ssl": ssl,
            "timeout": timeout,
            "tuning": tuning,
            "plugins": plugins,
            "vhost": vhost
        }
    )
    
    try:
        
        # Validate parameters
        if not target:
            response.add_error("target parameter is required")
            return response
        
        # Validate timeout
        if timeout < 5:
            response.add_error("timeout must be at least 5 seconds")
            return response
        if timeout > 300:  # 5 minutes max
            response.add_error("timeout cannot exceed 300 seconds")
            return response
        
        # Check if nikto is installed
        try:
            subprocess.run(["which", "nikto"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            response.add_error("nikto is not installed. Please install it with 'sudo apt-get install nikto'")
            response.return_code = -1
            response.end_process_timer()
            return response
        
        # Map scan types to nikto options
        scan_options = {
            "basic": [],
            "ssl": ["-ssl"],
            "cgi": ["-C", "all"],
            "files": ["-Tuning", "1"],
            "misconfig": ["-Tuning", "2"],
            "disclosure": ["-Tuning", "3"],
            "comprehensive": ["-Tuning", "1,2,3,4,5,6,7,8,9"],
            "fast": ["-timeout", "5"]
        }
        
        # Build command
        cmd = ["nikto", "-h", target]
        
        # Add scan type options
        if scan_type in scan_options:
            cmd.extend(scan_options[scan_type])
        
        # Add SSL option
        if ssl:
            cmd.extend(["-ssl"])
        
        # Add port
        if port:
            cmd.extend(["-port", str(port)])
        
        # Add timeout
        cmd.extend(["-timeout", str(timeout)])
        
        # Add custom tuning
        if tuning:
            cmd.extend(["-Tuning", tuning])
        
        # Add specific plugins
        if plugins:
            cmd.extend(["-Plugins", plugins])
        
        # Add virtual host
        if vhost:
            cmd.extend(["-vhost", vhost])
        
        # Add output format for better parsing
        cmd.extend(["-Format", "txt"])
        
        response.raw_command = " ".join(cmd)
        
        # Execute command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout + 60  # Add buffer time for nikto overhead
        )
        
        raw_output = result.stdout if result.stdout else ""
        raw_error = result.stderr if result.stderr else ""
        
        # Combine stdout and stderr for nikto (it uses both)
        combined_output = raw_output + "\n" + raw_error
        
        response.raw_output = combined_output
        response.raw_error = ""  # Combined into raw_output for nikto
        response.return_code = result.returncode
        response.end_process_timer()
        
        return response
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()
        return response


