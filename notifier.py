import re
import time
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message_text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing. Check config.")
        return

    # Convert literal \n strings to actual newlines
    message_text = message_text.replace('\\n', '\n')
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    MAX_LENGTH = 4000 
    
    # Split the text right before every <b> tag using regex
    parts = [p for p in re.split(r'(?=\<b\>)', message_text) if p.strip()]
    
    chunks = []
    current_chunk = ""

    for part in parts:
        if len(current_chunk) + len(part) > MAX_LENGTH:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = part
        else:
            current_chunk += "\n\n" + part.strip()

    if current_chunk:
        chunks.append(current_chunk.strip())

    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": chunk, 
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"✅ Telegram market brief (Part {i+1}/{len(chunks)}) sent successfully!")
            else:
                print(f"❌ Failed to send Part {i+1}. Telegram API responded with: {response.text}")
        except Exception as e:
            print(f"❌ Error connecting to Telegram on Part {i+1}: {e}")
        
        time.sleep(1) # Prevent rate limiting