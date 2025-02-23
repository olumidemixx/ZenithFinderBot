#!/bin/bash
# First, fix potential Windows line endings in this script
sed -i 's/\r$//' build.sh
# Download and install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update -y
apt-get install -y google-chrome-stable
# Install Chrome Driver
wget -N "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver
mv -f chromedriver /usr/local/bin/chromedriver
# Install Python dependencies


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

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found, skipping Python dependencies"
fi

echo "Installation complete!"
