import time
import re
import requests
import feedparser
from langchain_community.tools import DuckDuckGoSearchResults
from config import NEWSAPI_KEY, FINNHUB_KEY, SEARCH_QUERIES, RSS_FEEDS

# Create TWO separate search tools for DuckDuckGo
search_news = DuckDuckGoSearchResults(backend="news", num_results=15)
search_web = DuckDuckGoSearchResults(backend="text", num_results=15) 

def fetch_bse_announcements():
    headlines = []
    url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    params = {"strcat": "-1", "strPrevDate": "", "strscrip": "", "strSearch": "", "strToDate": "", "strType": "C", "subcategory": "-1"}
    headers = {"User-Agent": "Mozilla/5.0"}
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

def fetch_nse_announcements():
    url = "https://www.nseindia.com/api/corporate-announcements"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        resp = session.get(url, headers=headers)
        data = resp.json()
        headlines = []
        for item in data[:50]:
            company = item.get("symbol", "")
            subject = item.get("subject", "")
            headlines.append(f"[NSE Announcement] {company}: {subject}")
        return "\n".join(headlines)
    except Exception as e:
        print("Warning: NSE announcements failed:", e)
        return ""

def fetch_fii_dii():
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        resp = session.get(url, headers=headers)
        data = resp.json()
        return f"[FII/DII] {data}"
    except:
        return ""

def fetch_newsapi_news(yesterday_str):
    if not NEWSAPI_KEY:
        print("NewsAPI: skipped (no NEWSAPI_KEY in config)")
        return ""
    headlines = []
    queries = ["Indian stock market business news NSE BSE", "India corporate announcements updates today"]
    try:
        for q in queries:
            params = {"q": q, "language": "en", "sortBy": "publishedAt", "from": yesterday_str, "pageSize": 15, "apiKey": NEWSAPI_KEY}
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
    if not FINNHUB_KEY:
        print("Finnhub: skipped (no FINNHUB_KEY in config)")
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
            print(f"Warning: RSS failed for {feed_info.get('name')}: {e}")
    return "\n".join(headlines)

def fetch_ddg_news():
    all_results = []
    for query in SEARCH_QUERIES:
        try:
            if "site:" in query:
                result = search_web.invoke(query)
            else:
                result = search_news.invoke(query)
            if result:
                all_results.append(result)
        except Exception as e:
            print(f"Warning: DuckDuckGo failed for query '{query}': {e}")
        time.sleep(2) 
    return "\n".join(all_results)

def fetch_all_news(yesterday_str):
    sections = []
    print("--- Starting News Aggregation ---")
    
    bse = fetch_bse_announcements()
    if bse: sections.append("== BSE OFFICIAL CORPORATE ANNOUNCEMENTS ==\n" + bse)
    
    nse = fetch_nse_announcements()
    if nse: sections.append("== NSE OFFICIAL CORPORATE ANNOUNCEMENTS ==\n" + nse)
    
    fii_dii = fetch_fii_dii()
    if fii_dii: sections.append("== FII/DII TRADES ==\n" + fii_dii)
    
    newsapi = fetch_newsapi_news(yesterday_str)
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