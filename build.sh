#!/bin/bash

# Install Chrome in headless mode
apt-get update
apt-get install -y wget gnupg2 
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable xvfb

# Install ChromeDriver
CHROME_VERSION=$(google-chrome-stable --version | cut -d " " -f3 | cut -d "." -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
pip install -r requirements.txt

# Create directory for Chrome if it doesn't exist
mkdir -p /tmp/.chrome
