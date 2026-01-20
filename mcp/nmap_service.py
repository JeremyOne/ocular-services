from typing import Optional
import subprocess
from service_response import ServiceResponse

# nmap - Network Mapper version 7.94SVN
# Network exploration tool and security / port scanner
# 
# Scan types available:
#   fast: Fast scan of top 100 ports (-F -Pn)
#   service: Scan top 20 ports with service version detection (-sV --top-ports 20)
#   stealth: Stealth SYN scan without pinging (-sS -Pn)
#   rdp: Scan for RDP vulnerabilities on port 3389 (-p 3389 --script rdp-*)
#   aggressive: Aggressive scan with OS detection (-A -T4)
#   vuln: Scan for CVE vulnerabilities (-Pn --script vuln)

def get_service_info() -> dict:
    return {
        "name": "nmap",
        "endpoint": "/nmap",
        "description": "Network Mapper for network discovery and security auditing",
        "methods": ["GET", "POST"],
        "parameters": {
            "target": "Target host, IP, or network range to scan (required)",
            "scan_type": "Type of scan: fast, service, stealth, rdp, aggressive, vuln (default: fast)",
            "timeout": "Command timeout in seconds (30-1800, default: 240)",
            "ports": "Specific ports to scan (optional, overrides scan_type port selection)",
            "scripts": "Additional nmap scripts to run (optional)"
        }
    }



async def nmap_scan(target: str, scan_type: str = "fast", timeout: int = 240, 
                    ports: str = "", scripts: str = "") -> ServiceResponse:
    """Perform network scan using nmap.
    
    Parameters:
        target: Target host, IP, or network range to scan (required)
        scan_type: Type of scan to perform (default: fast)
        timeout: Command timeout in seconds (30-1800, default: 240)
        ports: Specific ports to scan (optional, overrides scan_type port selection)
        scripts: Additional nmap scripts to run (optional)
        
    Available scan types:
        "fast": Fast scan of top 100 ports (default)
        "service": Scan top 20 ports with service version detection
        "stealth": Stealth SYN scan without pinging
        "rdp": Scan for RDP vulnerabilities on port 3389
        "aggressive": Aggressive scan with OS detection
        "vuln": Scan for CVE vulnerabilities (slow)
        
    Target formats:
        - Single IP: 192.168.1.1
        - Hostname: example.com
        - IP range: 192.168.1.1-254
        - CIDR subnet: 192.168.1.0/24
        - Multiple targets: "192.168.1.1 192.168.1.2"
        
    Returns:
        JSON response with scan results and structured output
    """

    # Initialize ServiceResponse
    response = ServiceResponse(
        service="nmap",
        target=target,
        arguments={
            "target": target,
            "scan_type": scan_type,
            "timeout": timeout,
            "ports": ports,
            "scripts": scripts
        }
    )
    
    try:
        
        # Validate parameters
        if not target:
            response.add_error("target parameter is required")
            return response
        
        # Validate timeout
        if timeout < 30:
            response.add_error("timeout must be at least 30 seconds")
            return response
        if timeout > 1800:  # 30 minutes max
            response.add_error("timeout cannot exceed 1800 seconds")
            return response
        
        # Check if nmap is installed
        try:
            subprocess.run(["which", "nmap"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            response.add_error("nmap is not installed. Please install it with 'sudo apt-get install nmap'")
            response.return_code = -1
            response.end_process_timer()
            return response
        
        # Map scan types to nmap options
        scan_options = {
            "fast": ["-F", "-Pn"],
            "service": ["-sV", "--top-ports", "20"],
            "stealth": ["-sS", "-Pn"],
            "rdp": ["-p", "3389", "--script", "rdp-*"],
            "aggressive": ["-A", "-T4"],
            "vuln": ["-Pn", "--script", "vuln"]
        }
        
        # Build command
        cmd = ["nmap"]
        
        # Add scan type options
        if scan_type in scan_options:
            cmd.extend(scan_options[scan_type])
        else:
            # Use custom scan_type as nmap options
            cmd.extend(scan_type.split())
        
        # Add custom ports if specified
        if ports:
            # Remove any existing port specifications and add custom ones
            cmd = [arg for arg in cmd if not arg.startswith("-p") and not arg.startswith("--top-ports")]
            cmd.extend(["-p", ports])
        
        # Add custom scripts if specified
        if scripts:
            cmd.extend(["--script", scripts])
        
        # Add target(s)
        cmd.extend(target.split())
        
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

if __name__ == "__main__":
    pass
