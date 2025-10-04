#!/usr/bin/env python3
"""
Quick service status checker for MCP services
"""

import requests
import json
import sys

def check_service_status(host="localhost", port=8999):
    """Quick check of all MCP services"""
    base_url = f"http://{host}:{port}"
    
    print(f"🔍 Checking MCP services at {base_url}")
    print("="*50)
    
    try:
        # Check if server is running
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not healthy")
            return False
        
        print("✅ Server is healthy")
        
        # Get service list
        response = requests.get(f"{base_url}/services", timeout=5)
        if response.status_code != 200:
            print("❌ Cannot get service list")
            return False
        
        services_data = response.json()
        services = services_data.get("services", [])
        
        print(f"📊 Found {len(services)} services:")
        
        for service in services:
            name = service.get("name", "unknown")
            endpoint = service.get("endpoint", "unknown")
            description = service.get("description", "No description")
            methods = ", ".join(service.get("methods", []))
            
            print(f"  🔧 {name}")
            print(f"     Endpoint: {endpoint}")
            print(f"     Methods: {methods}")
            print(f"     Description: {description}")
            print()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("💡 Make sure the MCP server is running:")
        print("   cd /home/jp/Documents/ocular_agents/mcp")
        print("   /home/jp/Documents/ocular_agents/.venv/bin/python allservices.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python quick_status.py [host] [port]")
            print("Default: localhost 8999")
            return
        
        host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8999
    else:
        host = "localhost"
        port = 8999
    
    success = check_service_status(host, port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
