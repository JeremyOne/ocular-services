from autogen_core.tools import FunctionTool

from ping_tool import ping_host
from nmap_tool import nmap_scan

ping_tool = FunctionTool(
    ping_host,
    description="Ping a network host to check connectivity. " \
    "Args: host (str), count (int, default 4)," \
    "These options are available: " \
    "   '-c 10' to send 10 echo requests." \
    "   '-i 0.25' to set interval between requests to 0.25 seconds." \
)

nmap_tool = FunctionTool(
    nmap_scan,
    description="Run an nmap scan on a target. " \
    "Args: target (str), options (str, default '-F'), " \
    "These options are available: " \
    "   '-F' for a fast scan. (this operation is cheap)" \
    "   '-sV --top-ports 20' to scan the top 20 ports. (this operation is cheap)" \
    "   '-A -T4' for aggressive scan and OS detection. (this operation is expensive)" \
    "   '-sS -Pn' for a stealth scan without pinging the host. (this operation is cheap)" \
    "   '-sU' to scan for UDP ports. (this operation is expensive)" \
    "   '-Pn --script vuln' to scan for CVEs (this operation is expensive)" \
)