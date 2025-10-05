from typing import Optional
import subprocess
import re
import datetime
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# whois - WHOIS domain lookup tool
# Usage: whois [options] domain
# 
# Options:
#   -R    Show registrar information only
#   -a    Show administrative contact information  
#   -t    Show technical contact information
#   -H    Hide legal disclaimers, show full details
#   -h host  Connect to server HOST
#   -p port  Connect to PORT
#   -I    Show IANA whois server and exit
#   -v    Verbose debug output

# Create FastMCP server
mcp = FastMCP("Whois Service")

def get_service_info() -> list: [
    {
        "name": "whois",
        "endpoint": "/whois",
        "description": "WHOIS domain registration information lookup",
        "methods": ["GET", "POST"],
        "parameters": {
            "domain": "Domain name to lookup (required, e.g., example.com)",
            "options": "WHOIS options (optional, e.g., -R, -a, -t, -H)",
            "server": "Specific WHOIS server to query (optional)",
            "timeout": "Command timeout in seconds (10-120, default: 30)"
        }
    }
]

def parse_whois_output(whois_text: str, domain: str) -> dict:
    """Parse WHOIS output into structured JSON format matching schema.json"""
    result = {
        "domain": domain.upper(),
        "registrar_info": {
            "registrar": None,
            "registrar_url": None,
            "abuse_email": None,
            "abuse_phone": None
        },
        "registration_info": {
            "creation_date": None,
            "expiration_date": None,
            "updated_date": None,
            "status": []
        },
        "registrant_info": {
            "name": None,
            "organization": None,
            "email": None,
            "phone": None,
            "country": None
        },
        "admin_contact": {
            "name": None,
            "organization": None,
            "email": None,
            "phone": None
        },
        "tech_contact": {
            "name": None,
            "organization": None,
            "email": None,
            "phone": None
        },
        "name_servers": [],
        "dnssec": None,
        "summary": {
            "domain_age_days": None,
            "days_until_expiry": None,
            "is_available": False
        },
        "errors": []
    }
    
    if not whois_text.strip():
        result["errors"].append("Empty WHOIS response")
        return result
    
    lines = whois_text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('%') or line.startswith('#') or line.startswith('>>>') or line.startswith('NOTICE:'):
            continue
        
        line_lower = line.lower()
        
        # Check if domain is available
        if any(phrase in line_lower for phrase in ['no match', 'not found', 'no entries found', 'no data found']):
            result["summary"]["is_available"] = True
            continue
        
        # Extract registrar information
        if any(pattern in line_lower for pattern in ['registrar:', 'registrar organization:', 'sponsoring registrar:']):
            result["registrar_info"]["registrar"] = extract_value_after_colon(line)
        elif 'registrar url:' in line_lower:
            result["registrar_info"]["registrar_url"] = extract_value_after_colon(line)
        elif 'registrar abuse contact email:' in line_lower:
            result["registrar_info"]["abuse_email"] = extract_value_after_colon(line)
        elif 'registrar abuse contact phone:' in line_lower:
            result["registrar_info"]["abuse_phone"] = extract_value_after_colon(line)
        
        # Extract registration dates
        elif any(pattern in line_lower for pattern in ['creation date:', 'created:', 'created on:', 'domain registration date:']):
            result["registration_info"]["creation_date"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['expir', 'registry expiry date:', 'expires:', 'expiration date:']):
            if 'date' in line_lower:
                result["registration_info"]["expiration_date"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['updated date:', 'last updated:', 'modified:']):
            result["registration_info"]["updated_date"] = extract_value_after_colon(line)
        elif 'status:' in line_lower:
            status_val = extract_value_after_colon(line)
            if status_val and status_val not in result["registration_info"]["status"]:
                result["registration_info"]["status"].append(status_val)
        
        # Extract registrant information
        elif any(pattern in line_lower for pattern in ['registrant name:', 'registrant:']):
            result["registrant_info"]["name"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['registrant organization:', 'registrant org:']):
            result["registrant_info"]["organization"] = extract_value_after_colon(line)
        elif 'registrant email:' in line_lower:
            result["registrant_info"]["email"] = extract_value_after_colon(line)
        elif 'registrant phone:' in line_lower:
            result["registrant_info"]["phone"] = extract_value_after_colon(line)
        elif 'registrant country:' in line_lower:
            result["registrant_info"]["country"] = extract_value_after_colon(line)
        
        # Extract admin contact
        elif any(pattern in line_lower for pattern in ['admin name:', 'administrative contact name:']):
            result["admin_contact"]["name"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['admin organization:', 'administrative contact organization:']):
            result["admin_contact"]["organization"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['admin email:', 'administrative contact email:']):
            result["admin_contact"]["email"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['admin phone:', 'administrative contact phone:']):
            result["admin_contact"]["phone"] = extract_value_after_colon(line)
        
        # Extract tech contact
        elif any(pattern in line_lower for pattern in ['tech name:', 'technical contact name:']):
            result["tech_contact"]["name"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['tech organization:', 'technical contact organization:']):
            result["tech_contact"]["organization"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['tech email:', 'technical contact email:']):
            result["tech_contact"]["email"] = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['tech phone:', 'technical contact phone:']):
            result["tech_contact"]["phone"] = extract_value_after_colon(line)
        
        # Extract name servers
        elif any(pattern in line_lower for pattern in ['name server:', 'nserver:', 'nameserver:']):
            ns = extract_value_after_colon(line)
            if ns and ns not in result["name_servers"]:
                result["name_servers"].append(ns)
        
        # Extract DNSSEC
        elif 'dnssec:' in line_lower:
            result["dnssec"] = extract_value_after_colon(line)
    
    # Calculate summary information
    calculate_summary_info(result)
    
    return result

def extract_value_after_colon(line: str) -> str:
    """Extract the value after the first colon in a line."""
    if ':' in line:
        value = line.split(':', 1)[1].strip()
        # Remove URLs and extra info in parentheses for cleaner output
        value = re.sub(r'\s+https?://[^\s]+', '', value)
        value = re.sub(r'\s+\([^)]*\)', '', value)
        return value.strip()
    return ""

def calculate_summary_info(result: dict):
    """Calculate domain age and expiry information."""
    try:
        creation_date = result["registration_info"]["creation_date"]
        expiration_date = result["registration_info"]["expiration_date"]
        
        if creation_date:
            # Try multiple date formats
            date_formats = [
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d',
                '%d-%b-%Y',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(creation_date.split(' ')[0], fmt)
                    age = datetime.datetime.now() - parsed_date
                    result["summary"]["domain_age_days"] = age.days
                    break
                except ValueError:
                    continue
        
        if expiration_date:
            for fmt in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(expiration_date.split(' ')[0], fmt)
                    days_until = (parsed_date - datetime.datetime.now()).days
                    result["summary"]["days_until_expiry"] = days_until
                    break
                except ValueError:
                    continue
                    
    except Exception as e:
        result["errors"].append(f"Error calculating summary: {str(e)}")

@mcp.custom_route("/whois", methods=["GET", "POST"])
async def whois_lookup(request: Request) -> JSONResponse:
    """Perform WHOIS lookup on a domain to get registration information.
    
    Parameters:
        domain: Domain name to lookup (required, e.g., example.com)
        options: WHOIS options (optional, default: basic lookup)
        server: Specific WHOIS server to query (optional)
        timeout: Command timeout in seconds (default: 30)
        
    Available options:
        "": Basic WHOIS lookup (default)
        -R: Show registrar information only
        -a: Show administrative contact information
        -t: Show technical contact information
        -H: Hide legal disclaimers, show full details
        
    Returns:
        JSON response matching schema.json format
    """
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            domain = request.query_params.get("domain")
            options = request.query_params.get("options", "")
            server = request.query_params.get("server", "")
            timeout = int(request.query_params.get("timeout", 30))
        else:  # POST
            body = await request.json()
            domain = body.get("domain")
            options = body.get("options", "")
            server = body.get("server", "")
            timeout = body.get("timeout", 30)
        
        if not domain:
            return JSONResponse(
                {"error": "domain parameter is required"}, 
                status_code=400
            )
        
        # Clean domain input - remove protocol and path if present
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0].strip()
        
        # Validate timeout
        if timeout < 10:
            timeout = 10
        if timeout > 120:  # 2 minutes max
            timeout = 120
        
        # Check if whois is installed
        try:
            subprocess.run(["which", "whois"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            end_time = time.time()
            process_time_ms = int((end_time - start_time) * 1000)
            
            response = {
                "service": "whois",
                "process_time_ms": process_time_ms,
                "target": domain,
                "arguments": {
                    "options": options,
                    "server": server,
                    "timeout": timeout
                },
                "return_code": -1,
                "raw_output": "",
                "raw_error": "whois is not installed. Please install it with 'sudo apt-get install whois'",
                "structured_output": {}
            }
            
            return JSONResponse(response, status_code=500)
        
        # Build command
        cmd = ["whois"]
        
        # Add options if provided
        if options:
            option_parts = [opt.strip() for opt in options.split() if opt.strip()]
            cmd.extend(option_parts)
        
        # Add server if provided
        if server:
            cmd.extend(["-h", server])
        
        # Add domain
        cmd.append(domain)
        
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
        
        # Parse the whois output into structured format
        structured_output = parse_whois_output(raw_output, domain) if raw_output else {}
        
        # Format response according to schema.json
        response = {
            "service": "whois",
            "process_time_ms": process_time_ms,
            "target": domain,
            "arguments": {
                "options": options,
                "server": server,
                "timeout": timeout
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
            "service": "whois",
            "process_time_ms": process_time_ms,
            "target": domain if 'domain' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "server": server if 'server' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 30
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
            "service": "whois",
            "process_time_ms": process_time_ms,
            "target": domain if 'domain' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "server": server if 'server' in locals() else "",
                "timeout": timeout if 'timeout' in locals() else 30
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
    mcp.run(transport="http", host="0.0.0.0", port=9002)
