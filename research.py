import asyncio
import sys
import os

from autogen_agentchat.agents import UserProxyAgent 
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

from tools.ping_tool import ping_host
from tools.nmap_tool import nmap_scan
from tools.report_tool import write_report
from tools.dns_tool import dns_lookup
from tools.curl_tool import curl_test
from tools.util import load_template, log_text
from tools.datetime_tool import get_current_datetime
from tools.nbtscan_tool import nbtscan_scan
from tools.enum4linux_tool import enum4linux_scan
from tools.nikto_tool import nikto_scan
from tools.smbclient_tool import smbclient_scan


from dotenv import load_dotenv
load_dotenv()



# Define tools

ping_tool = FunctionTool(
    ping_host,
    description="Ping a network host to check connectivity. " \
    "Args: host (str), count (int, default 4)"
)

nmap_tool = FunctionTool(
    nmap_scan,
    description="Run an nmap scan on a target. " \
    "Args: target (str), options (str, default '-F'), " \
    "These options are available: " \
    "   '-F' for a fast scan (this operation is cheap)." \
    "   '-sV --top-ports 20' to scan the top 20 ports (this operation is cheap)." \
    "   '-sS -Pn' for a stealth scan without pinging the host (this operation is cheap)." \
    "   '-p 3389 --script rdp-* 192.168.0.9' to scan for RDP vulnerabilities." \
    "   '-A -T4' for aggressive scan and OS detection (this operation is expensive)." \
    "   '-sU' to scan for UDP ports (this operation is expensive)." \
    "   '-Pn --script vuln' to scan for CVEs (this operation is expensive)."
)

write_report_tool = FunctionTool(
    write_report,
    description="Write the provided markdown content to a file. Args: content (str), hostname (str)."
)

datetime_tool = FunctionTool(
    get_current_datetime,
    description="Returns the current date and time in ISO format."
)

dns_lookup_tool = FunctionTool(
    dns_lookup,
    description="Lookup a host's IP addresses and identify the email host from TXT records. Args: host (str). Returns a dict with 'ip_addresses' and 'email_host'."
)

curl_tool = FunctionTool(
    curl_test,
    description="Make an HTTP request to a URL using curl-like options to get HTTP information for penetration testing and discovery. " \
    "Args: url (str), method (str, default 'GET'), headers (dict, optional), data (str, optional), options (str, optional). " \
    "Returns the response content and status code." \
    "These options are available: " \
    "   '-I' to fetch headers only. " \
    "   '-L' to follow redirects. " \
    "   '-v' for verbose output. " \
    "   '--http2' to test HTTP/2 support. " \
    "   '--trace-ascii <file>' for detailed trace output."
)

# Tool registration example:
nbtscan_tool = FunctionTool(
    nbtscan_scan,
    description="Run nbtscan to enumerate NetBIOS information on a target. Args: target (str), options (str, optional). Returns the command output." \
    "" \
    "These options are available: " \
    "   '-r' to scan a range of IPs (e.g., 192.168.1.1-254), " \
    "   '-s' to scan a specific subnet (e.g., 192.168.1.0/24)" \
    "   '-v' for verbose output, " \
    "   '-d' to include domain information, " \
    "   '-n' to skip NetBIOS name resolution, "
)

enum4linux_tool = FunctionTool(
    enum4linux_scan,
    description="Run enum4linux to enumerate SMB/CIFS information on a target. Args: target (str), options (str, optional). Returns the command output." \
    "These options are available: " \
    "   '-a' for all enumeration (default), " \
    "   '-U' to get userlist, " \
    "   '-M' to get machine list, " \
    "   '-S' to get sharelist, " \
    "   '-P' to get password policy information, " \
    "   '-G' to get group and member list, " \
    "   '-d' to be detailed, " \
    "   '-u user -p pass' to specify credentials"
)

nikto_tool = FunctionTool(
    nikto_scan,
    description="Run nikto web vulnerability scanner on a target. Args: target (str), options (str, optional). Returns the command output." \
    "These options are available: " \
    "   '-h' for host scan (default), " \
    "   '-p' to specify port (e.g., '-p 80,443'), " \
    "   '-ssl' to force SSL mode, " \
    "   '-nossl' to disable SSL, " \
    "   '-C all' to check all CGI dirs, " \
    "   '-Tuning x' for specific tests (1=interesting files, 2=misconfiguration, 3=info disclosure, etc.), " \
    "   '-Format htm' to output in HTML format, " \
    "   '-o filename' to save output to file"
)

smbclient_tool = FunctionTool(
    smbclient_scan,
    description="Run smbclient to interact with SMB/CIFS shares on a target. Args: target (str), options (str, optional). Returns the command output." \
    "These options are available: " \
    "   '-L' to list shares (default), " \
    "   '-N' for null session (no password), " \
    "   '-U username' to specify username, " \
    "   '-W workgroup' to specify workgroup/domain, " \
    "   '-c \"command\"' to execute specific commands, " \
    "   '-m SMB2' to force SMB2 protocol, " \
    "   '-m SMB3' to force SMB3 protocol, " \
    "   '//target/share' to connect to specific share"
)

# LLM client
openai_api_key=os.getenv("OPENAI_API_KEY")
model_client = OpenAIChatCompletionClient(model="gpt-4.1", openai_api_key=openai_api_key)

# Agents
network_analysis_agent = AssistantAgent(
    name="Network_Analysis_Agent",
    model_client=model_client,
    tools=[ping_tool, nmap_tool, dns_lookup_tool, nbtscan_tool, enum4linux_tool, nikto_tool, smbclient_tool],
    description="Follow instructions and analyze a given network or host, recommend additional tools to use and actions to take. If a tool times out, run it again with a cheaper option. ",
    system_message="You are a professional penetration tester and helpful AI assistant.",
)

intent_analysis_agent = AssistantAgent(
    name="Intent_Analysis_Agent",
    model_client=model_client,
    description="Analyze the intent of the user request and suggest actions for the Network_Analysis_Agent. \n" \
        "- If the request is too vague, ask for more details. If the request is too complex, break it down into smaller tasks and assign them to the Network_Analysis_Agent. \n"
        "- If the request is too simple, suggest additional tools or actions that could be taken. \n"
        "When you satisfied with the report, reply with TERMINATE.",
    system_message="You are a professional penetration tester and helpful AI assistant.",
)

report_agent = AssistantAgent(
    name="Report_Agent",
    model_client=model_client,
    tools=[write_report_tool, datetime_tool],
    description="Generate a report based the analysis and tool outputs in HTML. \n",
    system_message="You are a helpful assistant that can write a comprehensive report using the information provided by the analysis agent. \n" \
    "If you need more information, ask the Network_Analysis_Agent or Intent_Analysis_Agent to provide it. \n" \
    "If you are ready to write the report, use the write_report tool. \n" \
    "You can also ask the Agent_Manager to review the report before writing it. \n" \
    "Use this HTML template to write the report: \n\n------\n\n" + load_template("reports/report_template.htmlt")
)

agent_manager = AssistantAgent( 
    name="Agent_Manager",
    model_client=model_client,
    description="Manages the team of agents and coordinates their actions.",
    system_message="You are a helpful manager with that can analyze networking, " \
    "security and suggest improvements to all agents. When the report is ready to generate and has enough detail, ask the Report_Agent to write it.",
)

#user_agent = UserProxyAgent (
#    name="User_Agent",
#    description="Receives instructions from the user via keyboard input and relays them to the team.",
#)

team = RoundRobinGroupChat([network_analysis_agent, intent_analysis_agent, report_agent], max_turns=5)

async def main():
    
    if len(sys.argv) < 2:
        print("Usage: python research.py '<task description>'")
        return

    log_text(f"Starting research task: {sys.argv[1]}")

    task = sys.argv[1]
    stream = team.run_stream(task=task)
    await Console(stream)
    await model_client.close()
    

asyncio.run(main())
