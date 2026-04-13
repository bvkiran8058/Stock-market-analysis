import os
from dotenv import load_dotenv

# Load environment variables (useful for local testing)
load_dotenv()

# Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  
FINNHUB_KEY = os.getenv("FINNHUB_KEY")

print(f"Loaded config: Gemini key {'found' if GEMINI_API_KEY else 'missing'}, "
      f"Telegram token {'found' if TELEGRAM_BOT_TOKEN else 'missing'}, "
      f"NewsAPI key {'found' if NEWSAPI_KEY else 'missing'}, "
      f"Finnhub key {'found' if FINNHUB_KEY else 'missing'}")

# DuckDuckGo Search Queries
SEARCH_QUERIES = [
    "Nifty 50 Sensex BSE NSE market today India",
    "NSE BSE company deal contract merger acquisition India today",
    "Indian company quarterly results earnings profit loss today",
    "SEBI penalty regulation stock market India today",
    "RBI policy inflation impact banks India today",
    "Global crude oil US Fed dollar rupee market impact India today",
    "Ministry of defense railways major contract awarded today India",
    "Indian IT banking pharma auto energy stocks news today", 
]

# RSS Feeds
RSS_FEEDS = [
    {"name": "ET Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
    {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml"},
    {"name": "LiveMint Markets", "url": "https://www.livemint.com/rss/markets"},
    {"name": "CNBC TV18", "url": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/market.xml"},
    {"name": "Investing.com India", "url": "https://in.investing.com/rss/news_301.rss"},
    {"name": "Financial Express Market", "url": "https://www.financialexpress.com/market/feed/"},  
    {"name": "Financial Express Economy", "url": "https://www.financialexpress.com/economy/feed/"}, 
    
    # --- GOOGLE NEWS MACRO FILTERS ---
    {"name": "Google News RBI & Banks", "url": "https://news.google.com/rss/search?q=RBI+monetary+policy+OR+bank+regulation+India+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News SEBI", "url": "https://news.google.com/rss/search?q=SEBI+circular+OR+penalty+OR+market+rule+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Govt Orders", "url": "https://news.google.com/rss/search?q=Government+of+India+contract+OR+tender+defense+railways+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Rupee/Forex", "url": "https://news.google.com/rss/search?q=Indian+Rupee+USD+INR+surge+crash+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Stocks", "url": "https://news.google.com/rss/search?q=india+stock+NSE+BSE+company+results&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Deals", "url": "https://news.google.com/rss/search?q=india+company+deal+contract+merger+acquisition+order&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Midcap", "url": "https://news.google.com/rss/search?q=india+midcap+smallcap+company+stock+news&hl=en-IN&gl=IN&ceid=IN:en"},
]