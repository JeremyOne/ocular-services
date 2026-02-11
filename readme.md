# Ocular-services
A set of MCP services focused on network and security scanning. Tested on ubuntu 24.04 and the provided docker image.

`python mcp/server.py` to start all services.

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

Run unit tests via HTTP:
```
curl http://localhost:8999/test
```

## Using the services
Using the above launch, services will be available on http://localhost:8999/mcp/

In LM Studio you can add the server to mcp.json:

```
{
  "mcpServers": {
    "ocular-services": {
      "url": "http://localhost:8999/mcp/"
    }
  }
}
```

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

## Testing
Warning: the unit tests call actual commands and use networking including doing things like resolving dns, and curl on example.com and running nmap on localhost. 

Run unit tests:
```
python -m pytest tests/
```

Or run with unittest:
```
python tests/run_tests.py
```

Run specific test file:
```
python -m pytest tests/test_service_response.py
python -m pytest tests/test_ping_service.py -v
```

The test suite includes:
- `test_service_response.py` - ServiceResponse class tests
- `test_ping_service.py` - Ping service validation and execution tests
- `test_dns_service.py` - DNS lookup tests
- `test_whois_service.py` - WHOIS service tests
- `test_curl_service.py` - cURL service tests
- `test_nmap_service.py` - Nmap service tests
- `test_httpx_service.py` - HTTPX service tests
- `test_nbtscan_service.py` - NBTScan service tests
- `test_nikto_service.py` - Nikto service tests
- `test_wpscan_service.py` - WPScan service tests
- `test_dns_service.py` - DNS lookup tests
- `test_whois_service.py` - WHOIS service tests
- `test_curl_service.py` - cURL service tests
- `test_nmap_service.py` - Nmap service tests

All tests verify:
- Parameter validation
- Error handling
- JSON serialization (fixes for datetime objects)
- Command building
- Response structure