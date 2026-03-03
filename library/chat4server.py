import requests
import time

def send_test_command(text):
    url = "http://localhost:5000/stt"
    print(f"[TESTER] Mengirim perintah: '{text}'")
    
    try:
        # Mengirim text mentah (request.data) sesuai logic server.py kamu
        response = requests.post(url, data=text, timeout=5)
        
        if response.status_code == 200:
            print(f"[TESTER] Server merespon: {response.text}")
            print("[TESTER] Tunggu ai_core memproses (cek log di terminal server)...")
        else:
            print(f"[TESTER] FAILLL! Status code: {response.status_code}")
            
    except Exception as e:
        print(f"[TESTER] Error: {e}")

if __name__ == "__main__":
    print("--- ANDRO32 AI TESTER ---")
    print("Pastikan server.py sudah jalan sebelum running ini.\n")
    
    while True:
        command = input("Masukkan teks perintah (atau 'exit'): ")
        if command.lower() == 'exit':
            break
            
        send_test_command(command)
        print("-" * 30)
