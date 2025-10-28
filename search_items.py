import pandas as pd
import time
import re

# Read the CSV file
df = pd.read_csv('price_list_draft.csv')

# Create a Python script that will be executed in the browser to search and extract data
# We'll process items in batches and use Selenium or similar approach

# For now, let's create a list of search keywords to use
search_keywords = []
for idx, row in df.iterrows():
    keywords = row['Search Keyword'].split(' | ')
    search_keywords.append({
        'original_name': row['Original Name'],
        'keywords': keywords,
        'index': idx
    })

# Save this for use in the browser automation
import json
with open('search_keywords.json', 'w', encoding='utf-8') as f:
    json.dump(search_keywords[:50], f, ensure_ascii=False, indent=2)

print(f"Prepared {len(search_keywords)} items for searching")
print(f"First 5 items:")
for item in search_keywords[:5]:
    print(f"  - {item['original_name']}")
    print(f"    Keywords: {item['keywords']}")

