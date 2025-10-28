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
    It looks for the pattern where JSON is typically found within the `"` `"` of the string.
    Args:
        text_string: The string containing the escaped JSON.
    Returns:
        A Python dictionary representing the JSON object, or None if no valid
        escaped JSON is found and successfully parsed.
    """
    # Regex to find content that looks like an escaped JSON string.
    # We're looking for something that starts with '{"' and ends with '"}'
    # within a quoted string, or generally, a block that resembles escaped JSON.    # This pattern is quite specific to the format you provided:
    # "19:[\"$\",\"$L72\",null,{...escaped JSON here...}]"
    # Let's try to find the segment that contains the JSON first.
    # The JSON itself starts after a colon and within double quotes if it's part of a string.
    # The example string has: "19:[\"$\",\"$L72\",null,{\"adtechComponentApiResponse\"..."
    # The actual JSON starts with the first `{"` inside the outer `"`
    # We need to unescape the string content first if it's truly embedded as an
escaped string.
    # Let's assume the JSON part itself is correctly escaped within some outer quotes.
    # First, find the main string that potentially contains the escaped JSON.
    # In your example, the main content is within `"` and then ends with `"`
    # e.g., "19:[...]"
    # Find the largest quoted string that might contain our JSON
    match = re.search(r'"(.*?)"', text_string, re.DOTALL)
    if not match:
        return None
    potential_json_container_string = match.group(1)
    # Now, this `potential_json_container_string` might itself be escaped.
    # The actual JSON starts after `null,` followed by `{"`
    # Example: "19:[\"$\",\"$L72\",null,{\"adtechComponentApiResponse\":{...}}]"
    # We're looking for the pattern `null,` followed by `{"`
    # The `re.escape` is used here because the content of `null,{"` could have special regex chars
    search_pattern = r'null,(?P<json_data>\{.*?\})'
    # Since the string itself is escaped, we need to carefully handle that.
    # The inner JSON content itself is *not* doubly escaped, it's just escaped once
    # because it's inside an outer string.
    # Let's unescape the potential_json_container_string first for easier regex
matching.
    # json.loads can actually handle unescaping within a string if it's valid JSON
    # but we are trying to extract it from a non-pure JSON string.
    # A simple approach: find the first occurrence of '{' and last occurrence of '}'
    # within the *unescaped* version of the part that should contain JSON.
    try:
        # Step 1: Find the part of the string that holds the "19:[\"$\",...]"
        # This will be between the first pair of unescaped quotes enclosing it.
        # Since the example provided had `push([1, "19: [...]"])`, the JSON
        # is part of the second element of the array, which is a string.
        # Let's try to parse the outermost array first if possible.
        # We need to find the part that looks like `"{...escaped json...}"`
        # and then extract the content and unescape it.
        # Your example string structure:
        # self.__next_f.push([1, "19:[...escaped JSON...]]\n"])
        # The key is to get the content of the string "19:[... ]"
        # Use regex to find the second element of the `push` array
        # This regex targets the string literal that contains the escaped JSON.
        print("Searching for string literal containing JSON...")
        string_literal_match = re.search(r'push\(\[\d+\s*,\s*"(.*?)"', text_string, re.DOTALL)
        print(f"String literal match: {string_literal_match}")
        if not string_literal_match:
            return None
        # This `escaped_content_string` is the "19:[\"$\",...]" part.
        escaped_content_string = text_string
        print(f"Escaped content string: {escaped_content_string[:500]}...")  # Print first 500 chars
        json_start_potential = 0
        # The JSON will be `{...}`.
        # We need to handle the fact that the outer string quotes mean the
        # internal double quotes for JSON keys/values are escaped `\"`.
        # A simple approach: use `json.loads` on the *entire* escaped_content_string
        # if it's a valid JSON string (it's not).
        # We need to extract the raw JSON part from the escaped_content_string and then unescape it.
        # Find the first `{"` sequence after `null,`
        print("Finding first brace index...")
        first_brace_index = escaped_content_string.find('{')
        print(f"First brace index: {first_brace_index}")
        if first_brace_index == -1:
            return None
        # The actual JSON string starts at `first_brace_index`
        print("Extracting JSON candidate string...")
        json_candidate_string = escaped_content_string[first_brace_index:]
        print(f"JSON candidate string: {json_candidate_string[:500]}...")  # Print first 500 chars
        # Now, this `json_candidate_string` has escaped quotes inside it.
        # Example: `{\"key\":\"value\"}`
        # We need to properly unescape it so `json.loads` can work.
        # The trick is that Python's `json.loads` expects *pure* JSON.
        # If the JSON is embedded as a *string literal* in another language,
        # its internal quotes (e.g., for keys and values) will be escaped (`\"`).
        # When we extract that string literal, we get the literal backslashes.
        # So, we should try to unescape the backslashes first to get valid JSON.        # A simple `replace('\\"', '"')` isn't enough, as it needs to respect structure.
        # The `json` module itself can help with this by parsing it as a string
literal
        # and then parsing the content of that string.
        # Wrap the found JSON candidate in quotes so json.loads can parse it as
a string literal
        # This will correctly unescape all the `\"` inside.
        print("Unescaping JSON candidate string...")
        # unescaped_json_string = json.loads(f'"{json_candidate_string}"')
        unescaped_json_string = json_candidate_string
        print(f"Unescaped JSON string: {unescaped_json_string[:500]}...")  # Print first 500 chars
        # Now, `unescaped_json_string` should be a clean JSON string, e.g., `{"key":"value"}`
        # We can try to parse this as a JSON object.
        # Find the final '}' for the JSON
        # Iterating from the end to find the last valid '}'
        bracket_count = 0
        last_valid_brace_index = -1
        print("Locating last valid closing brace...")
        # Iterate backwards to find the matching '}'
        json_object = None
        # Iterate backwards, try each '}' as a potential end of JSON and attempt to decode
        for i in range(len(unescaped_json_string) - 1, -1, -1):
            if unescaped_json_string[i] != '}':
                continue
            candidate = unescaped_json_string[:i + 1]
            print("candidat last brace at index:", i)
            print("candidaterange:", candidate[:20],"...",candidate[ -20:])
            try:
                try:
                    # If the candidate contains backslash-escaped sequences, try to unescape it
                    if '\\\"' in candidate or '\\\\' in candidate or '\\n' in candidate or '\\t' in candidate or '\\/' in candidate:
                        # Preferred: treat it as a JSON string literal so json.loads will unescape it correctly
                        try:
                            candidate = json.loads(f'"{candidate}"')
                        except Exception:
                            # Fallback: decode common escape sequences
                            try:
                                candidate = candidate.encode('utf-8').decode('unicode_escape')
                            except Exception:
                                # Last-resort naive replacements
                                candidate = candidate.replace('\\"', '"').replace('\\\\', '\\').replace('\\/', '/')
                except Exception:
                    # If anything goes wrong with unescaping, proceed with the original candidate and let json.loads fail later
                    pass
                json_object = json.loads(candidate)
                print(f"Successfully parsed JSON ending at index {i}")
                break
            except json.JSONDecodeError:
            # Not valid JSON yet, try the next earlier '}'
                continue
            except Exception as e:
                print(f"Unexpected error parsing candidate ending at {i}: {e}")
            continue
        if json_object is None:
            print("No valid JSON found after trying all candidates.")
            return None
        return json_object
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        sys.exit(1)
    # Save HTML response for debugging
    with open("debug.html", 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("HTML saved to debug.html for debugging.")
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script')
    extracted_data = None
    for script in scripts:
        if script.string and "adtechComponentApiResponse" in script.string:
            content = script.string.strip()
            print(f"Found script content: {content[:500]}...")  # Print first 500 chars
            # Try the improved JSON extraction function first, as it handles escaped JSON better
            extracted_data = extract_escaped_json_from_string(content)
            if extracted_data:
                print("Successfully extracted JSON using advanced parsing!")
                break
            # Fallback to original simple method
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
                    print(f"Extracted JSON str: {json_str[:500]}...")  # Print first 500
                    if json_str:
                        try:
                            extracted_data = json.loads(json_str)
                            print("Successfully parsed JSON using simple method!")
                            break  # Assuming only one such script
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON with simple method: {e}")                            continue
    if extracted_data is None:
        print("Could not find adtechComponentApiResponse data.")
        sys.exit(1)
    # Sanitize keyword for filename
    sanitized_name = re.sub(r'[^\w\s-]', '', keyword).strip().replace(' ', '_').lower()
    if not sanitized_name:
        sanitized_name = "unknown_keyword"
    # Create results directory
    os.makedirs("results", exist_ok=True)
    # Save to JSON
    output_path = f"results/{sanitized_name}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {output_path}")