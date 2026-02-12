# Ocular-services
A set of MCP services focused on network and security scanning. Tested on ubuntu 24.04 and the provided docker image.

`python mcp/server.py` to start all services.

## Version Management

Update version across all project files:
```powershell
.\update-version.ps1 -Version "1.0.0"
```

This updates:
- `mcp/LLM_SERVICE_DOCUMENTATION.md` - Documentation version and date
- `mcp/llm_service_schema.json` - Schema version and last_updated
- `mcp/server.py` - FastMCP server version
- `VERSION` - Version file

## Docker

Build (with unit tests):
```
docker build -t ocular-services .
```

Build without running tests (skip test stage):
```
docker build --target production -t ocular-services .
```

Build and stop at test stage (to verify tests pass):
```
docker build --target test -t ocular-services-test .
```

Run (port 8999):
```
docker run --rm -p 8999:8999 ocular-services
```

Run with extra capabilities (may be required for `ping` and some `nmap` scan types):
```
docker run --rm -p 8999:8999 --cap-add=NET_RAW --cap-add=NET_ADMIN ocular-services
```

Compose:
```
docker compose up --build
```

Quick check:
```
curl http://localhost:8999/health
```


## Using the services
Using the above launch, services will be available on http://localhost:8999/mcp/

In LM Studio you can add the server to mcp.json:

```
{
  "mcpServers": {
    "ocular-services": {
      "url": "http://localhost:8999/mcp/",
      "timeout": 60000
    }
  }
}
```
Notes:
Timeout is in MS and is on the LM Studio (client side)


## Envionment Setup
git config --global push.autoSetupRemote true


Tested with venv environments:
```
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
```

Or in windows:
(Powershell does not like paths that start with a .)
```
python3 -m venv venv
.\venv\Scripts\Activate.ps1
```


Install Packages:
```
pip install -r requirements.txt
pip install --upgrade -r requirements.txt
```

## Implemented command line tools
(If running locally, the docker image has all dependencies built in)

These are not required to run the server, but individual tools return an error if the command is unavailable.

### APT/SNAP installs
```
sudo apt install nmap smbclient nikto masscan whois nbtscan
sudo snap install enum4linux
```

### HTTPX
#### Install Go if not already installed
```
sudo apt-get update
sudo apt-get install golang-go
```

#### Set up Go environment variables
```
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
source ~/.bashrc
```

#### Install httpx
```
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

### Install Ruby and WPscan
```
sudo apt install ruby-rubygems ruby-dev
sudo gem install wpscan
```

## Envionment Varables
These envionment variables can be used to customize some behaviours

MCP_TIMEOUT_SECONDS Default: 600
Note: This is the server HTTP level timeout, some tools have a seperate timeout