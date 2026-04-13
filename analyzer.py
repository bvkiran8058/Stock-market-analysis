from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config import GEMINI_API_KEY
import re

# 1. Setup Model Waterfall
# Updated with exact model strings from your genai.list_models() output
llm_primary = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview", 
    api_key=GEMINI_API_KEY
)

llm_backup_1 = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    api_key=GEMINI_API_KEY
)

llm_backup_2 = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    api_key=GEMINI_API_KEY
)

llm_backup_3 = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    api_key=GEMINI_API_KEY
)

# Chain them together for fallback protection
llm = llm_primary.with_fallbacks([llm_backup_1, llm_backup_2, llm_backup_3])

# 2. Setup Prompt
prompt_template = PromptTemplate.from_template("""
You are an expert Indian stock market analyst specialized in NSE/BSE markets.

TODAY'S DATE IS: {today_date}

CRITICAL GROUNDING RULES:
1. You must ONLY use information that is explicitly present in the "Live News Feed" section below.
2. DO NOT use pre-existing knowledge, oast data, memory, or assumptions about companies. 
3. If a piece of news is not in the feed, it DOES NOT exist. Do not invent or extrapolate.
4. If you are uncertain about a ticker symbol, write "?" instead of guessing.
5. If the news provides no clear financial direction, the signal MUST be HOLD.

YOUR TASK:
 - Scan ALL news items to identify every specific company or sector that is impacted. 
 - For each, determine whether the news is positive, negative, or neutral for the stock price.
 - Give a clear actionable signal (BUY/SELL/HOLD) based on the news impact.
 - Assign as signal strength: STRONG(direct, unambiguous impact), MEDIUM (moderate or indirect impact), WEAK (minor, speculative or mixed).
 - Cross-reference with any technical insights you can glean from the news (e.g. "RSI is oversold at 28, MACD just had a bullish crossover") to adjust your confidence in the signal.

FORMATTING RULES:
- Format STRICTLY as an HTML message for Telegram.
- Use <b> tags for bold and <i> tags for italics.
- DO NOT use Markdown asterisks (*) or underscores (_).

EXACT LAYOUT PER ITEM:

<b>[Company Name] ([NSE/BSE ticker or ?])</b>
<i>News:</i> [One-sentence summary of the event sourced strictly from the feed.]
<i>Sector:</i> [Give the sector if the news impacts a broader industry or government policy, e.g. "Banking Sector". If it's specific to one company, write "N/A".]
<i>Signal:</i> [BUY/SELL/HOLD] | <b>Strength: [STRONG/MEDIUM/WEAK]</b> 
<i>Whyy:</i> [Specific reason from news why this moves the price.]
<i>Technicals:</i> [RSI and MACD insight from Technical Snapshot, or "N/A" if not available.]
<i>SL:</i> [Stop-loss % e.g., -2.0% for BUY / +2.0% for SELL / N/A for HOLD] | <i>TP:</i> [Take-profit % e.g., +5.0% for BUY / -5.0% for SELL / N/A for HOLD]
<i>Source:</i> [Exact source tag(s) from the news feed.]
<i>Date & Time:</i> [dd/mm/yyyy HH:mm as published in the news item.]

SL/TP GUIDELINES (Apply when news does not specify levels):
- STRONG signal: SL ±2.0%, TP ±10.0%
- MEDIUM signal: SL ±2.0%, TP ±5.0%
- WEAK signal:   SL ±1.5%, TP ±3.0%

ADDITIONAL RULES:
1. List UP TO 15 most actionable signals. NEVER invent news to reach a count. It is perfectly fine to have only 1 or 2 signals if the news feed is light. Focus on quality, not quantity.
2. MACRO EVENTS: If news impacts a broader government rule or RBI policy, list the specific SECTOR (e.g., <b>Banking Sector</b>).
3. DATE FILTERING IS ABSOLUTE: Ignore any news older than {yesterday_date}. Completely discard older articles from before {yesterday_date}.
4. Leave a blank empty line between the end of one company's block and the start of the next.
5. Do NOT include any greeting, intro, closing text, or disclaimers. Output ONLY the signal blocks.
6. ZERO HALLUCINATION: Every fact must trace back to the feed. If no supporting news, do NOT generate a signal.
7. TECHNICAL CONFIRMATION: IF RSI > 70 on a BUY signal, or RSI < 30 on a SELL signal, downgrade strength by one level (e.g., STRONG to MEDIUM, MEDIUM to WEAK).

Technical Snapshot (live price + RSI/MACD - use to validate signals, not as a news source):
{tech_data}

Live News Feed:
{news_data}

Stock Signals:
""")

chain = prompt_template | llm

filter_prompt_template =PromptTemplate.from_template("""
You are a strict news curator for an Indian stock market signal bot.

TODAY'S DATE: {today_date}
CUTOFF (Discard anything older than this date): {yesterday_date}

Apply ALL rules below to the raw news feed and return only the items that survive:

RULE 1 - RELEVANCE: Keep ONLY news with a direct financial or market impact on Indian stocks, sectors, indices (NSE/BSE/Nifty/Sensex), or the broader Indian macro-economy (RBI, SEBI, Union Budget, FII/DII flows, corporate results, deals, IPOs, regulations). Discard sports, entertainment, lifestyle, weather, and international news with zero India market link.

RULE 2 - DEDUPLICATION: If the same story appears from multiple sources, keep only the single most informative version. Remove near-duplicates where the headline is simply reworded.

RULE 3 - DATE FILTER: Discard any article explicitly dated before {yesterday_date}. Ensure all output news is fresh.

RULE 4 - SIGNAL POTENTIAL: Discard vague filler phrases like "markets may be volatile," "experts suggest caution," or "stay tuned for updates" if they contain no specific company news, data points, or events.

RAW NEWS FEED:
{news_data}

FILTERED NEWS (one item per line, source tag preserved):
""")

filter_chain = filter_prompt_template | llm

def filter_news(raw_news: str, today_str: str, yesterday_str: str) -> str:
    """
    LLM pre-filter: removes off-topic, duplicate, and stale items from the 
    combined news feed before the main analysis pass.
    Falls back to the raw feed if the filter call fails.
    """
    
    if not raw_news or not raw_news.strip():
        return raw_news

    try:
        print("--- Running LLM news filter pass ---")
        
        # Invoking the filter chain with correct key-value pairs
        response = filter_chain.invoke({
            "news_data": raw_news,
            "today_date": today_str,
            "yesterday_date": yesterday_str
        })
        
        # Handle different response types (BaseMessage or String)
        filtered = response.content if hasattr(response, "content") else str(response)
        # Ensure filtered is a string (handle case where content might be a list)
        if isinstance(filtered, list):
            filtered = "\n".join(str(item) for item in filtered)
        filtered = str(filtered).strip()

        if filtered:
            # Calculate the reduction percentage
            raw_len = max(len(raw_news), 1)
            filtered_len = len(filtered)
            reduction = round((1 - (filtered_len / raw_len)) * 100)
            
            print(f"Filter pass complete: {raw_len} -> {filtered_len} chars ({reduction}% reduction)")
            return filtered
        
        print("Filter returned empty, falling back to raw feed")
        return raw_news

    except Exception as e:
        print(f"Warning: LLM filter pass failed ({e})")
        # Ensure the process continues even if filtering fails
        return raw_news

ticker_extract_prompt = PromptTemplate.from_template("""
From the financial news headlines below, extract the NSE ticker symbols of all specifically named Indian companies.

Return ONLY a comma-separated list of NSE tickers in uppercase (e.g. RELIANCE, TCS, INFY).

CRITICAL RULES:
- Skip sectors (e.g., "BANKING") and indices (e.g., "NIFTY").
- Only include specific company tickers.
- Skip any company whose NSE ticker you are not 100% confident about.
- Return ONLY the tickers. No explanations, no headers, no intro.

NEWS:
{news_data}

NSE TICKERS:
""")

ticker_extract_chain = ticker_extract_prompt | llm

def extract_tickers(filtered_news: str) -> list:
    """
    Uses LLM to extract NSE ticker symbols from filtered news. 
    Returns a clean, unique list of uppercase tickers.
    """
    if not filtered_news or not filtered_news.strip():
        return []

    try:
        # Invoking the chain with the correct input key
        resp = ticker_extract_chain.invoke({"news_data": filtered_news})
        
        # Extract content from response object
        raw = resp.content if hasattr(resp, "content") else str(resp)
        # Ensure raw is a string (handle case where content might be a list)
        if isinstance(raw, list):
            raw = ",".join(str(item) for item in raw)
        raw = str(raw).strip()
        
        # Split by commas, newlines, or whitespace
        tokens = re.split(r"[,\n\s]+", raw)
        
        # Validates that tickers follow the NSE format (2-20 alphanumeric characters)
        # Fixed the regex syntax: [A-Z0-9]{1,19} instead of (1,19)
        tickers = [
            t.strip().upper() 
            for t in tokens 
            if re.fullmatch(r"[A-Z][A-Z0-9]{1,19}", t.strip().upper())
        ]
        
        # Remove duplicates while preserving order
        unique_tickers = list(dict.fromkeys(tickers))
        
        print(f"Extracted tickers: {unique_tickers}")
        return unique_tickers

    except Exception as e:
        print(f"Warning: Ticker extraction failed ({e})")
        return []
    
premarket_prompt = PromptTemplate.from_template("""
You are an expert Indian stock market analyst. It is pre-market time (before 9:15 AM IST).

TODAY'S DATE: {today_date}

Based on the overnight news and technical data below, build a pre-market watchlist of stocks likely to see significant movement at market open.

Format STRICTLY as an HTML Telegram message. Use <b> for bold and <i> for italics. DO NOT use Markdown asterisks.

Use this EXACT layout for each stock:

<b>[Company Name] ([TICKER or ?])</b>
<i>Bias:</i> <b>Bullish/Bearish/Neutral</b>
<i>Catalyst:</i> [One-line reason explaining what news or event will drive the move at open]
<i>Technicals:</i> [RSI/MACD insight from snapshot, or "N/A"]
<i>Level to Watch:</i> [Key % move or price level to watch, or "N/A"]
<i>Source:</i> [Exact source tag from the news feed]

CRITICAL RULES:
1. List UP TO 10 stocks. Quality over quantity; only include stocks with a clear, specific catalyst. It is okay to have 1 or 2 if the news is light. Do NOT include stocks with vague or generic news that doesn't clearly indicate a strong move at open.
2. ZERO HALLUCINATION: Every entry must trace back to the news feed.
4. Leave a blank line between entries.
5. No intro, no closing text, no disclaimers. Output ONLY the watchlist blocks.

Technical Snapshot:
{tech_data}

Overnight News Feed:
{news_data}

Pre-Market Watchlist:
""")

premarket_chain = premarket_prompt | llm

def premarket_watchlist(filtered_news: str, tech_data: str, today_str: str) -> str:
    try:
        response = premarket_chain.invoke({
            "news_data": filtered_news, 
            "tech_data": tech_data if tech_data else "N/A", 
            "today_date": today_str
        })
        result = response.content if hasattr(response, 'content') else response
        # Ensure result is a string (handle case where content might be a list)
        if isinstance(result, list):
            result = "\n".join(str(item) for item in result)
        return str(result)
    except Exception as e:
        print(f"Warning: Pre-market watchlist generation failed ({e})")
        return ""

def analyze_news(filtered_news: str, tech_data: str, today_str: str, yesterday_str: str) -> str:
    response = chain.invoke({
        "news_data": filtered_news, 
        "today_date": today_str, 
        "yesterday_date": yesterday_str,
        "tech_data": tech_data if tech_data else "N/A"
    })
    result = response.content if hasattr(response, 'content') else response
    # Ensure result is a string (handle case where content might be a list)
    if isinstance(result, list):
        result = "\n".join(str(item) for item in result)
    return str(result)