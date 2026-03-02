import config
from tts_engine import speak_stream
import pyfiglet

uhhh = pyfiglet.figlet_format("TEST SOUND")
print(uhhh)

ipe = input("insert esp32 ip : ")
config.EIP = ipe  # set dulu biar aman

menu = int(input("want to use custom text? (1/0) : "))

if menu == 1:
    custom = input("insert custom speech : ")
    speak_stream(custom)

elif menu == 0:
    speak_stream("testing tts to e s p 32")

else:
    print("what are you talking about")