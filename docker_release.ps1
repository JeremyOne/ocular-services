docker build -t ocular-services:0.3.2 . 
docker tag ocular-services:0.3.2 ocular-services:latest
docker push jeremyone/ocular-services:0.3.2