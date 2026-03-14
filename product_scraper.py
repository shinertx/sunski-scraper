import json
import time
from seleniumbase import SB

def extract_json_object(text, start_idx):
    stack = 0
    in_string = False
    escape = False
    for i in range(start_idx, len(text)):
        char = text[i]
        if not escape and char == '"':
            in_string = not in_string
        elif not in_string:
            if char == '{':
                stack += 1
            elif char == '}':
                stack -= 1
                if stack == 0:
                    return text[start_idx:i+1]
        
        if char == '\\' and not escape:
            escape = True
        else:
            escape = False
    return None

def extract_product_api(target_urls, max_items=5):
    """
    Uses SeleniumBase with CDP Network Interception to capture the raw JSON API
    responses that Kohl's uses to populate its product detail pages natively.
    """
    base_url = "https://www.kohls.com"
    extracted_products = []
    
    print(f"Preparing to scrape {min(len(target_urls), max_items)} products using Network Interception...")
    
    # We use UC (undetected_chromedriver) to bypass Akamai bot protection
    with SB(uc=True, headless=True) as sb:
        print("Navigating to homepage to clear Akamai Challenge...")
        sb.uc_open_with_reconnect(base_url, 10)
        time.sleep(5) # Wait for challenge to pass
        
        # 2. Iterate over target URLs
        for i, url in enumerate(target_urls[:max_items]):
            print(f"\n[{i+1}/{max_items}] Fetching product: {url}")
            
            try:
                # Use standard open to inherit the cleared Akamai session state
                sb.open(url)
                time.sleep(4)
                
                print(f"Extracting HTML for {url}...")
                
                # Fetching the page source directly from the browser
                html = sb.get_page_source()
                
                start_marker = 'var productV2JsonData = '
                start_idx = html.find(start_marker)
                
                if start_idx != -1:
                    json_start = html.find('{', start_idx)
                    json_str = extract_json_object(html, json_start)
                    
                    if json_str:
                        try:
                            parsed = json.loads(json_str)
                            extracted_products.append({
                                "url": url,
                                "data": parsed
                            })
                            print(f"Successfully extracted product payload via string matching!")
                        except Exception as e:
                            print(f"Failed to parse JSON string: {e}")
                    else:
                        print("Failed to find matching braces for JSON object.")
                else:
                    print(f"Failed to locate product JSON in HTML.")
                    
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                
            time.sleep(3) # Be polite between requests
            
    # Save the extracted data
    output_file = "extracted_network_products.json"
    with open(output_file, "w") as f:
        json.dump(extracted_products, f, indent=2)
        
    print(f"\nSuccessfully saved {len(extracted_products)} API payloads to {output_file}")

if __name__ == "__main__":
    try:
        with open("target_skus.json", "r") as f:
            urls = json.load(f)
            
        if urls:
            extract_product_api(urls, max_items=3)
        else:
            print("No URLs found in target_skus.json")
    except FileNotFoundError:
        print("target_skus.json not found.")
