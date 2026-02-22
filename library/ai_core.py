from library.tts_engine import make_wav, send_audio
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
        if line.startswith("CMD:"):
            cmds.append(line[4:].strip())

    wav_file = make_wav(speech)
    send_audio(wav_file)

    for c in cmds:
        send_cmd(c)