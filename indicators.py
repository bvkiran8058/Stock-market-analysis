import yfinance as yf
import pandas as pd


def _rsi(close: pd.Series, period: int = 14):
    """Calculates the Relative Strength Index (RSI)."""
    if len(close) < period:
        return None
        
    delta = close.diff().dropna()
    
    # Gain is the positive change, Loss is the absolute of the negative change
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0) 

    # Use EWM for the smoothed moving average (Wilder's Smoothing)
    # alpha = 1/period is equivalent to com = period - 1
    avg_gain = gain.ewm(com=period - 1, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period, adjust=False).mean()

    # Avoid division by zero
    rs = avg_gain / avg_loss
    rsi_val = 100 - (100 / (1 + rs))
    
    val = rsi_val.iloc[-1]
    return round(float(val), 2) if pd.notna(val) else None\

def _macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculates MACD Line, Signal Line, and Histogram."""
    if len(close) < slow:
        return None, None, None

    # Standard MACD calculation: Fast EMA - Slow EMA
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    
    hist = macd_line - signal_line

    return (
        round(float(macd_line.iloc[-1]), 2),
        round(float(signal_line.iloc[-1]), 2),
        round(float(hist.iloc[-1]), 2)
    )

def get_technical_summary(tickers: list) -> str:
    """
    Fetches 60 days of daily OHLCV from NSE for each ticker, 
    computes RSI(14) and MACD (12,26,9), and returns a formatted string.
    """
    if not tickers:
        return ""

    lines = []
    # Cap to 15 to keep network latency and prompt size manageable
    for symbol in tickers[:15]: 
        try:
            # Ensure the ticker has the .NS suffix for Yahoo Finance India
            yf_ticker = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol
            ticker_obj = yf.Ticker(yf_ticker)
            hist = ticker_obj.history(period="60d")

            if hist.empty or len(hist) < 30:
                continue

            close = hist["Close"]
            last = round(float(close.iloc[-1]), 2)
            prev = round(float(close.iloc[-2]), 2)
            
            # Calculate Percentage Change
            chg = round(((last - prev) / prev) * 100, 2)
            
            # Use the custom functions defined previously
            rsi_val = _rsi(close)
            macd_val, sig_val, hist_val = _macd(close)

            # Determine RSI Sentiment Tag
            rsi_tag = ""
            if rsi_val is not None:
                if rsi_val < 30:
                    rsi_tag = " [OVERSOLD]"
                elif rsi_val > 70:
                    rsi_tag = " [OVERBOUGHT]"

            # Determine MACD Sentiment Tag
            macd_tag = "Bullish" if (hist_val and hist_val > 0) else "Bearish"

            # Format the output line
            sign = "+" if chg >= 0 else ""
            lines.append(
                f"{symbol}: {last} ({sign}{chg}%) | "
                f"RSI(14)={rsi_val}{rsi_tag} | "
                f"MACD Hist={hist_val} [{macd_tag}]"
            )
            print(f"Technicals fetched: {symbol}")

        except Exception as e:
            print(f"Warning: Technical fetch failed for {symbol}: {e}")

    return "\n".join(lines)