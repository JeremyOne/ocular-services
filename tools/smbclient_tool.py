import subprocess
from . import util

def smbclient_scan(target: str, options: str = "-L") -> str:
    """
    Runs smbclient to interact with SMB/CIFS shares on the given target.
    Args:
        target (str): The IP address or hostname to scan.
        options (str): Additional smbclient options (default: "-L" to list shares).
    Returns:
        str: The output of the smbclient command.
    """
    util.log_text(f"smbclient_scan called with target: '{target}', options: '{options}'")
    try:
        cmd = ["smbclient"] + options.split() + [target]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            input="\n"  # Send newline for password prompt if no password specified
        )
        output = result.stdout + "\n" + result.stderr
        return output
    except Exception as e:
        return f"Error running smbclient: {e}"
