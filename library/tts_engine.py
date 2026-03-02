import config as config
from gtts import gTTS
import uuid
import requests
import os
import subprocess
import traceback
import time
import pyfiglet

def speak_stream(text):
    eip = config.EIP
    if not eip:
        print("[ERR] ESP32 IP not set")
        return

    print("[INFO] Generating TTS...")
    tts = gTTS(text=text, lang="en")
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    tts.save(filename)
    print("[INFO] MP3 saved:", filename)

    try:
        print("[INFO] Converting to raw PCM via ffmpeg...")
        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-i", filename,
            "-f", "s16le",
            "-ac", "1",
            "-ar", "22050",
            "-"
        ]

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_audio, stderr = p.communicate()

        if p.returncode != 0:
            print("[ERR] ffmpeg failed:", stderr.decode())
            return

        print(f"[INFO] Raw audio size: {len(raw_audio)} bytes")

        url = f"http://{eip}/audio"
        print("[INFO] Sending to:", url)

        # ✅ Kirim pakai generator chunks biar ESP32 tidak kewalahan
        CHUNK_SIZE = 4096

        def audio_chunks(data, chunk_size):
            for i in range(0, len(data), chunk_size):
                yield data[i:i + chunk_size]

        response = requests.post(
            url,
            data=audio_chunks(raw_audio, CHUNK_SIZE),
            headers={
                "Content-Type": "application/octet-stream",
                "Transfer-Encoding": "chunked"
            },
            timeout=60
        )

        print("[INFO] Status:", response.status_code)
        print("[INFO] Response:", response.text)

    except Exception as e:
        print("[ERR] Audio streaming failed:", e)
        traceback.print_exc()

    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print("[INFO] Temp file removed")