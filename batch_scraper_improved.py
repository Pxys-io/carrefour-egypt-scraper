import subprocess
import json
import pandas as pd
import time
import os
from pathlib import Path

# Create directories for storing data
os.makedirs("results", exist_ok=True)
os.makedirs("raw_json", exist_ok=True)

# Read the CSV file with items
df = pd.read_csv('price_list_draft.csv')

# Initialize results
price_list_results = []
all_products_list = []

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
                
                # Save raw JSON to raw_json folder
                raw_json_path = f"raw_json/{sanitized_name}.json"
                with open(raw_json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                products = data.get('products', [])
                
                if products:
                    # Add all products to the comprehensive list
                    for product in products:
                        product_entry = {
                            'search_keyword': search_keyword,
                            'original_item': original_name,
                            'product_id': product.get('id', ''),
                            'product_name': product.get('name', ''),
                            'brand': product.get('brand', {}).get('name', ''),
                            'price_original': product.get('price', {}).get('price', ''),
                            'price_discounted': product.get('price', {}).get('discount', {}).get('price', ''),
                            'discount_percentage': product.get('price', {}).get('discount', {}).get('value', ''),
                            'availability': product.get('availability', {}).get('isAvailable', ''),
                            'category': ' > '.join([c.get('name', '') for c in product.get('category', [])]),
                            'supplier': product.get('supplier', ''),
                            'ean': product.get('ean', '')
                        }
                        all_products_list.append(product_entry)
                    
                    # Get the first product for the price list
                    product = products[0]
                    carrefour_name = product.get('name', 'N/A')
                    
                    # Get the price (use discount price if available)
                    price_info = product.get('price', {})
                    discount = price_info.get('discount', {})
                    if discount and 'price' in discount:
                        price = discount['price']
                    else:
                        price = price_info.get('price', 'N/A')
                    
                    price_list_results.append({
                        'Original Name': original_name,
                        'Search Keyword': search_keyword,
                        'Item Name on Carrefour': carrefour_name,
                        'Price': price
                    })
                    
                    print(f"  ✓ Found {len(products)} products")
                    print(f"  First match: {carrefour_name}")
                    print(f"  Price: {price} EGP")
                else:
                    price_list_results.append({
                        'Original Name': original_name,
                        'Search Keyword': search_keyword,
                        'Item Name on Carrefour': 'Not found',
                        'Price': ''
                    })
                    print(f"  ✗ No products found")
            else:
                price_list_results.append({
                    'Original Name': original_name,
                    'Search Keyword': search_keyword,
                    'Item Name on Carrefour': 'Error',
                    'Price': ''
                })
                print(f"  ✗ JSON file not found")
        else:
            price_list_results.append({
                'Original Name': original_name,
                'Search Keyword': search_keyword,
                'Item Name on Carrefour': 'Error',
                'Price': ''
            })
            print(f"  ✗ Scraper failed")
    
    except subprocess.TimeoutExpired:
        price_list_results.append({
            'Original Name': original_name,
            'Search Keyword': search_keyword,
            'Item Name on Carrefour': 'Timeout',
            'Price': ''
        })
        print(f"  ✗ Timeout")
    except Exception as e:
        price_list_results.append({
            'Original Name': original_name,
            'Search Keyword': search_keyword,
            'Item Name on Carrefour': 'Error',
            'Price': ''
        })
        print(f"  ✗ Exception: {str(e)[:100]}")
    
    # Add a small delay to avoid overwhelming the server
    time.sleep(1)

# Save price list results
price_list_df = pd.DataFrame(price_list_results)
price_list_df.to_csv('carrefour_price_list.csv', index=False, encoding='utf-8')
print(f"\n\nPrice list saved to carrefour_price_list.csv")

# Save all products to a comprehensive database
all_products_df = pd.DataFrame(all_products_list)
all_products_df.to_csv('carrefour_all_products_database.csv', index=False, encoding='utf-8')
print(f"All products database saved to carrefour_all_products_database.csv")
print(f"Total unique products found: {len(all_products_list)}")

# Summary
print(f"\n=== SUMMARY ===")
print(f"Total items processed: {len(price_list_results)}")
print(f"Items found: {len([r for r in price_list_results if r['Item Name on Carrefour'] not in ['Not found', 'Error', 'Timeout']])}")
print(f"Total unique products in database: {len(all_products_list)}")

