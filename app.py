import time
import schedule
import threading
from datetime import datetime, timedelta, timezone
from flask import Flask

# Import from our modular files
from fetchers import fetch_all_news
from analyzer import analyze_news, filter_news, extract_tickers, premarket_watchlist
from indicators import get_technical_summary
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
    IST = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(IST)
    yesterday = now - timedelta(days=1)
    
    today_str = now.strftime('%Y-%m-%d')
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    # Ensure it only runs between 8:00 and 22:00 (adjust to your timezone if needed)
    if not (0 <= now.hour < 22):
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
        
        filtered_news = filter_news(raw_news, today_str, yesterday_str)
        tickers = extract_tickers(filtered_news)
        tech_data = get_technical_summary(tickers) if tickers else ""
        print(f"filtered news: {len(filtered_news)} chars, tickers found: {tickers}, tech data length: {len(tech_data)} chars")

        signals = analyze_news(filtered_news, tech_data, today_str, yesterday_str)
        print(f"Generated signals: {len(signals)} chars")
        
        # Step C: Send to Telegram
        if signals:
            send_telegram_message(signals)
        else:
            print("Gemini returned an empty response.")
            
    except Exception as e:
        print(f"Error during job execution: {e}")

from datetime import datetime, timedelta

def premarket_job():
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    # Use a 1-day delta for the yesterday string
    yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')

    print(f"\n--- Pre-Market Watchlist at {now.strftime('%Y-%m-%d %H:%M:%S')} ---")

    try:
        # 1. Fetch news
        raw_news = fetch_all_news(yesterday_str)
        
        if not raw_news or not raw_news.strip():
            print("No news for pre-market watchlist.")
            return

        # 2. Filter news using LLM
        filtered = filter_news(raw_news, today_str, yesterday_str)
        
        # 3. Extract company tickers to get technicals for
        tickers = extract_tickers(filtered)
        
        # 4. Fetch Technical Snapshot for those tickers
        tech_data = get_technical_summary(tickers) if tickers else "N/A"

        # 5. Generate the watchlist via LLM
        # Ensure the keys match your PREMARKET_PROMPT placeholders
        watchlist = premarket_watchlist(
            filtered_news=filtered,
            tech_data=tech_data,
            today_str=today_str,
        )
        
        # Handle response content
        watchlist_content = watchlist.content if hasattr(watchlist, "content") else str(watchlist)

        if watchlist_content.strip():
            header = f"<b>🚀 Pre-Market Watchlist - {now.strftime('%d %b %Y')}</b>\n\n"
            # Ensure the response is stripped of unwanted whitespace
            send_telegram_message(header + watchlist_content.strip())
            print("Pre-market watchlist sent to Telegram.")
        else:
            print("Watchlist generation resulted in an empty string.")

    except Exception as e:
        print(f"Error during pre-market job: {e}")

# 3. Execution Loop
if __name__ == "__main__":
    # Start the Flask web server in a background thread to keep HF happy
    threading.Thread(target=run_server, daemon=True).start()
    
    print("🚀 Starting Continuous Market Analyst Bot...")
    
    schedule.every().day.at("09:00").do(premarket_job)  

    # Schedule the job
    schedule.every(20).minutes.do(job)
    job() # Run once immediately on startup
    
    # Keep the main thread alive running the schedule
    while True:
        schedule.run_pending()
        time.sleep(1)