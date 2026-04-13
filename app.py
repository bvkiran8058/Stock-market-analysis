import time
import schedule
import threading
from datetime import datetime, timedelta
from flask import Flask

# Import from our modular files
from fetchers import fetch_all_news
from analyzer import analyze_news
from notifier import send_telegram_message

# 1. Setup Dummy Web Server (For Hugging Face Spaces)
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Stock Market AI Bot is running smoothly in the background!"

def run_server():
    # Hugging Face requires port 7860
    web_app.run(host="0.0.0.0", port=7860)

# 2. Main Bot Logic
def job():
    # Calculate dates dynamically so they are always fresh
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    today_str = now.strftime('%Y-%m-%d')
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    # Ensure it only runs between 8:00 and 22:00 (adjust to your timezone if needed)
    if not (8 <= now.hour < 22):
        print(f"Market closed at {now.strftime('%H:%M:%S')}. Skipping.")
        return
        
    print(f"\n--- Stock Signal Run at {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
    try:
        # Step A: Fetch News
        raw_news = fetch_all_news(yesterday_str)
        if not raw_news or not raw_news.strip():
            print("No news found this cycle.")
            return
            
        print(f"\nTotal combined news: {len(raw_news)} chars. Analyzing...")
        
        # Step B: Analyze with Gemini
        signals = analyze_news(raw_news, today_str, yesterday_str)
        
        # Step C: Send to Telegram
        if signals:
            send_telegram_message(signals)
        else:
            print("Gemini returned an empty response.")
            
    except Exception as e:
        print(f"Error during job execution: {e}")

# 3. Execution Loop
if __name__ == "__main__":
    # Start the Flask web server in a background thread to keep HF happy
    threading.Thread(target=run_server, daemon=True).start()
    
    print("🚀 Starting Continuous Market Analyst Bot...")
    
    # Schedule the job
    schedule.every(10).minutes.do(job)
    job() # Run once immediately on startup
    
    # Keep the main thread alive running the schedule
    while True:
        schedule.run_pending()
        time.sleep(1)