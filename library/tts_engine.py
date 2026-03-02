import config as config
from gtts import gTTS
import uuid
import requests
import os
import subprocess
import traceback
import time

CHUNK_SIZE = 4096  # 4KB per chunk — aman untuk RAM ESP32
SAMPLE_RATE = 16000

def speak_stream(text):
    eip = config.EIP
    if not eip:
        print("[ERR] ESP32 IP not set")
        return

    base_url = f"http://{eip}"
    filename = f"temp_{uuid.uuid4().hex}.mp3"

    try:
        # 1. Generate TTS
        print("[INFO] Generating TTS...")
        tts = gTTS(text=text, lang="en")
        tts.save(filename)
        print("[INFO] MP3 saved:", filename)

        # 2. Convert ke raw PCM
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
            print("[ERR] ffmpeg failed:", stderr.decode())
            return

        print(f"[INFO] Raw audio: {len(raw_audio)} bytes")

        # 3. Start stream
        r = requests.post(f"{base_url}/audio/start", timeout=5)
        if r.status_code != 200:
            print("[ERR] Start failed:", r.text)
            return
        print("[INFO] Stream started")

        # 4. Kirim per chunk
        total_chunks = (len(raw_audio) + CHUNK_SIZE - 1) // CHUNK_SIZE
        for i in range(0, len(raw_audio), CHUNK_SIZE):
            chunk = raw_audio[i:i + CHUNK_SIZE]
            chunk_num = (i // CHUNK_SIZE) + 1

            r = requests.post(
                f"{base_url}/audio/chunk",
                data=chunk,
                headers={"Content-Type": "application/octet-stream"},
                timeout=10
            )

            if r.status_code != 200:
                print(f"[ERR] Chunk {chunk_num} failed:", r.text)
                break

            print(f"[INFO] Chunk {chunk_num}/{total_chunks} sent ({len(chunk)} bytes)")

        # 5. End stream
        requests.post(f"{base_url}/audio/end", timeout=5)
        print("[INFO] Stream ended")

    except Exception as e:
        print("[ERR] speak_stream failed:", e)
        traceback.print_exc()

    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print("[INFO] Temp file removed")