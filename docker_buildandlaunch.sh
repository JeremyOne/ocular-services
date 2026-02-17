#!/bin/bash
docker build --target production -t ocular-services .
docker rm ocular-services
docker run --rm -p 8999:8999 ocular-services
