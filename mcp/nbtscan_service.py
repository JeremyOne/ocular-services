from typing import Optional
import subprocess
from service_response import ServiceResponse
from fastmcp import Context
from utility import execute_command

# nbtscan - NetBIOS name scanner version 1.7.2
# Usage: nbtscan [options] <scan_range>
# 
# Options:
#   -v              Verbose output. Print all names received from each host
#   -d              Dump packets. Print whole packet contents
#   -e              Format output in /etc/hosts format
#   -l              Format output in lmhosts format
#   -t timeout      Wait timeout milliseconds for response (default 1000)
#   -b bandwidth    Output throttling (bandwidth in bps)
#   -r              Use local port 137 for scans (requires root on Unix)
#   -q              Suppress banners and error messages
#   -s separator    Script-friendly output with field separator
#   -h              Print human-readable names for services (use with -v)
#   -m retransmits  Number of retransmits (default 0)
#   -f filename     Take IP addresses from file


def get_service_info() -> dict:
    return {
        "name": "nbtscan",
        "endpoint": "/nbtscan",
        "description": "NetBIOS name scanner for Windows network discovery",
        "methods": ["GET", "POST"],
        "parameters": {
            "target": "IP address, range, or subnet to scan (required)",
            "options": "Scan options: basic, verbose, script, hosts, lmhosts (default: basic)",
            "timeout": "Response timeout in milliseconds (100-30000, default: 1000)",
            "verbose": "Enable verbose output (boolean)",
            "retransmits": "Number of retransmits (0-10, default: 0)",
            "use_local_port": "Use local port 137 for scans (boolean, requires root)"
        }
    }


def get_netbios_name_type(suffix: str) -> str:
    """Get the NetBIOS name type description based on suffix"""
    name_types = {
        "00": "Workstation Service",
        "01": "Messenger Service",
        "03": "Messenger Service (User)",
        "06": "RAS Server Service",
        "1B": "Domain Master Browser",
        "1C": "Domain Controllers",
        "1D": "Master Browser",
        "1E": "Browser Service Elections",
        "20": "File Server Service",
        "21": "RAS Client Service",
        "22": "Microsoft Exchange Interchange",
        "23": "Microsoft Exchange Store",
        "24": "Microsoft Exchange Directory",
        "30": "Modem Sharing Server Service",
        "31": "Modem Sharing Client Service",
        "43": "SMS Clients Remote Control",
        "44": "SMS Administrators Remote Control Tool",
        "45": "SMS Clients Remote Chat",
        "46": "SMS Clients Remote Transfer",
        "4C": "DEC Pathworks TCPIP",
        "52": "DEC Pathworks TCPIP",
        "87": "Microsoft Exchange MTA",
        "6A": "Microsoft Exchange IMC",
        "BE": "Network Monitor Agent",
        "BF": "Network Monitor Application"
    }
    return name_types.get(suffix.upper(), f"Unknown Service (0x{suffix})")

async def nbtscan_scan(target: str, options: str = "basic", timeout: int = 1000, verbose: bool = False,
                       retransmits: int = 0, use_local_port: bool = False, ctx: Context = None) -> ServiceResponse:
    
    """Perform NetBIOS name scan using nbtscan.
    
    Parameters:
        target: IP address, range, or subnet to scan (required)
        options: Scan options (default: basic scan)
        timeout: Response timeout in milliseconds (default: 1000)
        verbose: Enable verbose output (boolean)
        retransmits: Number of retransmits (0-10, default: 0)
        use_local_port: Use local port 137 for scans (boolean, requires root)
        
    Available scan options:
        "basic": Standard NetBIOS name scan (default)
        "verbose": Verbose output with all names from each host
        "script": Script-friendly output format
        "hosts": Format output in /etc/hosts format
        "lmhosts": Format output in lmhosts format
        
    Target formats:
        - Single IP: 192.168.1.1
        - IP range: 192.168.1.1-254
        - CIDR subnet: 192.168.1.0/24
        
    Returns:
        JSON response matching schema.json format
    """

    # Initialize ServiceResponse
    response = ServiceResponse(
        service="nbtscan",
        target=target,
        arguments={
            "target": target,
            "options": options,
            "timeout": timeout,
            "verbose": verbose,
            "retransmits": retransmits,
            "use_local_port": use_local_port
        }
    )

    try:

        # Validate parameters
        if not target:
            response.add_error("target parameter is required")
            return response
        
        if timeout < 100:
            response.add_error("timeout must be at least 100 milliseconds")
            return response
        
        if timeout > 30000:  # 30 seconds max
            response.add_error("timeout cannot exceed 30000 milliseconds")
            return response
        
        if retransmits < 0:
            response.add_error("retransmits cannot be negative")
            return response
        
        if retransmits > 10:
            response.add_error("retransmits cannot exceed 10")
            return response
        
        # Map friendly option names to actual nbtscan parameters
        option_mapping = {
            "basic": "",
            "verbose": "-v",
            "script": "-v -s :",
            "hosts": "-e",
            "lmhosts": "-l"
        }
        
        # Get the actual options string
        if options in option_mapping:
            options_str = option_mapping[options]
        else:
            options_str = options  # Use as-is if not in mapping
        
        # Build command
        cmd_parts = ["nbtscan"]
        
        # Add options
        if options_str:
            cmd_parts.append(options_str)
        
        # Add verbose flag if specifically requested
        if verbose and "-v" not in cmd_parts:
            cmd_parts.append("-v")
        
        # Add timeout
        cmd_parts.extend(["-t", str(timeout)])
        
        # Add retransmits
        if retransmits > 0:
            cmd_parts.extend(["-m", str(retransmits)])
        
        # Add local port option (requires root)
        if use_local_port:
            cmd_parts.append("-r")
        
        # Suppress banners for cleaner output
        cmd_parts.append("-q")
        
        # Add target
        cmd_parts.append(target)
        
        cmd = " ".join(cmd_parts)
        
        # Execute command with real-time output processing
        return await execute_command(
            cmd=cmd,
            response=response,
            ctx=ctx,
            timeout=60,  # 1 minute max timeout
            expected_lines=100
        )
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()
        return response

