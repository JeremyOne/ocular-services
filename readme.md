python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

pip install --upgrade -r requirements.txt


# required tools
nmap (apt)
enum4linux (snap)
smbclient (apt)
nikto (apt)

https://docs.docker.com/desktop/setup/install/linux/ubuntu/
java 17+ - sudo apt install openjdk-21-jre-headless
https://www.zaproxy.org/download/


For PDFs
sudo apt-get install wkhtmltopdf

Docker
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update -y
sudo apt install ./docker-desktop-<version>-<arch>.deb

sudo usermod -aG kvm $USER

#Docker
sudo systemctl status docker
sudo service docker start