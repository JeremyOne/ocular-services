from typing import Optional
import subprocess
import re
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

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

# Create FastMCP server
mcp = FastMCP("NBTScan Service")

def parse_nbtscan_output(output: str, target: str) -> dict:
    """Parse nbtscan output into structured JSON format matching schema.json"""
    result = {
        "target_range": target,
        "discovered_hosts": [],
        "statistics": {
            "total_hosts_scanned": 0,
            "responsive_hosts": 0,
            "total_netbios_names": 0,
            "unique_domains": [],
            "unique_workgroups": []
        },
        "netbios_names": {
            "computers": [],
            "domains": [],
            "services": [],
            "users": []
        },
        "errors": []
    }
    
    if not output.strip():
        result["errors"].append("Empty nbtscan output")
        return result
    
    lines = output.split('\n')
    domains = set()
    workgroups = set()
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines, headers, and error messages
        if not line or line.startswith("Doing NBT name scan") or "IP address" in line:
            continue
        
        # Parse standard nbtscan output format
        # Format: IP_ADDRESS    NETBIOS_NAME<XX>   SERVICE_TYPE
        # Example: 192.168.1.1   COMPUTER<00>      UNIQUE
        standard_match = re.match(r'(\d+\.\d+\.\d+\.\d+)\s+([^\s<]+)<([0-9A-Fa-f]{2})>\s+(.+)', line)
        if standard_match:
            ip = standard_match.group(1)
            name = standard_match.group(2)
            suffix = standard_match.group(3)
            service_type = standard_match.group(4).strip()
            
            # Check if this is a new host
            existing_host = None
            for host in result["discovered_hosts"]:
                if host["ip_address"] == ip:
                    existing_host = host
                    break
            
            if not existing_host:
                existing_host = {
                    "ip_address": ip,
                    "netbios_names": [],
                    "computer_name": None,
                    "domain": None,
                    "workgroup": None,
                    "services": []
                }
                result["discovered_hosts"].append(existing_host)
                result["statistics"]["responsive_hosts"] += 1
            
            # Add NetBIOS name entry
            name_entry = {
                "name": name,
                "suffix": suffix,
                "service_type": service_type,
                "name_type": get_netbios_name_type(suffix)
            }
            existing_host["netbios_names"].append(name_entry)
            result["statistics"]["total_netbios_names"] += 1
            
            # Categorize the name based on suffix
            if suffix == "00":
                if service_type.upper() == "UNIQUE":
                    existing_host["computer_name"] = name
                    result["netbios_names"]["computers"].append({
                        "ip": ip,
                        "name": name,
                        "suffix": suffix
                    })
                elif service_type.upper() == "GROUP":
                    existing_host["workgroup"] = name
                    workgroups.add(name)
            elif suffix == "1C":
                existing_host["domain"] = name
                domains.add(name)
                result["netbios_names"]["domains"].append({
                    "ip": ip,
                    "name": name,
                    "suffix": suffix
                })
            elif suffix == "20":
                result["netbios_names"]["services"].append({
                    "ip": ip,
                    "name": name,
                    "suffix": suffix,
                    "service": "File Server Service"
                })
            elif suffix == "03":
                result["netbios_names"]["users"].append({
                    "ip": ip,
                    "name": name,
                    "suffix": suffix,
                    "service": "Messenger Service"
                })
            
            # Add to services list
            existing_host["services"].append({
                "name": name,
                "suffix": suffix,
                "type": name_entry["name_type"],
                "service_type": service_type
            })
        
        # Parse verbose output (script-friendly format with separator)
        # Format: IP:NAME<XX>:SERVICE_TYPE
        elif ':' in line:
            parts = line.split(':')
            if len(parts) >= 3:
                ip = parts[0].strip()
                name_part = parts[1].strip()
                service_type = parts[2].strip()
                
                # Extract name and suffix
                name_match = re.match(r'([^<]+)<([0-9A-Fa-f]{2})>', name_part)
                if name_match:
                    name = name_match.group(1)
                    suffix = name_match.group(2)
                    
                    # Similar processing as above
                    existing_host = None
                    for host in result["discovered_hosts"]:
                        if host["ip_address"] == ip:
                            existing_host = host
                            break
                    
                    if not existing_host:
                        existing_host = {
                            "ip_address": ip,
                            "netbios_names": [],
                            "computer_name": None,
                            "domain": None,
                            "workgroup": None,
                            "services": []
                        }
                        result["discovered_hosts"].append(existing_host)
                        result["statistics"]["responsive_hosts"] += 1
                    
                    name_entry = {
                        "name": name,
                        "suffix": suffix,
                        "service_type": service_type,
                        "name_type": get_netbios_name_type(suffix)
                    }
                    existing_host["netbios_names"].append(name_entry)
                    result["statistics"]["total_netbios_names"] += 1
        
        # Check for errors
        if any(error_keyword in line.lower() for error_keyword in ['error', 'failed', 'timeout', 'unable']):
            result["errors"].append(line)
    
    # Calculate scan range statistics
    if target:
        if '/' in target:
            # CIDR notation
            try:
                import ipaddress
                network = ipaddress.IPv4Network(target, strict=False)
                result["statistics"]["total_hosts_scanned"] = network.num_addresses
            except:
                result["statistics"]["total_hosts_scanned"] = len(result["discovered_hosts"])
        elif '-' in target:
            # Range notation
            try:
                base_ip, end_range = target.split('-')
                start_octet = int(base_ip.split('.')[-1])
                end_octet = int(end_range)
                result["statistics"]["total_hosts_scanned"] = end_octet - start_octet + 1
            except:
                result["statistics"]["total_hosts_scanned"] = len(result["discovered_hosts"])
        else:
            # Single IP
            result["statistics"]["total_hosts_scanned"] = 1
    
    # Update statistics
    result["statistics"]["unique_domains"] = sorted(list(domains))
    result["statistics"]["unique_workgroups"] = sorted(list(workgroups))
    
    return result

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

async def nbtscan_scan(request: Request) -> JSONResponse:
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
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            target = request.query_params.get("target")
            options = request.query_params.get("options", "basic")
            timeout = int(request.query_params.get("timeout", 1000))
            verbose = request.query_params.get("verbose", "false").lower() == "true"
            retransmits = int(request.query_params.get("retransmits", 0))
            use_local_port = request.query_params.get("use_local_port", "false").lower() == "true"
        else:  # POST
            body = await request.json()
            target = body.get("target")
            options = body.get("options", "basic")
            timeout = body.get("timeout", 1000)
            verbose = body.get("verbose", False)
            retransmits = body.get("retransmits", 0)
            use_local_port = body.get("use_local_port", False)
        
        if not target:
            return JSONResponse(
                {"error": "target parameter is required"}, 
                status_code=400
            )
        
        # Validate parameters
        if timeout < 100:
            timeout = 100
        if timeout > 30000:  # 30 seconds max
            timeout = 30000
        if retransmits < 0:
            retransmits = 0
        if retransmits > 10:
            retransmits = 10
        
        # Check if nbtscan is installed
        try:
            subprocess.run(["which", "nbtscan"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            response = {
                "service": "nbtscan",
                "process_time_ms": process_time_ms,
                "target": target,
                "arguments": {
                    "options": options,
                    "timeout": timeout,
                    "verbose": verbose,
                    "retransmits": retransmits,
                    "use_local_port": use_local_port
                },
                "return_code": -1,
                "raw_output": "",
                "raw_error": "nbtscan is not installed. Please install it with 'sudo apt-get install nbtscan'",
                "structured_output": {}
            }
            
            return JSONResponse(response, status_code=500)
        
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
        cmd = ["nbtscan"]
        
        # Add options
        if options_str:
            cmd.extend(options_str.split())
        
        # Add verbose flag if specifically requested
        if verbose and "-v" not in cmd:
            cmd.append("-v")
        
        # Add timeout
        cmd.extend(["-t", str(timeout)])
        
        # Add retransmits
        if retransmits > 0:
            cmd.extend(["-m", str(retransmits)])
        
        # Add local port option (requires root)
        if use_local_port:
            cmd.append("-r")
        
        # Suppress banners for cleaner output
        cmd.append("-q")
        
        # Add target
        cmd.append(target)
        
        # Execute command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60  # 1 minute max timeout
        )
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        raw_output = result.stdout if result.stdout else ""
        raw_error = result.stderr if result.stderr else ""
        
        # Parse the nbtscan output into structured format
        structured_output = parse_nbtscan_output(raw_output, target) if raw_output else {}
        
        # Format response according to schema.json
        response = {
            "service": "nbtscan",
            "process_time_ms": process_time_ms,
            "target": target,
            "arguments": {
                "options": options,
                "timeout": timeout,
                "verbose": verbose,
                "retransmits": retransmits,
                "use_local_port": use_local_port
            },
            "return_code": result.returncode,
            "raw_output": raw_output,
            "raw_error": raw_error,
            "structured_output": structured_output
        }
        
        return JSONResponse(response)
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "nbtscan",
            "process_time_ms": process_time_ms,
            "target": target if 'target' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 1000,
                "verbose": verbose if 'verbose' in locals() else False,
                "retransmits": retransmits if 'retransmits' in locals() else 0,
                "use_local_port": use_local_port if 'use_local_port' in locals() else False
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": "Command timed out after 60 seconds",
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=408)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "nbtscan",
            "process_time_ms": process_time_ms,
            "target": target if 'target' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 1000,
                "verbose": verbose if 'verbose' in locals() else False,
                "retransmits": retransmits if 'retransmits' in locals() else 0,
                "use_local_port": use_local_port if 'use_local_port' in locals() else False
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": str(e),
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=500)

@mcp.custom_route("/nbtscan", methods=["GET", "POST"])
async def nbtscan_endpoint(request: Request) -> JSONResponse:
    return await nbtscan_scan(request)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    #mcp.run() stdio
    mcp.run(transport="http", host="0.0.0.0", port=9005)
