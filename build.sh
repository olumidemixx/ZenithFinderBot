#!/bin/bash
set -e  # Exit on error

echo "Starting installation process..."

# Install required dependencies
echo "Installing dependencies..."
apt-get update
apt-get install -y wget unzip

# Download and install Chrome
echo "Installing Chrome..."
wget -q https://dl-ssl.google.com/linux/linux_signing_key.pub
mv linux_signing_key.pub /etc/apt/trusted.gpg.d/google.asc
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Verify Chrome installation and get version
echo "Verifying Chrome installation..."
if ! command -v google-chrome &> /dev/null; then
    echo "ERROR: Chrome installation failed"
    exit 1
fi

CHROME_VERSION=$(google-chrome --version | awk '{ print $3 }' | awk -F'.' '{ print $1 }')
echo "Chrome version detected: $CHROME_VERSION"

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
echo "ChromeDriver version to install: $CHROMEDRIVER_VERSION"

wget -N "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
chmod +x chromedriver
mv -f chromedriver /usr/local/bin/chromedriver

# Clean up downloaded files
rm -f chromedriver_linux64.zip

# Verify final installations
echo "Final verification..."
echo "Chrome version:"
google-chrome --version
echo "ChromeDriver version:"
chromedriver --version

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found, skipping Python dependencies"
fi

echo "Installation complete!"
