#!/bin/bash

# Exit on any error
set -e

echo "Starting Chrome and ChromeDriver installation..."

# Install dependencies
apt-get update
apt-get install -y wget unzip

# Install Chrome
echo "Installing Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# Install ChromeDriver
echo "Installing ChromeDriver..."
wget -q https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm -rf chromedriver-linux64.zip chromedriver-linux64

# Verify installations
echo "Verifying installations..."

# Check Chrome version
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "Chrome installed successfully: $CHROME_VERSION"
else
    echo "Chrome installation failed!"
    exit 1
fi

# Check ChromeDriver version
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version)
    echo "ChromeDriver installed successfully: $CHROMEDRIVER_VERSION"
else
    echo "ChromeDriver installation failed!"
    exit 1
fi

echo "Installation completed successfully!"

pip install -r requirements.txt
