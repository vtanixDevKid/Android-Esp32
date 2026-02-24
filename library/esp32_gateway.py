import requests
import library.config as config

def send_cmd(cmd):
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