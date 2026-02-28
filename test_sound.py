import library.config as config
from library.tts_engine import speak_stream

ipe = input("insert esp32 ip : ")
config.EIP = ipe
speak_stream("Testing audio connection to E S P thirty two")