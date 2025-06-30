from autogen_agentchat.agents import UserProxyAgent 
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

from tools.ping_tool import ping_host
from tools.nmap_tool import nmap_scan
from tools.markdown_tool import write_report_to_markdown
from tools.dns_tool import dns_lookup


import asyncio
import os
from util import load_markdown_template

from dotenv import load_dotenv
import sys

load_dotenv()

# Define the tools with their descriptions

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
    "   '-sS -Pn' for a stealth scan without pinging the host. (this operation is cheap)" \
    "   '-A -T4' for aggressive scan and OS detection. (this operation is expensive)" \
    "   '-sU' to scan for UDP ports. (this operation is expensive)" \
    "   '-Pn --script vuln' to scan for CVEs (this operation is expensive)"
)

write_report_tool = FunctionTool(
    write_report_to_markdown,
    description="Write the provided markdown content to a file. Args: content (str), hostname (str)."
)

dns_lookup_tool = FunctionTool(
    dns_lookup,
    description="Lookup a host's IP addresses and identify the email host from TXT records. Args: host (str). Returns a dict with 'ip_addresses' and 'email_host'."
)



# Initialize the OpenAI client
openai_api_key=os.getenv("OPENAI_API_KEY")
model_client = OpenAIChatCompletionClient(model="gpt-4.1", openai_api_key=openai_api_key)

# Define the agents with their roles and tools
network_analysis_agent = AssistantAgent(
    name="Network_Analysis_Agent",
    model_client=model_client,
    tools=[ping_tool, nmap_tool, dns_lookup_tool],
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
    tools=[write_report_tool],
    description="Generate a report based the analysis and tool outputs in markdown and PDF.",
    system_message="You are a helpful assistant that can write a comprehensive markdown using the information provided by the analysis agent. " \
    "Use this template exactly to write the report: \n\n" + load_markdown_template()
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
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python security-research.py '<task description>'")
        return

    task = sys.argv[1]
    stream = team.run_stream(task=task)
    await Console(stream)
    await model_client.close()
    

asyncio.run(main())
