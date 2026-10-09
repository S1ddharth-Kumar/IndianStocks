#!/usr/bin/env python
"""
CMIN-IN: Indian Stock Financial Data Pipeline
==============================================
Fetches 2-3 years of price data and financial news for 15 major Indian stocks.
Output format matches CMIN-US dataset structure.

Structure:
CMIN-IN/
├── news/
│   ├── raw/           # CSV files per stock with full news articles
│   └── preprocessed/  # JSONL files per day per stock (tokenized text + timestamp)
└── price/
    ├── raw/           # CSV files per stock with OHLCV data
    └── processed/     # (reserved for future processing)

Usage: python run_pipeline.py
"""

import subprocess
import sys

def run_script(script_name):
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def main():
    print("CMIN-IN Pipeline: Indian Stock Financial Data")
    print("=" * 60)
    print("This will fetch ~3 years of data for 15 major Indian stocks:")
    print("  RELIANCE, TCS, HDFCBANK, ICICIBANK, INFY,")
    print("  HINDUNILVR, ITC, SBIN, BHARTIARTL, KOTAKBANK,")
    print("  LT, ASIANPAINT, MARUTI, SUNPHARMA, TITAN")
    print()
    
    # Step 1: Fetch price data
    if not run_script("fetch_data.py"):
        print("Price data fetch failed!")
        return 1
    
    # Step 2: Fetch news data
    if not run_script("fetch_news_enhanced.py"):
        print("News data fetch failed!")
        return 1
    
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print("\nOutput directory: CMIN-IN/")
    print("Structure:")
    print("  CMIN-IN/news/raw/           - Raw news CSV per stock")
    print("  CMIN-IN/news/preprocessed/  - Tokenized JSONL per day per stock")
    print("  CMIN-IN/price/raw/          - OHLCV price CSV per stock")
    print("  CMIN-IN/price/processed/    - (reserved)")
    print("\nFormat matches CMIN-US dataset for compatibility.")
    return 0

if __name__ == "__main__":
    sys.exit(main())