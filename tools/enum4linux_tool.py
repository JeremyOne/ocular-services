import subprocess
from . import util
from .enums import Enum4linuxOptions

def enum4linux_scan(target: str, options: Enum4linuxOptions = Enum4linuxOptions.ALL_ENUMERATION) -> str:
    """
    Runs enum4linux on the given target to enumerate SMB/CIFS information.
    Args:
        target (str): The IP address or hostname to scan.
        options (Enum4linuxOptions): Enum4linux options enum (default: Enum4linuxOptions.ALL_ENUMERATION).
    Returns:
        str: The output of the enum4linux command.
    """
    util.log_text(f"enum4linux_scan called with target: '{target}', options: '{options.value}'")
    try:
        cmd = ["enum4linux"] + options.value.split() + [target]
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
