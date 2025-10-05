# This tool requires root, not tested or verified, not recommended for production use.

import subprocess
import shlex
from enum import Enum
import re
import os
from .enums import MasscanOptions
from .util import log_text

def masscan_scan(target: str, options=MasscanOptions.TOP_100_PORTS):
    """
    Run a masscan scan on the target.
    
    Args:
        target: Target IP address or hostname
        options: MasscanOptions enum for scan options
        
    Returns:
        str: Output of the masscan command
    """
    # Check if masscan is installed
    try:
        subprocess.run(["which", "masscan"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return "Error: masscan is not installed. Please install it with 'sudo apt-get install masscan'"
    
    # Convert option enum to string if it's an enum
    if isinstance(options, MasscanOptions):
        options_str = options.value
    else:
        options_str = options
    
    # Create a temporary file for masscan output
    output_file = f"/tmp/masscan_{os.getpid()}.json"
    
    try:
        # Build the command
        cmd = f"sudo masscan {target} {options_str} -oJ {output_file}"
        log_text(f"Running masscan with options: '{options_str}' on target: '{target}'")
        
        # Run masscan with sudo
        process = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        
        # Read the JSON output file
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                json_output = f.read()
            
            # Parse and format the output more nicely
            formatted_output = parse_masscan_output(json_output)
            
            # Clean up the temporary file
            os.remove(output_file)
            
            return f"masscan output:\n{formatted_output}\n \n------\n"
        else:
            return f"masscan output: {process.stdout}\nError: {process.stderr}\n \n------\n"
            
    except subprocess.TimeoutExpired:
        return f"Error: masscan timed out after 5 minutes. Try with a smaller port range."
    except subprocess.CalledProcessError as e:
        return f"Error running masscan: {e.stderr}\n \n------\n"
    except Exception as e:
        return f"Error: {str(e)}\n \n------\n"
    finally:
        # Make sure to clean up
        if os.path.exists(output_file):
            os.remove(output_file)


def parse_masscan_output(json_output):
    """Parse the masscan JSON output and format it nicely."""
    # Simple pattern to extract port information
    port_pattern = r'"ports": \[\s*{\s*"port": (\d+),\s*"proto": "([^"]+)",\s*"status": "([^"]+)"'
    
    # Find all matches
    ports = re.findall(port_pattern, json_output)
    
    if not ports:
        return "No open ports found"
    
    # Format the output
    result = "Open ports:\n"
    result += "PORT      STATE   SERVICE\n"
    for port, proto, state in ports:
        service = get_common_service(int(port), proto)
        result += f"{port}/{proto}    {state}    {service}\n"
    
    return result


def get_common_service(port, proto):
    """Return the common service name for a given port and protocol."""
    common_services = {
        21: "ftp",
        22: "ssh",
        23: "telnet",
        25: "smtp",
        53: "domain",
        80: "http",
        110: "pop3",
        111: "rpcbind",
        135: "msrpc",
        139: "netbios-ssn",
        143: "imap",
        443: "https",
        445: "microsoft-ds",
        993: "imaps",
        995: "pop3s",
        1723: "pptp",
        3306: "mysql",
        3389: "ms-wbt-server",
        5900: "vnc",
        8080: "http-proxy"
    }
    
    return common_services.get(port, "unknown")

