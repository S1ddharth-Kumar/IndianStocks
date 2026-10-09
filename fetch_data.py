import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from indian_stocks import STOCK_SYMBOLS, INDIAN_STOCKS

DATA_DIR = "CMIN-IN"
NEWS_RAW_DIR = os.path.join(DATA_DIR, "news", "raw")
NEWS_PREPROCESSED_DIR = os.path.join(DATA_DIR, "news", "preprocessed")
PRICE_RAW_DIR = os.path.join(DATA_DIR, "price", "raw")
PRICE_PROCESSED_DIR = os.path.join(DATA_DIR, "price", "processed")

for d in [NEWS_RAW_DIR, NEWS_PREPROCESSED_DIR, PRICE_RAW_DIR, PRICE_PROCESSED_DIR]:
    os.makedirs(d, exist_ok=True)

END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=3*365)

def fetch_price_data(symbol):
    """Fetch historical price data for a stock."""
    print(f"Fetching price data for {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=START_DATE.strftime("%Y-%m-%d"), 
                              end=END_DATE.strftime("%Y-%m-%d"),
                              interval="1d")
        if hist.empty:
            print(f"  No price data for {symbol}")
            return None
        
        hist = hist.reset_index()
        hist.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        hist = hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        hist['Adj Close'] = hist['Close']
        
        return hist
    except Exception as e:
        print(f"  Error fetching price for {symbol}: {e}")
        return None

def save_price_data(symbol, df):
    """Save price data to CSV."""
    if df is not None and not df.empty:
        filepath = os.path.join(PRICE_RAW_DIR, f"{symbol.replace('.NS', '')}.csv")
        df.to_csv(filepath, index=False)
        print(f"  Saved price data to {filepath}")

def fetch_news_data(symbol, name):
    """Fetch news data for a stock using yfinance."""
    print(f"Fetching news for {symbol} ({name})...")
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if not news:
            print(f"  No news found for {symbol}")
            return None
        
        news_data = []
        for article in news:
            content = article.get('content', {})
            title = content.get('title', '')
            summary = content.get('summary', '')
            pub_time = content.get('pubDate', '')
            provider = content.get('provider', {}).get('name', '')
            url = content.get('canonicalUrl', {}).get('url', '')
            
            if pub_time:
                try:
                    dt = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                    pub_date = dt.strftime('%Y-%m-%d')
                    pub_datetime = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pub_date = datetime.now().strftime('%Y-%m-%d')
                    pub_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                pub_date = datetime.now().strftime('%Y-%m-%d')
                pub_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            full_text = f"{title}. {summary}" if summary else title
            
            news_data.append({
                'date': pub_date,
                'datetime': pub_datetime,
                'title': title,
                'summary': summary,
                'full_text': full_text,
                'provider': provider,
                'url': url
            })
        
        df = pd.DataFrame(news_data)
        return df
    except Exception as e:
        print(f"  Error fetching news for {symbol}: {e}")
        return None

def save_news_raw(symbol, df):
    """Save raw news data to CSV."""
    if df is not None and not df.empty:
        filepath = os.path.join(NEWS_RAW_DIR, f"{symbol.replace('.NS', '')}.csv")
        df.to_csv(filepath, index=False)
        print(f"  Saved raw news to {filepath}")

def save_news_preprocessed(symbol, df):
    """Save preprocessed news data in CMIN format (JSONL per day)."""
    if df is None or df.empty:
        return
    
    stock_dir = os.path.join(NEWS_PREPROCESSED_DIR, symbol.replace('.NS', ''))
    os.makedirs(stock_dir, exist_ok=True)
    
    for date, group in df.groupby('date'):
        filepath = os.path.join(stock_dir, date)
        with open(filepath, 'w') as f:
            for _, row in group.iterrows():
                text_tokens = row['full_text'].split()
                entry = {
                    "text": text_tokens,
                    "created_at": row['datetime']
                }
                f.write(json.dumps(entry) + '\n')
        print(f"  Saved preprocessed news for {date}")

def main():
    print("=" * 60)
    print("CMIN-IN: Indian Stock Financial Data Pipeline")
    print("=" * 60)
    print(f"Date range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"Stocks: {len(STOCK_SYMBOLS)}")
    print()
    
    for i, symbol in enumerate(STOCK_SYMBOLS):
        name = INDIAN_STOCKS[symbol]
        print(f"\n[{i+1}/{len(STOCK_SYMBOLS)}] Processing {symbol} - {name}")
        
        price_df = fetch_price_data(symbol)
        save_price_data(symbol, price_df)
        
        news_df = fetch_news_data(symbol, name)
        save_news_raw(symbol, news_df)
        save_news_preprocessed(symbol, news_df)
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Pipeline completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()