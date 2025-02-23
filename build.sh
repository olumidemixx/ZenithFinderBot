#!/bin/bash

# Exit on any error
set -e

echo "Starting Chrome and ChromeDriver installation..."

# Create a directory for the installations
mkdir -p $HOME/chrome
cd $HOME/chrome

# Install Chrome directly from the binary
echo "Installing Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb $HOME/chrome
rm google-chrome-stable_current_amd64.deb

# Add Chrome binary to PATH
export PATH=$HOME/chrome/usr/bin:$PATH
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
export PATH=$HOME/chrome/usr/bin:$HOME/chrome/driver:\$PATH
export CHROME_PATH=$HOME/chrome/usr/bin/google-chrome
EOL

# Verify installations
echo "Verifying installations..."

# Check Chrome version
if [ -f "$HOME/chrome/usr/bin/google-chrome" ]; then
    CHROME_VERSION=$($HOME/chrome/usr/bin/google-chrome --version)
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

pip install -r requirements.txt
