# CMIN-IN: Indian Stock Financial Dataset

This pipeline creates a dataset for Indian stocks similar to the [CMIN-US dataset](https://github.com/BigRoddy/CMIN-Dataset) from the ACL2023 paper "Causality-Guided Multi-Memory Interaction Network for Multivariate Stock Price Movement Prediction".

## Stocks Covered (15 major NSE stocks)

| Symbol | Company | Sector |
|--------|---------|--------|
| RELIANCE.NS | Reliance Industries | Conglomerate |
| TCS.NS | Tata Consultancy Services | IT |
| HDFCBANK.NS | HDFC Bank | Banking |
| ICICIBANK.NS | ICICI Bank | Banking |
| INFY.NS | Infosys | IT |
| HINDUNILVR.NS | Hindustan Unilever | FMCG |
| ITC.NS | ITC Limited | FMCG |
| SBIN.NS | State Bank of India | Banking |
| BHARTIARTL.NS | Bharti Airtel | Telecom |
| KOTAKBANK.NS | Kotak Mahindra Bank | Banking |
| LT.NS | Larsen & Toubro | Infrastructure |
| ASIANPAINT.NS | Asian Paints | Paints |
| MARUTI.NS | Maruti Suzuki | Auto |
| SUNPHARMA.NS | Sun Pharma | Pharma |
| TITAN.NS | Titan Company | Consumer |

## Data Period
~3 years (2023-10-10 to 2026-10-09)

## Output Structure

```
CMIN-IN/
├── news/
│   ├── raw/                    # CSV files per stock
│   │   ├── RELIANCE.csv
│   │   ├── TCS.csv
│   │   └── ...
│   └── preprocessed/           # JSONL files per day per stock
│       ├── RELIANCE/
│       │   ├── 2024-01-15
│       │   └── 2024-01-16
│       └── ...
└── price/
    ├── raw/                    # CSV files per stock (OHLCV)
    │   ├── RELIANCE.csv
    │   ├── TCS.csv
    │   └── ...
    └── processed/              # Reserved for future processing
```

## File Formats

### Price Data (CMIN-IN/price/raw/{SYMBOL}.csv)
```
Date,Open,High,Low,Close,Volume,Adj Close
2023-10-10,1139.53,1145.14,1138.15,1140.45,10236032,1140.45
...
```
Matches CMIN-US price format exactly.

### News Raw Data (CMIN-IN/news/raw/{SYMBOL}.csv)
```
date,datetime,title,summary,full_text,provider,url
2026-10-09,2026-10-09 02:45:37,"Title","Summary","Full text","provider.com","https://..."
...
```

### News Preprocessed (CMIN-IN/news/preprocessed/{SYMBOL}/{YYYY-MM-DD})
JSONL format (one JSON per line):
```json
{"text": ["Tokenized", "news", "headline", "..."], "created_at": "2026-10-09 02:45:37"}
{"text": ["Another", "news", "item", "..."], "created_at": "2026-10-09 00:30:00"}
```
Matches CMIN-US preprocessed format exactly.

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run complete pipeline
python run_pipeline.py

# Or run individual steps
python fetch_data.py      # Price data only
python fetch_news_enhanced.py  # News data only
```

## Data Sources

- **Price Data**: Yahoo Finance (via yfinance)
- **News Data**: RSS feeds from:
  - Economic Times Markets
  - Moneycontrol
  - Business Standard
  - LiveMint
  - Yahoo Finance RSS per stock

## Requirements
- Python 3.8+
- yfinance
- pandas
- feedparser
- requests

## Notes

- News coverage varies by stock (large caps like RELIANCE, TCS, INFY have more coverage)
- Some stocks may have limited news from RSS sources
- Price data is comprehensive for all 15 stocks
- Format is compatible with CMIN-US processing code