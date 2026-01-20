from typing import Optional
import subprocess
import re
import json
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


    """Parse nmap output into structured JSON format"""
    result = {
        "target": target,
        "scan_type": scan_type,
        "scan_stats": {
            "hosts_up": 0,
            "hosts_down": 0,
            "hosts_total": 0,
            "ports_scanned": 0,
            "scan_time": "0.00s"
        },
        "hosts": [],
        "vulnerabilities": [],
        "errors": []
    }
    
    if not output.strip():
        result["errors"].append("Empty nmap output")
        return result
    
    lines = output.split('\n')
    current_host = None
    in_port_section = False
    in_script_section = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Parse Nmap scan report header
        if line.startswith("Nmap scan report for"):
            # Extract host information
            host_match = re.search(r'Nmap scan report for (.+)', line)
            if host_match:
                host_info = host_match.group(1)
                
                # Parse hostname and IP
                if '(' in host_info and ')' in host_info:
                    # Format: hostname (ip)
                    hostname = host_info.split('(')[0].strip()
                    ip = host_info.split('(')[1].replace(')', '').strip()
                else:
                    # Format: just IP or just hostname
                    hostname = host_info if not re.match(r'^\d+\.\d+\.\d+\.\d+$', host_info) else None
                    ip = host_info if re.match(r'^\d+\.\d+\.\d+\.\d+$', host_info) else None
                
                current_host = {
                    "ip": ip,
                    "hostname": hostname,
                    "status": "unknown",
                    "ports": [],
                    "os_info": {},
                    "services": [],
                    "scripts": [],
                    "vulnerabilities": []
                }
                result["hosts"].append(current_host)
                result["scan_stats"]["hosts_total"] += 1
        
        # Parse host status
        elif line.startswith("Host is"):
            if current_host:
                if "up" in line:
                    current_host["status"] = "up"
                    result["scan_stats"]["hosts_up"] += 1
                elif "down" in line:
                    current_host["status"] = "down"
                    result["scan_stats"]["hosts_down"] += 1
        
        # Parse port section header
        elif "PORT" in line and "STATE" in line and "SERVICE" in line:
            in_port_section = True
            in_script_section = False
        
        # Parse port information
        elif in_port_section and current_host and re.match(r'^\d+/', line):
            # Parse port line: 22/tcp open ssh OpenSSH 8.9p1
            port_parts = line.split()
            if len(port_parts) >= 3:
                port_protocol = port_parts[0]  # e.g., "22/tcp"
                state = port_parts[1]          # e.g., "open"
                service = port_parts[2] if len(port_parts) > 2 else "unknown"
                version = " ".join(port_parts[3:]) if len(port_parts) > 3 else ""
                
                port_info = {
                    "port": port_protocol,
                    "state": state,
                    "service": service,
                    "version": version
                }
                current_host["ports"].append(port_info)
                
                # Add to services list if open
                if state == "open":
                    current_host["services"].append({
                        "port": port_protocol,
                        "service": service,
                        "version": version
                    })
        
        # Parse OS detection
        elif "OS details:" in line or "Running:" in line or "OS CPE:" in line:
            if current_host:
                if "OS details:" in line:
                    current_host["os_info"]["details"] = line.replace("OS details:", "").strip()
                elif "Running:" in line:
                    current_host["os_info"]["running"] = line.replace("Running:", "").strip()
                elif "OS CPE:" in line:
                    current_host["os_info"]["cpe"] = line.replace("OS CPE:", "").strip()
        
        # Parse script results (vulnerabilities, etc.)
        elif "|" in line and current_host:
            script_line = line.replace("|", "").strip()
            if script_line:
                current_host["scripts"].append(script_line)
                
                # Check for vulnerability indicators
                if any(vuln_word in script_line.lower() for vuln_word in ['cve-', 'vulnerability', 'vulnerable', 'exploit']):
                    vuln_info = {
                        "type": "script_detection",
                        "description": script_line,
                        "severity": "unknown"
                    }
                    current_host["vulnerabilities"].append(vuln_info)
                    result["vulnerabilities"].append(vuln_info)
        
        # Parse scan statistics
        elif "Nmap done:" in line:
            # Extract scan time and other stats
            time_match = re.search(r'(\d+\.\d+) seconds', line)
            if time_match:
                result["scan_stats"]["scan_time"] = f"{time_match.group(1)}s"
            
            # Extract hosts scanned
            hosts_match = re.search(r'(\d+) IP address(?:es)? \((\d+) host(?:s)? up\)', line)
            if hosts_match:
                result["scan_stats"]["hosts_total"] = int(hosts_match.group(1))
                result["scan_stats"]["hosts_up"] = int(hosts_match.group(2))
                result["scan_stats"]["hosts_down"] = result["scan_stats"]["hosts_total"] - result["scan_stats"]["hosts_up"]
        
        # Parse port count information
        elif "ports scanned" in line.lower():
            ports_match = re.search(r'(\d+) ports scanned', line)
            if ports_match:
                result["scan_stats"]["ports_scanned"] = int(ports_match.group(1))
        
        # Check for errors
        elif any(error_keyword in line.lower() for error_keyword in ['error', 'failed', 'warning', 'cannot', 'unable']):
            result["errors"].append(line)
    
    return result

async def nmap_scan(request: Request):
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
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            target = request.query_params.get("target")
            scan_type = request.query_params.get("scan_type", "fast")
            timeout = int(request.query_params.get("timeout", 240))
            ports = request.query_params.get("ports")
            scripts = request.query_params.get("scripts")
        else:  # POST
            body = await request.json()
            target = body.get("target")
            scan_type = body.get("scan_type", "fast")
            timeout = body.get("timeout", 240)
            ports = body.get("ports")
            scripts = body.get("scripts")
        
        if not target:
            return ServiceResponse(
                service="nmap",
                process_time_ms=0,
                target="",
                arguments={},
                return_code=-1,
                raw_output="",
                raw_error="target parameter is required"
            )
        
        # Validate parameters
        if timeout < 30:
            timeout = 30
        if timeout > 1800:  # 30 minutes max
            timeout = 1800
        
        # Check if nmap is installed
        try:
            subprocess.run(["which", "nmap"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            response = ServiceResponse(
                service="nmap",
                process_time_ms=process_time_ms,
                target=target,
                arguments={
                    "scan_type": scan_type,
                    "timeout": timeout,
                    "ports": ports,
                    "scripts": scripts
                },
                return_code=-1,
                raw_output="",
                raw_error="nmap is not installed. Please install it with 'sudo apt-get install nmap'"
            )
            
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
            service="nmap",
            process_time_ms=process_time_ms,
            target=target,
            arguments={
                "scan_type": scan_type,
                "timeout": timeout,
                "ports": ports,
                "scripts": scripts
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
            service="nmap",
            process_time_ms=process_time_ms,
            target=target if 'target' in locals() else "unknown",
            arguments={
                "scan_type": scan_type if 'scan_type' in locals() else "fast",
                "timeout": timeout if 'timeout' in locals() else 240,
                "ports": ports if 'ports' in locals() else None,
                "scripts": scripts if 'scripts' in locals() else None
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
            service="nmap",
            process_time_ms=process_time_ms,
            target=target if 'target' in locals() else "unknown",
            arguments={
                "scan_type": scan_type if 'scan_type' in locals() else "fast",
                "timeout": timeout if 'timeout' in locals() else 240,
                "ports": ports if 'ports' in locals() else None,
                "scripts": scripts if 'scripts' in locals() else None
            },
            return_code=-1,
            raw_output="",
            raw_error=str(e)
        )
        
        return response

if __name__ == "__main__":
    pass
