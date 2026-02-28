import requests
import threading
import library.config as config

lock = threading.lock()

def send_cmd(cmd):
    with lock:
        ser.write((cmd + "\n").encode())
    eip = config.EIP
    if not eip:
        print("ESP32 IP not set, skipping CMD:", cmd)
        return

    try:
        url = f"http://{eip}/cmd"
        r = requests.get(url, params={"cmd": cmd}, timeout=3)
        print("CMD -> ESP32:", cmd, "RESP:", r.text)
    except Exception as e:
        print("WiFi send failed:", e)