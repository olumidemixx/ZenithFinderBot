#!/bin/bash

# Update package list
sudo apt-get update

# Install dependencies
sudo apt-get install -y unzip wget

# Install latest Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y
rm google-chrome-stable_current_amd64.deb

# Get latest Chrome version
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')

# Get matching ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# Install ChromeDriver
wget "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

# Verify installations
echo "Chrome version:"
google-chrome --version
echo "ChromeDriver version:"
chromedriver --version

pip install -r requirements.txt

# Verify Chrome installation
if ! command -v google-chrome &> /dev/null; then
    echo "Chrome is not installed"
    
else
    echo "Chrome is installed:"
    google-chrome --version
fi

# Verify ChromeDriver installation
if ! command -v chromedriver &> /dev/null; then
    echo "ChromeDriver is not installed"
    
else
    echo "ChromeDriver is installed:"
    chromedriver --version
fi
