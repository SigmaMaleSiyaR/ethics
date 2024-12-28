#!/usr/bin/env bash
# Update package lists
apt-get update

# Install Chrome
apt-get install -y wget unzip chromium-browser

# Install ChromeDriver
CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip -d /usr/local/bin/
rm /tmp/chromedriver.zip
