import subprocess
from . import util

def nbtscan_scan(target: str, options: str = "") -> str:
    """
    Runs nbtscan on the given target.
    Args:
        target (str): The IP address or subnet to scan.
        options (str): Additional nbtscan options (optional).
    Returns:
        str: The output of the nbtscan command.
    """
    util.log_text(f"nbtscan_scan called with target={target}, options={options}")
    try:
        cmd = ["nbtscan"] + options.split() + [target]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )
        output = result.stdout + "\n" + result.stderr
        return output
    except Exception as e:
        return f"Error running nbtscan: {e}"