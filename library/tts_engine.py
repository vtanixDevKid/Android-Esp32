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
        if os.path.exists("temp.mp3"):
            os.remove("temp.mp3")