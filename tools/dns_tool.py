import dns.resolver
from . import util

def dns_lookup(host: str) -> dict:
    """
    Looks up the A and TXT records for a host.
    Args:
        host (str): The hostname to look up.
    Returns:
        dict: Contains 'ip_addresses' (list of str) and 'email_host' (str or None).
    """
    result = {"ip_addresses": [], "email_host": None}
    try:
        util.log_text(f"Performing DNS lookup for host: '{host}'")
        # Lookup A records (IP addresses)
        answers = dns.resolver.resolve(host, 'A')
        result["ip_addresses"] = [rdata.address for rdata in answers]
    except Exception:
        result["ip_addresses"] = []

    try:
        # Lookup TXT records and search for email host (e.g., via SPF)
        txt_answers = dns.resolver.resolve(host, 'TXT')
        for rdata in txt_answers:
            txt_record = str(rdata.strings[0], 'utf-8') if hasattr(rdata, 'strings') else str(rdata)
            if "v=spf1" in txt_record:
                # Try to extract the mail host from the SPF record
                parts = txt_record.split()
                for part in parts:
                    if part.startswith("include:"):
                        result["email_host"] = part.split(":", 1)[1]
                        break
                if result["email_host"]:
                    break
    except Exception:
        result["email_host"] = None

    util.log_text(f"DNS lookup result for '{host}': {result} \n------\n")
    return result