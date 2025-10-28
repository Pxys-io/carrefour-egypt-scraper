import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import re
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def extract_escaped_json_from_string(text_string):
    """
    Extracts an escaped JSON object from a string that contains other text.
    """
    try:
        first_brace_index = text_string.find('{')
        if first_brace_index == -1:
            return None
        
        json_candidate_string = text_string[first_brace_index:]
        unescaped_json_string = json_candidate_string
        
        json_object = None
        for i in range(len(unescaped_json_string) - 1, -1, -1):
            if unescaped_json_string[i] != '}':
                continue
            candidate = unescaped_json_string[:i + 1]
            try:
                if '\\\"' in candidate or '\\\\' in candidate or '\\n' in candidate or '\\t' in candidate or '\\/' in candidate:
                    try:
                        candidate = json.loads(f'"{candidate}"')
                    except Exception:
                        try:
                            candidate = candidate.encode('utf-8').decode('unicode_escape')
                        except Exception:
                            candidate = candidate.replace('\\"', '"').replace('\\\\', '\\').replace('\\/', '/')
                json_object = json.loads(candidate)
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                continue
        
        if json_object is None:
            return None
        return json_object
    except Exception as e:
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <keyword>")
        sys.exit(1)
    
    keyword = sys.argv[1].strip()
    encoded_keyword = quote(keyword)
    url = f"https://www.carrefouregypt.com/mafegy/ar/search?keyword={encoded_keyword}"
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'cookie': 'cart_api=v2; maf-session-id=0F02ED7B-ABD7-4040-9F0F-B4EBF037582F; AKA_A2=A; isNewPLP=true; mafegy-preferred-delivery-area=Maadi - Cairo; isNewPDP=true; isNewHome=true; selectedTabData={"selectedTabId":"129","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL","pagePath":"homepage-standard-egy-2025","pageType":"Homepage","pageId":"4415","pageUid":"homepage-standard-egy-2025-test"}; posInfo=express=700_Zone02,food=201_Zone02,nonfood=299_Zone01; bm_mi=1D3E035777283ED90AC67E80FA880F8F~YAAQITwSAlQ6IiWaAQAALLmrKh1D3PQIriu8UukkHneaMi1Q0bWE5r48ewlCd6+i+X2n7CdUqEjfJY9uV7fIKmZcXe0G+IZ+zkVQ7KbEuS/6Lm1UH/JRQz2MqvmIXbCZ4RREhnzuM38Q8lEb9PaBQMXbisY64F2p+8v1GD5T8YgUy+P3bGL3KNGYk6L+FicDL945faorL5syxGRz5bX5kVEp+6H69qyVlPK3ZuACVmmGXsqQ1cRYJkIy1F0hjZLzrgaZNWxxAcEdf43xnFWORtKNFzVejyBupkXIyU0+B7dQfm93jIHl/HNb6WLyvQ37JdWemCBpocPQUAxtzBgVY8cguw==~1; bm_sv=781C5FE40B99ACE5C03399BBCC9F24FF~YAAQITwSAiQ7IiWaAQAAgtarKh3zYzcnW8nsdeUbAVqSvopqmrtfpAENJv3qnI4dY9iAsfE0ExdAJIurVLRCs4CoMuJwvCtfeCveElRJ9lvN++lEw4zeEdO8VzlBBGpCvCjbC4OMNYcF0wjMD/LyDqSlvqGYiJborVCoNBVP4Lm81I5/U7ybe/kCluJa84LyOHzi00CMbL4TSFuhVUP4jt/Q0wFz7mayqERO0M4enujwO253nqJRtuWNsHUFH9CQAOb+jn6p2WTR~1; cart_api=v2; storeInfo=mafegy|ar|EGP; ak_bmsc=1B4A2CAF11EA922AF5A64137AC720ED2~000000000000000000000000000000~YAAQVm0UAtufriaaAQAA+GO5Kh1y5baViLsEBF1MfTLlViOlu1jzLdnyi1pEb6OcPyPshG/CGnH6rTNCHBTZtS+MU4IL50yatYas+EBmuLApHppuvzmgpwJz1CuwZz6LBqdLg/1K1KzJUidJ7kSxrE+Xnu+USmVVQCL/Mfg4JMzcqPiz2x6DojRzBhYmaEknA96P7OX7bLfj+DLpSqZUYnglIBtpbYlt20O1kYDNb1tlVupu1iz06VPzsBf+qJAoQ6JPgYckTowzDaD/qopnYA4eXviKav2Oky/rBLCqasmW6tVGDCv5zQVOznW8D3pctCQZX+K6RabhnbbMbKxtRP+3xJtYk/Y8qRByHIKEx9IRxEqA3O8z+wAhBCeJLjS/RB4JrhsRE8fEeIknKGQJEHL4uSRpZ8c2WClldgtXk8qHQIv/1Uoa/vHgSRki1I2r6ZJW4Z//PuXPsXILG/Gkq5hl2oQ=; bm_sz=7B3C47F4412FBBBAB680C8F07E38B86D~YAAQVm0UAtyfriaaAQAA+GO5Kh2ZSecGAqKWvDwl9L14B7nsnR33R9ojsshR4rz8SyjoF2nzkuZ5XZocZOPo0/848IAf+dAMjBGzqJy0mM5ECMC2wawSBEM2rGI23I/ZqORH6s32ob9Pq5Yydhzg7Ge655Kt//dDAmWX0Ce4Cg++BVGF6heZlp4ResqWKQOhNPBzPCz3KDYqipNzHvF37mly53jGrSQ7lJIw4uul95+n9OPtADTwHwazqh7KJtsLkia73EFPoGl1hkDWBry4ZM023Fa1B5Jfo+njgSR7bI5ylQL1SxB7EWfHZQG6n8zq0B0cMuhlq7X9+oU3HPyt0qokTt8ixzNFNVZ6uitrvlPKGXW9AsHGvlLTjX+knUWjZPjT6IqWz3IE7NcIoTppLNIrZaKQbk3OUuygGECnCmyaO3fgO2F1bthCqRB+~3225141~3421747; _abck=52F72A940086FF4F1DD6B5B7A8E69F1E~0~YAAQVm0UAjCgriaaAQAAAmq5Kg6YfAsnIRK87/agFCPdcbX/eUgiCeUWvdDJ3ikV9qxlcgxK4Gc+0K1nBvPk+NgLIAHDa/fD4Y6YPT1VpOYEZSGTS8c323rsHvGwBMcvhxhYX6KMsjvRHOfqR8KVsoTNfyUDBFFIkPCR+mCwdQyUcvjEUvb4w1TpVK7Wc+QZjRGoVinpVIR1LNpvGz0YE7ystBxNMODt2aAXjvq68hPY1bqpLPksy2ThTj7UDbJC/FSxwLzpKmzkk8yXxLYIfNL5fJ9W9J3hU6iOLegHW4azBjSaMuq1oSjk36VrWpYGGdhq1jTgw+WVFtVWVYOOMaRBMApmEJrNQtIIpeNANDNtjvOP2mXMwc2Ur81wA6ZMYEhwFw7IkaNKxFwDaMvHUy4s~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2fx1wcihF50qhS28R9Y0PXtUYuqXrpilcwuBSgMTfMuSZi%2fnp+%2fJwl54DkPIGpPpPPRYE06tgoqJBb0fNaapeDcD3gPxE2LTKQXiv8IGusP55xvWmW1GcnzY8Kj%2fq8t3M7+8a27Q%3d~-1; JSESSIONID=0827886395FDF9332F370D4CEC38A489',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        sys.exit(1)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script')
    extracted_data = None
    
    for script in scripts:
        if script.string and "adtechComponentApiResponse" in script.string:
            content = script.string.strip()
            extracted_data = extract_escaped_json_from_string(content)
            if extracted_data:
                break
            
            key_index = content.find('"adtechComponentApiResponse":')
            if key_index != -1:
                colon_index = content.find(':', key_index)
                start = content.find('{', colon_index)
                if start != -1:
                    brace_count = 0
                    end = start
                    for i in range(start, len(content)):
                        if content[i] == '{':
                            brace_count += 1
                        elif content[i] == '}':
                            brace_count -= 1
                        end = i
                        if brace_count == 0:
                            break
                    json_str = content[start:end+1]
                    if json_str:
                        try:
                            extracted_data = json.loads(json_str)
                            break
                        except json.JSONDecodeError as e:
                            continue
    
    if extracted_data is None:
        print("Could not find adtechComponentApiResponse data.")
        sys.exit(1)
    
    sanitized_name = re.sub(r'[^\w\s-]', '', keyword).strip().replace(' ', '_').lower()
    if not sanitized_name:
        sanitized_name = "unknown_keyword"
    
    os.makedirs("results", exist_ok=True)
    
    output_path = f"results/{sanitized_name}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to {output_path}")
