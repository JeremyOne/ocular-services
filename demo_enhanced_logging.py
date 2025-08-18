#!/usr/bin/env python3
"""
Enhanced logging wrapper for research.py
This shows how to integrate comprehensive logging into agent communications
"""

from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

from tools.util import log_text, log_tool_call, log_agent_interaction

class AgentLogger:
    """Enhanced logging class for agent interactions."""
    
    def __init__(self, session_name="research_session"):
        self.session_name = session_name
        self.start_time = datetime.now()
        self.message_count = 0
        self.tool_count = 0
        self.interaction_count = 0
        
        # Start session logging
        self.log_session_start()
    
    def log_session_start(self):
        """Log the start of a research session."""
        log_text("=" * 80)
        log_text(f"🚀 RESEARCH SESSION STARTED: {self.session_name}")
        log_text(f"📅 Start Time: {self.start_time.isoformat()}")
        log_text(f"🖥️  Working Directory: {os.getcwd()}")
        log_text(f"🐍 Python Version: {sys.version}")
        log_text("=" * 80)
    
    def log_message(self, agent_name, content, message_type="message"):
        """Log a message from an agent."""
        self.message_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_text(f"[{timestamp}] MSG#{self.message_count:03d} {message_type.upper()} FROM {agent_name}:")
        
        # Log content with proper formatting
        if len(content) > 200:
            preview = content[:200].replace('\n', ' ') + "..."
            log_text(f"  📝 Preview: {preview}")
            log_text(f"  📄 Full Content: ({len(content)} chars)")
            
            # Log full content line by line for better readability
            for i, line in enumerate(content.split('\n')):
                log_text(f"    L{i+1:03d}: {line}")
        else:
            log_text(f"  📝 Content: {content}")
        
        log_text(f"  ⏱️  Message Length: {len(content)} characters")
        log_text("  " + "─" * 60)
    
    def log_tool_execution(self, agent_name, tool_name, args=None, result=None, duration=None):
        """Log tool execution details."""
        self.tool_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_text(f"[{timestamp}] TOOL#{self.tool_count:03d} {agent_name} → {tool_name}")
        
        if args:
            log_text(f"  🔧 Arguments:")
            for key, value in args.items():
                log_text(f"    {key}: {value}")
        
        if result:
            result_preview = result[:150].replace('\n', ' ')
            if len(result) > 150:
                result_preview += "..."
            log_text(f"  ✅ Result Preview: {result_preview}")
            log_text(f"  📊 Result Size: {len(result)} characters")
            
            # Log first few lines of result
            result_lines = result.split('\n')
            log_text(f"  📄 Result Sample (first 5 lines):")
            for i, line in enumerate(result_lines[:5]):
                log_text(f"    R{i+1:02d}: {line}")
        
        if duration:
            log_text(f"  ⏱️  Execution Time: {duration:.2f} seconds")
        
        log_text("  " + "─" * 60)
    
    def log_agent_communication(self, from_agent, to_agent=None, comm_type="message", content=""):
        """Log communication between agents."""
        self.interaction_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if to_agent:
            log_text(f"[{timestamp}] COMM#{self.interaction_count:03d} {from_agent} → {to_agent} [{comm_type}]")
        else:
            log_text(f"[{timestamp}] COMM#{self.interaction_count:03d} {from_agent} [broadcast:{comm_type}]")
        
        if content:
            content_preview = content[:100].replace('\n', ' ')
            if len(content) > 100:
                content_preview += "..."
            log_text(f"  💬 Message: {content_preview}")
        
        log_text("  " + "─" * 60)
    
    def log_session_end(self):
        """Log the end of a research session."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        log_text("=" * 80)
        log_text(f"🏁 RESEARCH SESSION COMPLETED: {self.session_name}")
        log_text(f"📅 End Time: {end_time.isoformat()}")
        log_text(f"⏱️  Total Duration: {duration}")
        log_text(f"📊 Session Statistics:")
        log_text(f"   💬 Messages: {self.message_count}")
        log_text(f"   🔧 Tool Calls: {self.tool_count}")
        log_text(f"   📡 Interactions: {self.interaction_count}")
        log_text("=" * 80)

def demo_enhanced_logging():
    """Demonstrate the enhanced logging capabilities."""
    
    # Create logger instance
    logger = AgentLogger("Demo Enhanced Logging Session")
    
    # Simulate a research session with detailed logging
    logger.log_message("User", "Research in detail https://example.com/, enumerate all services, ports, vulnerabilities", "task_request")
    
    logger.log_agent_communication("Agent_Manager", "Network_Analysis_Agent", "task_assignment", 
                                 "Please start with network reconnaissance of example.com")
    
    logger.log_message("Network_Analysis_Agent", "Starting network analysis. I'll begin with basic connectivity and DNS resolution.", "status_update")
    
    # Simulate tool executions with detailed logging
    import time
    start_time = time.time()
    time.sleep(0.1)  # Simulate tool execution time
    end_time = time.time()
    
    logger.log_tool_execution("Network_Analysis_Agent", "ping_tool", 
                            {"host": "example.com", "count": "4"},
                            "PING example.com (93.184.216.34): 56 data bytes\n64 bytes from 93.184.216.34: icmp_seq=0 ttl=54 time=12.345 ms\n64 bytes from 93.184.216.34: icmp_seq=1 ttl=54 time=11.234 ms\n64 bytes from 93.184.216.34: icmp_seq=2 ttl=54 time=13.456 ms\n64 bytes from 93.184.216.34: icmp_seq=3 ttl=54 time=10.987 ms\n\n--- example.com ping statistics ---\n4 packets transmitted, 4 received, 0% packet loss\nround-trip min/avg/max/stddev = 10.987/12.006/13.456/1.023 ms",
                            end_time - start_time)
    
    logger.log_message("Network_Analysis_Agent", "Host is responsive. Proceeding with port scan.", "analysis")
    
    logger.log_tool_execution("Network_Analysis_Agent", "nmap_tool",
                            {"target": "example.com", "options": "FAST_SCAN"},
                            "Starting Nmap 7.93 ( https://nmap.org )\nNmap scan report for example.com (93.184.216.34)\nHost is up (0.012s latency).\nNot shown: 98 filtered tcp ports (no-responses)\nPORT   STATE SERVICE\n80/tcp open  http\n443/tcp open  https\n\nNmap done: 1 IP address (1 host up) scanned in 4.21 seconds",
                            4.21)
    
    logger.log_agent_communication("Network_Analysis_Agent", "WebApp_Analysis_Agent", "handoff",
                                 "Found web services on ports 80 and 443. Please analyze the web application.")
    
    logger.log_message("WebApp_Analysis_Agent", "Starting web application analysis for example.com", "status_update")
    
    logger.log_tool_execution("WebApp_Analysis_Agent", "httpx_tool",
                            {"target": "https://example.com", "options": "BASIC_PROBE"},
                            "httpx output:\nURL: https://example.com\nStatus Code: 200\nTitle: Example Domain\nContent Type: text/html\nContent Length: 1256\nWeb Server: ECS (dcb/7F83)\nTechnologies: nginx\n\n📊 Summary:\nDomain 'example.com' appears to be a standard example website with minimal functionality.",
                            2.15)
    
    logger.log_agent_communication("WebApp_Analysis_Agent", "Report_Agent", "data_ready", 
                                 "Web analysis complete. Ready for report generation.")
    
    logger.log_message("Report_Agent", "Generating comprehensive security assessment report...", "task_execution")
    
    # End the session
    logger.log_session_end()
    
    print("✅ Enhanced logging demonstration completed!")
    print("📁 Check the reports/ directory for the detailed log file")

if __name__ == "__main__":
    demo_enhanced_logging()
