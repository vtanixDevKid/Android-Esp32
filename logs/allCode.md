## monitorNonRoot.py
```python
import sys, os
import pyfiglet

fig = pyfiglet.Figlet(font='slant')

print(fig.renderText('ESP32 Monitor'))
print("")
print("before use make sure you run the following command under:")
print("termux-usb -l                        # to see the list of connected USB devices")
print("termux-usb -r /dev/bus/usb/001/00n   # to request access to the device")

fd = int(sys.argv[1])
f = os.fdopen(fd, 'rb+', buffering=0)

print("--- connected to ESP32 ---")
try:
    while True:
        data = f.read(64)  # read up to 64 bytes from the device
        if data:
            print(data.decode('utf-8', errors='ignore'), end='')
except KeyboardInterrupt:
    print("\nStopping...")
    f.close()
```

## server.py
```python

import pyfiglet
import threading
from flask import Flask, request
import library.config as config
from library.ai_core import handle_text
from library.esp32_gateway import connect_bt

figlet = pyfiglet.Figlet(font='larry3')
print(figlet.renderText("ANDRO32"))

connect_bt()

eip = input("Enter ESP32 IP: ")
config.EIP = eip
print("ESP32 IP set to:", eip)

app = Flask(__name__)

@app.route("/stt", methods=["POST"])
def stt():
    text = request.data.decode()
    print("STT:", text)
    handle_text(text)
    t = threading.Thread(target=handle_text, args=(text,))
    t.start()
    return "OK"

app.run(host="0.0.0.0", port=5000)
```
## ai_core.py
```py
from library.tts_engine import speak_stream
from library.esp32_gateway import send_cmd

def ask_ai(text):
    # nanti ganti ke LLM
    return """SPEECH: Lamp turned on.
CMD:LIGHT=ON"""

def handle_text(text):
    reply = ask_ai(text)

    speech = ""
    cmds = []

    for line in reply.splitlines():
        if line.startswith("SPEECH:"):
            speech = line[7:].strip()
        elif line.startswith("CMD:"):
            cmds.append(line[4:].strip())

    # send cmd to ESP32 via BT/Serial first
    for c in cmds:
        send_cmd(c)

    # TTS STREAM to ESP32 for speech response
    if speech:
        speak_stream(speech)
```
## config.py
```py
EIP = None
```

## esp32_gateway.py
```py
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
```
## tts_engine.py
```py
from gtts import gTTS
import requests, os, subprocess
import library.config as config

def speak_stream(text):
    eip = config.EIP
    if not eip:
        print("ESP32 IP not set")
        return

    tts = gTTS(text=text, lang="en")
    tts.save("temp.mp3")

    cmd = [
        "ffmpeg", "-loglevel", "quiet",
        "-i", "temp.mp3",
        "-f", "s16le", "-ac", "1", "-ar", "22050",
        "-"
    ]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def gen():
        while True:
            if p.poll() is not None:
                break
            chunk = p.stdout.read(4096)
            if not chunk:
                break
            yield chunk

    try:
        requests.post(
            f"http://{eip}/audio",
            data=gen(),
            headers={"Content-Type": "application/octet-stream"},
            timeout=10
        )
    finally:
        p.kill()
        os.remove("temp.mp3")
```
## __init__.py
```py
#what do you seek here lol, this is just __init__.py .
#dont tell me you dont know what __init__.py is for lol.
```