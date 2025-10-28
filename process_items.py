import re
import csv
import pandas as pd

def generate_search_terms(item_desc):
    # 1. Remove parenthetical content (like codes or special offers)
    cleaned_desc = re.sub(r'\s*\(.*?\)\s*', ' ', item_desc).strip()
    
    # 2. Remove special words (like "عرض سعر", "خصم", "مجانا", "زياده", "عرض")
    special_words = r'\b(عرض|خصم|مجانا|زياده|سعر|ك\*|علبه\*|لفه\*|شنطه\*|كارت\*|برومو باك|برطمان|انبوبه|كيس|حصائر|مكينه|فرشه)\b'
    cleaned_desc = re.sub(special_words, '', cleaned_desc, flags=re.IGNORECASE).strip()
    
    # 3. Normalize spaces and remove extra characters
    cleaned_desc = re.sub(r'\s+', ' ', cleaned_desc).strip()
    
    # 4. Generate terms: most specific to least specific
    
    # Simple tokenization for initial keywords
    tokens = cleaned_desc.split()
    
    # A simple approach to get a few search terms:
    # Term 1 (Most specific): The full cleaned description
    term1 = cleaned_desc
    
    # Term 2: Brand name + Product type + Size (if available)
    # This is a heuristic and might need manual refinement, but we'll try to automate it.
    # For now, let's just take the first few words as a slightly less specific term.
    term2 = ' '.join(tokens[:5]) if len(tokens) > 5 else cleaned_desc
    
    # Term 3 (Least specific): Brand name + Product type (e.g., "بانتين شامبو")
    # Let's try to extract the first two or three words as the most generic.
    term3 = ' '.join(tokens[:3]) if len(tokens) > 3 else cleaned_desc
    
    # Filter out duplicates and ensure non-empty
    terms = [t for t in [term1, term2, term3] if t]
    terms = list(pd.unique(terms))
    
    return ' | '.join(terms)

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_items = f.read().splitlines()
    
    # Remove empty lines
    raw_items = [item.strip() for item in raw_items if item.strip()]
    
    data = []
    for item in raw_items:
        search_terms = generate_search_terms(item)
        data.append({
            'Original Name': item,
            'Search Keyword': search_terms,
            'Item Name on Carrefour': '',
            'Price': ''
        })
        
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
    print(f"Processed {len(data)} items and saved to {output_path}")

if __name__ == "__main__":
    process_file('items_list_raw.txt', 'price_list_draft.csv')
