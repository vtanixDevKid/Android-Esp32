from gtts import gTTS
import uuid
import requests, os, subprocess
import library.config as config

def speak_stream(text):
    eip = config.EIP
    if not eip:
        print("ESP32 IP not set")
        return

    tts = gTTS(text=text, lang="en")
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    tts.save(filename)

    cmd = [
        "ffmpeg", "-loglevel", "quiet",
        "-i", filename,
        "-f", "s16le", "-ac", "1", "-ar", "22050",
        "-"
    ]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def gen():
        while True:
            chunk = p.stdout.read(4096)
            if not chunk:
                break
            yield chunk

    try:
        requests.post(
            f"http://{eip}/audio",
            data=gen(),
            headers={"Content-Type": "application/octet-stream"},
            timeout=20
        )
    except Exception as e:
        print("Audio stream failed:", e)
    finally:
        p.kill()
        if os.path.exists(filename):
            os.remove(filename)