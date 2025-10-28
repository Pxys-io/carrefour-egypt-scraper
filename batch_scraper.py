import subprocess
import json
import pandas as pd
import time
import os
from pathlib import Path

# Read the CSV file with items
df = pd.read_csv('price_list_draft.csv')

# Initialize results
results = []

# Process each item
for idx, row in df.iterrows():
    original_name = row['Original Name']
    keywords = row['Search Keyword'].split(' | ')
    
    # Use the most specific keyword (first one)
    search_keyword = keywords[0]
    
    print(f"\n[{idx+1}/{len(df)}] Processing: {original_name}")
    print(f"  Search keyword: {search_keyword}")
    
    # Run the scraper
    try:
        result = subprocess.run(
            ['python3', 'carrefour_scraper.py', search_keyword],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Try to find the saved JSON file
            sanitized_name = search_keyword.replace(' ', '_').lower()
            json_path = f"results/{sanitized_name}.json"
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                products = data.get('products', [])
                
                if products:
                    # Get the first product
                    product = products[0]
                    carrefour_name = product.get('name', 'N/A')
                    
                    # Get the price (use discount price if available)
                    price_info = product.get('price', {})
                    discount = price_info.get('discount', {})
                    if discount and 'price' in discount:
                        price = discount['price']
                    else:
                        price = price_info.get('price', 'N/A')
                    
                    results.append({
                        'Original Name': original_name,
                        'Search Keyword': search_keyword,
                        'Item Name on Carrefour': carrefour_name,
                        'Price': price
                    })
                    
                    print(f"  ✓ Found: {carrefour_name}")
                    print(f"  Price: {price} EGP")
                else:
                    results.append({
                        'Original Name': original_name,
                        'Search Keyword': search_keyword,
                        'Item Name on Carrefour': 'Not found',
                        'Price': ''
                    })
                    print(f"  ✗ No products found")
            else:
                results.append({
                    'Original Name': original_name,
                    'Search Keyword': search_keyword,
                    'Item Name on Carrefour': 'Error',
                    'Price': ''
                })
                print(f"  ✗ JSON file not found")
        else:
            results.append({
                'Original Name': original_name,
                'Search Keyword': search_keyword,
                'Item Name on Carrefour': 'Error',
                'Price': ''
            })
            print(f"  ✗ Scraper failed: {result.stderr[:100]}")
    
    except subprocess.TimeoutExpired:
        results.append({
            'Original Name': original_name,
            'Search Keyword': search_keyword,
            'Item Name on Carrefour': 'Timeout',
            'Price': ''
        })
        print(f"  ✗ Timeout")
    except Exception as e:
        results.append({
            'Original Name': original_name,
            'Search Keyword': search_keyword,
            'Item Name on Carrefour': 'Error',
            'Price': ''
        })
        print(f"  ✗ Exception: {str(e)[:100]}")
    
    # Add a small delay to avoid overwhelming the server
    time.sleep(1)

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv('carrefour_price_list.csv', index=False, encoding='utf-8')
print(f"\n\nResults saved to carrefour_price_list.csv")
print(f"Total items processed: {len(results)}")
print(f"Items found: {len([r for r in results if r['Item Name on Carrefour'] not in ['Not found', 'Error', 'Timeout']])}")

