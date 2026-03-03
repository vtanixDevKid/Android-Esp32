import sys
import config
from tts_engine import speak_stream
import pyfiglet

print(pyfiglet.figlet_format("TEST SOUND"))

# Set IP ESP32
config.EIP = input("Insert ESP32 IP: ")

menu = input("Use custom text? (1/0): ").strip()
if menu == "1":
    custom = input("Insert custom speech: ")
    speak_stream(custom)
elif menu == "0":
    prompts = [
        "one zero zero one two three four five six seven eight nine and ten",
        "1 0 0 1 2 3 4 5 6 7 8 9 0",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "one zero zero one two three four five six seven eight nine and ten. 1 0 0 1 2 3 4 5 6 7 8 9 0.a b c d e f g h i j k l m n o p q r s t u v w x y z. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    ]

    for idx, text in enumerate(prompts, 1):
        print(f"\nTesting audio prompt {idx}")
        speak_stream(text)
        cont = input("Continue? (y/n): ").strip().lower()
        if cont != "y":
            sys.exit(0)
else:
    print("Invalid choice, exiting...")