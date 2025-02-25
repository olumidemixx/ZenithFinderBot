#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip"

pip install -r requirements.txt
# Add verification to check if Chrome is already installed and working
if [[ -d $STORAGE_DIR/chrome ]] && [[ -f $STORAGE_DIR/chrome/opt/google/chrome/chrome ]]; then
  echo "Verifying Chrome installation..."
  # Try to run Chrome with --version flag
  if $STORAGE_DIR/chrome/opt/google/chrome/chrome --version --headless >/dev/null 2>&1; then
    echo "✓ Chrome is properly installed and working"
    echo "...Using Chrome from cache"
  else
    echo "× Chrome installation found but not working properly, reinstalling..."
    rm -rf $STORAGE_DIR/chrome
    mkdir -p $STORAGE_DIR/chrome
    cd $STORAGE_DIR/chrome
    wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
    rm ./google-chrome-stable_current_amd64.deb
  fi
else
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
fi

# Add ChromeDriver installation and verification
if [[ -f $STORAGE_DIR/chromedriver/chromedriver-linux64/chromedriver ]]; then
  echo "Verifying ChromeDriver installation..."
  # Try to run ChromeDriver with --version flag
  if $STORAGE_DIR/chromedriver/chromedriver-linux64/chromedriver --version >/dev/null 2>&1; then
    echo "✓ ChromeDriver is properly installed and working"
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
  fi
else
  echo "...Downloading ChromeDriver"
  mkdir -p $STORAGE_DIR/chromedriver
  cd $STORAGE_DIR/chromedriver
  wget -q -O chromedriver.zip $CHROMEDRIVER_URL
  unzip -q chromedriver.zip
  chmod +x chromedriver-linux64/chromedriver
  rm chromedriver.zip
fi

if $STORAGE_DIR/chromedriver/chromedriver-linux64/chromedriver --version >/dev/null 2>&1; then
    echo "✓ ChromeDriver is properly installed and working"
    echo "...Using ChromeDriver from cache"
else
    echo "not installed"
fi



# Return to original directory
cd $HOME/project/src
apt install chromium

# be sure to add Chrome and ChromeDriver locations to the PATH as part of your Start Command
# export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome:/opt/render/project/.render/chromedriver/chromedriver-linux64"

# add your own build commands...
