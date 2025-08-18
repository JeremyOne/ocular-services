#!/usr/bin/env python3
"""
Log analysis script for ocular_agents
Parses and analyzes the log files to provide insights into agent interactions
"""

import sys
import os
import re
from datetime import datetime
from collections import defaultdict, Counter
import glob

def analyze_log_file(log_file_path):
    """Analyze a single log file and extract statistics."""
    
    if not os.path.exists(log_file_path):
        print(f"❌ Log file not found: {log_file_path}")
        return
    
    print(f"📊 Analyzing log file: {log_file_path}")
    print("=" * 60)
    
    # Statistics counters
    message_count = 0
    tool_calls = 0
    agent_interactions = 0
    agents_active = set()
    tools_used = Counter()
    interaction_types = Counter()
    hourly_activity = defaultdict(int)
    
    # Read and parse the log file
    with open(log_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Parse timestamp and extract hour
            timestamp_match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    hourly_activity[dt.hour] += 1
                except ValueError:
                    pass
            
            # Count different types of log entries
            if 'MSG#' in line and 'FROM' in line:
                message_count += 1
                # Extract agent name
                agent_match = re.search(r'FROM (\w+):', line)
                if agent_match:
                    agents_active.add(agent_match.group(1))
            
            elif 'TOOL_CALL:' in line:
                tool_calls += 1
                # Extract tool and agent names
                tool_match = re.search(r'TOOL_CALL: (\w+) -> (\w+)', line)
                if tool_match:
                    agent_name = tool_match.group(1)
                    tool_name = tool_match.group(2)
                    agents_active.add(agent_name)
                    tools_used[tool_name] += 1
            
            elif 'AGENT_INTERACTION:' in line:
                agent_interactions += 1
                # Extract interaction type
                interaction_match = re.search(r'\[(\w+)\]', line)
                if interaction_match:
                    interaction_types[interaction_match.group(1)] += 1
                
                # Extract agent names
                agent_match = re.search(r'AGENT_INTERACTION: (\w+)', line)
                if agent_match:
                    agents_active.add(agent_match.group(1))
    
    # Display statistics
    print(f"📈 Session Statistics:")
    print(f"  Total Messages: {message_count}")
    print(f"  Tool Calls: {tool_calls}")
    print(f"  Agent Interactions: {agent_interactions}")
    print(f"  Active Agents: {len(agents_active)}")
    print()
    
    print(f"🤖 Active Agents ({len(agents_active)}):")
    for agent in sorted(agents_active):
        print(f"  • {agent}")
    print()
    
    if tools_used:
        print(f"🔧 Tools Used ({len(tools_used)}):")
        for tool, count in tools_used.most_common():
            print(f"  • {tool}: {count} times")
        print()
    
    if interaction_types:
        print(f"💬 Interaction Types:")
        for interaction_type, count in interaction_types.most_common():
            print(f"  • {interaction_type}: {count} times")
        print()
    
    if hourly_activity:
        print(f"🕐 Activity by Hour:")
        for hour in sorted(hourly_activity.keys()):
            activity = hourly_activity[hour]
            bar = "█" * min(20, activity // 5 + 1) if activity > 0 else ""
            print(f"  {hour:02d}:00 - {activity:3d} events {bar}")
    print()

def find_latest_log():
    """Find the most recent log file."""
    log_files = glob.glob("reports/ocular_*.log")
    if not log_files:
        return None
    return max(log_files, key=os.path.getctime)

def main():
    """Main function to analyze log files."""
    
    if len(sys.argv) > 1:
        # Analyze specific log file
        log_file = sys.argv[1]
        analyze_log_file(log_file)
    else:
        # Find and analyze the latest log file
        latest_log = find_latest_log()
        if latest_log:
            analyze_log_file(latest_log)
        else:
            print("❌ No log files found in reports/ directory")
            print("💡 Run a research session first to generate log files")
            return
    
    print("✅ Log analysis completed!")

if __name__ == "__main__":
    main()
