"""
Utility functions for MCP services.
This module provides shared utility functions for executing commands and processing results across multiple MCP services.
"""

from typing import Optional, List
import subprocess
from service_response import ServiceResponse
from fastmcp import Context


"""
Command Executor
Provides generic functions for executing external commands with real-time output processing.
"""
async def execute_command(
    cmd: str,
    response: ServiceResponse,
    ctx: Optional[Context] = None,
    timeout: int = 60,
    expected_lines: Optional[int] = 100
) -> ServiceResponse:
    """
    Execute a command with real-time output processing and progress reporting.
    
    Args:
        cmd: Command and arguments as a string (e.g., "ping -c 5 example.com")
        response: ServiceResponse object to populate with results
        ctx: Optional FastMCP Context for progress reporting
        timeout: Command timeout in seconds (default: 60)
        expected_lines: Optional expected number of output lines for progress calculation
        
    Returns:
        ServiceResponse object populated with command results
    """
    try:
        # Store the command
        response.raw_command = cmd
        
        print(f"running: {cmd}", flush=True)

        # Check if the command is available (use 'where' on Windows, 'which' on Unix)
        import platform
        which_cmd = "where" if platform.system() == "Windows" else "which"
        command_name = cmd.split()[0]  # Extract the command name from the full command string
        
        try:
            subprocess.run([which_cmd, command_name], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            response.add_error(f"{command_name} is not installed on the server", return_code=-1)
            return response
        
        # Execute command with Popen for real-time output processing
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Process stdout in real-time
        stdout_lines = []
        line_count = 0
        for line in process.stdout:
            line_count += 1
            
            # Report progress if context is available
            if ctx:
                try:
                    await ctx.report_progress(
                        progress=line_count,
                        total=expected_lines,
                        message=line.strip()
                    )
                except Exception as progress_error:
                    # Log but don't fail if progress reporting fails
                    print(f"Progress reporting failed: {progress_error}", flush=True)
            
            stdout_lines.append(line)
        
        # Wait for process to complete and get stderr
        stderr_output = process.stderr.read()
        return_code = process.wait(timeout=timeout)
        
        # Populate response
        response.raw_output = "".join(stdout_lines)
        response.raw_error = stderr_output if stderr_output else ""
        response.return_code = return_code
        response.end_process_timer()
        
        return response
        
    except subprocess.TimeoutExpired:
        process.kill()
        response.add_error(f"Command timed out after {timeout} seconds", return_code=124)
        return response
        
    except Exception as e:
        response.add_error(str(e))
        return response
