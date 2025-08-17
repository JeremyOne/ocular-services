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
#from tools.masscan_tool import masscan_scan
from tools.httpx_tool import httpx_scan

from tools.enums import (
    PingOptions, NmapOptions, CurlOptions, NbtscanOptions,
    Enum4linuxOptions, NiktoOptions, SmbclientOptions, DnsRecordTypes, MasscanOptions, HttpxOptions
)

from dotenv import load_dotenv
load_dotenv()

# Define tools

ping_tool = FunctionTool(
    ping_host,
    description="Ping a network host to check connectivity. " \
    f"Args: host (str), count (PingOptions, default {PingOptions.DEFAULT_COUNT.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in PingOptions])}"
)

nmap_tool = FunctionTool(
    nmap_scan,
    description="Run an nmap scan on a target. " \
    f"Args: target (str), options (NmapOptions, default {NmapOptions.FAST_SCAN.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in NmapOptions])}"
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
    description="Lookup DNS records for a host. " \
    f"Args: host (str), record_types (Optional[List[DnsRecordTypes]], default A and TXT records). " \
    f"Available record types: {', '.join([f'{opt.name}: {opt.description}' for opt in DnsRecordTypes])}"
)

curl_tool = FunctionTool(
    curl_test,
    description="Make an HTTP request to a URL using curl for penetration testing and discovery. " \
    f"Args: url (str), options (CurlOptions, default {CurlOptions.HEADERS_ONLY.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in CurlOptions])}"
)

# Tool registration example:
nbtscan_tool = FunctionTool(
    nbtscan_scan,
    description="Run nbtscan to enumerate NetBIOS information on a target. " \
    f"Args: target (str), options (Optional[NbtscanOptions]). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in NbtscanOptions])}"
)

enum4linux_tool = FunctionTool(
    enum4linux_scan,
    description="Run enum4linux to enumerate SMB/CIFS information on a target. " \
    f"Args: target (str), options (Enum4linuxOptions, default {Enum4linuxOptions.ALL_ENUMERATION.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in Enum4linuxOptions])}"
)

nikto_tool = FunctionTool(
    nikto_scan,
    description="Run nikto web vulnerability scanner on a target. " \
    f"Args: target (str), options (NiktoOptions, default {NiktoOptions.HOST_SCAN.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in NiktoOptions])}"
)

smbclient_tool = FunctionTool(
    smbclient_scan,
    description="Run smbclient to interact with SMB/CIFS shares on a target. " \
    f"Args: target (str), options (SmbclientOptions, default {SmbclientOptions.LIST_SHARES.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in SmbclientOptions])}"
)

httpx_tool = FunctionTool(
    httpx_scan,
    description="Run httpx HTTP probe on a target URL or IP. " \
    f"Args: target (str), options (HttpxOptions, default {HttpxOptions.BASIC_PROBE.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in HttpxOptions])}"
)

# Note this tool requires sudo - disabling for now
#masscan_tool = FunctionTool(
#    masscan_scan,
#    description="Run a masscan scan on a target. " \
#    f"Args: target (str), options (MasscanOptions, default {MasscanOptions.TOP_100_PORTS.name}). " \
#    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in MasscanOptions])}"
#)

# LLM client
openai_api_key=os.getenv("OPENAI_API_KEY")
model_client = OpenAIChatCompletionClient(model="gpt-4.1", openai_api_key=openai_api_key)

# Agents
network_analysis_agent = AssistantAgent(
    name="Network_Analysis_Agent",
    model_client=model_client,
    tools=[curl_tool, dns_lookup_tool, enum4linux_tool, nbtscan_tool, nmap_tool, ping_tool, smbclient_tool],
    description="Follow instructions and analyze a given network or host, recommend additional tools to use and actions to take. If a tool times out, run it again with a cheaper option. ",
    system_message="You are a professional penetration tester and helpful AI assistant.",
)

webapp_analysis_agent = AssistantAgent(
    name="WebApp_Analysis_Agent",
    model_client=model_client,
    tools=[curl_tool, nikto_tool, httpx_tool],
    description="Analyze a web application for vulnerabilities and recommend actions.",
    system_message="You are a professional web application expert and penetration tester.",
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

team = RoundRobinGroupChat([network_analysis_agent, webapp_analysis_agent, intent_analysis_agent, report_agent, agent_manager], max_turns=5)

async def main():
    
    if len(sys.argv) < 2:
        print("Usage: python research.py '<task description>'")
        return

    log_text(f"Starting research task: {sys.argv[1]}")

    task = sys.argv[1]
    stream = team.run_stream(task=task)
    
    # Create a custom handler to log messages while displaying them
    async def log_and_display():
        async for message in stream:
            # Log the message
            if hasattr(message, 'source') and hasattr(message, 'content'):
                log_text(f"[{message.source}]: {message.content}")
            elif hasattr(message, 'content'):
                log_text(f"[MESSAGE]: {message.content}")
            else:
                log_text(f"[STREAM]: {str(message)}")
            
            # Yield the message for console display
            yield message
    
    await Console(log_and_display())
    await model_client.close()
    

asyncio.run(main())
