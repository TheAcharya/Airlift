#!/bin/bash

# Convenience script to run Docker setup from project root
# This script calls the docker/install_from_docker.sh script

echo "Setting up Airlift Docker environment..."

chmod +x docker/install_from_docker.sh

bash docker/install_from_docker.sh 