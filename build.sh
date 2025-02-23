#!/bin/bash

# Exit on any error
set -e

echo "Starting setup process..."

# Install Python requirements first
echo "Installing Python requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found!"
    # Install minimum required packages for Selenium
    pip install selenium webdriver_manager
fi

echo "Starting Chrome and ChromeDriver installation..."

# Create a directory for the installations
mkdir -p $HOME/chrome
cd $HOME/chrome

# Install Chrome directly from the binary
echo "Installing Chrome..."
wget -i https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb $HOME/chrome
apt-get install -f
goggle-chrome

# Add Chrome binary to PATH
export PATH=$HOME/chrome:$PATH
export CHROME_PATH=$HOME/chrome/usr/bin/google-chrome

# Install ChromeDriver
echo "Installing ChromeDriver..."
wget -q https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
mkdir -p $HOME/chrome/driver
mv chromedriver-linux64/chromedriver $HOME/chrome/driver/
chmod +x $HOME/chrome/driver/chromedriver
rm -rf chromedriver-linux64.zip chromedriver-linux64

# Add ChromeDriver to PATH
export PATH=$HOME/chrome/driver:$PATH

# Create a script to set environment variables
cat > $HOME/chrome/env.sh << EOL
export PATH=$HOME/chrome/:$HOME/chrome/driver:\$PATH
export CHROME_PATH=$HOME/chrome/usr/bin/google-chrome
EOL

# Verify installations
echo "Verifying installations..."

# Check Python packages
echo "Checking Python packages..."
#pip list

# Check Chrome version
if [ -f "$HOME/chrome/google-chrome" ]; then
    CHROME_VERSION=$($HOME/chrome/google-chrome --version)
    echo "Chrome installed successfully: $CHROME_VERSION"
else
    echo "Chrome installation failed!"
    
fi

# Check ChromeDriver version
if [ -f "$HOME/chrome/driver/chromedriver" ]; then
    CHROMEDRIVER_VERSION=$($HOME/chrome/driver/chromedriver --version)
    echo "ChromeDriver installed successfully: $CHROMEDRIVER_VERSION"
else
    echo "ChromeDriver installation failed!"
    
fi

echo "Installation completed successfully!"
echo "Don't forget to source the environment variables before running your tests:"
echo "source \$HOME/chrome/env.sh"
