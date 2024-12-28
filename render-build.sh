#!/usr/bin/env bash

# Update package manager and install Chromium browser
apt-get update && apt-get install -y chromium-browser

# Check if Chromium is installed
if ! command -v chromium-browser &> /dev/null
then
    echo "Chromium installation failed"
    exit 1
fi

# Download and install ChromeDriver
wget https://chromedriver.storage.googleapis.com/$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Check if Chromedriver is installed
if ! command -v chromedriver &> /dev/null
then
    echo "Chromedriver installation failed"
    exit 1
fi

# Install Python dependencies
pip install -r requirements.txt
