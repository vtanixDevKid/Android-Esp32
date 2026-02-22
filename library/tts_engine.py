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
        "ffmpeg", "-fflags", "nobuffer", "-flags", "low_delay",
        "-i", "temp.mp3",
        "-f", "s16le", "-ac", "1", "-ar", "22050",
        "-"
    ]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def gen():
        while True:
            chunk = p.stdout.read(4096)
            if not chunk:
                break
            yield chunk

    headers = {"Content-Type": "application/octet-stream"}
    requests.post(f"http://{eip}/audio", data=gen(), headers=headers)

    os.remove("temp.mp3")