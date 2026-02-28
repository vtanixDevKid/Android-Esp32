from gtts import gTTS
import uuid
import requests
import os
import subprocess
import config as config


def speak_stream(text):
    eip = config.EIP
    if not eip:
        print("ESP32 IP not set")
        return

    # 1. Generate MP3 dari gTTS
    tts = gTTS(text=text, lang="en")
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    tts.save(filename)

    # 2. Convert ke raw PCM 16bit mono 22050 Hz
    cmd = [
        "ffmpeg", "-loglevel", "quiet",
        "-i", filename,
        "-f", "s16le",
        "-ac", "1",
        "-ar", "22050",
        "-"
    ]


    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    chunk_size = 1024  # bisa disesuaikan, ESP32 aman sampai 1-2KB
    try:
        while True:
            chunk = p.stdout.read(chunk_size)
            if not chunk:
                break
            # kirim per chunk
            try:
                response = requests.post(
                    f"http://{eip}/audio",
                    data=chunk,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=5
                )
                # optional print status tiap chunk
                print("Chunk sent, length:", len(chunk), "Status:", response.status_code)
            except Exception as e:
                print("Chunk send failed:", e)
                break

        p.wait()
    except Exception as e:
        print("Audio streaming failed:", e)
    finally:
        if os.path.exists(filename):
            os.remove(filename)