import asyncio
import sys
import os
from datetime import datetime

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
from tools.httpx_tool import httpx_scan
from tools.wpscan_tool import wpscan_scan
from tools.whois_tool import whois_lookup
#from tools.masscan_tool import masscan_scan - needs root

from tools.enums import (
    PingOptions, NmapOptions, CurlOptions, NbtScanOptions,
    Enum4linuxOptions, NiktoOptions, SmbClientOptions, DnsRecordTypes, MasscanOptions, HttpxOptions, WpScanOptions, WhoisOptions
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

nbtscan_tool = FunctionTool(
    nbtscan_scan,
    description="Run nbtscan to enumerate NetBIOS information on a target. " \
    f"Args: target (str), options (Optional[NbtScanOptions]). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in NbtScanOptions])}"
)

enum4linux_tool = FunctionTool(
    enum4linux_scan,
    description="Run enum4linux to enumerate SMB/CIFS information on a target. " \
    f"Args: target (str), options (Enum4linuxOptions, default {Enum4linuxOptions.ALL_ENUMERATION.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in Enum4linuxOptions])}"
)

nikto_tool = FunctionTool(
    nikto_scan,
    description="Run nikto web vulnerability scanner on a target. This tool is designed to identify potential vulnerabilities in web applications." \
    f"Args: target (str), options (NiktoOptions, default {NiktoOptions.HOST_SCAN.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in NiktoOptions])}"
)

smbclient_tool = FunctionTool(
    smbclient_scan,
    description="Run smbclient to interact with SMB/CIFS shares on a target. " \
    f"Args: target (str), options (SmbClientOptions, default {SmbClientOptions.LIST_SHARES.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in SmbClientOptions])}"
)

httpx_tool = FunctionTool(
    httpx_scan,
    description="Run httpx HTTP probe on a target URL or IP. This tool is designed to identify potential vulnerabilities in web applications." \
    f"Args: target (str), options (HttpxOptions, default {HttpxOptions.BASIC_PROBE.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in HttpxOptions])}"
)

wpscan_tool = FunctionTool(
    wpscan_scan,
    description="Run WPScan on a WordPress target URL. This tool should be run on all WordPress sites." \
    f"Args: target (str), options (WpScanOptions, default {WpScanOptions.BASIC_SCAN.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in WpScanOptions])}"
)

whois_tool = FunctionTool(
    whois_lookup,
    description="Perform WHOIS lookup on a domain to get registration details including registrar and registrant information. " \
    f"Args: domain (str), options (WhoisOptions, default {WhoisOptions.BASIC_WHOIS.name}). " \
    f"Available options: {', '.join([f'{opt.name}: {opt.description}' for opt in WhoisOptions])}"
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
    tools=[curl_tool, dns_lookup_tool, enum4linux_tool, nbtscan_tool, nmap_tool, ping_tool, smbclient_tool, whois_tool],
    description="Follow instructions and analyze a given network or host, recommend additional tools to use and actions to take. If a tool times out, run it again with a cheaper option. ",
    system_message="You are a professional penetration tester and helpful AI assistant.",
)

webapp_analysis_agent = AssistantAgent(
    name="WebApp_Analysis_Agent",
    model_client=model_client,
    tools=[curl_tool, nikto_tool, httpx_tool, wpscan_tool],
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
    description="Generate a report based the analysis and tool outputs in markdown. \n",
    system_message="You are a helpful assistant that can write a comprehensive report using the information provided by all agents. \n" \
    "Use this template to write the report: \n\n------\n\n" + load_template("reports/template.mdt")
)

agent_manager = AssistantAgent( 
    name="Agent_Manager",
    model_client=model_client,
    description="Manages the team of agents and coordinates their actions.",
    system_message="You are a skilled manager of agents that can advise on networking, security, and compliance. Suggest improvements to all agents. \r\n" \
    "If you need more information to complete the report and the intention provided by the user, ask the Network_Analysis_Agent, WebApp_Analysis_Agent, or Intent_Analysis_Agent to provide it. \r\n" \
    "When the report is ready to generate and has enough detail, ask the Report_Agent to write it.",
)

user_agent = UserProxyAgent(
    name="User_Agent",
    description="Receives instructions from the user via keyboard input and relays them to the team. Can provide additional context, clarifications, or new tasks."
)

# Two different team configurations
interactive_team = RoundRobinGroupChat([user_agent, network_analysis_agent, webapp_analysis_agent, intent_analysis_agent, report_agent, agent_manager], max_turns=10)
automated_team = RoundRobinGroupChat([network_analysis_agent, webapp_analysis_agent, intent_analysis_agent, report_agent, agent_manager], max_turns=5)

async def main():
    
    # Check for interactive mode
    interactive_mode = len(sys.argv) > 1 and sys.argv[1].lower() in ['-i', '--interactive', 'interactive']
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python research.py '<task description>'          # Automated mode")
        print("  python research.py --interactive                 # Interactive mode")
        print("  python research.py -i                            # Interactive mode (short)")
        return

    if interactive_mode:
        print("🤖 Starting Interactive Research Session")
        print("💬 You can now chat with the agent team!")
        print("📝 Type your requests and the agents will respond")
        print("🚪 Type 'exit', 'quit', or press Ctrl+C to end the session")
        print("=" * 60)
        
        task = input("\n🔍 Enter your initial research task: ").strip()
        if not task:
            task = "Hello, I'd like to start a research session. Please introduce yourselves and let me know what you can help with."
        
        team = interactive_team
        log_text(f"=== INTERACTIVE RESEARCH SESSION STARTED ===")
    else:
        task = sys.argv[1]
        team = automated_team
        log_text(f"=== AUTOMATED RESEARCH SESSION STARTED ===")
    
    log_text(f"Task: {task}")
    log_text(f"Timestamp: {datetime.now().isoformat()}")
    log_text(f"Mode: {'Interactive' if interactive_mode else 'Automated'}")
    log_text(f"Agents: {', '.join([agent.name for agent in team._participants])}")
    log_text(f"=====================================")

    team._group_chat_manager_name = "Agent_Manager"
    stream = team.run_stream(task=task)
    
    # Create a custom handler to log messages while displaying them
    async def log_and_display():
        message_count = 0
        tool_call_count = 0
        
        async for message in stream:
            message_count += 1
            
            # Enhanced message logging with more details
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            try:
                if hasattr(message, 'source') and hasattr(message, 'content'):
                    # Log agent messages with structured format
                    agent_name = message.source
                    content = message.content
                    
                    # Handle both string and list content
                    if isinstance(content, list):
                        content_str = ' '.join(str(item) for item in content)
                    elif isinstance(content, str):
                        content_str = content
                    elif content is None:
                        content_str = "[None]"
                    else:
                        content_str = str(content)
                    
                    # Detect tool calls (with safety check)
                    try:
                        is_tool_call = any(keyword in content_str.lower() for keyword in ['running', 'tool', 'function_call'])
                    except (AttributeError, TypeError):
                        is_tool_call = False
                        log_text(f"[{timestamp}] WARNING: Unable to process content for tool detection")
                    
                    if is_tool_call:
                        tool_call_count += 1
                        log_text(f"[{timestamp}] TOOL#{tool_call_count:03d} FROM {agent_name}:")
                    else:
                        log_text(f"[{timestamp}] MSG#{message_count:03d} FROM {agent_name}:")
                    
                    # Log with proper formatting - truncate preview but log full content separately
                    preview = content_str[:150].replace('\n', ' ')
                    log_text(f"  Preview: {preview}{'...' if len(content_str) > 150 else ''}")
                    
                    # Always log full content for debugging
                    log_text(f"  Full Content:")
                    for line in content_str.split('\n'):
                        log_text(f"    {line}")
                    
                    # Log message metadata if available
                    if hasattr(message, 'type'):
                        log_text(f"  Message Type: {message.type}")
                    
                    # Log content type for debugging
                    log_text(f"  Content Type: {type(content).__name__}")
                        
                    # Log additional attributes for debugging
                    attrs = [attr for attr in dir(message) if not attr.startswith('_')]
                    if attrs:
                        log_text(f"  Attributes: {', '.join(attrs)}")
                        
                elif hasattr(message, 'content'):
                    content = message.content
                    
                    # Handle both string and list content for system messages
                    if isinstance(content, list):
                        content_str = ' '.join(str(item) for item in content)
                    elif isinstance(content, str):
                        content_str = content
                    elif content is None:
                        content_str = "[None]"
                    else:
                        content_str = str(content)
                        
                    log_text(f"[{timestamp}] MSG#{message_count:03d} SYSTEM:")
                    log_text(f"  Content: {content_str}")
                    log_text(f"  Content Type: {type(content).__name__}")
                else:
                    log_text(f"[{timestamp}] MSG#{message_count:03d} STREAM:")
                    log_text(f"  Data: {str(message)}")
                
            except Exception as e:
                # Catch any unexpected errors in logging
                log_text(f"[{timestamp}] ERROR in logging message #{message_count:03d}: {str(e)}")
                log_text(f"  Message type: {type(message).__name__}")
                log_text(f"  Message attributes: {[attr for attr in dir(message) if not attr.startswith('_')]}")
            
            # Log separator for readability
            log_text("  " + "=" * 60)
            
            # Yield the message for console display
            yield message
            
            # In interactive mode, allow user input after each agent response
            if interactive_mode and hasattr(message, 'source') and message.source not in ["user", "User_Agent"]:
                try:
                    # Give user option to respond
                    print(f"\n💬 {message.source} has responded. You can:")
                    print("   - Type a message to continue the conversation")
                    print("   - Press Enter to let agents continue")
                    print("   - Type 'exit' to end the session")
                    
                    user_input = input("\n➤ Your response: ").strip()
                    
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        log_text(f"[{timestamp}] User requested session termination")
                        break
                    elif user_input:
                        # Log user input
                        log_text(f"[{timestamp}] USER_INPUT: {user_input}")

                        stream.asend(user_input)

                except KeyboardInterrupt:
                    print("\n\n🚪 Session terminated by user (Ctrl+C)")
                    log_text(f"[{timestamp}] Session terminated by KeyboardInterrupt")
                    break
                except EOFError:
                    print("\n🚪 Session terminated (EOF)")
                    log_text(f"[{timestamp}] Session terminated by EOF")
                    break
        
        # Log final statistics
        log_text(f"Session Statistics: {message_count} messages, {tool_call_count} tool calls")
    
    await Console(log_and_display())
    
    # Log session end
    log_text(f"=== RESEARCH SESSION COMPLETED ===")
    log_text(f"Timestamp: {datetime.now().isoformat()}")
    log_text(f"=====================================")
    
    await model_client.close()
    

asyncio.run(main())
