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
    "India IPO listing stock debut today NSE BSE",
    "India company block deal bulk deal stake sale today",
    "India FII FPI institutional buying selling today NSE",
    "India budget tax import export duty impact sector today"
]

# RSS Feeds
RSS_FEEDS = [
    # ET MARKETS & ECONOMY
    {"name": "ET Markets - All Latest", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
    {"name": "ET Markets - Stocks", "url": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"},
    {"name": "ET Markets - IPOs", "url": "https://economictimes.indiatimes.com/markets/ipos/rssfeeds/14658208.cms"},
    {"name": "ET Economy", "url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/13733806.cms"},
    
    # MONEYCONTROL
    {"name": "Moneycontrol Latest", "url": "https://www.moneycontrol.com/rss/latestnews.xml"},
    {"name": "Moneycontrol Markets", "url": "https://www.moneycontrol.com/rss/marketreports.xml"},
    {"name": "Moneycontrol Business", "url": "https://www.moneycontrol.com/rss/business.xml"},
    
    # LIVEMINT
    {"name": "LiveMint Markets", "url": "https://www.livemint.com/rss/markets"},
    {"name": "LiveMint Companies", "url": "https://www.livemint.com/rss/companies"},
    
    # BUSINESS STANDARD
    {"name": "Business Standard Markets", "url": "https://www.business-standard.com/rss/markets-106.rss"},
    {"name": "Business Standard Companies", "url": "https://www.business-standard.com/rss/companies-101.rss"},
    {"name": "Business Standard Economy", "url": "https://www.business-standard.com/rss/economy-102.rss"},
    
    # HINDU BUSINESSLINE
    {"name": "Hindu BusinessLine Markets", "url": "https://www.thehindubusinessline.com/markets/feeder/default.rss"},
    {"name": "Hindu BusinessLine Companies", "url": "https://www.thehindubusinessline.com/companies/feeder/default.rss"},
    
    # BROADCAST & GLOBAL
    {"name": "CNBC TV18 Markets", "url": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/market.xml"},
    {"name": "CNBC TV18 Economy", "url": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/economy.xml"},
    {"name": "Investing.com India", "url": "https://in.investing.com/rss/news_301.rss"},
    {"name": "Financial Express Market", "url": "https://www.financialexpress.com/market/feed/"},
    {"name": "Financial Express Economy", "url": "https://www.financialexpress.com/economy/feed/"},
    {"name": "Zee Business", "url": "https://www.zeebiz.com/rss.xml"},

    # TIER 2: GOOGLE NEWS REAL-TIME FILTERS (Last 24 Hours)
    {"name": "Google News RBI & Banks", "url": "https://news.google.com/rss/search?q=RBI+monetary+policy+OR+bank+regulations+India+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News SEBI", "url": "https://news.google.com/rss/search?q=SEBI+circular+OR+penalty+OR+market+rule+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Govt Orders", "url": "https://news.google.com/rss/search?q=Government+of+India+contract+OR+tenders+defense+railways+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Rupee/Forex", "url": "https://news.google.com/rss/search?q=Indian+Rupee+USD+INR+surge+crash+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Deals", "url": "https://news.google.com/rss/search?q=india+company+deal+contract+mergers+acquisitions+order+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Stocks NSE BSE", "url": "https://news.google.com/rss/search?q=india+stock+NSE+BSE+company+results+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News IT Sector", "url": "https://news.google.com/rss/search?q=india+IT+sector+Infosys+TCS+Wipro+HCL+results+contract+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Pharma", "url": "https://news.google.com/rss/search?q=India+pharma+USFDA+approval+drug+recall+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News IPO", "url": "https://news.google.com/rss/search?q=India+IPO+listing+allotment+NSE+BSE+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News FII", "url": "https://news.google.com/rss/search?q=FII+FPI+institutional+investor+india+buying+selling+when:1d&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Google News Auto Sector", "url": "https://news.google.com/rss/search?q=India+auto+sector+sales+EV+Tata+Motors+Maruti+when:1d&hl=en-IN&gl=IN&ceid=IN:en"}
]