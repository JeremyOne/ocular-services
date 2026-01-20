from typing import Optional
import subprocess
import re
import json
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


    """Parse nikto output into structured JSON format"""
    result = {
        "target": target,
        "scan_type": scan_type,
        "scan_info": {
            "nikto_version": "",
            "target_ip": "",
            "target_hostname": "",
            "target_port": 80,
            "ssl_enabled": False,
            "start_time": "",
            "scan_duration": ""
        },
        "server_info": {
            "server_banner": "",
            "powered_by": "",
            "allowed_methods": [],
            "server_version": ""
        },
        "findings": {
            "total_items_checked": 0,
            "vulnerabilities": [],
            "information_disclosures": [],
            "misconfigurations": [],
            "interesting_files": [],
            "cookies": [],
            "headers": []
        },
        "statistics": {
            "total_requests": 0,
            "items_found": 0,
            "severity_breakdown": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            }
        },
        "errors": []
    }
    
    if not output.strip():
        result["errors"].append("Empty nikto output")
        return result
    
    lines = output.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Parse nikto version and target information
        if "Nikto v" in line:
            version_match = re.search(r'Nikto v([\d.]+)', line)
            if version_match:
                result["scan_info"]["nikto_version"] = version_match.group(1)
        
        # Parse target information
        if line.startswith("+ Target IP:"):
            ip_match = re.search(r'Target IP:\s+(\S+)', line)
            if ip_match:
                result["scan_info"]["target_ip"] = ip_match.group(1)
        
        if line.startswith("+ Target Hostname:"):
            hostname_match = re.search(r'Target Hostname:\s+(\S+)', line)
            if hostname_match:
                result["scan_info"]["target_hostname"] = hostname_match.group(1)
        
        if line.startswith("+ Target Port:"):
            port_match = re.search(r'Target Port:\s+(\d+)', line)
            if port_match:
                result["scan_info"]["target_port"] = int(port_match.group(1))
        
        # Check for SSL
        if "SSL Info:" in line or "https://" in line:
            result["scan_info"]["ssl_enabled"] = True
        
        # Parse start time
        if line.startswith("+ Start Time:"):
            start_time = line.replace("+ Start Time:", "").strip()
            result["scan_info"]["start_time"] = start_time
        
        # Parse server banner
        if line.startswith("+ Server:"):
            server_info = line.replace("+ Server:", "").strip()
            result["server_info"]["server_banner"] = server_info
            
            # Extract server version
            server_match = re.search(r'(\S+)/([0-9.]+)', server_info)
            if server_match:
                result["server_info"]["server_version"] = f"{server_match.group(1)} {server_match.group(2)}"
        
        # Parse X-Powered-By header
        if "X-Powered-By:" in line:
            powered_by = re.search(r'X-Powered-By:\s*([^,\n]+)', line)
            if powered_by:
                result["server_info"]["powered_by"] = powered_by.group(1).strip()
        
        # Parse allowed methods
        if "Allowed HTTP Methods:" in line:
            methods_match = re.search(r'Allowed HTTP Methods:\s*([A-Z, ]+)', line)
            if methods_match:
                methods = [m.strip() for m in methods_match.group(1).split(',')]
                result["server_info"]["allowed_methods"] = methods
        
        # Parse findings (vulnerabilities, issues, etc.)
        if line.startswith("+") and "OSVDB-" in line:
            # Parse OSVDB entries
            finding = {
                "type": "vulnerability",
                "severity": "medium",
                "description": line,
                "osvdb_id": "",
                "path": "",
                "details": ""
            }
            
            # Extract OSVDB ID
            osvdb_match = re.search(r'OSVDB-(\d+)', line)
            if osvdb_match:
                finding["osvdb_id"] = osvdb_match.group(1)
            
            # Extract path
            path_match = re.search(r'(/[^:]*)', line)
            if path_match:
                finding["path"] = path_match.group(1)
            
            # Determine severity based on keywords
            line_lower = line.lower()
            if any(word in line_lower for word in ['critical', 'exploit', 'remote code', 'sql injection']):
                finding["severity"] = "critical"
            elif any(word in line_lower for word in ['high', 'dangerous', 'privilege']):
                finding["severity"] = "high"
            elif any(word in line_lower for word in ['authentication', 'bypass', 'disclosure']):
                finding["severity"] = "medium"
            elif any(word in line_lower for word in ['information', 'banner', 'version']):
                finding["severity"] = "low"
            else:
                finding["severity"] = "info"
            
            result["findings"]["vulnerabilities"].append(finding)
            result["statistics"]["severity_breakdown"][finding["severity"]] += 1
        
        elif line.startswith("+") and any(keyword in line.lower() for keyword in ['cookie', 'set-cookie']):
            # Parse cookie information
            cookie_info = {
                "description": line,
                "type": "cookie_analysis"
            }
            result["findings"]["cookies"].append(cookie_info)
        
        elif line.startswith("+") and any(keyword in line.lower() for keyword in ['header', 'x-', 'server:']):
            # Parse header information
            header_info = {
                "description": line,
                "type": "header_analysis"
            }
            result["findings"]["headers"].append(header_info)
        
        elif line.startswith("+") and any(keyword in line.lower() for keyword in ['file', 'directory', 'backup', 'config']):
            # Parse interesting files
            file_info = {
                "description": line,
                "type": "interesting_file"
            }
            result["findings"]["interesting_files"].append(file_info)
        
        elif line.startswith("+") and any(keyword in line.lower() for keyword in ['config', 'misconfigur', 'default']):
            # Parse misconfigurations
            misconfig_info = {
                "description": line,
                "type": "misconfiguration"
            }
            result["findings"]["misconfigurations"].append(misconfig_info)
        
        elif line.startswith("+") and any(keyword in line.lower() for keyword in ['disclosure', 'information', 'reveals']):
            # Parse information disclosures
            disclosure_info = {
                "description": line,
                "type": "information_disclosure"
            }
            result["findings"]["information_disclosures"].append(disclosure_info)
        
        # Parse scan statistics
        if "items checked:" in line.lower():
            items_match = re.search(r'(\d+)\s+item', line)
            if items_match:
                result["findings"]["total_items_checked"] = int(items_match.group(1))
        
        # Parse error messages
        if any(error_keyword in line.lower() for error_keyword in ['error', 'failed', 'timeout', 'unable', 'cannot']):
            result["errors"].append(line)
    
    # Calculate total findings
    result["statistics"]["items_found"] = (
        len(result["findings"]["vulnerabilities"]) +
        len(result["findings"]["information_disclosures"]) +
        len(result["findings"]["misconfigurations"]) +
        len(result["findings"]["interesting_files"])
    )
    
    return result

async def nikto_scan(request: Request):
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
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            target = request.query_params.get("target")
            scan_type = request.query_params.get("scan_type", "basic")
            port = request.query_params.get("port")
            ssl = request.query_params.get("ssl", "false").lower() == "true"
            timeout = int(request.query_params.get("timeout", 10))
            tuning = request.query_params.get("tuning")
            plugins = request.query_params.get("plugins")
            vhost = request.query_params.get("vhost")
        else:  # POST
            body = await request.json()
            target = body.get("target")
            scan_type = body.get("scan_type", "basic")
            port = body.get("port")
            ssl = body.get("ssl", False)
            timeout = body.get("timeout", 10)
            tuning = body.get("tuning")
            plugins = body.get("plugins")
            vhost = body.get("vhost")
        
        if not target:
            return ServiceResponse(
                service="nikto",
                process_time_ms=0,
                target="",
                arguments={},
                return_code=-1,
                raw_output="",
                raw_error="target parameter is required"
            )
        
        # Validate parameters
        if timeout < 5:
            timeout = 5
        if timeout > 300:  # 5 minutes max
            timeout = 300
        
        # Auto-detect SSL if not specified
        if not ssl and (target.startswith("https://") or (port and int(port) == 443)):
            ssl = True
        
        # Check if nikto is installed
        try:
            subprocess.run(["which", "nikto"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            response = ServiceResponse(
                service="nikto",
                process_time_ms=process_time_ms,
                target=target,
                arguments={
                    "scan_type": scan_type,
                    "port": port,
                    "ssl": ssl,
                    "timeout": timeout,
                    "tuning": tuning,
                    "plugins": plugins,
                    "vhost": vhost
                },
                return_code=-1,
                raw_output="",
                raw_error="nikto is not installed. Please install it with 'sudo apt-get install nikto'"
            )
            
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
        
        # Execute command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout + 60  # Add buffer time for nikto overhead
        )
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        raw_output = result.stdout if result.stdout else ""
        raw_error = result.stderr if result.stderr else ""
        
        # Combine stdout and stderr for nikto (it uses both)
        combined_output = raw_output + "\n" + raw_error
        
        # Format response according to schema.json
        response = ServiceResponse(
            service="nikto",
            process_time_ms=process_time_ms,
            target=target,
            arguments={
                "scan_type": scan_type,
                "port": port,
                "ssl": ssl,
                "timeout": timeout,
                "tuning": tuning,
                "plugins": plugins,
                "vhost": vhost
            },
            return_code=result.returncode,
            raw_output=combined_output,
            raw_error=""  # Combined into raw_output for nikto
        )
        
        return response
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="nikto",
            process_time_ms=process_time_ms,
            target=target if 'target' in locals() else "unknown",
            arguments={
                "scan_type": scan_type if 'scan_type' in locals() else "basic",
                "port": port if 'port' in locals() else None,
                "ssl": ssl if 'ssl' in locals() else False,
                "timeout": timeout if 'timeout' in locals() else 10,
                "tuning": tuning if 'tuning' in locals() else None,
                "plugins": plugins if 'plugins' in locals() else None,
                "vhost": vhost if 'vhost' in locals() else None
            },
            return_code=-1,
            raw_output="",
            raw_error=f"Command timed out after {timeout + 60} seconds"
        )
        
        return response
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="nikto",
            process_time_ms=process_time_ms,
            target=target if 'target' in locals() else "unknown",
            arguments={
                "scan_type": scan_type if 'scan_type' in locals() else "basic",
                "port": port if 'port' in locals() else None,
                "ssl": ssl if 'ssl' in locals() else False,
                "timeout": timeout if 'timeout' in locals() else 10,
                "tuning": tuning if 'tuning' in locals() else None,
                "plugins": plugins if 'plugins' in locals() else None,
                "vhost": vhost if 'vhost' in locals() else None
            },
            return_code=-1,
            raw_output="",
            raw_error=str(e)
        )
        
        return response


