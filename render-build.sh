#!/bin/bash

# Update and install necessary dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    wget \
    unzip

# Download and install chromium-browser
CHROMIUM_VERSION="112.0.5615.49-1"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O google-chrome.deb
sudo dpkg -i google-chrome.deb
sudo apt-get -f install

# Install chromedriver
CHROMEDRIVER_VERSION="112.0.5615.49"
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/

# Ensure chromedriver is in the correct path
sudo chmod +x /usr/local/bin/chromedriver

# Check and log the installation status of chromium and chromedriver
echo "Checking installation paths..."
which google-chrome-stable || echo "Chromium not installed"
which chromedriver || echo "Chromedriver not installed"

# Install Python dependencies from requirements.txt
pip install -r requirements.txt

# Log versions of installed tools for debugging
echo "Chromium version:"
google-chrome-stable --version
echo "Chromedriver version:"
chromedriver --version
