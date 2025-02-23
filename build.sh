#!/bin/bash
# Create chrome directory
mkdir -p $HOME/chrome
cd $HOME/chrome

# Install Chrome
echo "Installing Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Extract and verify the extraction
dpkg -x google-chrome-stable_current_amd64.deb $HOME/chrome
if [ $? -ne 0 ]; then
    echo "Failed to extract Chrome package"
    exit 1
fi

# Clean up the deb file
rm google-chrome-stable_current_amd64.deb

# Find the actual chrome binary
CHROME_BINARY=$(find $HOME/chrome -name "google-chrome" -type f)

if [ -n "$CHROME_BINARY" ]; then
    # Export the paths
    export PATH=$(dirname "$CHROME_BINARY"):$PATH
    export CHROME_PATH="$CHROME_BINARY"
    
    # Verify installation
    CHROME_VERSION=$("$CHROME_BINARY" --version 2>/dev/null)
    if [ -n "$CHROME_VERSION" ]; then
        echo "Chrome installed successfully: $CHROME_VERSION"
        echo "Chrome binary location: $CHROME_BINARY"
    else
        echo "Chrome binary found but version check failed"
    fi
else
    echo "Chrome binary not found after extraction!"
    echo "Contents of chrome directory:"
    ls -R $HOME/chrome
fi
