#!/bin/bash

figlet "update"
sleep 1
clear
figlet "update"
REPO_DIR="$HOME/Android-Esp32"
REPO_URL="https://github.com/vtanixDevKid/Android-Esp32"

echo "Checking for updates in Android-Esp32..."
echo "--------------------------------------"

if [ -d "$REPO_DIR/.git" ]; then
    echo "Folder ditemukan. Menarik update terbaru (git pull)..."
    
    cd "$REPO_DIR" || exit 1
    
    if git pull; then
        echo ""
        echo "Update sukses via git pull!"
    else
        echo "Gagal melakukan pull. Mencoba cara reset..."
        git fetch --all
        git reset --hard origin/main
    fi

else
    echo "Folder tidak ditemukan atau rusak. Melakukan clone ulang..."
    
    rm -rf "$REPO_DIR"
    
    if git clone "$REPO_URL" "$REPO_DIR"; then
        echo ""
        echo "Clone selesai!"
        cd "$REPO_DIR" || exit 1
    else
        echo "Gagal melakukan clone. Cek koneksi internet kamu."
        exit 1
    fi
fi
echo "--------------------------------------"
ls --color=auto
sleep 1
