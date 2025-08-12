import subprocess
from . import util

def nikto_scan(target: str, options: str = "-h") -> str:
    """
    Runs nikto web vulnerability scanner on the given target.
    Args:
        target (str): The URL or IP address to scan.
        options (str): Additional nikto options (default: "-h" for host scan).
    Returns:
        str: The output of the nikto command.
    """
    util.log_text(f"nikto_scan called with target: '{target}', options: '{options}'")
    try:
        cmd = ["nikto"] + options.split() + [target]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120  # nikto can take a while for thorough scans
        )
        output = result.stdout + "\n" + result.stderr
        return output
    except Exception as e:
        return f"Error running nikto: {e}"
