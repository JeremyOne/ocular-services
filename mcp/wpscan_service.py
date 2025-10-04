from typing import Optional
import subprocess
import json
import os
import tempfile
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

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

# Create FastMCP server
mcp = FastMCP("WPScan Service")

def parse_wpscan_output(json_output: str, target_url: str) -> dict:
    """Parse wpscan JSON output into structured JSON format matching schema.json"""
    result = {
        "target_info": {
            "target_url": target_url,
            "effective_url": None,
            "cms_detected": False,
            "cms_version": None,
            "cms_version_status": None
        },
        "interesting_findings": [],
        "plugins": {},
        "themes": {},
        "main_theme": {},
        "users": {},
        "vulnerabilities": {
            "total_count": 0,
            "plugin_vulnerabilities": 0,
            "theme_vulnerabilities": 0,
            "core_vulnerabilities": 0
        },
        "config_backups": [],
        "db_exports": [],
        "scan_stats": {
            "requests_done": 0,
            "elapsed_seconds": 0,
            "scan_aborted": False
        },
        "errors": []
    }
    
    if not json_output.strip():
        result["errors"].append("Empty WPScan output")
        return result
    
    try:
        data = json.loads(json_output)
        
        # Extract target information
        if "target_url" in data:
            result["target_info"]["target_url"] = data["target_url"]
        if "effective_url" in data:
            result["target_info"]["effective_url"] = data["effective_url"]
        
        # WordPress version detection
        if "version" in data:
            version_info = data["version"]
            result["target_info"]["cms_detected"] = True
            if "number" in version_info:
                result["target_info"]["cms_version"] = version_info["number"]
            if "status" in version_info:
                result["target_info"]["cms_version_status"] = version_info["status"]
        
        # Interesting findings
        if "interesting_findings" in data:
            findings = data["interesting_findings"]
            for finding in findings:
                finding_obj = {
                    "title": finding.get("to_s", ""),
                    "url": finding.get("url", ""),
                    "found_by": finding.get("found_by", ""),
                    "confidence": finding.get("confidence", 0),
                    "interesting_entries": finding.get("interesting_entries", [])
                }
                result["interesting_findings"].append(finding_obj)
        
        # Plugins analysis
        if "plugins" in data:
            plugins = data["plugins"]
            for plugin_name, plugin_info in plugins.items():
                plugin_obj = {
                    "name": plugin_name,
                    "version": None,
                    "version_confidence": 0,
                    "location": plugin_info.get("location", ""),
                    "last_updated": plugin_info.get("last_updated", ""),
                    "outdated": plugin_info.get("outdated", False),
                    "vulnerabilities": [],
                    "found_by": plugin_info.get("found_by", "")
                }
                
                # Version information
                if "version" in plugin_info and plugin_info["version"]:
                    version_data = plugin_info["version"]
                    if "number" in version_data:
                        plugin_obj["version"] = version_data["number"]
                    if "confidence" in version_data:
                        plugin_obj["version_confidence"] = version_data["confidence"]
                
                # Vulnerabilities
                if "vulnerabilities" in plugin_info:
                    vulns = plugin_info["vulnerabilities"]
                    for vuln in vulns:
                        vuln_obj = {
                            "title": vuln.get("title", ""),
                            "type": vuln.get("type", ""),
                            "fixed_in": vuln.get("fixed_in", ""),
                            "references": vuln.get("references", [])
                        }
                        plugin_obj["vulnerabilities"].append(vuln_obj)
                        result["vulnerabilities"]["plugin_vulnerabilities"] += 1
                
                result["plugins"][plugin_name] = plugin_obj
        
        # Themes analysis
        if "themes" in data:
            themes = data["themes"]
            for theme_name, theme_info in themes.items():
                theme_obj = {
                    "name": theme_name,
                    "version": None,
                    "version_confidence": 0,
                    "location": theme_info.get("location", ""),
                    "last_updated": theme_info.get("last_updated", ""),
                    "outdated": theme_info.get("outdated", False),
                    "vulnerabilities": [],
                    "found_by": theme_info.get("found_by", "")
                }
                
                # Version information
                if "version" in theme_info and theme_info["version"]:
                    version_data = theme_info["version"]
                    if "number" in version_data:
                        theme_obj["version"] = version_data["number"]
                    if "confidence" in version_data:
                        theme_obj["version_confidence"] = version_data["confidence"]
                
                # Vulnerabilities
                if "vulnerabilities" in theme_info:
                    vulns = theme_info["vulnerabilities"]
                    for vuln in vulns:
                        vuln_obj = {
                            "title": vuln.get("title", ""),
                            "type": vuln.get("type", ""),
                            "fixed_in": vuln.get("fixed_in", ""),
                            "references": vuln.get("references", [])
                        }
                        theme_obj["vulnerabilities"].append(vuln_obj)
                        result["vulnerabilities"]["theme_vulnerabilities"] += 1
                
                result["themes"][theme_name] = theme_obj
        
        # Main theme
        if "main_theme" in data:
            main_theme = data["main_theme"]
            if main_theme:
                result["main_theme"] = {
                    "name": main_theme.get("slug", ""),
                    "version": None,
                    "location": main_theme.get("location", ""),
                    "vulnerabilities": []
                }
                
                if "version" in main_theme and main_theme["version"]:
                    if "number" in main_theme["version"]:
                        result["main_theme"]["version"] = main_theme["version"]["number"]
                
                if "vulnerabilities" in main_theme:
                    vulns = main_theme["vulnerabilities"]
                    for vuln in vulns:
                        vuln_obj = {
                            "title": vuln.get("title", ""),
                            "type": vuln.get("type", ""),
                            "fixed_in": vuln.get("fixed_in", ""),
                            "references": vuln.get("references", [])
                        }
                        result["main_theme"]["vulnerabilities"].append(vuln_obj)
                        result["vulnerabilities"]["theme_vulnerabilities"] += 1
        
        # Users enumeration
        if "users" in data:
            users = data["users"]
            for user_id, user_info in users.items():
                user_obj = {
                    "id": user_id,
                    "username": user_info.get("username", ""),
                    "found_by": user_info.get("found_by", ""),
                    "confidence": user_info.get("confidence", 0)
                }
                result["users"][user_id] = user_obj
        
        # Config backups
        if "config_backups" in data:
            for backup in data["config_backups"]:
                backup_obj = {
                    "url": backup.get("url", ""),
                    "found_by": backup.get("found_by", "")
                }
                result["config_backups"].append(backup_obj)
        
        # Database exports
        if "db_exports" in data:
            for export in data["db_exports"]:
                export_obj = {
                    "url": export.get("url", ""),
                    "found_by": export.get("found_by", "")
                }
                result["db_exports"].append(export_obj)
        
        # Scan statistics
        if "scan_aborted" in data:
            result["scan_stats"]["scan_aborted"] = data["scan_aborted"]
        if "requests_done" in data:
            result["scan_stats"]["requests_done"] = data["requests_done"]
        if "elapsed" in data:
            result["scan_stats"]["elapsed_seconds"] = data["elapsed"]
        
        # Calculate total vulnerabilities
        result["vulnerabilities"]["total_count"] = (
            result["vulnerabilities"]["plugin_vulnerabilities"] +
            result["vulnerabilities"]["theme_vulnerabilities"] +
            result["vulnerabilities"]["core_vulnerabilities"]
        )
        
    except json.JSONDecodeError as e:
        result["errors"].append(f"JSON parsing error: {str(e)}")
    except Exception as e:
        result["errors"].append(f"Processing error: {str(e)}")
    
    return result

@mcp.custom_route("/wpscan", methods=["GET", "POST"])
async def wpscan_scan(request: Request) -> JSONResponse:
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
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            url = request.query_params.get("url")
            options = request.query_params.get("options", "basic")
            api_token = request.query_params.get("api_token", "")
            timeout = int(request.query_params.get("timeout", 300))
            force = request.query_params.get("force", "false").lower() == "true"
            random_user_agent = request.query_params.get("random_user_agent", "false").lower() == "true"
        else:  # POST
            body = await request.json()
            url = body.get("url")
            options = body.get("options", "basic")
            api_token = body.get("api_token", "")
            timeout = body.get("timeout", 300)
            force = body.get("force", False)
            random_user_agent = body.get("random_user_agent", False)
        
        if not url:
            return JSONResponse(
                {"error": "url parameter is required"}, 
                status_code=400
            )
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        
        # Validate timeout
        if timeout < 60:
            timeout = 60
        if timeout > 1800:  # 30 minutes max
            timeout = 1800
        
        # Check if wpscan is installed
        try:
            subprocess.run(["which", "wpscan"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            response = {
                "service": "wpscan",
                "process_time_ms": process_time_ms,
                "target": url,
                "arguments": {
                    "options": options,
                    "timeout": timeout,
                    "force": force,
                    "random_user_agent": random_user_agent
                },
                "return_code": -1,
                "raw_output": "",
                "raw_error": "wpscan is not installed. Please install it with 'gem install wpscan'",
                "structured_output": {}
            }
            
            return JSONResponse(response, status_code=500)
        
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
            
            # Read JSON output if file exists
            structured_output = {}
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, "r") as f:
                    json_output = f.read()
                structured_output = parse_wpscan_output(json_output, url)
            
            # Format response according to schema.json
            response = {
                "service": "wpscan",
                "process_time_ms": process_time_ms,
                "target": url,
                "arguments": {
                    "options": options,
                    "timeout": timeout,
                    "force": force,
                    "random_user_agent": random_user_agent,
                    "api_token_provided": bool(api_token)
                },
                "return_code": result.returncode,
                "raw_output": raw_output,
                "raw_error": raw_error,
                "structured_output": structured_output
            }
            
            return JSONResponse(response)
            
        finally:
            # Clean up temporary file
            if os.path.exists(output_file):
                os.remove(output_file)
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "wpscan",
            "process_time_ms": process_time_ms,
            "target": url if 'url' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 300,
                "force": force if 'force' in locals() else False,
                "random_user_agent": random_user_agent if 'random_user_agent' in locals() else False,
                "api_token_provided": bool(api_token) if 'api_token' in locals() else False
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": f"Command timed out after {timeout} seconds",
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=408)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "wpscan",
            "process_time_ms": process_time_ms,
            "target": url if 'url' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 300,
                "force": force if 'force' in locals() else False,
                "random_user_agent": random_user_agent if 'random_user_agent' in locals() else False,
                "api_token_provided": bool(api_token) if 'api_token' in locals() else False
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": str(e),
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=500)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    #mcp.run() stdio
    mcp.run(transport="http", host="0.0.0.0", port=9003)
