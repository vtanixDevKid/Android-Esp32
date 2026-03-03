import requests
import library.config as config
from library.tts_engine import speak_stream
from library.esp32_gateway import send_cmd

SYSTEM_PROMPT = """You are an AI assistant embedded in a smart home device controller.
You control physical devices via an ESP32 microcontroller and speak responses via TTS.
ALWAYS REPLY WITH ENGLISH LANGUAGE

Reply ONLY in this exact format, no extra text:

SPEECH: <what to say out loud, 1-2 sentences>
CMD:<COMMAND=VALUE>

CMD lines are optional. Include them only when controlling a device.
Multiple CMD lines are allowed.

Available commands:
- LIGHT=ON / LIGHT=OFF
- FAN=ON / FAN=OFF
- RELAY1=ON / RELAY1=OFF
- RELAY2=ON / RELAY2=OFF
- BUZZER=ON / BUZZER=OFF
- TEST_SOUND
"""

_history = []

def ask_ai(text):
    global _history

    api_key = config.GEMINI_API_KEY
    if not api_key:
        print("[ERR] GEMINI_API_KEY kosong.")
        return "SPEECH: API key is missing."

    # Tambahkan user input ke history
    _history.append({
        "role": "user",
        "parts": [{"text": text}]
    })

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": SYSTEM_PROMPT}]
            }
        ] + _history,
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 256
        }
    }

    try:
        print(f"[AI] sending to gemini: {text}")
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()

        data = r.json()

        reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"[AI] reply:\n{reply}")

        # Simpan jawaban model ke history
        _history.append({
            "role": "model",
            "parts": [{"text": reply}]
        })

        # Batasi memory
        if len(_history) > 20:
            _history = _history[-20:]

        return reply

    except requests.exceptions.HTTPError:
        print("[ERR] HTTP:", r.text)
        return "SPEECH: connection problem."
    except Exception as e:
        print("[ERR] Other:", e)
        return "SPEECH: unexpected error."

def handle_text(text):
    reply = ask_ai(text)

    print("[AI] playing reminder...")
    send_cmd("PLAY_WAITING")

    speech = ""
    cmds = []

    for line in reply.splitlines():
        line = line.strip()
        if line.startswith("SPEECH:"):
            speech = line[7:].strip()
        elif line.startswith("CMD:"):
            cmds.append(line[4:].strip())

    for c in cmds:
        print(f"[CMD] → ESP32: {c}")
        send_cmd(c)

    if speech:
        print(f"[TTS] speech: {speech}")
        speak_stream(speech)

def reset_history():
    global _history
    _history = []
    print("[AI] history cleared.")

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        handle_text(user_input)