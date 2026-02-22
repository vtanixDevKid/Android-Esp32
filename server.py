from flask import Flask, request
from ai_core import handle_text

app = Flask(__name__)

@app.route("/stt", methods=["POST"])
def stt():
    text = request.data.decode()
    print("STT:", text)
    handle_text(text)
    return "OK"

app.run(host="0.0.0.0", port=5000)