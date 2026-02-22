#!/data/data/com.termux/files/usr/bin/bash
figlet "Android ESP32"

cd ~/ai_home

# wakelock dont kill randomly
termux-wake-lock

# nessesary installation
REQ_FLAG=".requirements_installed"

if [ ! -f "$REQ_FLAG" ]; then
    echo "[+] Installing requirements..."
    pkg update -y && pkg upgrade -y
    pkg install python -y && pkg install figlet -y && pkg install tmux -y && pkg install ffmpeg -y && pkg install mpv -y
    pip install -r requirements.txt
    touch $REQ_FLAG
else
    echo "[+] Requirements already installed"
fi

# run server
python server.py &

# optional: log monitor
tail -f nohup.out