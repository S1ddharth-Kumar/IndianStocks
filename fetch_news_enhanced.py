import os
import requests
import feedparser
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import re
from indian_stocks import STOCK_SYMBOLS, INDIAN_STOCKS

DATA_DIR = "CMIN-IN"
NEWS_RAW_DIR = os.path.join(DATA_DIR, "news", "raw")
NEWS_PREPROCESSED_DIR = os.path.join(DATA_DIR, "news", "preprocessed")

for d in [NEWS_RAW_DIR, NEWS_PREPROCESSED_DIR]:
    os.makedirs(d, exist_ok=True)

END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=3*365)

SEARCH_TERMS = {
    "RELIANCE.NS": ["Reliance Industries", "RIL", "Mukesh Ambani"],
    "TCS.NS": ["TCS", "Tata Consultancy Services", "TCS stock"],
    "HDFCBANK.NS": ["HDFC Bank", "HDFC Bank stock"],
    "ICICIBANK.NS": ["ICICI Bank", "ICICI Bank stock"],
    "INFY.NS": ["Infosys", "Infosys stock", "INFY"],
    "HINDUNILVR.NS": ["Hindustan Unilever", "HUL stock"],
    "ITC.NS": ["ITC Limited", "ITC stock"],
    "SBIN.NS": ["State Bank of India", "SBI stock", "SBIN"],
    "BHARTIARTL.NS": ["Bharti Airtel", "Airtel stock"],
    "KOTAKBANK.NS": ["Kotak Mahindra Bank", "Kotak Bank stock"],
    "LT.NS": ["Larsen Toubro", "L&T stock", "Larsen & Toubro"],
    "ASIANPAINT.NS": ["Asian Paints", "Asian Paints stock"],
    "MARUTI.NS": ["Maruti Suzuki", "Maruti stock"],
    "SUNPHARMA.NS": ["Sun Pharma", "Sun Pharmaceutical stock"],
    "TITAN.NS": ["Titan Company", "Titan stock"],
}

RSS_FEEDS = [
    "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146843.cms",
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://www.moneycontrol.com/rss/marketnews.xml",
    "https://www.moneycontrol.com/rss/businessnews.xml",
    "https://www.business-standard.com/rss/markets-106.rss",
    "https://www.business-standard.com/rss/companies-101.rss",
    "https://www.livemint.com/rss/markets",
    "https://www.livemint.com/rss/companies",
    "https://finance.yahoo.com/rss/headline?s=RELIANCE.NS",
    "https://finance.yahoo.com/rss/headline?s=TCS.NS",
    "https://finance.yahoo.com/rss/headline?s=HDFCBANK.NS",
    "https://finance.yahoo.com/rss/headline?s=ICICIBANK.NS",
    "https://finance.yahoo.com/rss/headline?s=INFY.NS",
    "https://finance.yahoo.com/rss/headline?s=HINDUNILVR.NS",
    "https://finance.yahoo.com/rss/headline?s=ITC.NS",
    "https://finance.yahoo.com/rss/headline?s=SBIN.NS",
    "https://finance.yahoo.com/rss/headline?s=BHARTIARTL.NS",
    "https://finance.yahoo.com/rss/headline?s=KOTAKBANK.NS",
    "https://finance.yahoo.com/rss/headline?s=LT.NS",
    "https://finance.yahoo.com/rss/headline?s=ASIANPAINT.NS",
    "https://finance.yahoo.com/rss/headline?s=MARUTI.NS",
    "https://finance.yahoo.com/rss/headline?s=SUNPHARMA.NS",
    "https://finance.yahoo.com/rss/headline?s=TITAN.NS",
]

def clean_text(text):
    """Clean HTML tags and extra whitespace from text."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_rss_feed(url):
    """Fetch and parse RSS feed."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        return feed.entries
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []

def is_relevant_article(title, summary, search_terms):
    """Check if article is relevant to the stock."""
    text = f"{title} {summary}".lower()
    for term in search_terms:
        if term.lower() in text:
            return True
    return False

def fetch_news_from_rss(symbol, name):
    """Fetch news from RSS feeds for a specific stock."""
    search_terms = SEARCH_TERMS.get(symbol, [name])
    all_articles = []
    
    for feed_url in RSS_FEEDS:
        entries = fetch_rss_feed(feed_url)
        for entry in entries:
            title = clean_text(entry.get('title', ''))
            summary = clean_text(entry.get('summary', entry.get('description', '')))
            
            if not is_relevant_article(title, summary, search_terms):
                continue
            
            pub_time = entry.get('published', entry.get('updated', ''))
            try:
                dt = datetime(*entry.published_parsed[:6]) if entry.get('published_parsed') else datetime.now()
                pub_date = dt.strftime('%Y-%m-%d')
                pub_datetime = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pub_date = datetime.now().strftime('%Y-%m-%d')
                pub_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if dt < START_DATE:
                continue
            
            full_text = f"{title}. {summary}" if summary else title
            provider = feed_url.split('/')[2]
            url = entry.get('link', '')
            
            all_articles.append({
                'date': pub_date,
                'datetime': pub_datetime,
                'title': title,
                'summary': summary,
                'full_text': full_text,
                'provider': provider,
                'url': url
            })
    
    df = pd.DataFrame(all_articles)
    if not df.empty:
        df = df.drop_duplicates(subset=['title', 'url'])
        df = df.sort_values('datetime', ascending=False)
    return df

def save_news_raw(symbol, df):
    """Save raw news data to CSV."""
    if df is not None and not df.empty:
        filepath = os.path.join(NEWS_RAW_DIR, f"{symbol.replace('.NS', '')}.csv")
        df.to_csv(filepath, index=False)
        print(f"  Saved raw news ({len(df)} articles) to {filepath}")
    else:
        print(f"  No news found for {symbol}")

def save_news_preprocessed(symbol, df):
    """Save preprocessed news data in CMIN format (JSONL per day)."""
    if df is None or df.empty:
        return
    
    stock_dir = os.path.join(NEWS_PREPROCESSED_DIR, symbol.replace('.NS', ''))
    os.makedirs(stock_dir, exist_ok=True)
    
    for date, group in df.groupby('date'):
        filepath = os.path.join(stock_dir, date)
        with open(filepath, 'w', encoding='utf-8') as f:
            for _, row in group.iterrows():
                text_tokens = row['full_text'].split()
                entry = {
                    "text": text_tokens,
                    "created_at": row['datetime']
                }
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"  Saved preprocessed news for {date} ({len(group)} articles)")

def main():
    print("=" * 60)
    print("CMIN-IN: Enhanced Indian Stock News Pipeline")
    print("=" * 60)
    print(f"Date range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"Stocks: {len(STOCK_SYMBOLS)}")
    print(f"RSS Feeds: {len(RSS_FEEDS)}")
    print()
    
    for i, symbol in enumerate(STOCK_SYMBOLS):
        name = INDIAN_STOCKS[symbol]
        print(f"\n[{i+1}/{len(STOCK_SYMBOLS)}] Fetching news for {symbol} - {name}")
        
        news_df = fetch_news_from_rss(symbol, name)
        save_news_raw(symbol, news_df)
        save_news_preprocessed(symbol, news_df)
        
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("News pipeline completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()