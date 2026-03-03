#!/bin/bash

echo "Updating Android-Esp32 repo..."
echo ""

BASE_DIR="$HOME"

REPO_DIR="$BASE_DIR/Android-Esp32"

if [ -d "$REPO_DIR" ]; then
    echo "Removing old folder..."
    rm -rf "$REPO_DIR"
fi

echo "Cloning repository..."
git clone https://github.com/vtanixDevKid/Android-Esp32 "$REPO_DIR"

cd "$REPO_DIR" || { echo "Failed to enter repo folder"; exit 1; }

echo "Update complete!"