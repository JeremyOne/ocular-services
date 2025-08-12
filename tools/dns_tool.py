import dns.resolver
from . import util
from .enums import DnsRecordTypes
from typing import Optional, List

def dns_lookup(host: str, record_types: Optional[List[DnsRecordTypes]] = None) -> dict:
    """
    Looks up DNS records for a host.
    Args:
        host (str): The hostname to look up.
        record_types (Optional[List[DnsRecordTypes]]): List of DNS record types to query (default: A and TXT).
    Returns:
        dict: Contains DNS query results with record types as keys.
    """
    if record_types is None:
        record_types = [DnsRecordTypes.A_RECORD, DnsRecordTypes.TXT_RECORD]
    
    result = {"ip_addresses": [], "email_host": None}
    
    util.log_text(f"Performing DNS lookup for host: '{host}' with record types: {[rt.value for rt in record_types]}")
    
    for record_type in record_types:
        try:
            if record_type.value == "A":
                # Lookup A records (IP addresses)
                answers = dns.resolver.resolve(host, 'A')
                result["ip_addresses"] = [rdata.address for rdata in answers]
            elif record_type.value == "TXT":
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
            else:
                # Handle other record types
                try:
                    answers = dns.resolver.resolve(host, record_type.value)
                    result[f"{record_type.value.lower()}_records"] = [str(rdata) for rdata in answers]
                except Exception:
                    result[f"{record_type.value.lower()}_records"] = []
        except Exception as e:
            util.log_text(f"Error querying {record_type.value} record for {host}: {e}")

    util.log_text(f"DNS lookup result for '{host}': {result} \n------\n")
    return result