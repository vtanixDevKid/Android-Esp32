import sys
import serial

# Android akan mengirimkan file descriptor lewat termux-usb
fd = int(sys.argv[1])

# Membuka serial menggunakan file descriptor dari Android
ser = serial.Serial()
ser.fd = fd
ser.baudrate = 115200
ser.open()

print("--- Terkoneksi ke ESP32 (Press Ctrl+C to stop) ---")
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore')
            print(line, end='')
except KeyboardInterrupt:
    print("\nStopping...")
    ser.close()