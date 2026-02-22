import serial

ser = serial.Serial("/dev/rfcomm0", 115200)

def send_cmd(cmd):
    print("CMD -> ESP32:", cmd)
    ser.write((cmd + "\n").encode())