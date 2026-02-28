echo "================================"
echo "          Test Sound"
echo "================================"
echo ""
cek() {
    read -p "$1 (y/n): " jaw
    case "$jaw" in
        [yY][eE][sS]|[yY])
        nmap -sn 192.168.1.0/24
        ;;
    *)
        return 0
        ;;
    esac
}

if cek "scan ip addreas?"; then
    python ~/Android-Esp32/library/test_sound.py
else
    echo ""
fi
