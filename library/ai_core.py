from library.tts_engine import speak_stream
from library.esp32_gateway import send_cmd

def ask_ai(text):
    # nanti ganti ke LLM
    return """SPEECH: Lamp turned on.
CMD:LIGHT=ON"""

def handle_text(text):
    reply = ask_ai(text)

    speech = ""
    cmds = []

    for line in reply.splitlines():
        if line.startswith("SPEECH:"):
            speech = line[7:].strip()
        elif line.startswith("CMD:"):
            cmds.append(line[4:].strip())

    # send cmd to ESP32 via BT/Serial first
    for c in cmds:
        send_cmd(c)

    # TTS STREAM to ESP32 for speech response
    if speech:
        speak_stream(speech)