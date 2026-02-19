# Ocular-services
A set of MCP services focusted on network and security scanning



## Docker

Build:
```
docker build -t ocular-services .
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
Using the above launch, services will be available on http://localhost:8889/mcp/

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

## Environment Setup
git config --global push.autoSetupRemote true


Tested with venv environments:
```
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
```

Or in windows:
(Powershell does not like paths that start with a .)
'''
python3 -m venv venv
.\venv\Scripts\Activate.ps1
'''


Install Packages:
```
pip install -r requirements.txt
pip install --upgrade -r requirements.txt
```

## Implemented / required tools

### MCP
pip install uv fastmcp 



### HTTPX
#### Install Go if not already installed
sudo apt-get update
sudo apt-get install golang-go

#### Set up Go environment variables
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
source ~/.bashrc

#### Install httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

### wpscan
sudo apt install ruby-rubygems ruby-dev
sudo gem install wpscan

