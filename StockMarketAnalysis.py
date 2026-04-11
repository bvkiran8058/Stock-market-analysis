import os
import time, re
import schedule
import requests
import feedparser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchResults
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  
FINNHUB_KEY = os.getenv("FINNHUB_KEY")
print(f"Loaded config: Gemini key {'found' if GEMINI_API_KEY else 'missing'}, Telegram token {'found' if TELEGRAM_BOT_TOKEN else 'missing'}, Chat ID {'found' if TELEGRAM_CHAT_ID else 'missing'}, NewsAPI key {'found' if NEWSAPI_KEY else 'missing'}, Finnhub key {'found' if FINNHUB_KEY else 'missing'}")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=GEMINI_API_KEY
)

search = DuckDuckGoSearchResults(backend="news", num_results=10)

SEARCH_QUERIES = [
    "Nifty 50 Sensex BSE NSE market today India",
    "midcap smallcap stock surge crash India today",
    "Indian company quarterly results earnings profit loss today",
    "NSE BSE company deal contract order win India today",
    "India company merger acquisition stake buyout news today",
    "SEBI penalty fine suspension ban Indian company today",
    "RBI policy rate inflation impact Indian banking stocks",
    "Indian IT TCS Infosys Wipro HCL software news today",
    "Indian banking HDFC ICICI SBI Axis NPA news today",
    "Indian pharma Cipla Sun Reddy FDA approval news today",
    "Indian auto Tata Motors Maruti Hero TVS EV news today",
    "Indian energy Reliance ONGC NTPC coal power news today",
    "Global crude oil price India energy stock impact",
    "US Fed dollar rupee India Sensex impact today",
    "India smallcap company IPO listing allotment news today"
]

RSS_FEEDS = [
    {"name": "ET Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
    {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml"},
    {"name": "Business Standard", "url": "https://www.business-standard.com/rss/markets-106.rss"},
    {"name": "LiveMint Markets", "url": "https://www.livemint.com/rss/markets"},
    {"name": "Google News Stocks", "url": "https://news.google.com/rss/search?q=india+stock+NSE+BSE+company+results&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Deals", "url": "https://news.google.com/rss/search?q=india+company+deal+contract+merger+acquisition+order&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Midcap", "url": "https://news.google.com/rss/search?q=india+midcap+smallcap+company+stock+news&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Reddit IndianStockMarket", "url": "https://www.reddit.com/r/IndianStockMarket/.rss"},
    {"name": "Reddit IndiaInvestments", "url": "https://www.reddit.com/r/IndiaInvestments/.rss"}
]

prompt_template = PromptTemplate.from_template("""
You are an expert Indian stock market analyst (NSE/BSE).

Below is a live news feed collected right now from multiple sources:
BSE official announcements, Reddit investor communities, RSS feeds, NewsAPI, Finnhub, and DuckDuckGo.

Your task:
 - Scan ALL news items and identify every specific company or sector that is impacted.
 - For each, determine whether the news is positive or negative for the stock price.
 - Give a clear actionable signal: BUY, SELL, or HOLD.

Format STRICTLY as an HTML Telegram message. Use <b> tags for bold and <i> tags for italics. Do NOT use Markdown asterisks.

Use this exact layout for each stock or sector identified:

<b>[Company Name] ([NSE/BSE ticker if known])</b>
<i>News:</i> [summary of what happened]
<i>Signal:</i> BUY/SELL/HOLD
<i>Why:</i> [ reason this moves the stock up or down]

Rules:
1. List the TOP 5 most actionable signals only.
2. If only a sector is impacted (e.g., Banking, IT, Pharma), use the sector name and a key ETF or index.
3. Do NOT include any greeting, intro, or closing text. Only the signals formatted as requested.

Live News Feed:
{news_data}

Stock Signals:
""")

chain = prompt_template | llm

def fetch_bse_announcements():
    """
    Fetches official BSE corporate announcements.
    Completely free, no API key. Covers every listed company.
    """
    headlines = []
    url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    params = {
        "strcat": "-1", "strPrevDate": "", "strscrip": "",
        "strSearch": "", "strToDate": "", "strType": "C", "subcategory": "-1"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bseindia.com/"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        announcements = data.get("Table", [])
        for item in announcements:
            company = item.get("SLONGNAME", "Unknown Company").strip()
            subject = item.get("NEWSSUB", item.get("HEADLINE", "No Subject")).strip()
            if company and subject:
                headlines.append(f"[BSE Announcement] {company}: {subject}")
        print(f"BSE Announcements: {len(headlines)} items")
    except Exception as e:
        print(f"Warning: BSE announcements failed: {e}")
    return "\n".join(headlines)

def fetch_newsapi_news():
    """
    Fetches news from NewsAPI.org.
    Requires a NEWSAPI_KEY from environment variables or defined globally.
    """
    if not NEWSAPI_KEY:
        print("NewsAPI: skipped (no NEWSAPI_KEY in .env)")
        return ""
    headlines = []
    queries = ["India stock market company earnings results", "india company deal contract merger acquisition NSE BSE"]
    try:
        for q in queries:
            params = {"q": q, "language": "en", "sortBy": "publishedAt", "pageSize": 15, "apiKey": NEWSAPI_KEY}
            resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=15)
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            for article in articles:
                title = article.get("title", "")
                desc = (article.get("description") or "")[:150]
                if title and "[Removed]" not in title:
                    headlines.append(f"[NewsAPI] {title}: {desc}...")
        print(f"NewsAPI: {len(headlines)} items")
    except Exception as e:
        print(f"Warning: NewsAPI failed: {e}")
    return "\n".join(headlines)

def fetch_finnhub_news():
    """
    Finnhub free tier: 60 calls/min, no daily limit.
    Sign up: https://finnhub.io/register then add FINNHUB_KEY to .env
    """
    if not FINNHUB_KEY:
        print("Finnhub: skipped (no FINNHUB_KEY in .env)")
        return ""
    headlines = []
    try:
        params = {"category": "general", "minId": 0, "token": FINNHUB_KEY}
        resp = requests.get("https://finnhub.io/api/v1/news", params=params, timeout=15)
        resp.raise_for_status()
        news_items = resp.json()
        for item in news_items[:20]:
            headline = item.get("headline", "").strip()
            summary = (item.get("summary") or "")[:150].strip()
            if headline:
                headlines.append(f"[Finnhub] {headline}: {summary}...")
        print(f"Finnhub: {len(headlines)} items")
    except Exception as e:
        print(f"Warning: Finnhub failed: {e}")
    return "\n".join(headlines)

def fetch_rss_news():
    """
    Pulls latest headlines from free Indian financial RSS + Reddit feeds.
    """
    headlines = []
    for feed_info in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            source = feed_info["name"]
            count = 0
            for entry in feed.entries[:12]:
                title = entry.get("title", "").strip()
                raw_summary = entry.get("summary", entry.get("description", ""))
                summary = re.sub(r"<[^>]+>", "", raw_summary).strip()[:200]
                if title:
                    headlines.append(f"[{source}] {title}: {summary}...")
                    count += 1
            print(f"{source}: {count} items")
        except Exception as e:
            source_name = feed_info.get('name', 'Unknown Source')
            print(f"Warning: RSS failed for {source_name}: {e}")
    return "\n".join(headlines)

def fetch_ddg_news():
    """
    Uses DuckDuckGoSearchResults tool to fetch news.
    This is a fallback if RSS and APIs fail, but can be unreliable due to scraping blocks.
    """
    all_results = []
    for query in SEARCH_QUERIES:
        try:
            result = search.invoke(query)
            if result:
                all_results.append(result)
        except Exception as e:
            print(f"Warning: DuckDuckGo failed for query '{query}': {e}")
    return "\n".join(all_results)

def fetch_all_news():
    """
    Combines all 5 sources: BSE, NewsAPI, Finnhub, RSS/Reddit, and DuckDuckGo.
    """
    sections = []
    print("--- Starting News Aggregation ---")
    bse = fetch_bse_announcements()
    if bse: sections.append("== BSE OFFICIAL CORPORATE ANNOUNCEMENTS ==\n" + bse)
    newsapi = fetch_newsapi_news()
    if newsapi: sections.append("== NEWSAPI (India Company News) ==\n" + newsapi)
    finnhub = fetch_finnhub_news()
    if finnhub: sections.append("== FINNHUB MARKET NEWS ==\n" + finnhub)
    rss = fetch_rss_news()
    if rss: sections.append("== RSS + REDDIT FEEDS ==\n" + rss)
    ddg = fetch_ddg_news()
    if ddg: sections.append("== DUCKDUCKGO SEARCH RESULTS ==\n" + ddg)
    combined = "\n\n".join(sections)
    print(f"--- Aggregation Complete: {len(combined)} total characters ---")
    return combined

def send_telegram_message(message_text):
    """Sends the formatted message via Telegram using HTML mode."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Telegram market brief sent successfully!")
        else:
            print(f"❌ Failed to send: {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")

def job():
    """
    Collects news from all 5 sources, generates BUY/SELL signals, 
    and sends them to Telegram.
    """
    now = time.localtime()
    if not (8 <= now.tm_hour < 24):
        print(f"Market closed at {time.strftime('%H:%M:%S')}. Skipping.")
        return
    print(f"\n--- Stock Signal Run at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    try:
        raw_news = fetch_all_news()
        if not raw_news or not raw_news.strip():
            print("No news found this cycle.")
            return
        print(f"\nTotal combined news: {len(raw_news)} chars")
        response = chain.invoke({"news_data": raw_news})
        signals = response.content if hasattr(response, 'content') else response
        if signals:
            send_telegram_message(signals)
        else:
            print("Gemini returned an empty response.")
    except Exception as e:
        print(f"Error during job execution: {e}")

schedule.every(10).minutes.do(job)
job() 

while True:
    schedule.run_pending()
    time.sleep(1)