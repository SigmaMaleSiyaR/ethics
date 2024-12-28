#!/usr/bin/env bash
# Update package manager and install Chromium browser
apt-get update && apt-get install -y chromium-browser

# Download and install ChromeDriver
wget https://chromedriver.storage.googleapis.com/$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
pip install -r requirements.txt
