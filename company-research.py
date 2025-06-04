from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

from tools.stock_analysis import analyze_stock

import asyncio
import os
import time

from dotenv import load_dotenv

load_dotenv()


google_search_tool = FunctionTool(
    google_search, description="Search Google for information, returns results with a snippet and body content"
)
stock_analysis_tool = FunctionTool(analyze_stock, description="Analyze stock data and generate a plot")

openai_api_key=os.getenv("OPENAI_API_KEY")
model_client = OpenAIChatCompletionClient(model="gpt-4.1", openai_api_key=openai_api_key)

search_agent = AssistantAgent(
    name="Google_Search_Agent",
    model_client=model_client,
    tools=[google_search_tool],
    description="Search Google for information, returns top 2 results with a snippet and body content",
    system_message="You are a helpful AI assistant. Solve tasks using your tools.",
)

stock_analysis_agent = AssistantAgent(
    name="Stock_Analysis_Agent",
    model_client=model_client,
    tools=[stock_analysis_tool],
    description="Analyze stock data and generate a plot",
    system_message="Perform data analysis.",
)

report_agent = AssistantAgent(
    name="Report_Agent",
    model_client=model_client,
    description="Generate a report based the search and results of stock analysis",
    system_message="You are a helpful assistant that can generate a comprehensive report on a given topic based on search and stock analysis. When you done with generating the report, reply with TERMINATE.",
)

team = RoundRobinGroupChat([stock_analysis_agent, search_agent, report_agent], max_turns=3)



async def main():
    load_dotenv()
    
    stream = team.run_stream(task="Write a financial report on American airlines")
    await Console(stream)
    await model_client.close()

asyncio.run(main())
