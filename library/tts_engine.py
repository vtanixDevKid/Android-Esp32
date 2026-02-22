from gtts import gTTS
import requests, os
from library.config import EIP

def make_wav(text):
    tts = gTTS(text=text, lang='en')
    tts.save("reply.mp3")

    os.system("ffmpeg -i reply.mp3 -ar 22050 -ac 1 -sample_fmt s16 reply.wav")
    return "reply.wav"

def send_audio():
    eip = EIP
    with open("reply.wav", "rb") as f:
        requests.post(f"http://{eip}/audio", data=f)
    os.remove("reply.mp3")
    os.remove("reply.wav")
    