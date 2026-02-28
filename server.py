import pyfiglet
import threading
from flask import Flask, request
import library.config as config
from library.ai_core import handle_text

figlet = pyfiglet.Figlet(font='larry3d')
print(figlet.renderText("ANDRO32"))

eip = input("Enter ESP32 IP: ")
config.EIP = eip
print("ESP32 IP set to:", eip)

app = Flask(__name__)

@app.route("/stt", methods=["POST"])
def stt():
    text = request.data.decode()
    print("STT:", text)
    t = threading.Thread(target=handle_text, args=(text,))
    t.start()
    return "OK"

app.run(host="0.0.0.0", port=5000)