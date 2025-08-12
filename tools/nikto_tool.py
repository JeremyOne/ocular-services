import subprocess
from . import util
from .enums import NiktoOptions

def nikto_scan(target: str, options: NiktoOptions = NiktoOptions.HOST_SCAN) -> str:
    """
    Runs nikto web vulnerability scanner on the given target.
    Args:
        target (str): The URL or IP address to scan.
        options (NiktoOptions): Nikto options enum (default: NiktoOptions.HOST_SCAN).
    Returns:
        str: The output of the nikto command.
    """
    util.log_text(f"nikto_scan called with target: '{target}', options: '{options.value}'")
    try:
        cmd = ["nikto"] + options.value.split() + [target]
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
