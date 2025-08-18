import subprocess
from . import util
from .enums import CurlOptions


def curl_test(url: str, options: CurlOptions = CurlOptions.HEADERS_ONLY) -> str:
    """
    Uses curl to get HTTP information relevant to penetration testing and HTTP discovery.
    Args:
        url (str): The target URL.
        options (CurlOptions): Curl options enum (default: CurlOptions.HEADERS_ONLY).
    Returns:
        str: The output of the curl command.
    """
    try:
        util.log_text(f"Running curl with options: '{options.name}:{options.value}' on URL: '{url}'")

        result = subprocess.run(
            ["curl"] + options.value.split() + [url],
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
