## monitorNonRoot.py
```python
import sys, os
import pyfiglet

fig = pyfiglet.Figlet(font='slant')

print(fig.renderText('ESP32 Monitor'))
print("")
print("before use make sure you run the following command under:")
print("termux-usb -l                        # to see the list of connected USB devices")
print("termux-usb -r /dev/bus/usb/001/00n   # to request access to the device")

fd = int(sys.argv[1])
f = os.fdopen(fd, 'rb+', buffering=0)

print("--- connected to ESP32 ---")
try:
    while True:
        data = f.read(64)  # read up to 64 bytes from the device
        if data:
            print(data.decode('utf-8', errors='ignore'), end='')
except KeyboardInterrupt:
    print("\nStopping...")
    f.close()
```

## test_sound.py
```py
import config as config
from tts_engine import speak_stream

ipe = input("insert esp32 ip : ")
config.EIP = ipe
speak_stream("Testing audio connection to E S P thirty two")
```

## server.py
```python
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
```
## ai_core.py
```py
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
```
## config.py
```py
EIP = None
```

## esp32_gateway.py
```py
import requests
import config as config

def send_cmd(cmd):
    eip = config.EIP
    if not eip:
        print("ESP32 IP not set")
        return

    try:
        url = f"http://{eip}/cmd"
        r = requests.get(url, params={"cmd": cmd}, timeout=3)
        print("CMD -> ESP32:", cmd, "RESP:", r.text)
    except Exception as e:
        print("WiFi send failed:", e)
```
## tts_engine.py
```py
from gtts import gTTS
import uuid
import requests
import os
import subprocess
import config as config


def speak_stream(text):
    eip = config.EIP
    if not eip:
        print("ESP32 IP not set")
        return

    # 1. Generate MP3 dari gTTS
    tts = gTTS(text=text, lang="en")
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    tts.save(filename)

    # 2. Convert ke raw PCM 16bit mono 22050 Hz
    cmd = [
        "ffmpeg", "-loglevel", "quiet",
        "-i", filename,
        "-f", "s16le",
        "-ac", "1",
        "-ar", "22050",
        "-"
    ]

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        # 3. Buffer seluruh output jadi satu blob
        audio_bytes = p.stdout.read()
        p.wait()

        print("Sending bytes:", len(audio_bytes))

        # 4. Kirim ke ESP dengan Content-Length otomatis
        response = requests.post(
            f"http://{eip}/audio",
            data=audio_bytes,
            headers={"Content-Type": "application/octet-stream"},
            timeout=None
        )

        print("STATUS:", response.status_code)
        print("BODY:", response.text)

    except Exception as e:
        print("Audio stream failed:", e)

    finally:
        if os.path.exists(filename):
            os.remove(filename)
```
## __init__.py
```py
#what do you seek here lol, this is just __init__.py .
#dont tell me you dont know what __init__.py is for lol.
```

## esp32 example code
``` cpp
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <driver/i2s.h>

const char* ssid = "ESP32_IoT";
const char* pass = "wannacry";

IPAddress local_ip(192, 168, 4, 1);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);

// ================= PIN =================
#define LED_PIN 2
#define I2S_BCLK 26
#define I2S_LRC  27
#define I2S_DOUT 19
#define I2S_SD   21

WebServer server(80);

// ================= I2S SETUP =================
void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = 22050,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 512,
    .use_apll = false,
    .tx_desc_auto_clear = true,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCLK,
    .ws_io_num = I2S_LRC,
    .data_out_num = I2S_DOUT,
    .data_in_num = I2S_PIN_NO_CHANGE
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  i2s_zero_dma_buffer(I2S_NUM_0);
}

// ================= HANDLERS =================
void handleCmd() {
  String cmd = server.arg("cmd");
  if (cmd == "LIGHT=ON") digitalWrite(LED_PIN, HIGH);
  else if (cmd == "LIGHT=OFF") digitalWrite(LED_PIN, LOW);
  server.send(200, "text/plain", "OK");
}

void handleAudio() {
  WiFiClient client = server.client();
  const size_t bufSize = 1024;
  uint8_t buffer[bufSize];

  while (client.connected()) {
    int len = client.read(buffer, bufSize);
    if (len > 0) {
      size_t written;
      i2s_write(I2S_NUM_0, buffer, len, &written, portMAX_DELAY);
    }
    if (len == 0) delay(1);
    if (len < 0) break;
  }
  server.send(200, "text/plain", "OK");
}

void handleStatus() {
  String s = "ESP32 HOST OK\nIP: " + WiFi.softAPIP().toString();
  server.send(200, "text/plain", s);
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  pinMode(I2S_SD, OUTPUT);
  digitalWrite(I2S_SD, HIGH);
  pinMode(LED_PIN, OUTPUT);

  // SETTING SEBAGAI HOST (AP)
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(local_ip, gateway, subnet);
  WiFi.softAP(ssid, pass);

  Serial.println("\nWiFi Host Started");
  Serial.print("SSID: "); Serial.println(ssid);
  Serial.print("IP Address: "); Serial.println(WiFi.softAPIP());

  if (MDNS.begin("andro32")) {
    Serial.println("mDNS: http://andro32.local");
  }

  setupI2S();

  server.on("/cmd", handleCmd);
  server.on("/audio", HTTP_POST, handleAudio);
  server.on("/status", handleStatus);
  server.begin();
}

void loop() {
  server.handleClient();
  delay(2); // stabilitas mDNS & webserver#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <driver/i2s.h>

// ================= WIFI STA SETTINGS =================
const char* ssid = "Yenni";
const char* pass = "masterliem";

// ================= PIN =================
#define LED_PINR 23
#define LED_PINB 2  // LED indikator WiFi
#define I2S_BCLK 26
#define I2S_LRC  27
#define I2S_DOUT 19
#define I2S_SD   21

WebServer server(80);

// ================= I2S SETUP =================
void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = 22050,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 512,
    .use_apll = false,
    .tx_desc_auto_clear = true,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCLK,
    .ws_io_num = I2S_LRC,
    .data_out_num = I2S_DOUT,
    .data_in_num = I2S_PIN_NO_CHANGE
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  i2s_zero_dma_buffer(I2S_NUM_0);
}

// ================= HANDLERS =================
void handleCmd() {
  String cmd = server.arg("cmd");
  if (cmd == "LIGHT=ON") {
    digitalWrite(LED_PINR, HIGH);
    Serial.println("CMD: LED RED ON");
  } else if (cmd == "LIGHT=OFF") {
    digitalWrite(LED_PINR, LOW);
    Serial.println("CMD: LED RED OFF");
  }
  server.send(200, "text/plain", "OK");
}

// SAFE AUDIO STREAM WITH DEBUG
void handleAudio() {
    WiFiClient client = server.client();
    const size_t bufSize = 1024;
    uint8_t buffer[bufSize];

    unsigned long start = millis();
    while (client.connected()) {
        while (client.available()) {
            int len = client.read(buffer, bufSize);
            if (len > 0) {
                size_t written;
                i2s_write(I2S_NUM_0, buffer, len, &written, portMAX_DELAY);
            }
        }
        // Kalau nggak ada data baru selama 5 detik, anggap streaming selesai
        if (millis() - start > 5000) break;
        yield();
    }
    server.send(200, "text/plain", "Finished");
}

void handleStatus() {
  String s = "ESP32 STA OK\nIP: " + WiFi.localIP().toString();
  server.send(200, "text/plain", s);
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  pinMode(LED_PINB, OUTPUT);
  pinMode(LED_PINR, OUTPUT);
  pinMode(I2S_SD, OUTPUT);
  digitalWrite(I2S_SD, HIGH); // Enable amplifier

  // WiFi STA connect
  WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, pass);

    Serial.print("Connecting to WiFi");
    unsigned long startAttemptTime = millis();
    const unsigned long timeout = 30000; // 30 detik max

    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < timeout) {
        digitalWrite(LED_PINB, !digitalRead(LED_PINB)); // kedip LED
        delay(250);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        digitalWrite(LED_PINB, LOW); // LED LOW \connect
        Serial.println("\nWiFi Connected!");
        Serial.print("IP: "); Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi Connection Failed!");
        while(1) { 
            digitalWrite(LED_PINB, !digitalRead(LED_PINB));
            delay(100);
        }
    }

  if (MDNS.begin("andro32")) {
    Serial.println("mDNS: http://andro32.local");
  }

  setupI2S();

  // Collect header
  const char* headerkeys[] = {"Content-Length"};
  server.collectHeaders(headerkeys, 1);

  // Routes
  server.on("/cmd", handleCmd);
  server.on("/audio", HTTP_POST, handleAudio);
  server.on("/status", handleStatus);

  server.begin();
  Serial.println("HTTP Server started");
}

// ================= LOOP =================
void loop() {
  server.handleClient();
  // Delay minimal agar stream lancar
}
}
```