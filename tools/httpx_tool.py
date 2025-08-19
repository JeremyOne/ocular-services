#!/usr/bin/env python3
# filepath: /home/jp/Documents/ocular_agents/tools/httpx_tool.py

import subprocess
import shlex
from enum import Enum
import json
import os
import tempfile
import re
from typing import Union, Optional

from .enums import HttpxOptions

def httpx_scan(target: str, options: Optional[HttpxOptions] = HttpxOptions.BASIC_PROBE):

    """
    Run httpx on a target to analyze HTTP/HTTPS services.
    
    Args:
        target: Target URL, domain, IP or CIDR range
        options: HttpxOptions enum for scan options
        
    Returns:
        str: Output of the httpx command
    """
    # Check if httpx is installed
    try:
        subprocess.run(["which", "httpx"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return "Error: httpx is not installed. Please install it with 'go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest'"
    
    # Convert option enum to string if it's an enum
    if isinstance(options, HttpxOptions):
        options_str = options.value
    else:
        options_str = options
    
    # Create a temporary file for output
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        output_file = temp_file.name
    
    try:
        # Build the command
        # If target contains commas, it might be multiple targets
        if ',' in target:
            # Write targets to temporary file
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as targets_file:
                targets_file.write("\n".join(target.split(',')))
                target_input = f"-list {targets_file.name}"
        else:
            target_input = f"-u {target}"
        
        cmd = f"httpx {target_input} {options_str} -json -o {output_file}"
        print(f"Running httpx with options: '{options_str}' on target: '{target}'")
        
        # Run httpx
        process = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=180  # 3-minute timeout
        )
        
        # Check if the output file exists and has content
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r") as f:
                json_output = f.read()
            
            # Parse and format the output more nicely
            formatted_output = parse_httpx_output(json_output)
            
            # Clean up the temporary file
            os.remove(output_file)
            
            return f"httpx output:\n{formatted_output}\n \n------\n"
        else:
            stderr = process.stderr if process.stderr else "No error output"
            stdout = process.stdout if process.stdout else "No standard output"
            return f"httpx output: No valid JSON output found.\nStdout: {stdout}\nStderr: {stderr}\n \n------\n"
            
    except subprocess.TimeoutExpired:
        return f"Error: httpx timed out after 3 minutes. Try with fewer targets or simpler options."
    except subprocess.CalledProcessError as e:
        return f"Error running httpx: {e.stderr}\n \n------\n"
    except Exception as e:
        return f"Error: {str(e)}\n \n------\n"
    finally:
        # Make sure to clean up
        if os.path.exists(output_file):
            os.remove(output_file)


def parse_httpx_output(json_output):
    """Parse the httpx JSON output and format it nicely."""
    try:
        # Split the input into lines and parse each JSON object
        lines = json_output.strip().split("\n")
        results = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                results.append(data)
            except json.JSONDecodeError:
                pass
        
        if not results:
            return "No valid results found in the output."
        
        # Format the results
        output = "HTTP Probe Results:\n"
        output += "===================\n\n"
        
        for result in results:
            url = result.get("url", "Unknown URL")
            status_code = result.get("status_code", "N/A")
            title = result.get("title", "No title")
            content_type = result.get("content_type", "Unknown")
            content_length = result.get("content_length", "N/A")
            technologies = ", ".join(result.get("technologies", []))
            webserver = result.get("webserver", "Unknown")
            
            output += f"URL: {url}\n"
            output += f"Status Code: {status_code}\n"
            output += f"Title: {title}\n"
            
            if content_type != "Unknown":
                output += f"Content Type: {content_type}\n"
            
            if content_length != "N/A":
                output += f"Content Length: {content_length}\n"
                
            if webserver != "Unknown":
                output += f"Web Server: {webserver}\n"
                
            if technologies:
                output += f"Technologies: {technologies}\n"
            
            # Add headers if present
            if "headers" in result:
                output += "Headers:\n"
                for header, value in result["headers"].items():
                    if isinstance(value, list):
                        value = ", ".join(value)
                    output += f"  {header}: {value}\n"
            
            # Add a line separator between results
            output += "\n" + "-" * 50 + "\n\n"
        
        return output
        
    except Exception as e:
        return f"Error parsing httpx output: {str(e)}\nRaw output: {json_output[:500]}..."