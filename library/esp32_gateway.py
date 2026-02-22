import serial

ser = None

def connect_bt():
    global ser
    try:
        ser = serial.Serial("/dev/rfcomm0", 115200, timeout=1)
        print("BT connected")
    except Exception as e:
        print("BT not connected:", e)
        ser = None

def send_cmd(cmd):
    global ser
    if ser is None:
        print("BT not ready, skipping CMD:", cmd)
        return

    try:
        ser.write((cmd + "\n").encode())
        print("CMD -> ESP32:", cmd)
    except Exception as e:
        print("BT send failed:", e)
        ser = None