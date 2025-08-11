import subprocess
from . import util

def enum4linux_scan(target: str, options: str = "-a") -> str:
    """
    Runs enum4linux on the given target to enumerate SMB/CIFS information.
    Args:
        target (str): The IP address or hostname to scan.
        options (str): Additional enum4linux options (default: "-a" for all enumeration).
    Returns:
        str: The output of the enum4linux command.
    """
    util.log_text(f"enum4linux_scan called with target={target}, options={options}")
    try:
        cmd = ["enum4linux"] + options.split() + [target]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60  # enum4linux can take a while
        )
        output = result.stdout + "\n" + result.stderr
        return output
    except Exception as e:
        return f"Error running enum4linux: {e}"
