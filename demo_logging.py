#!/usr/bin/env python3
"""
Demo script to test the enhanced logging functionality
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

from tools.util import log_text, log_tool_call, log_agent_interaction

def demo_logging():
    """Demonstrate the enhanced logging capabilities."""
    
    # Start logging session
    log_text("=== LOGGING DEMO SESSION STARTED ===")
    log_text(f"Demo started at: {datetime.now().isoformat()}")
    log_text("Testing enhanced agent communication logging")
    log_text("=" * 50)
    
    # Simulate agent interactions
    log_agent_interaction("Network_Analysis_Agent", "WebApp_Analysis_Agent", 
                         "request", "Please analyze the web application at example.com")
    
    log_agent_interaction("WebApp_Analysis_Agent", None, 
                         "response", "Starting web application analysis...")
    
    # Simulate tool calls
    log_tool_call("ping_tool", "Network_Analysis_Agent", 
                  {"host": "example.com", "count": "4"}, 
                  "PING example.com (93.184.216.34): 56 data bytes\n64 bytes from 93.184.216.34: icmp_seq=0 ttl=54 time=12.345 ms")
    
    log_tool_call("nmap_tool", "Network_Analysis_Agent",
                  {"target": "example.com", "options": "FAST_SCAN"},
                  "Starting Nmap scan...\nNmap scan report for example.com (93.184.216.34)\nHost is up (0.012s latency).\nPORT   STATE SERVICE\n80/tcp open  http\n443/tcp open  https")
    
    log_tool_call("httpx_tool", "WebApp_Analysis_Agent",
                  {"target": "https://example.com", "options": "BASIC_PROBE"},
                  "httpx output:\nURL: https://example.com\nStatus Code: 200\nTitle: Example Domain\nTechnologies: nginx")
    
    # Simulate more agent interactions
    log_agent_interaction("WebApp_Analysis_Agent", "Report_Agent",
                         "data_handoff", "Web analysis complete. Found web server running nginx on ports 80,443")
    
    log_agent_interaction("Report_Agent", None,
                         "task_completion", "Generating comprehensive security report...")
    
    # End logging session
    log_text("=" * 50)
    log_text("=== LOGGING DEMO SESSION COMPLETED ===")
    log_text(f"Demo completed at: {datetime.now().isoformat()}")
    
    print("✅ Logging demo completed successfully!")
    print("📝 Check the reports/ directory for the generated log file")
    
    # Show the log file location
    import glob
    log_files = glob.glob("reports/ocular_*.log")
    if log_files:
        latest_log = max(log_files, key=os.path.getctime)
        print(f"📄 Latest log file: {latest_log}")
        
        # Show last few lines of the log
        print("\n📋 Last 10 lines of the log file:")
        print("-" * 40)
        with open(latest_log, 'r') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(line.rstrip())

if __name__ == "__main__":
    demo_logging()
