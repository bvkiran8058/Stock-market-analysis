from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config import GEMINI_API_KEY

# 1. Setup Model Waterfall
llm_primary = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", api_key=GEMINI_API_KEY)
llm_backup_1 = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=GEMINI_API_KEY)
llm_backup_2 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_API_KEY)
llm_backup_3 = ChatGoogleGenerativeAI(model="gemini-3-flash", api_key=GEMINI_API_KEY)

# Chain them together for fallback protection
llm = llm_primary.with_fallbacks([llm_backup_1, llm_backup_2, llm_backup_3])

# 2. Setup Prompt
prompt_template = PromptTemplate.from_template("""
You are an expert Indian stock market analyst (NSE/BSE).
TODAY'S DATE IS: {today_date}

Below is a live news feed collected right now from multiple sources.

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
<i>Date & Time: dd/MM/yyyy - HH:mm</i> [Date and time of the news when it was published]

Rules:
1. List UP TO 15 most actionable signals. It is perfectly fine to list only 2 or 3 signals if there is not much news. NEVER invent news or force old news just to reach 15.
2. MACRO EVENTS: If the news is a broader government rule, RBI policy change, or currency shift (Rupee value), list the specific SECTOR it impacts (e.g., <b>Banking Sector (NIFTY BANK)</b>).
3. DATE FILTERING IS ABSOLUTE: Ignore any news older than {yesterday_date}. If you see an article from 2024, 2025, or anything prior to {yesterday_date}, completely discard it.
4. You MUST leave a blank empty line between the end of one company's block and the start of the next company's block.
5. Do NOT include any greeting, intro, or closing text. Only the signals.

Live News Feed:
{news_data}

Stock Signals:
""")

chain = prompt_template | llm

def analyze_news(raw_news, today_str, yesterday_str):
    response = chain.invoke({
        "news_data": raw_news, 
        "today_date": today_str, 
        "yesterday_date": yesterday_str
    })
    return response.content if hasattr(response, 'content') else response