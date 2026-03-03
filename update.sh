#!/bin/bash

echo "Updating Android-Esp32 repo..."
echo ""

BASE_DIR="$HOME"
REPO_DIR="$BASE_DIR/Android-Esp32"

# Langkah krusial: Pindah ke BASE_DIR dulu
# Agar kita tidak menghapus folder yang sedang kita tempati
cd "$BASE_DIR" || exit 1

if [ -d "$REPO_DIR" ]; then
    echo "Removing old folder..."
    rm -rf "$REPO_DIR"
fi

echo "Cloning repository..."
# Pastikan git clone berjalan di BASE_DIR
git clone https://github.com/vtanixDevKid/Android-Esp32 "$REPO_DIR"

# Masuk kembali ke folder yang baru di-clone
if cd "$REPO_DIR"; then
    echo "Update complete!"
else
    echo "Failed to enter repo folder"
    exit 1
fi
