import subprocess
from . import util


def curl_test(url: str, options: str = "-I") -> str:
    """
    Uses curl to get HTTP information relevant to penetration testing and HTTP discovery.
    Args:
        url (str): The target URL.
        options (str): Additional curl options (default: '-I' for HTTP headers only).
    Returns:
        str: The output of the curl command.
    """
    try:
        # Common options for penetration testing:
        # -I: Fetch headers only
        # -L: Follow redirects
        # -v: Verbose output (shows request/response)
        # --http2: Test HTTP/2 support
        # --trace-ascii: Detailed trace
        util.log_text(f"Running curl with options: '{options}' on URL: '{url}'")

        result = subprocess.run(
            ["curl"] + options.split() + [url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )
        output = result.stdout + "\n" + result.stderr

        util.log_text(f"Curl output: {output} \n------\n")

        return output
    except Exception as e:
        return f"Error running curl: {e}"
