import subprocess
from . import util
from .enums import PingOptions

def ping_host(host: str, count: PingOptions = PingOptions.DEFAULT_COUNT) -> str:
    """
    Pings a host and returns the output.
    Args:
        host (str): The hostname or IP address to ping.
        count (PingOptions): Number of echo requests to send.
    Returns:
        str: The output of the ping command.
    """
    try:
        count_value = int(count.value)
            
        util.log_text(f"Pinging host: '{host}' with count: {count_value}")
        result = subprocess.run(
            ["ping", "-c", str(count_value), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            util.log_text(f"Ping output: {result.stdout} \n------\n")
            return result.stdout
        else:
            util.log_text(f"Ping failed: {result.stderr} \n------\n")
            return f"Ping failed: {result.stderr}"
    except Exception as e:
        util.log_text(f"Error running ping: {e}")
        return f"Error running ping: {e}"
