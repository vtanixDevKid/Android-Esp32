import pyfiglet
from flask import Flask, request
from library.ai_core import handle_text
from library.tts_engine import send_tts

#figlet :P
figlet.setFont(font='larry3')
title = pyfiglet.figlet_format("ANDRO32")
print(title)
print("")

eip = input("Enter ESP32 IP: ")
print("")

app = Flask(__name__)

@app.route("/stt", methods=["POST"])
def stt():
    text = request.data.decode()
    print("STT:", text)
    handle_text(text)
    return "OK"

app.run(host="0.0.0.0", port=5000)