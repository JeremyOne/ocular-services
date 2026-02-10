# Ocular Services (FastMCP) - container image
# Runs the unified server in mcp/allservices.py on port 8999

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Optional: pin httpx binary version (ProjectDiscovery)
ARG HTTPX_VERSION=1.6.10

WORKDIR /app

# System tools used by the MCP services
# - ping_service: iputils-ping
# - curl_service: curl
# - whois_service: whois
# - nbtscan_service: nbtscan
# - nmap_service: nmap
# - nikto_service: nikto
# - enum4linux_service: enum4linux + smbclient
# - wpscan_service: ruby + wpscan gem
# - httpx_service: httpx binary

RUN echo "deb http://deb.debian.org/debian stable main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security stable-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list

RUN cat /etc/apt/sources.list

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      iputils-ping \
      whois \
      nbtscan \
      nmap \
      smbclient \
      ruby \
      ruby-dev \
      build-essential \
      unzip \
      libcurl4-openssl-dev \
      libxml2-dev \
      libxslt1-dev \
      zlib1g-dev \ 
      nikto

#RUN apt-get install -y enum4linux

# Clean up apt cache to reduce image size
RUN rm -rf /var/lib/apt/lists/*

# Install WPScan (with Ruby gem)
RUN gem install wpscan --no-document

# Install ProjectDiscovery httpx (prebuilt binary)
RUN curl -fsSL -o /tmp/httpx.zip \
      "https://github.com/projectdiscovery/httpx/releases/download/v${HTTPX_VERSION}/httpx_${HTTPX_VERSION}_linux_amd64.zip" \
 && unzip -o /tmp/httpx.zip -d /usr/local/bin \
 && chmod +x /usr/local/bin/httpx \
 && rm -f /tmp/httpx.zip

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY mcp ./mcp

EXPOSE 8999

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
     CMD curl -fsS http://localhost:8999/health || exit 1

# server.py uses local imports (ping_service, etc.), so run from mcp/
WORKDIR /app/mcp
#CMD ["fastmcp", "run", "/app/mcp/fastmcp.json", "--skip-env"]
CMD ["python", "server.py"]
