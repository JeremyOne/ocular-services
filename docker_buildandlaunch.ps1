docker build -t ocular-services . 
docker rm ocular-services
docker run --rm -p 8999:8999 ocular-services