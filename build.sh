#!/bin/bash

# Configuration
REPO_OWNER="olumidemixx"
REPO_NAME="ZenithFinderBot"
CHROMEDRIVER_PATH="chromedriver"
GITHUB_RAW_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${CHROMEDRIVER_PATH}"

# Function to check if ChromeDriver is already installed
check_chromedriver() {
    if [ -f "./chromedriver" ]; then
        echo "ChromeDriver is already present in current directory"
        chmod +x ./chromedriver
        if ./chromedriver --version > /dev/null 2>&1; then
            echo "ChromeDriver version check successful:"
            ./chromedriver --version
            return 0
        else
            echo "ChromeDriver version check failed.  Possibly corrupted."
            return 1
        fi
    else
        return 1
    fi
}

# Function to download ChromeDriver from GitHub
download_chromedriver() {
    echo "Downloading ChromeDriver from your GitHub repository..."

    # Download the ChromeDriver
    if curl -L -o chromedriver "$GITHUB_RAW_URL"; then
        echo "ChromeDriver downloaded successfully"

        # Make it executable
        chmod +x chromedriver

        # Verify the download
        if ./chromedriver --version > /dev/null 2>&1; then
            echo "ChromeDriver installation verified successfully"
            ./chromedriver --version
            return 0
        else
            echo "Error: ChromeDriver verification failed"
            return 1
        fi
    else
        echo "Error: Failed to download ChromeDriver"
        return 1
    fi
}

# Main script execution
echo "Checking for existing ChromeDriver..."

if ! check_chromedriver; then
    echo "ChromeDriver not found. Downloading from GitHub..."
    if download_chromedriver; then
        echo "ChromeDriver setup completed successfully!"
    else
        echo "ChromeDriver setup failed!"

    fi
else
    echo "ChromeDriver already installed."
fi

#Final verification
if check_chromedriver; then
    echo "ChromeDriver verified successfully after script execution."
else
    echo "ChromeDriver verification failed after script execution."
fi

pip install -r requirements.txt
