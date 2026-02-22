## server.py
```python
import pyfiglet
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
    return "OK"

app.run(host="0.0.0.0", port=5000)
```
## config.py
```python
EIP = None
```

## ai_core.py
```python
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

## tts_engine.py
```python
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

## esp32_gateway.py
```python
import serial

ser = None

def connect_bt():
    global ser
    try:
        ser = serial.Serial("/dev/rfcomm0", 115200, timeout=1)
        print("BT connected")
    except Exception as e:
        print("BT not connected:", e)
        ser = None

def send_cmd(cmd):
    global ser
    if ser is None:
        print("BT not ready, skipping CMD:", cmd)
        return

    try:
        ser.write((cmd + "\n").encode())
        print("CMD -> ESP32:", cmd)
    except Exception as e:
        print("BT send failed:", e)
        ser = None
```