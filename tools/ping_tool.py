import subprocess
# ...existing code...

def ping_host(host: str, count: int = 4) -> str:
    """
    Pings a host and returns the output.
    Args:
        host (str): The hostname or IP address to ping.
        count (int): Number of echo requests to send.
    Returns:
        str: The output of the ping command.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Ping failed: {result.stderr}"
    except Exception as e:
        return f"Error running ping: {e}"


# ...existing code...