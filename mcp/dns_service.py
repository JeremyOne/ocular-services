from typing import Optional, List
import dns.resolver
import dns.exception
from service_response import ServiceResponse

# DNS service for DNS record lookups and domain analysis
# Useful for reconnaissance, mail server discovery, and DNS enumeration


def get_service_info() -> dict:
    return {
        "name": "dns",
        "endpoint": "/dns",
        "methods": ["GET", "POST"],
        "description": "Perform DNS lookups for various record types",
        "parameters": {
            "host": "Target hostname (required)",
            "record_types": "Comma-separated list of DNS record types (default: A,MX,TXT)"
        }
    }

def dns_lookup_mcp(host: str, record_types: List[str], resolver=None) -> dict:
    """Perform DNS lookup for specified record types"""
    result = {}
    
    # Use provided resolver or default
    if resolver is None:
        resolver = dns.resolver
    
    for record_type in record_types:
        try:
            if record_type == "A":
                # Lookup A records (IP addresses)
                answers = resolver.resolve(host, 'A')
                result["a_records"] = [rdata.address for rdata in answers]
                # Keep legacy format for compatibility
                result["ip_addresses"] = result["a_records"]
                
            elif record_type == "TXT":
                # Lookup TXT records and search for email host (e.g., via SPF)
                txt_answers = resolver.resolve(host, 'TXT')
                txt_records = []
                for rdata in txt_answers:
                    if hasattr(rdata, 'strings'):
                        txt_record = b''.join(rdata.strings).decode('utf-8')
                    else:
                        txt_record = str(rdata)
                    txt_records.append(txt_record)
                    
                    # Extract SPF information for legacy compatibility
                    if "v=spf1" in txt_record and "email_host" not in result:
                        parts = txt_record.split()
                        for part in parts:
                            if part.startswith("include:"):
                                result["email_host"] = part.split(":", 1)[1]
                                break
                
                result["txt_records"] = txt_records
                
            elif record_type == "MX":
                # Lookup MX records (mail servers)
                mx_answers = resolver.resolve(host, 'MX')
                result["mx_records"] = [f"{rdata.preference} {rdata.exchange}" for rdata in mx_answers]
                
            elif record_type == "CNAME":
                # Lookup CNAME records
                cname_answers = resolver.resolve(host, 'CNAME')
                result["cname_records"] = [str(rdata) for rdata in cname_answers]
                
            elif record_type == "NS":
                # Lookup NS records (name servers)
                ns_answers = resolver.resolve(host, 'NS')
                result["ns_records"] = [str(rdata) for rdata in ns_answers]
                
            elif record_type == "PTR":
                # Lookup PTR records (reverse DNS)
                ptr_answers = resolver.resolve(host, 'PTR')
                result["ptr_records"] = [str(rdata) for rdata in ptr_answers]
                
            else:
                # Handle other record types generically
                try:
                    answers = resolver.resolve(host, record_type)
                    result[f"{record_type.lower()}_records"] = [str(rdata) for rdata in answers]
                except Exception:
                    result[f"{record_type.lower()}_records"] = []
                    
        except dns.resolver.NXDOMAIN:
            result[f"{record_type.lower()}_records"] = []
        except dns.resolver.NoAnswer:
            result[f"{record_type.lower()}_records"] = []
        except Exception as e:
            result[f"{record_type.lower()}_records"] = []
            result[f"{record_type.lower()}_error"] = str(e)
    
    return result

async def dns_lookup(host: str, record_types: Optional[str] = "A,TXT", timeout: Optional[float] = 5, asJson: Optional[bool] = True) -> ServiceResponse:
    """Perform DNS lookups for various record types.
        host: The hostname or domain to look up (required)
        record_types: Comma-separated list of DNS record types (default: A,TXT)
        timeout: DNS query timeout in seconds (default: 5)
    Returns:
        ServiceResponse with DNS information
    """

    # Parse record types
    if isinstance(record_types, str):
        record_types_list = [rt.strip().upper() for rt in record_types.split(",")]
    else:
        record_types_list = record_types
    
    # Initialize ServiceResponse
    response = ServiceResponse(
        service="dns",
        target=host,
        arguments={
            "host": host,
            "record_types": record_types_list,
            "timeout": timeout
        }
    )
    
    try:
        
        # Validate parameters
        if not host:
            response.add_error("host parameter is required")
            return response
        
        if timeout < 1:
            response.add_error("timeout must be at least 1 second")
            return response
        
        if timeout > 30:
            response.add_error("timeout cannot exceed 30 seconds")
            return response
        
        # Configure DNS resolver with timeout
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        # Perform DNS lookup
        lookup_results = dns_lookup_mcp(host, record_types_list, resolver)
        
        # Create raw output summary
        raw_output_lines = []
        for record_type in record_types_list:
            record_key = f"{record_type.lower()}_records"
            if record_key in lookup_results and lookup_results[record_key]:
                raw_output_lines.append(f"{record_type} records for {host}:")
                for record in lookup_results[record_key]:
                    raw_output_lines.append(f"  {record}")
            else:
                raw_output_lines.append(f"{record_type} records for {host}: No records found")
        
        raw_output = "\n".join(raw_output_lines)
        
        response.raw_output = raw_output
        response.raw_command = f"dns.resolver.resolve({host}, types={record_types_list})"
        response.return_code = 0
        response.end_process_timer()
        
        return response
        
    except Exception as e:
        
        response.raw_error = str(e)
        response.return_code = None
        response.end_process_timer()
        return response
