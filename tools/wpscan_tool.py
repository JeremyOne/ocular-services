#!/usr/bin/env python3

import subprocess
import shlex
from .enums import WpScanOptions
import json
import os
import tempfile
from typing import Union, Optional


def wpscan_scan(target: str, options: Optional[Union[WpScanOptions, str]] = WpScanOptions.BASIC_SCAN) -> str:
    """
    Run WPScan on a WordPress target.
    
    Args:
        target: Target WordPress URL (should include http:// or https://)
        options: WpScanOptions enum for scan options
        
    Returns:
        str: Output of the wpscan command
    """
    # Check if wpscan is installed
    try:
        subprocess.run(["which", "wpscan"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return "Error: wpscan is not installed. Please install it with 'gem install wpscan'"
    
    # Convert option enum to string if it's an enum
    if isinstance(options, WpScanOptions):
        options_str = options.value
    else:
        options_str = options
    
    # Ensure target has protocol
    if not target.startswith(('http://', 'https://')):
        target = f"http://{target}"
    
    # Create a temporary file for output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
        output_file = temp_file.name
    
    try:
        # Build the command
        cmd = f"wpscan --url {target} {options_str} --format json --output {output_file} --no-banner"
        print(f"Running wpscan with options: '{options_str}' on target: '{target}'")
        
        # Run wpscan
        process = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        
        # Check if the output file exists and has content
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r") as f:
                json_output = f.read()
            
            # Parse and format the output more nicely
            formatted_output = parse_wpscan_output(json_output)
            
            # Clean up the temporary file
            os.remove(output_file)
            
            return f"wpscan output:\n{formatted_output}\n \n------\n"
        else:
            # If no JSON output, return the text output
            stderr = process.stderr if process.stderr else "No error output"
            stdout = process.stdout if process.stdout else "No standard output"
            return f"wpscan output:\nStdout: {stdout}\nStderr: {stderr}\n \n------\n"
            
    except subprocess.TimeoutExpired:
        return f"Error: wpscan timed out after 5 minutes. Try with a more focused scan option."
    except subprocess.CalledProcessError as e:
        return f"Error running wpscan: {e.stderr}\n \n------\n"
    except Exception as e:
        return f"Error: {str(e)}\n \n------\n"
    finally:
        # Make sure to clean up
        if os.path.exists(output_file):
            os.remove(output_file)


def parse_wpscan_output(json_output):
    """Parse the wpscan JSON output and format it nicely."""
    try:
        data = json.loads(json_output)
        
        output = "WordPress Security Scan Results:\n"
        output += "===================================\n\n"
        
        # Target information
        if "target_url" in data:
            output += f"Target URL: {data['target_url']}\n"
        
        if "effective_url" in data:
            output += f"Effective URL: {data['effective_url']}\n"
        
        # WordPress version
        if "version" in data:
            version_info = data["version"]
            if "number" in version_info:
                output += f"WordPress Version: {version_info['number']}\n"
                if "status" in version_info:
                    output += f"Version Status: {version_info['status']}\n"
        
        output += "\n"
        
        # Interesting findings
        if "interesting_findings" in data:
            findings = data["interesting_findings"]
            if findings:
                output += "Interesting Findings:\n"
                output += "--------------------\n"
                for finding in findings:
                    if "to_s" in finding:
                        output += f"• {finding['to_s']}\n"
                    elif "url" in finding:
                        output += f"• {finding['url']}\n"
                        if "found_by" in finding:
                            output += f"  Found by: {finding['found_by']}\n"
                output += "\n"
        
        # Plugins
        if "plugins" in data:
            plugins = data["plugins"]
            if plugins:
                output += f"Plugins Found ({len(plugins)}):\n"
                output += "------------------------\n"
                for plugin_name, plugin_info in plugins.items():
                    output += f"• {plugin_name}\n"
                    if "version" in plugin_info and plugin_info["version"]:
                        if "number" in plugin_info["version"]:
                            output += f"  Version: {plugin_info['version']['number']}\n"
                    if "vulnerabilities" in plugin_info:
                        vulns = plugin_info["vulnerabilities"]
                        if vulns:
                            output += f"  Vulnerabilities: {len(vulns)} found\n"
                            for vuln in vulns[:3]:  # Show first 3
                                if "title" in vuln:
                                    output += f"    - {vuln['title']}\n"
                output += "\n"
        
        # Themes
        if "themes" in data:
            themes = data["themes"]
            if themes:
                output += f"Themes Found ({len(themes)}):\n"
                output += "----------------------\n"
                for theme_name, theme_info in themes.items():
                    output += f"• {theme_name}\n"
                    if "version" in theme_info and theme_info["version"]:
                        if "number" in theme_info["version"]:
                            output += f"  Version: {theme_info['version']['number']}\n"
                    if "vulnerabilities" in theme_info:
                        vulns = theme_info["vulnerabilities"]
                        if vulns:
                            output += f"  Vulnerabilities: {len(vulns)} found\n"
                output += "\n"
        
        # Users
        if "users" in data:
            users = data["users"]
            if users:
                output += f"Users Found ({len(users)}):\n"
                output += "--------------------\n"
                for user_id, user_info in users.items():
                    if "username" in user_info:
                        output += f"• ID {user_id}: {user_info['username']}\n"
                        if "found_by" in user_info:
                            output += f"  Found by: {user_info['found_by']}\n"
                output += "\n"
        
        # Main theme
        if "main_theme" in data:
            main_theme = data["main_theme"]
            if main_theme:
                output += "Main Theme:\n"
                output += "-----------\n"
                if "slug" in main_theme:
                    output += f"Name: {main_theme['slug']}\n"
                if "version" in main_theme and main_theme["version"]:
                    if "number" in main_theme["version"]:
                        output += f"Version: {main_theme['version']['number']}\n"
                if "vulnerabilities" in main_theme:
                    vulns = main_theme["vulnerabilities"]
                    if vulns:
                        output += f"Vulnerabilities: {len(vulns)} found\n"
                output += "\n"
        
        # Config backups
        if "config_backups" in data:
            backups = data["config_backups"]
            if backups:
                output += f"Config Backups Found ({len(backups)}):\n"
                output += "------------------------------\n"
                for backup in backups:
                    if "url" in backup:
                        output += f"• {backup['url']}\n"
                output += "\n"
        
        # DB exports
        if "db_exports" in data:
            exports = data["db_exports"]
            if exports:
                output += f"Database Exports Found ({len(exports)}):\n"
                output += "--------------------------------\n"
                for export in exports:
                    if "url" in export:
                        output += f"• {export['url']}\n"
                output += "\n"
        
        # Scan stats
        if "scan_aborted" in data and data["scan_aborted"]:
            output += "⚠️  Scan was aborted!\n\n"
        
        if "requests_done" in data:
            output += f"Requests made: {data['requests_done']}\n"
        
        if "elapsed" in data:
            output += f"Scan duration: {data['elapsed']} seconds\n"
        
        return output
        
    except json.JSONDecodeError as e:
        return f"Error parsing wpscan JSON output: {str(e)}\nRaw output: {json_output[:500]}..."
    except Exception as e:
        return f"Error processing wpscan output: {str(e)}\nRaw output: {json_output[:500]}..."


def get_wp_api_token():
    """Get WordPress API token from environment or return None."""
    return os.getenv("WPSCAN_API_TOKEN")
