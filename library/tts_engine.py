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

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        # 3. Buffer seluruh output jadi satu blob
        audio_bytes = p.stdout.read()
        p.wait()

        print("Sending bytes:", len(audio_bytes))

        # 4. Kirim ke ESP dengan Content-Length otomatis
        response = requests.post(
            f"http://{eip}/audio",
            data=audio_bytes,
            headers={"Content-Type": "application/octet-stream"},
            timeout=20
        )

        print("STATUS:", response.status_code)
        print("BODY:", response.text)

    except Exception as e:
        print("Audio stream failed:", e)

    finally:
        if os.path.exists(filename):
            os.remove(filename)