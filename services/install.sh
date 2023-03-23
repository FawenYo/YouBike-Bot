#!/bin/bash

set -e

# Update package list and install curl
apt-get update
apt-get install -y curl

# Install Docker
curl -s https://get.docker.com | sh 

# Install Docker Compose
apt-get install -y docker-compose-plugin