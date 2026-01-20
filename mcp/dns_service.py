from typing import Optional, List
import time
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

def dns_lookup_mcp(host: str, record_types: List[str]) -> dict:
    """Perform DNS lookup for specified record types"""
    result = {}
    
    for record_type in record_types:
        try:
            if record_type == "A":
                # Lookup A records (IP addresses)
                answers = dns.resolver.resolve(host, 'A')
                result["a_records"] = [rdata.address for rdata in answers]
                # Keep legacy format for compatibility
                result["ip_addresses"] = result["a_records"]
                
            elif record_type == "TXT":
                # Lookup TXT records and search for email host (e.g., via SPF)
                txt_answers = dns.resolver.resolve(host, 'TXT')
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
                mx_answers = dns.resolver.resolve(host, 'MX')
                result["mx_records"] = [f"{rdata.preference} {rdata.exchange}" for rdata in mx_answers]
                
            elif record_type == "CNAME":
                # Lookup CNAME records
                cname_answers = dns.resolver.resolve(host, 'CNAME')
                result["cname_records"] = [str(rdata) for rdata in cname_answers]
                
            elif record_type == "NS":
                # Lookup NS records (name servers)
                ns_answers = dns.resolver.resolve(host, 'NS')
                result["ns_records"] = [str(rdata) for rdata in ns_answers]
                
            elif record_type == "PTR":
                # Lookup PTR records (reverse DNS)
                ptr_answers = dns.resolver.resolve(host, 'PTR')
                result["ptr_records"] = [str(rdata) for rdata in ptr_answers]
                
            else:
                # Handle other record types generically
                try:
                    answers = dns.resolver.resolve(host, record_type)
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

async def dns_lookup(host: str, record_types: Optional[str] = "A,TXT", timeout: Optional[float] = 5, asJson: Optional[bool] = True) -> dict:
    """Perform DNS lookups for various record types.
        host: The hostname or domain to look up (required)
        record_types: Comma-separated list of DNS record types (default: A,TXT)
        timeout: DNS query timeout in seconds (default: 5)
    Returns:
        JSON response matching schema.json format with DNS information
    """
    start_time = time.time()
    
    try:
        # Get parameters from query string or JSON body
        if not host:
            return {"error": "host parameter is required"}
        
        # Parse record types
        if isinstance(record_types, str):
            record_types = [rt.strip().upper() for rt in record_types.split(",")]
        
        # Validate timeout
        if timeout < 1:
            return {"error": "timeout must be at least 1 second"}
        elif timeout > 30:
            return {"error": "timeout cannot exceed 30 seconds"}
        
        # Set DNS resolver timeout
        dns.resolver.default_resolver.timeout = timeout
        dns.resolver.default_resolver.lifetime = timeout
        
        # Perform DNS lookup
        lookup_results = dns_lookup_mcp(host, record_types)
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        # Create raw output summary
        raw_output_lines = []
        for record_type in record_types:
            record_key = f"{record_type.lower()}_records"
            if record_key in lookup_results and lookup_results[record_key]:
                raw_output_lines.append(f"{record_type} records for {host}:")
                for record in lookup_results[record_key]:
                    raw_output_lines.append(f"  {record}")
            else:
                raw_output_lines.append(f"{record_type} records for {host}: No records found")
        
        raw_output = "\n".join(raw_output_lines)
        
        # Format response according to schema.json
        response = ServiceResponse(
            service="dns",
            process_time_ms=process_time_ms,
            target=host,
            arguments={
                "record_types": record_types,
                "timeout": timeout
            },
            return_code=0,
            raw_output=raw_output,
            raw_error=""
        )
        
        return response
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = ServiceResponse(
            service="dns",
            process_time_ms=process_time_ms,
            target=host if 'host' in locals() else "unknown",
            arguments={
                "record_types": record_types if 'record_types' in locals() else ["A", "TXT"],
                "timeout": timeout if 'timeout_param' in locals() else 5
            },
            return_code=-1,
            raw_output="",
            raw_error=str(e)
        )
        
        return response
