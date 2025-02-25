#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Define the URLs for Chrome and ChromeDriver
CHROME_URL="https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chrome-linux64.zip"
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip"

# Define installation directories
INSTALL_DIR="/opt/render/project/.render"
CHROME_DIR="${INSTALL_DIR}/chrome"
CHROMEDRIVER_DIR="${INSTALL_DIR}/chromedriver"

echo "Starting Selenium environment setup..."

# Create installation directories
echo "Creating installation directories..."
mkdir -p $CHROME_DIR
mkdir -p $CHROMEDRIVER_DIR

# Install required dependencies
echo "Installing dependencies..."
apt-get update
apt-get install -y wget unzip libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1

# Download and install Chrome
echo "Downloading Chrome..."
wget $CHROME_URL -O /tmp/chrome.zip
echo "Extracting Chrome..."
unzip -o /tmp/chrome.zip -d /tmp
cp -r /tmp/chrome-linux64/* $CHROME_DIR/
chmod +x $CHROME_DIR/chrome

# Download and install ChromeDriver
echo "Downloading ChromeDriver..."
wget $CHROMEDRIVER_URL -O /tmp/chromedriver.zip
echo "Extracting ChromeDriver..."
unzip -o /tmp/chromedriver.zip -d /tmp
cp -r /tmp/chromedriver-linux64/* $CHROMEDRIVER_DIR/
chmod +x $CHROMEDRIVER_DIR/chromedriver

# Add to PATH for the current session
export PATH=$PATH:$CHROME_DIR:$CHROMEDRIVER_DIR

# Create symbolic links to make Chrome and ChromeDriver accessible system-wide
echo "Creating symbolic links..."
ln -sf $CHROME_DIR/chrome /usr/local/bin/chrome
ln -sf $CHROMEDRIVER_DIR/chromedriver /usr/local/bin/chromedriver

# Clean up
echo "Cleaning up temporary files..."
rm -rf /tmp/chrome.zip /tmp/chromedriver.zip /tmp/chrome-linux64 /tmp/chromedriver-linux64

# Verify installation
echo "Verifying Chrome installation..."
if chrome --version; then
    echo "Chrome installed successfully!"
else
    echo "Chrome installation failed!"
    exit 1
fi

echo "Verifying ChromeDriver installation..."
if chromedriver --version; then
    echo "ChromeDriver installed successfully!"
else
    echo "ChromeDriver installation failed!"
    exit 1
fi

# Create a .env file with paths (can be used by your application)
echo "Creating environment file..."
echo "CHROME_PATH=$CHROME_DIR/chrome" > .env
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_DIR/chromedriver" >> .env

echo "Selenium environment setup completed successfully!"
