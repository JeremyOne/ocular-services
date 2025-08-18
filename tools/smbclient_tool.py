import subprocess
from . import util
from .enums import SmbClientOptions

def smbclient_scan(target: str, options: SmbClientOptions = SmbClientOptions.LIST_SHARES) -> str:
    """
    Runs smbclient to interact with SMB/CIFS shares on the given target.
    Args:
        target (str): The IP address or hostname to scan.
        options (SmbClientOptions): Smbclient options enum (default: SmbClientOptions.LIST_SHARES).
    Returns:
        str: The output of the smbclient command.
    """
    util.log_text(f"smbclient_scan called with target: '{target}', options: '{options.value}'")
    try:
        cmd = ["smbclient"] + options.value.split() + [target]
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
