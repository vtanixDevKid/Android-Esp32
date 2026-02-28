import config as config
from tts_engine import speak_stream

ipe = input("insert esp32 ip : ")
config.EIP = ipe
speak_stream("Testing audio connection to E S P thirty two")