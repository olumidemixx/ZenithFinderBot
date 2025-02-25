#!/usr/bin/env bash
# exit on error
set -o errexit
STORAGE_DIR=/opt/render/project/.render
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip"
pip install -r requirements.txt

# Function to extract and display Chrome version
get_chrome_version() {
  local version
  version=$($STORAGE_DIR/chrome/opt/google/chrome/chrome --version 2>/dev/null | cut -d " " -f 3)
  echo "Chrome version: $version"
}

# Function to extract and display ChromeDriver version
get_chromedriver_version() {
  local version
  version=$($STORAGE_DIR/chromedriver/chromedriver-linux64/chromedriver --version 2>/dev/null | cut -d " " -f 2)
  echo "ChromeDriver version: $version"
}

# Add verification to check if Chrome is already installed and working
if [[ -d $STORAGE_DIR/chrome ]] && [[ -f $STORAGE_DIR/chrome/opt/google/chrome/chrome ]]; then
  echo "Verifying Chrome installation..."
  # Try to run Chrome with --version flag
  if $STORAGE_DIR/chrome/opt/google/chrome/chrome --version --headless >/dev/null 2>&1; then
    echo "✓ Chrome is properly installed and working"
    get_chrome_version
    echo "...Using Chrome from cache"
  else
    echo "× Chrome installation found but not working properly, reinstalling..."
    rm -rf $STORAGE_DIR/chrome
    mkdir -p $STORAGE_DIR/chrome
    cd $STORAGE_DIR/chrome
    wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
    rm ./google-chrome-stable_current_amd64.deb
    get_chrome_version
  fi
else
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  get_chrome_version
fi

# Add ChromeDriver installation and verification
if [[ -f $STORAGE_DIR/chromedriver/chromedriver-linux64/chromedriver ]]; then
  echo "Verifying ChromeDriver installation..."
  # Try to run ChromeDriver with --version flag
  if $STORAGE_DIR/chromedriver/chromedriver-linux64/chromedriver --version >/dev/null 2>&1; then
    echo "✓ ChromeDriver is properly installed and working"
    get_chromedriver_version
    echo "...Using ChromeDriver from cache"
  else
    echo "× ChromeDriver installation found but not working properly, reinstalling..."
    rm -rf $STORAGE_DIR/chromedriver
    mkdir -p $STORAGE_DIR/chromedriver
    cd $STORAGE_DIR/chromedriver
    echo "...Downloading ChromeDriver"
    wget -q -O chromedriver.zip $CHROMEDRIVER_URL
    unzip -q chromedriver.zip
    chmod +x chromedriver-linux64/chromedriver
    rm chromedriver.zip
    get_chromedriver_version
  fi
else
  echo "...Downloading ChromeDriver"
  mkdir -p $STORAGE_DIR/chromedriver
  cd $STORAGE_DIR/chromedriver
  wget -q -O chromedriver.zip $CHROMEDRIVER_URL
  unzip -q chromedriver.zip
  chmod +x chromedriver-linux64/chromedriver
  rm chromedriver.zip
  get_chromedriver_version
fi

# Print version compatibility check
echo "-----------------------------------"
echo "Checking version compatibility..."
#CHROME_VERSION=$(get_chrome_version | cut -d " " -f 3 | cut -d "." -f 1)
#CHROMEDRIVER_VERSION=$(get_chromedriver_version | cut -d " " -f 2 | cut -d "." -f 1)
CHROME_VERSION=$(get_chrome_version)
CHROMEDRIVER_VERSION=$(get_chromedriver_version)

if [[ "$CHROME_VERSION" == "$CHROMEDRIVER_VERSION" ]]; then
  echo "✓ Chrome and ChromeDriver major versions match: $CHROME_VERSION"
else
  echo "⚠ WARNING: Version mismatch detected!"
  echo "  Chrome version: $CHROME_VERSION"
  echo "  ChromeDriver version: $CHROMEDRIVER_VERSION"
  echo "  This may cause compatibility issues"
fi
echo "-----------------------------------"

# Return to original directory
cd $HOME/project/src

# be sure to add Chrome and ChromeDriver locations to the PATH as part of your Start Command
# export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome:/opt/render/project/.render/chromedriver/chromedriver-linux64"
# add your own build commands...

echo "Setup complete! Chrome and ChromeDriver are ready to use."
