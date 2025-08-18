git config --global push.autoSetupRemote true

sudo apt install python3.12-venv

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

pip install --upgrade -r requirements.txt


# Implemented / required tools

## Simple installs
sudo apt install nmap
sudo apt install smbclient
sudo apt install nikto
sudo apt install masscan
sudo apt install whois
sudo snap install enum4linux

## HTTPX
### Install Go if not already installed
sudo apt-get update
sudo apt-get install golang-go

### Set up Go environment variables
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
source ~/.bashrc

### Install httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

## wpscan
sudo apt install ruby-rubygems ruby-dev
sudo gem install wpscan

## Below here, notes
https://docs.docker.com/desktop/setup/install/linux/ubuntu/
java 17+ - sudo apt install openjdk-21-jre-headless
https://www.zaproxy.org/download/

sudo systemctl status docker
sudo service docker start

## Not implemented - potential PDF renderer
sudo apt-get install wkhtmltopdf

Docker
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update -y
sudo apt install ./docker-desktop-<version>-<arch>.deb

sudo usermod -aG kvm $USER