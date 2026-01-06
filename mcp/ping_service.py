from typing import Optional
import subprocess
import re
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# Usage
#   ping [options] <destination>
# 
# Options:
#   <destination>      DNS name or IP address
#   -a                 use audible ping
#   -A                 use adaptive ping
#   -B                 sticky source address
#   -c <count>         stop after <count> replies
#   -C                 call connect() syscall on socket creation
#   -D                 print timestamps
#   -d                 use SO_DEBUG socket option
#   -e <identifier>    define identifier for ping session, default is random for
#                      SOCK_RAW and kernel defined for SOCK_DGRAM
#                      Imply using SOCK_RAW (for IPv4 only for identifier 0)
#   -f                 flood ping
#   -h                 print help and exit
#   -H                 force reverse DNS name resolution (useful for numeric
#                      destinations or for -f), override -n
#   -I <interface>     either interface name or address
#   -i <interval>      seconds between sending each packet
#   -L                 suppress loopback of multicast packets
#   -l <preload>       send <preload> number of packages while waiting replies
#   -m <mark>          tag the packets going out
#   -M <pmtud opt>     define path MTU discovery, can be one of <do|dont|want|probe>
#   -n                 no reverse DNS name resolution, override -H
#   -O                 report outstanding replies
#   -p <pattern>       contents of padding byte
#   -q                 quiet output
#   -Q <tclass>        use quality of service <tclass> bits
#   -s <size>          use <size> as number of data bytes to be sent
#   -S <size>          use <size> as SO_SNDBUF socket option value
#   -t <ttl>           define time to live
#   -U                 print user-to-user latency
#   -v                 verbose output
#   -V                 print version and exit
#   -w <deadline>      reply wait <deadline> in seconds
#   -W <timeout>       time to wait for response
# 
# IPv4 options:
#   -4                 use IPv4
#   -b                 allow pinging broadcast
#   -R                 record route
#   -T <timestamp>     define timestamp, can be one of <tsonly|tsandaddr|tsprespec>
# 
# IPv6 options:
#   -6                 use IPv6
#   -F <flowlabel>     define flow label, default is random
#   -N <nodeinfo opt>  use IPv6 node info query, try <help> as argument

# To run: uvicorn tools.ping_mcp_service:app --reload
# Create FastMCP server
mcp = FastMCP("Ping Service")

def get_service_info() -> dict:
    return {
        "name": "ping",
        "endpoint": "/ping",
        "description": "Network connectivity testing using ICMP ping",
        "methods": ["GET", "POST"],
        "parameters": {
            "host": "Target hostname or IP address (required)",
            "count": "Number of ping packets (1-99, default: 5)",
            "interval": "Interval between packets (0.01-5.0, default: 1.0)",
            "packet_size": "Size of data bytes (1-65524, default: 56)"
        }
    }

def parse_ping_output(output: str) -> dict:
    """Parse ping output into structured JSON format matching schema.json"""
    result = {
        "bytes": None,
        "from": None,
        "ttl": None,
        "packets": [],
        "errors": [],
        "statistics": {
            "packets_transmitted": 0,
            "packets_received": 0,
            "packet_loss_percent": 0,
            "time_ms": 0,
            "errors": 0,
            "rtt": {
                "min": 0.0,
                "avg": 0.0,
                "max": 0.0,
                "mdev": 0.0
            }
        }
    }
    
    lines = output.strip().split('\n')
    
    # Parse header line: PING 192.168.0.0 (192.168.0.0) 56(84) bytes of data.
    header_pattern = r'PING\s+(\S+)\s+\(([^)]+)\)\s+(\d+)\((\d+)\)\s+bytes'
    for line in lines:
        match = re.search(header_pattern, line)
        if match:
            result["from"] = match.group(2)  # Target IP address
            result["bytes"] = int(match.group(3))  # Data bytes
            break
    
    # Parse successful ping responses
    ping_pattern = r'(\d+)\s+bytes\s+from\s+([^:]+):\s+icmp_seq=(\d+)\s+ttl=(\d+)\s+time=([0-9.]+)\s+ms'
    for line in lines:
        match = re.search(ping_pattern, line)
        if match:
            # Store TTL from first successful packet
            if result["ttl"] is None:
                result["ttl"] = int(match.group(4))
            
            packet = {
                "sequence": int(match.group(3)),
                "time_ms": float(match.group(5)),
                "status": "success"
            }
            result["packets"].append(packet)
    
    # Parse error responses (Destination Host Unreachable, etc.)
    error_pattern = r'From\s+([^:]+)\s+icmp_seq=(\d+)\s+(.+)'
    for line in lines:
        match = re.search(error_pattern, line)
        if match:
            error_entry = {
                "sequence": int(match.group(2)),
                "error_message": match.group(3).strip(),
                "from": match.group(1),
                "status": "error"
            }
            result["errors"].append(error_entry)
            
            # Also add to packets array for consistency
            packet = {
                "sequence": int(match.group(2)),
                "time_ms": None,
                "status": "error",
                "error": match.group(3).strip()
            }
            result["packets"].append(packet)
    
    # Parse statistics line with error handling
    # Format: 5 packets transmitted, 0 received, +5 errors, 100% packet loss, time 4110ms
    stats_pattern = r'(\d+)\s+packets\s+transmitted,\s+(\d+)\s+received(?:,\s+\+(\d+)\s+errors)?,\s+([0-9.]+)%\s+packet\s+loss,\s+time\s+(\d+)ms'
    for line in lines:
        match = re.search(stats_pattern, line)
        if match:
            result["statistics"]["packets_transmitted"] = int(match.group(1))
            result["statistics"]["packets_received"] = int(match.group(2))
            result["statistics"]["errors"] = int(match.group(3)) if match.group(3) else 0
            result["statistics"]["packet_loss_percent"] = float(match.group(4))
            result["statistics"]["time_ms"] = int(match.group(5))
            break
    
    # Parse RTT line (only available if there were successful responses)
    rtt_pattern = r'rtt\s+min/avg/max/mdev\s+=\s+([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+)\s+ms'
    for line in lines:
        match = re.search(rtt_pattern, line)
        if match:
            result["statistics"]["rtt"]["min"] = float(match.group(1))
            result["statistics"]["rtt"]["avg"] = float(match.group(2))
            result["statistics"]["rtt"]["max"] = float(match.group(3))
            result["statistics"]["rtt"]["mdev"] = float(match.group(4))
            break
    
    # Sort packets by sequence number for consistency
    result["packets"].sort(key=lambda x: x["sequence"])
    
    return result
 


@mcp.custom_route("/ping", methods=["GET", "POST"])
async def ping_host(request: Request) -> JSONResponse:
    """Ping a host to test network connectivity.
        host: The hostname or IP address to ping
        count: Number of ping packets to send (default: 5)
        Max: 65524
    Returns:
        JSON response matching schema.json format
    """
    import time
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if request.method == "GET":
            host = request.query_params.get("host")
            count = int(request.query_params.get("count", 5))
            interval = float(request.query_params.get("interval", 1.0))
            packet_size = int(request.query_params.get("packet_size", 56))
        else:  # POST
            body = await request.json()
            host = body.get("host")
            count = body.get("count", 5)
            interval = body.get("interval", 1.0)
            packet_size = body.get("packet_size", 56)
        
        if not host:
            return JSONResponse(
                {"error": "host parameter is required"}, 
                status_code=400
            )
        
        # Validate parameters
        if count < 1:
            count = 1
        if count > 99:
            count = 99
        if interval < 0.01:
            interval = 0.01
        if interval > 5:
            interval = 5
        if packet_size < 1:
            packet_size = 56
        if packet_size > 65524:
            packet_size = 65524

        result = subprocess.run(
            ["ping", 
            "-c", str(count), 
            "-i", str(interval), 
            "-s", str(packet_size), 
            host
            ], capture_output=True, text=True, timeout=60)
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        success = result.returncode == 0
        raw_output = result.stdout if result.stdout else ""
        raw_error = result.stderr if result.stderr else ""
        
        # Parse the ping output into structured format
        structured_output = parse_ping_output(raw_output) if success and raw_output else {}
        
        # Format response according to schema.json
        response = {
            "service": "ping",
            "process_time_ms": process_time_ms,
            "target": host,
            "arguments": {
                "count": count,
                "interval": interval,
                "packet_size": packet_size
            },
            "return_code": result.returncode,
            "raw_output": raw_output,
            "raw_error": raw_error,
            "structured_output": structured_output
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "ping",
            "process_time_ms": process_time_ms,
            "target": host if 'host' in locals() else "unknown",
            "arguments": {
                "count": count if 'count' in locals() else 0,
                "interval": interval if 'interval' in locals() else 0,
                "packet_size": packet_size if 'packet_size' in locals() else 0
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
    mcp.run(transport="http", host="0.0.0.0", port=9000)