    # Android Esp32

---

````md
# AI Home Assistant + ESP32 Voice Control Project

so, my target is making an app with connection to esp32 http recieve from http post to control other module that attach to esp32.

## Objective

- i want an assistant ai with sound command without using n8n.
- i want that the ai will reply with speech sound to that will be an output for max98357a module.
- i want that the ai speech sound generate from python code that based on pyttsx3.
- i want that every procces backend run in python code.
- i want that generate .wav file that run on esp32 just one-in-use. like it will be an output sound speech just 1 time before it get deleted from storage

i already make an app that use vosk android demo based (we can call it vadb) to send final text to ai through http post using ai token, so we use this based app.

## Workflow Overview

Mic → vadb → GPT → Android TTS (or cloud TTS)

so it will be complete different this will be complicated.

first, we must now what will be running  
well be using pcm stream via bluetooth A2DP, wifi udp stream and http chunked.  
esp in the other hand will receive pcm stream, feed to max98357 via l2s and command parsing via seperate channel, and it will be btserial

but chaquopy is python embedded, not an server proper so we cant use it inside the app  
we have to run the server in other device  

so idk nvm. we can use termux instead.

## System Layout

### Android
- Vosk Android app (STT) aka vadb
- Termux Python server (GPT + TTS + IoT gateway)

### ESP32
- attached module like relay, sensor and importand being. max98357A
- receive command + audio

## Main Flow

Mic → Vadb → Final text → HTTP POST ke Termux server

### Example Java Code (pseudo)

```java
HttpURLConnection con = (HttpURLConnection) new URL("http://127.0.0.1:5000/stt").openConnection();
con.setRequestMethod("POST");
con.getOutputStream().write(text.getBytes());
````

---

# Termux Setup

## Step 1: Install packages

```bash
pkg update
pkg install python git ffmpeg
pip install openai pyttsx3 flask requests pyserial
```

```bash
termux-wake-lock
termux-chroot  # optional
```

---

## Step 2: Python Flask AI Server

```python
from flask import Flask, request
import openai
import pyttsx3
import os

app = Flask(__name__)
engine = pyttsx3.init()

OPENAI_KEY = "YOUR_KEY"

@app.route("/stt", methods=["POST"])
def stt():
    text = request.data.decode()
    print("USER:", text)

    # GPT
    reply = ask_ai(text)

    # TTS to wav
    filename = "out.wav"
    engine.save_to_file(reply, filename)
    engine.runAndWait()

    # TODO send wav + cmd to ESP32
    send_to_esp(reply, filename)

    return "OK"

def ask_ai(text):
    # use openai python sdk or raw HTTP
    return "dummy reply for now"

def send_to_esp(reply, wavfile):
    pass

app.run(host="0.0.0.0", port=5000)
```

---

## Run Server

```bash
python server.py
```

### Or keep alive using tmux

```bash
pkg install tmux
tmux
python server.py
```

---

# CHANNEL A - COMMAND

## Python

```python
import serial

ser = serial.Serial("/dev/rfcomm0", 115200)

def send_cmd(cmd):
    ser.write((cmd + "\n").encode())
```

## ESP32 C

```c
String cmd = Serial.readStringUntil('\n');
if(cmd == "LIGHT=ON") digitalWrite(RELAY, HIGH);
```

---

# CHANNEL B - AUDIO

```python
import requests

with open("out.wav", "rb") as f:
    requests.post("http://esp32-ip/play", data=f)

then
os.remove("out.wav")
```

so out.wav will instatly remove after being called.

---

# GPT Command Format

```
SPEECH: hello
CMD:LIGHT=ON
CMD:FAN=0
```

## Python Parser

```python
for line in reply.splitlines():
    if line.startswith("CMD:"):
        send_cmd(line[4:])
```

---

# Multi Process Architecture

we can make all python code in 1 kind of file code. but, it cause some problem, like blocking and it will cause server freezing.
for ideal this should work :

* procces 1 = stt receive server
* procces 2 = ai brain (gpt + parsing)
* procces 3 = tts engine
* procces 4 = esp32 gateway

but for setup this must be done with some effort that im to lazy to do.

---

## Threading Example

```python
import threading

def handle_request(text):
    reply = ask_ai(text)
    threading.Thread(target=speak_and_send, args=(reply,)).start()
    threading.Thread(target=parse_and_send_cmd, args=(reply,)).start()
```

---

# Project Structure

```
ai_home/
 ├ server.py     	# obtain STT from Vosk
 ├ ai_core.py     	# GPT + parsing command
 ├ tts_engine.py 	# TTS + send audio to ESP32
 ├ esp32_gateway.py 	# BT / HTTP to ESP32
 ├ start.sh 
```

server.py is the procces, and other python files was the library

---

# start.sh Script

```bash
#!/data/data/com.termux/files/usr/bin/bash

cd ~/ai_home

# wakelock so android dont kill it randomly
termux-wake-lock

# run server
python server.py &

# optional: log monitor
tail -f nohup.out
```

## Make executable

```bash
chmod +x start.sh
```

## Run

```bash
./start.sh
```

---

# tmux Advanced Script

```bash
#!/bin/bash

termux-wake-lock
tmux new-session -d -s ai

tmux send-keys -t ai "python server.py" C-m
tmux split-window -h
tmux send-keys "python monitor.py" C-m

tmux attach -t ai
```

---

```

im a kid and my main language wasnt english, so if my english look so bad dont blame me. hate this language, dont hate me.
```
