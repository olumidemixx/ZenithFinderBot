#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

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
    cd $HOME/project/src # Make sure we return to where we were
  fi
else
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src # Make sure we return to where we were
fi

# be sure to add Chrome's location to the PATH as part of your Start Command
# export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"

# add your own build commands...
