#!/bin/bash

# Konfigurasi lokasi
REPO_DIR="$HOME/Android-Esp32"
REPO_URL="https://github.com/vtanixDevKid/Android-Esp32"

echo "Checking for updates in Android-Esp32..."
echo "--------------------------------------"

# 1. Cek apakah folder repo sudah ada dan merupakan git repo
if [ -d "$REPO_DIR/.git" ]; then
    echo "Folder ditemukan. Menarik update terbaru (git pull)..."
    
    # Pindah ke folder repo, jika gagal exit
    cd "$REPO_DIR" || exit 1
    
    # Ambil update tanpa menghapus folder (Solusi agar 'ls' tidak kosong)
    if git pull; then
        echo ""
        echo "Update sukses via git pull!"
    else
        echo "Gagal melakukan pull. Mencoba cara reset..."
        git fetch --all
        git reset --hard origin/main
    fi

# 2. Jika folder tidak ada, baru lakukan clone pertama kali
else
    echo "Folder tidak ditemukan atau rusak. Melakukan clone ulang..."
    
    # Hapus folder lama jika ada sisa-sisa rusak
    rm -rf "$REPO_DIR"
    
    # Clone ke folder tujuan
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
echo "Sekarang kamu berada di: $(pwd)"
echo "Isi folder saat ini:"
ls --color=auto
