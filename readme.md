# Ocular-services
A set of MCP services focusted on network and security scanning


## Envionment Setup
git config --global push.autoSetupRemote true


Tested with venv environments:
```
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
```

Install Packages:
```
pip install -r requirements.txt
pip install --upgrade -r requirements.txt
```

## Implemented / required tools

### MCP
pip install uv fastmcp 

uv venv
source .venv/bin/activate
uv pip install fastmcp

### Simple installs
sudo apt install nmap
sudo apt install smbclient
sudo apt install nikto
sudo apt install masscan
sudo apt install whois
sudo apt install nbtscan
sudo snap install enum4linux

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
