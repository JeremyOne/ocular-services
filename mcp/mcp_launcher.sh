#!/bin/bash

# MCP Services Launcher and Tester
# Provides easy commands to manage and test the MCP services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="../.venv/bin/python"
SERVER_PORT=8999

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo "MCP Services Launcher and Tester"
    echo "================================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the MCP unified server"
    echo "  stop      - Stop all MCP services"
    echo "  restart   - Restart the MCP unified server"
    echo "  status    - Check service status"
    echo "  test      - Run comprehensive test suite"
    echo "  quick     - Quick status check"
    echo "  logs      - Show server logs (if running in background)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start server in background"
    echo "  $0 test           # Run all tests"
    echo "  $0 status         # Check if services are running"
}

start_server() {
    echo -e "${BLUE}🚀 Starting MCP unified server...${NC}"
    
    # Kill any existing processes
    pkill -f "allservices.py" 2>/dev/null
    sleep 2
    
    # Start server in background
    cd "$SCRIPT_DIR"
    nohup $PYTHON_PATH allservices.py > mcp_server.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:$SERVER_PORT/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Server started successfully on port $SERVER_PORT${NC}"
            echo -e "${GREEN}📝 Server PID: $SERVER_PID${NC}"
            echo -e "${GREEN}📊 Logs: $SCRIPT_DIR/mcp_server.log${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Server failed to start within 30 seconds${NC}"
    return 1
}

stop_server() {
    echo -e "${BLUE}🛑 Stopping MCP services...${NC}"
    
    # Kill all MCP service processes
    pkill -f "allservices.py"
    pkill -f ".*_service.py"
    
    sleep 2
    
    # Check if any are still running
    if pgrep -f ".*service.py" >/dev/null; then
        echo -e "${YELLOW}⚠️  Force killing remaining processes...${NC}"
        pkill -9 -f ".*service.py"
    fi
    
    echo -e "${GREEN}✅ Services stopped${NC}"
}

check_status() {
    echo -e "${BLUE}🔍 Checking service status...${NC}"
    cd "$SCRIPT_DIR"
    $PYTHON_PATH quick_status.py
}

run_tests() {
    echo -e "${BLUE}🧪 Running comprehensive test suite...${NC}"
    cd "$SCRIPT_DIR"
    $PYTHON_PATH test_all_services.py
}

show_logs() {
    if [ -f "$SCRIPT_DIR/mcp_server.log" ]; then
        echo -e "${BLUE}📋 Server logs:${NC}"
        tail -f "$SCRIPT_DIR/mcp_server.log"
    else
        echo -e "${YELLOW}⚠️  No log file found${NC}"
    fi
}

restart_server() {
    stop_server
    sleep 2
    start_server
}

# Main command processing
case "${1:-help}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    test)
        run_tests
        ;;
    quick)
        check_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
