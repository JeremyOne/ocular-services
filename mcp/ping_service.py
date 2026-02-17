from typing import Optional
import subprocess
from service_response import ServiceResponse
from fastmcp import Context
from utility import execute_command

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


async def ping_host(host: str, 
                    count: int = 5, 
                    interval: float = 1.0, 
                    packet_size: int = 56,
                    timeout: int = 60, 
                    ctx: Context = None) -> ServiceResponse:
    
    # Initialize ServiceResponse
    response = ServiceResponse(
        service="ping",
        target=host,
        arguments={
            "host": host,
            "count": count,
            "interval": interval,
            "packet_size": packet_size,
            "timeout": timeout
        }
    )
    
    try:
        # Validate parameters
        if not host:
            response.add_error("host parameter is required")
            return response
                
        if count < 1 or count > 99:
            response.add_error("count must be between 1 and 99")
            return response
        
        if interval < 0.01 or interval > 5:
            response.add_error("interval must be between 0.01 and 5 seconds")
            return response
        
        if packet_size < 1 or packet_size > 65524:
            response.add_error("packet_size must be between 1 and 65524")
            return response
        
        # Build command
        cmds = f"ping -c {str(count)} -i {str(interval)} -s {str(packet_size)} {host}"
        response.raw_command = cmds
        
        # Execute command with real-time output processing
        return await execute_command(
            cmd=cmds,
            response=response,
            ctx=ctx,
            timeout=timeout,
            expected_lines=(count + 10)
        )
    
        return response
        
    except Exception as e:
        response.add_error(str(e))
        return response

