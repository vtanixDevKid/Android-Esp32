import pyfiglet
from flask import Flask, request
import library.config as config
from library.ai_core import handle_text
from library.esp32_gateway import connect_bt

figlet = pyfiglet.Figlet(font='larry3')
print(figlet.renderText("ANDRO32"))

connect_bt() 

eip = input("Enter ESP32 IP: ")
config.EIP = eip
print("ESP32 IP set to:", eip)

app = Flask(__name__)

@app.route("/stt", methods=["POST"])
def stt():
    text = request.data.decode()
    print("STT:", text)
    handle_text(text)
    return "OK"

app.run(host="0.0.0.0", port=5000)