#!/bin/bash

# First, fix potential Windows line endings in this script

sed -i 's/\r$//' build.sh

# Download and install Chrome

wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

apt-get update -y

apt-get install -y google-chrome-stable

# Install Chrome Driver

CHROME_VERSION=$(google-chrome --version | awk '{ print $3 }' | awk -F'.' '{ print $1 }')

CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

wget -N "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

unzip chromedriver_linux64.zip

chmod +x chromedriver

mv -f chromedriver /usr/local/bin/chromedriver

# Install Python dependencies

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

# After Chrome installation

google-chrome --version || echo "Error: $?"

# After ChromeDriver installation

ls -l /usr/local/bin/chromedriver || echo "Error: $?"
