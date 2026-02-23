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