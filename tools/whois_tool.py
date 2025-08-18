#!/usr/bin/env python3

import subprocess
import shlex
from enum import Enum
from typing import Union, Optional
import re
import datetime


class WhoisOptions(Enum):
    """Enum for whois options."""
    BASIC_WHOIS = ""
    REGISTRAR_INFO = "-R"
    ADMIN_CONTACT = "-a"
    TECH_CONTACT = "-t"
    FULL_DETAILS = "-H"
    
    def __init__(self, value):
        self.cmd_option = value
        if value == "":
            self.description = "Basic WHOIS lookup with all information"
        elif value == "-R":
            self.description = "Show registrar information only"
        elif value == "-a":
            self.description = "Show administrative contact information"
        elif value == "-t":
            self.description = "Show technical contact information"
        elif value == "-H":
            self.description = "Hide legal disclaimers, show full details"


def whois_lookup(domain: str, options: Optional[Union[WhoisOptions, str]] = WhoisOptions.BASIC_WHOIS) -> str:
    """
    Perform WHOIS lookup on a domain to get registration information.
    
    Args:
        domain: Domain name to lookup (e.g., example.com)
        options: WhoisOptions enum for lookup options
        
    Returns:
        str: Formatted WHOIS information with key details extracted
    """
    # Check if whois is installed
    try:
        subprocess.run(["which", "whois"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return "Error: whois is not installed. Please install it with 'sudo apt-get install whois'"
    
    # Clean domain input - remove protocol and path if present
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0].strip()
    
    # Convert option enum to string if it's an enum
    if isinstance(options, WhoisOptions):
        options_str = options.cmd_option
    else:
        options_str = options or ""
    
    try:
        # Build the command
        if options_str:
            cmd = f"whois {options_str} {domain}"
        else:
            cmd = f"whois {domain}"
        
        print(f"Running whois lookup on domain: '{domain}'")
        
        # Run whois
        process = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=30  # 30-second timeout
        )
        
        if process.returncode == 0:
            output = parse_whois_output(process.stdout, domain)
            return f"WHOIS lookup results:\n{output}\n \n------\n"
        else:
            stderr = process.stderr if process.stderr else "No error output"
            return f"Error running whois on {domain}: {stderr}\n \n------\n"
            
    except subprocess.TimeoutExpired:
        return f"Error: whois lookup for {domain} timed out after 30 seconds."
    except subprocess.CalledProcessError as e:
        return f"Error running whois: {e.stderr}\n \n------\n"
    except Exception as e:
        return f"Error: {str(e)}\n \n------\n"


def parse_whois_output(whois_text: str, domain: str) -> str:
    """Parse and format WHOIS output to extract key information."""
    
    lines = whois_text.split('\n')
    formatted_output = f"Domain: {domain.upper()}\n"
    formatted_output += "=" * 60 + "\n\n"
    
    # Key information to extract
    registrar = None
    registrant_name = None
    registrant_org = None
    creation_date = None
    expiration_date = None
    updated_date = None
    name_servers = []
    status = []
    admin_email = None
    tech_email = None
    registrar_abuse_email = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('%') or line.startswith('#') or line.startswith('>>>') or line.startswith('NOTICE:'):
            continue
            
        # Make line lowercase for comparison but keep original for display
        line_lower = line.lower()
        
        # Extract key information - handle various WHOIS formats
        if any(pattern in line_lower for pattern in ['registrar:', 'registrar organization:', 'sponsoring registrar:']):
            registrar = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['registrant name:', 'registrant:', 'name:']):
            if not registrant_name:  # Take first occurrence
                registrant_name = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['registrant organization:', 'registrant org:', 'organization:']):
            registrant_org = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['creation date:', 'created:', 'created on:', 'domain registration date:']):
            creation_date = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['expir', 'registry expiry date:', 'expires:', 'expiration date:']):
            if 'date' in line_lower:
                expiration_date = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['updated date:', 'last updated:', 'modified:']):
            updated_date = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['name server:', 'nserver:', 'nameserver:']):
            ns = extract_value_after_colon(line)
            if ns and ns not in name_servers:
                name_servers.append(ns)
        elif 'status:' in line_lower:
            status_val = extract_value_after_colon(line)
            if status_val:
                status.append(status_val)
        elif any(pattern in line_lower for pattern in ['admin email:', 'administrative contact email:']):
            admin_email = extract_value_after_colon(line)
        elif any(pattern in line_lower for pattern in ['tech email:', 'technical contact email:']):
            tech_email = extract_value_after_colon(line)
        elif 'registrar abuse contact email:' in line_lower:
            registrar_abuse_email = extract_value_after_colon(line)
    
    # Format the key information in a structured way
    if registrar:
        formatted_output += f"📋 Registrar: {registrar}\n"
    
    if registrant_name:
        formatted_output += f"👤 Registrant Name: {registrant_name}\n"
    
    if registrant_org:
        formatted_output += f"🏢 Registrant Organization: {registrant_org}\n"
    
    if creation_date:
        formatted_output += f"📅 Created: {creation_date}\n"
    
    if updated_date:
        formatted_output += f"🔄 Updated: {updated_date}\n"
        
    if expiration_date:
        formatted_output += f"⏰ Expires: {expiration_date}\n"
    
    if status:
        formatted_output += f"🔒 Status: {', '.join(status[:2])}\n"  # Show first 2 statuses
    
    if registrar_abuse_email:
        formatted_output += f"📧 Abuse Contact: {registrar_abuse_email}\n"
    
    if name_servers:
        formatted_output += f"\n🌐 Name Servers ({len(name_servers)}):\n"
        for ns in name_servers[:4]:  # Show first 4 name servers
            formatted_output += f"  • {ns}\n"
        if len(name_servers) > 4:
            formatted_output += f"  ... and {len(name_servers) - 4} more\n"
    
    # Add summary section
    formatted_output += f"\n📊 Summary:\n"
    formatted_output += f"Domain '{domain}' is "
    if registrar:
        formatted_output += f"registered with {registrar}"
    if registrant_name and registrant_name != registrar:
        formatted_output += f" by {registrant_name}"
    elif registrant_org:
        formatted_output += f" by {registrant_org}"
    
    if creation_date:
        try:
            # Try to parse the date to calculate age
            date_formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d', '%d-%b-%Y', '%Y-%m-%d %H:%M:%S']
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(creation_date.split(' ')[0], fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                age = datetime.datetime.now() - parsed_date
                years = age.days // 365
                if years > 0:
                    formatted_output += f". Domain is {years} years old"
        except:
            pass
    
    formatted_output += ".\n"
    
    # Add raw output section (truncated)
    formatted_output += f"\n📄 Raw WHOIS Data (first 20 lines):\n"
    formatted_output += "-" * 40 + "\n"
    raw_lines = [line for line in whois_text.split('\n') if line.strip() and not line.strip().startswith('%')]
    for line in raw_lines[:20]:
        formatted_output += f"{line}\n"
    if len(raw_lines) > 20:
        formatted_output += f"... ({len(raw_lines) - 20} more lines)\n"
    
    return formatted_output


def extract_value_after_colon(line: str) -> str:
    """Extract the value after the first colon in a line."""
    if ':' in line:
        value = line.split(':', 1)[1].strip()
        # Remove URLs and extra info in parentheses for cleaner output
        value = re.sub(r'\s+https?://[^\s]+', '', value)
        value = re.sub(r'\s+\([^)]*\)', '', value)
        return value.strip()
    return ""
