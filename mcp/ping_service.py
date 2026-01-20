from typing import Optional
import subprocess
import re
from service_response import ServiceResponse

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

async def ping_host(host: str, count: int = 5, interval: float = 1.0, packet_size: int = 56) -> dict:
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
        
        # Validate parameters
        if not host:
            return {"error": "host parameter is required"}
                
        if count < 1 or count > 99:
            return {"error": "count must be between 1 and 99"}
        
        if interval < 0.01 or interval > 5:
            return {"error": "interval must be between 0.01 and 5 seconds"}
        
        if packet_size < 1 or packet_size > 65524:
            return {"error": "packet_size must be between 1 and 65524"}

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
        
        # Format response according to schema.json
        response = ServiceResponse(
            service="ping",
            process_time_ms=process_time_ms,
            target=host,
            arguments={
                "count": count,
                "interval": interval,
                "packet_size": packet_size
            },
            return_code=result.returncode,
            raw_output=raw_output,
            raw_error=raw_error
        )
        
        return response
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="ping",
            process_time_ms=process_time_ms,
            target=host if 'host' in locals() else "unknown",
            arguments={
                "count": count if 'count' in locals() else 0,
                "interval": interval if 'interval' in locals() else 0,
                "packet_size": packet_size if 'packet_size' in locals() else 0
            },
            return_code=-1,
            raw_output="",
            raw_error=str(e)
        )
        
        return response


async def ping_host_raw(host: str, count: int = 5, interval: float = 0.25, packet_size: int = 56) -> str:
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
        
        if not host:
            return "error: host parameter is required"
        
        # Validate parameters
        if count < 1 or count > 99:
            return "error: count must be between 1 and 99"
        
        if interval < 0.01 or interval > 5:
            return "error: interval must be between 0.01 and 5 seconds"
        
        if packet_size < 1 or packet_size > 65524:
            return "error: packet_size must be between 1 and 65524"
        
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
        
        return (raw_output if success else raw_error)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = "Process_time_ms: " + str(process_time_ms) + "\n" + "Error: " + str(e)
        
        return response
