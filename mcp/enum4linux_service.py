from typing import Optional
import subprocess
import re
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# enum4linux v0.9.1 - SMB/CIFS enumeration tool
# Usage: enum4linux [options] ip
# 
# Options:
#   -U        get userlist
#   -M        get machine list
#   -S        get sharelist
#   -P        get password policy information
#   -G        get group and member list
#   -d        be detailed, applies to -U and -S
#   -u user   specify username to use (default "")
#   -p pass   specify password to use (default "")
#   -a        Do all simple enumeration (-U -S -G -P -r -o -n -i)
#   -r        enumerate users via RID cycling
#   -R range  RID ranges to enumerate (default: 500-550,1000-1050, implies -r)
#   -K n      Keep searching RIDs until n consecutive RIDs don't correspond to a username
#   -l        Get some (limited) info via LDAP 389/TCP (for DCs only)
#   -s file   brute force guessing for share names
#   -k user   User(s) that exists on remote system
#   -o        Get OS information
#   -i        Get printer information
#   -w wrkg   Specify workgroup manually
#   -n        Do an nmblookup (similar to nbtstat)
#   -v        Verbose. Shows full commands being run
#   -A        Aggressive. Do write checks on shares etc

# Create FastMCP server
mcp = FastMCP("Enum4linux Service")

def parse_enum4linux_output(output: str) -> dict:
    """Parse enum4linux output into structured JSON format matching schema.json"""
    result = {
        "target_info": {
            "hostname": None,
            "os_version": None,
            "workgroup": None,
            "domain": None
        },
        "users": [],
        "groups": [],
        "shares": [],
        "machines": [],
        "password_policy": {},
        "printer_info": [],
        "nmblookup": {},
        "errors": []
    }
    
    lines = output.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Parse target information
        if "NetBIOS computer name:" in line:
            hostname = line.split(":")[-1].strip()
            if hostname and hostname != "Could not determine":
                result["target_info"]["hostname"] = hostname
        elif "NetBIOS domain name:" in line:
            domain = line.split(":")[-1].strip()
            if domain and domain != "Could not determine":
                result["target_info"]["domain"] = domain
        elif "Workgroup/Domain:" in line:
            workgroup = line.split(":")[-1].strip()
            if workgroup and workgroup != "Could not determine":
                result["target_info"]["workgroup"] = workgroup
        elif "OS version:" in line:
            os_version = line.split(":")[-1].strip()
            if os_version and os_version != "Could not determine":
                result["target_info"]["os_version"] = os_version
        
        # Identify sections
        if line.startswith("==============") and "Getting userlist" in line:
            current_section = "users"
        elif line.startswith("==============") and "Getting group list" in line:
            current_section = "groups"
        elif line.startswith("==============") and "Getting shares" in line:
            current_section = "shares"
        elif line.startswith("==============") and "Getting machine list" in line:
            current_section = "machines"
        elif line.startswith("==============") and "Getting password policy" in line:
            current_section = "password_policy"
        elif line.startswith("==============") and "Getting printer info" in line:
            current_section = "printer_info"
        elif line.startswith("==============") and "Nbtstat Information" in line:
            current_section = "nmblookup"
        elif line.startswith("=============="):
            current_section = None
        
        # Parse users
        if current_section == "users":
            # Format: user:[RID] rid:[500]
            user_match = re.match(r'user:\[([^\]]+)\]\s+rid:\[(\d+)\]', line)
            if user_match:
                result["users"].append({
                    "username": user_match.group(1),
                    "rid": int(user_match.group(2))
                })
        
        # Parse groups
        elif current_section == "groups":
            # Format: group:[Domain Users] rid:[513]
            group_match = re.match(r'group:\[([^\]]+)\]\s+rid:\[(\d+)\]', line)
            if group_match:
                result["groups"].append({
                    "groupname": group_match.group(1),
                    "rid": int(group_match.group(2))
                })
        
        # Parse shares
        elif current_section == "shares":
            # Format: Sharename       Type      Comment
            # Format: ---------       ----      -------
            # Format: ADMIN$          Disk      Remote Admin
            if line and not line.startswith("Sharename") and not line.startswith("-"):
                parts = line.split()
                if len(parts) >= 2:
                    sharename = parts[0]
                    share_type = parts[1]
                    comment = " ".join(parts[2:]) if len(parts) > 2 else ""
                    
                    result["shares"].append({
                        "name": sharename,
                        "type": share_type,
                        "comment": comment
                    })
        
        # Parse machines
        elif current_section == "machines":
            # Similar to users but for machines
            machine_match = re.match(r'machine:\[([^\]]+)\]\s+rid:\[(\d+)\]', line)
            if machine_match:
                result["machines"].append({
                    "hostname": machine_match.group(1),
                    "rid": int(machine_match.group(2))
                })
        
        # Parse password policy
        elif current_section == "password_policy":
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    result["password_policy"][key] = value
        
        # Parse printer info
        elif current_section == "printer_info":
            if line and not line.startswith("No") and "printer" in line.lower():
                result["printer_info"].append(line)
        
        # Parse errors
        if "ERROR" in line or "Failed" in line or "Connection refused" in line:
            result["errors"].append(line)
    
    return result

@mcp.custom_route("/enum4linux", methods=["GET", "POST"])
async def enum4linux_scan(request: Request) -> JSONResponse:
    """Enumerate SMB/CIFS information from target host using enum4linux.
    
    Parameters:
        target: The hostname or IP address to enumerate
        options: Enumeration options (default: "-a" for all enumeration)
        username: Username for authentication (optional)
        password: Password for authentication (optional)
        timeout: Command timeout in seconds (default: 120)
        
    Available options:
        -U: Get userlist
        -M: Get machine list
        -S: Get sharelist
        -P: Get password policy information
        -G: Get group and member list
        -a: Do all simple enumeration (default)
        -r: Enumerate users via RID cycling
        -o: Get OS information
        -i: Get printer information
        -n: Do an nmblookup
        -v: Verbose output
        -A: Aggressive enumeration
        -d: Be detailed in output
        
    Returns:
        JSON response matching schema.json format
    """
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            target = request.query_params.get("target")
            options = request.query_params.get("options", "-a")
            username = request.query_params.get("username", "")
            password = request.query_params.get("password", "")
            timeout = int(request.query_params.get("timeout", 120))
        else:  # POST
            body = await request.json()
            target = body.get("target")
            options = body.get("options", "-a")
            username = body.get("username", "")
            password = body.get("password", "")
            timeout = body.get("timeout", 120)
        
        if not target:
            return JSONResponse(
                {"error": "target parameter is required"}, 
                status_code=400
            )
        
        # Validate timeout
        if timeout < 30:
            timeout = 30
        if timeout > 600:  # 10 minutes max
            timeout = 600
        
        # Build command
        cmd = ["enum4linux"]
        
        # Add options (split by space and filter empty strings)
        if options:
            option_parts = [opt.strip() for opt in options.split() if opt.strip()]
            cmd.extend(option_parts)
        
        # Add authentication if provided
        if username:
            cmd.extend(["-u", username])
        if password:
            cmd.extend(["-p", password])
        
        # Add target
        cmd.append(target)
        
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
        
        # Parse the enum4linux output into structured format
        structured_output = parse_enum4linux_output(raw_output) if raw_output else {}
        
        # Format response according to schema.json
        response = {
            "service": "enum4linux",
            "process_time_ms": process_time_ms,
            "target": target,
            "arguments": {
                "options": options,
                "username": username,
                "password": "***" if password else "",  # Mask password in response
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
            "service": "enum4linux",
            "process_time_ms": process_time_ms,
            "target": target if 'target' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "username": username if 'username' in locals() else "",
                "password": "***" if 'password' in locals() and password else "",
                "timeout": timeout if 'timeout' in locals() else 120
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
            "service": "enum4linux",
            "process_time_ms": process_time_ms,
            "target": target if 'target' in locals() else "unknown",
            "arguments": {
                "options": options if 'options' in locals() else "",
                "username": username if 'username' in locals() else "",
                "password": "***" if 'password' in locals() and password else "",
                "timeout": timeout if 'timeout' in locals() else 120
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
    mcp.run(transport="http", host="0.0.0.0", port=9001)
