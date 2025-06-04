import subprocess
# ...existing code...

def nmap_scan(target: str, options: str = "-F", timeout: int = 240) -> str:
    """
    Runs an nmap scan on the given target.
    Args:
        target (str): The host or network to scan.
        options (str): Additional nmap options (default: "-F" for fast scan).
            --top-ports 20
            -A -T4
        timeout (int): Timeout for the nmap command in seconds (default: 30).
    Returns:
        str: The output of the nmap command.
    """
    try:
        result = subprocess.run(
            ["nmap"] + options.split() + [target],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"nmap failed: {result.stderr}"
    except Exception as e:
        return f"Error running nmap: {e}"