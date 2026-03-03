import config as config
from gtts import gTTS
import uuid
import socket
import os
import subprocess
import traceback
import time

SAMPLE_RATE = 22050
CHUNK_SIZE  = 512
CHUNK_DELAY = 0.005 # ms throttle per chunk

def speak_stream(text):
    eip = config.EIP
    if not eip:
        print("[ERR] ESP32 IP not set")
        return

    filename = f"temp_{uuid.uuid4().hex}.mp3"

    try:
        # 1. Generate TTS
        print("[INFO] Generating TTS...")
        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        # 2. Convert ke raw PCM via ffmpeg
        print("[INFO] Converting via ffmpeg...")
        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-i", filename,
            "-f", "s16le",
            "-ac", "1",
            "-ar", str(SAMPLE_RATE),
            "-"
        ]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_audio, stderr = p.communicate()

        if p.returncode != 0:
            print("[ERR] ffmpeg:", stderr.decode())
            return

        print(f"[INFO] Raw audio: {len(raw_audio)} bytes")

        # 3. Kirim via raw TCP port 81
        print(f"[INFO] Connecting to {eip}:81 ...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((eip, 81))

        total = len(raw_audio)
        sent  = 0

        while sent < total:
            chunk = raw_audio[sent:sent + CHUNK_SIZE]
            sock.sendall(chunk)
            sent += len(chunk)
            time.sleep(CHUNK_DELAY)  # throttle agar ESP32 DMA tidak overflow
            print(f"[INFO] Sent {sent}/{total} bytes", end="\r")

        print(f"\n[INFO] All sent, closing...")
        sock.close()
        print("[INFO] Done")

    except Exception as e:
        print("[ERR]", e)
        traceback.print_exc()

    finally:
        if os.path.exists(filename):
            os.remove(filename) #if you want to hear the tts output directly, just remove this line
            print("[INFO] Temp file removed")