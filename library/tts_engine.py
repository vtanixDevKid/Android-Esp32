import pyttsx3, requests, os

engine = pyttsx3.init()

def speak(text):
    print("AI:", text)
    filename = "out.wav"
    engine.save_to_file(text, filename)
    engine.runAndWait()

    with open(filename, "rb") as f:
        requests.post("http://ESP32_IP/play", data=f)

    os.remove(filename)