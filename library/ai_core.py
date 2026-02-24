from library.tts_engine import speak_stream
from library.esp32_gateway import send_cmd

def ask_ai(text):
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

    for c in cmds:
        send_cmd(c)

    if speech:
        speak_stream(speech)