from typing import Optional, List
import time
import dns.resolver
import dns.exception
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# DNS service for DNS record lookups and domain analysis
# Useful for reconnaissance, mail server discovery, and DNS enumeration

# Create FastMCP server
mcp = FastMCP("DNS Service")

def parse_dns_output(host: str, record_types: List[str], results: dict) -> dict:
    """Parse DNS lookup results into structured format"""
    structured_result = {
        "host": host,
        "records": {},
        "summary": {
            "total_record_types": len(record_types),
            "successful_queries": 0,
            "failed_queries": 0,
            "has_ip_addresses": False,
            "has_mail_records": False,
            "has_txt_records": False
        }
    }
    
    for record_type in record_types:
        record_key = f"{record_type.lower()}_records"
        if record_key in results:
            structured_result["records"][record_type] = results[record_key]
            structured_result["summary"]["successful_queries"] += 1
            
            # Update summary flags
            if record_type == "A" and results[record_key]:
                structured_result["summary"]["has_ip_addresses"] = True
            elif record_type in ["MX", "SPF"] and results[record_key]:
                structured_result["summary"]["has_mail_records"] = True
            elif record_type == "TXT" and results[record_key]:
                structured_result["summary"]["has_txt_records"] = True
        else:
            structured_result["records"][record_type] = []
            structured_result["summary"]["failed_queries"] += 1
    
    # Handle legacy format from original tool
    if "ip_addresses" in results:
        structured_result["records"]["A"] = results["ip_addresses"]
        structured_result["summary"]["has_ip_addresses"] = bool(results["ip_addresses"])
    
    if "email_host" in results and results["email_host"]:
        if "SPF" not in structured_result["records"]:
            structured_result["records"]["SPF"] = []
        structured_result["records"]["SPF"].append(f"include:{results['email_host']}")
        structured_result["summary"]["has_mail_records"] = True
    
    return structured_result

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

@mcp.custom_route("/dns", methods=["GET", "POST"])
async def dns_lookup_service(request: Request) -> JSONResponse:
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
        if request.method == "GET":
            host = request.query_params.get("host")
            record_types_param = request.query_params.get("record_types", "A,TXT")
            timeout_param = float(request.query_params.get("timeout", 5))
        else:  # POST
            body = await request.json()
            host = body.get("host")
            record_types_param = body.get("record_types", "A,TXT")
            timeout_param = body.get("timeout", 5)
        
        if not host:
            return JSONResponse(
                {"error": "host parameter is required"}, 
                status_code=400
            )
        
        # Parse record types
        if isinstance(record_types_param, str):
            record_types = [rt.strip().upper() for rt in record_types_param.split(",")]
        else:
            record_types = record_types_param if record_types_param else ["A", "TXT"]
        
        # Validate timeout
        if timeout_param < 1:
            timeout_param = 1
        elif timeout_param > 30:
            timeout_param = 30
        
        # Set DNS resolver timeout
        dns.resolver.default_resolver.timeout = timeout_param
        dns.resolver.default_resolver.lifetime = timeout_param
        
        # Perform DNS lookup
        lookup_results = dns_lookup_mcp(host, record_types)
        
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        # Parse results into structured format
        structured_output = parse_dns_output(host, record_types, lookup_results)
        
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
        response = {
            "service": "dns",
            "process_time_ms": process_time_ms,
            "target": host,
            "arguments": {
                "record_types": record_types,
                "timeout": timeout_param
            },
            "return_code": 0,
            "raw_output": raw_output,
            "raw_error": "",
            "structured_output": structured_output
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        end_time = time.time()
        process_time_ms = int((end_time - start_time) * 1000)
        
        response = {
            "service": "dns",
            "process_time_ms": process_time_ms,
            "target": host if 'host' in locals() else "unknown",
            "arguments": {
                "record_types": record_types if 'record_types' in locals() else ["A", "TXT"],
                "timeout": timeout_param if 'timeout_param' in locals() else 5
            },
            "return_code": -1,
            "raw_output": "",
            "raw_error": str(e),
            "structured_output": {}
        }
        
        return JSONResponse(response, status_code=500)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    # mcp.run() # stdio
    mcp.run(transport="http", host="0.0.0.0", port=9004)
