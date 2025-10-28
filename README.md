# Carrefour Egypt Price Scraper

Comprehensive web scraper for Carrefour Egypt that extracts product information, pricing, and availability data.

## Overview

The scraper searches for items on the Carrefour Egypt website and extracts:
- Product names as listed on Carrefour
- Original and discounted prices
- Product IDs and EAN codes
- Brand information
- Category hierarchy
- Availability status
- Supplier information

## Files

- `carrefour_scraper.py` - Core scraper
- `batch_scraper_improved.py` - Batch processing script
- `process_items.py` - Item preprocessing
- `carrefour_price_list.csv` - Price list output
- `carrefour_all_products_database.csv` - All products database
- `results/` - JSON responses from searches
- `raw_json/` - Backup JSON data

## Usage

```bash
python3 carrefour_scraper.py "search term"
python3 batch_scraper_improved.py
```

## Requirements

- Python 3.7+
- requests, beautifulsoup4, pandas

## License

Educational and research purposes only.
