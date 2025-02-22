#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Chrome version
get_chrome_version() {
    if command_exists google-chrome; then
        google-chrome --version | cut -d ' ' -f 3
    else
        echo "Chrome not found"
    fi
}

# Function to get ChromeDriver version
get_chromedriver_version() {
    if command_exists chromedriver; then
        chromedriver --version | cut -d ' ' -f 2
    else
        echo "ChromeDriver not found"
    fi
}

echo "Starting Chrome and ChromeDriver installation..."

# Update package list
apt-get update

# Install dependencies
apt-get install -y wget unzip

# Install Chrome
if ! command_exists google-chrome; then
    echo "Installing Chrome..."
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
else
    echo "Chrome is already installed"
fi

# Get installed Chrome version
CHROME_VERSION=$(get_chrome_version)
echo "Chrome version: $CHROME_VERSION"

# Extract major version number
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d '.' -f 1)

# Install matching ChromeDriver
if ! command_exists chromedriver; then
    echo "Installing ChromeDriver..."
    CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}")
    wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip -q chromedriver_linux64.zip
    mv chromedriver /usr/local/bin/
    chmod +x /usr/local/bin/chromedriver
    rm chromedriver_linux64.zip
else
    echo "ChromeDriver is already installed"
fi

# Get installed ChromeDriver version
CHROMEDRIVER_VERSION=$(get_chromedriver_version)
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

# Verify installations
echo -e "\nVerification:"
echo "Chrome installation status: $(command_exists google-chrome && echo 'Installed' || echo 'Not installed')"
echo "ChromeDriver installation status: $(command_exists chromedriver && echo 'Installed' || echo 'Not installed')"

# Test Chrome and ChromeDriver
echo -e "\nTesting Chrome and ChromeDriver..."
if command_exists google-chrome && command_exists chromedriver; then
    echo "Both Chrome and ChromeDriver are installed and accessible"
    google-chrome --version
    chromedriver --version
else
    echo "Installation verification failed"
    
fi
