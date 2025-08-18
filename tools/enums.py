from enum import Enum

class NmapOptions(Enum):
    FAST_SCAN = ("-FPn", "Fast scan of top 100 ports (cheap operation)")
    SERVICE_VERSION_TOP_PORTS = ("-sV --top-ports 20", "Scan top 20 ports with service version detection (cheap operation)")
    STEALTH_NO_PING = ("-sS -Pn", "Stealth SYN scan without pinging the host (cheap operation)")
    RDP_VULN_SCAN = ("-p 3389 --script rdp-*", "Scan for RDP vulnerabilities on port 3389")
    AGGRESSIVE_OS_DETECTION = ("-A -T4", "Aggressive scan with OS detection and timing (expensive operation)")
    UDP_SCAN = ("-sU", "UDP port scan (expensive operation)")
    CVE_VULN_SCAN = ("-Pn --script vuln", "Scan for CVE vulnerabilities (expensive operation)")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class CurlOptions(Enum):
    HEADERS_ONLY = ("-I", "Fetch HTTP headers only")
    FOLLOW_REDIRECTS = ("-L", "Follow HTTP redirects")
    VERBOSE = ("-v", "Verbose output showing request/response details")
    HTTP2_TEST = ("--http2", "Test HTTP/2 support")
    TRACE_ASCII = ("--trace-ascii", "Detailed trace output to file")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class NbtScanOptions(Enum):
    RANGE_SCAN = ("-r", "Scan a range of IP addresses (e.g., 192.168.1.1-254)")
    SUBNET_SCAN = ("-s", "Scan a specific subnet (e.g., 192.168.1.0/24)")
    VERBOSE = ("-v", "Verbose output with detailed information")
    DOMAIN_INFO = ("-d", "Include domain information in results")
    SKIP_NETBIOS_RESOLUTION = ("-n", "Skip NetBIOS name resolution")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class Enum4linuxOptions(Enum):
    ALL_ENUMERATION = ("-a", "Perform all enumeration types")
    GET_USERLIST = ("-U", "Get list of users")
    GET_MACHINE_LIST = ("-M", "Get list of machines")
    GET_SHARELIST = ("-S", "Get list of shares")
    GET_PASSWORD_POLICY = ("-P", "Get password policy information")
    GET_GROUP_LIST = ("-G", "Get group and member list")
    DETAILED = ("-d", "Be detailed in output")
    SPECIFY_CREDENTIALS = ("-u user -p pass", "Specify username and password credentials")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class NiktoOptions(Enum):
    HOST_SCAN = ("-h", "Perform host scan (default)")
    SPECIFY_PORTS = ("-p", "Specify ports to scan (e.g., -p 80,443)")
    FORCE_SSL = ("-ssl", "Force SSL mode")
    DISABLE_SSL = ("-nossl", "Disable SSL")
    CHECK_ALL_CGI = ("-C all", "Check all CGI directories")
    INTERESTING_FILES = ("-Tuning 1", "Look for interesting files")
    MISCONFIGURATION = ("-Tuning 2", "Look for misconfigurations")
    INFO_DISCLOSURE = ("-Tuning 3", "Look for information disclosure")
    HTML_FORMAT = ("-Format htm", "Output results in HTML format")
    OUTPUT_TO_FILE = ("-o", "Save output to file")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class SmbClientOptions(Enum):
    LIST_SHARES = ("-L", "List available shares")
    NULL_SESSION = ("-N", "Use null session (no password)")
    SPECIFY_USERNAME = ("-U", "Specify username")
    SPECIFY_WORKGROUP = ("-W", "Specify workgroup/domain")
    EXECUTE_COMMAND = ("-c", "Execute specific commands")
    FORCE_SMB2 = ("-m SMB2", "Force SMB2 protocol")
    FORCE_SMB3 = ("-m SMB3", "Force SMB3 protocol")
    CONNECT_TO_SHARE = ("//", "Connect to specific share")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class PingOptions(Enum):
    DEFAULT_COUNT = ("4", "Default ping count")
    LOW_COUNT = ("2", "Low ping count for quick tests")
    HIGH_COUNT = ("10", "High ping count for thorough tests")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class DnsRecordTypes(Enum):
    A_RECORD = ("A", "IPv4 address records")
    TXT_RECORD = ("TXT", "Text records (often used for SPF, DKIM)")
    MX_RECORD = ("MX", "Mail exchange records")
    CNAME_RECORD = ("CNAME", "Canonical name records")
    NS_RECORD = ("NS", "Name server records")
    PTR_RECORD = ("PTR", "Pointer records (reverse DNS)")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj


class MasscanOptions(Enum):
    TOP_1000_PORTS = ("--top-ports 1000 --rate 1000", "Scans top 1000 ports at 1000 packets/sec")
    TOP_100_PORTS = ("--top-ports 100 --rate 1000", "Scans top 100 ports at 1000 packets/sec") 
    VERY_FAST_SCAN = ("--top-ports 100 --rate 10000", "Scans top 100 ports at 10000 packets/sec (very fast)")
    FULL_PORT_SCAN = ("-p 1-65535 --rate 1000", "Scans all 65535 ports at 1000 packets/sec (slow but comprehensive)")
    LITE_SCAN = ("-p 22,80,443,445,3389,8080 --rate 1000", "Scans only common ports (22,80,443,445,3389,8080) at 1000 packets/sec")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj


class HttpxOptions(Enum):
    BASIC_PROBE = ("-status-code -title -tech-detect", "Basic probe with status code, title and technology detection")
    HEADERS_ONLY = ("-status-code -headers -web -no-color -silent", "Returns only headers with status code")
    DETAILED_SCAN = ("-status-code -title -tech-detect -content-length -web-server -method -ip -cname -cdn -ports 80,443,8080,8443", "Detailed scan with multiple data points")
    VULNERABILITY_SCAN = ("-status-code -title -tech-detect -path '/robots.txt,/.git/HEAD,/.env,/wp-login.php,/admin/' -web -no-color", "Scan for common vulnerabilities and paths")
    #SCREENSHOT = ("-status-code -title -tech-detect -screenshot -silent", "Take screenshots of websites (requires Chrome/Chromium)")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj


class WpScanOptions(Enum):
    BASIC_SCAN = ("--enumerate p,t,u --plugins-detection mixed", "Basic scan for plugins, themes, and users with mixed detection")
    PLUGIN_ENUM = ("--enumerate p --plugins-detection aggressive", "Aggressive plugin enumeration")
    THEME_ENUM = ("--enumerate t --themes-detection aggressive", "Aggressive theme enumeration")
    USER_ENUM = ("--enumerate u", "User enumeration only")
    VULN_SCAN = ("--enumerate vp,vt --plugins-detection aggressive", "Scan for vulnerable plugins and themes")
    FULL_SCAN = ("--enumerate ap,at,tt,cb,dbe,u,m --plugins-detection aggressive", "Full comprehensive scan (slow but thorough)")
    PASSIVE_SCAN = ("--enumerate p,t,u --plugins-detection passive", "Passive scan (less likely to be detected)")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class WhoisOptions(Enum):
    BASIC_WHOIS = ("", "Basic WHOIS lookup with all information")
    REGISTRAR_INFO = ("-R", "Show registrar information only")
    ADMIN_CONTACT = ("-a", "Show administrative contact information")
    TECH_CONTACT = ("-t", "Show technical contact information")
    FULL_DETAILS = ("-H", "Hide legal disclaimers, show full details")
    
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
