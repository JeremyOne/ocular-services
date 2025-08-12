import subprocess
from . import util
from .enums import NbtscanOptions
from typing import Optional

def nbtscan_scan(target: str, options: Optional[NbtscanOptions] = None) -> str:
    """
    Runs nbtscan on the given target.
    Args:
        target (str): The IP address or subnet to scan.
        options (Optional[NbtscanOptions]): Nbtscan options enum (optional).
    Returns:
        str: The output of the nbtscan command.
    """
    util.log_text(f"nbtscan_scan called with target: '{target}', options: '{options.value if options else 'None'}'")
    try:
        cmd = ["nbtscan"]
        if options:
            cmd += options.value.split()
        cmd += [target]
        
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