import asyncio
import json
import time
from curl_cffi.requests import AsyncSession

# Import our robust JSON extractor since regex may not match exactly or fail on nested braces
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


async def fetch_product_data(session, url):
    """
    Fetches the raw HTML of a product page and extracts the inline JSON catalog data.
    """
    try:
        response = await session.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"[{response.status_code}] Failed to fetch {url}")
            return None
            
        html = response.text
        
        # Searching for the variable assignment in the raw HTML script tag
        start_marker = 'var productV2JsonData ='
        start_idx = html.find(start_marker)
        
        if start_idx != -1:
            json_start = html.find('{', start_idx)
            if json_start != -1:
                json_str = extract_json_object(html, json_start)
                
                if json_str:
                    try:
                        parsed = json.loads(json_str)
                        return {
                            "url": url,
                            "catalog_data": parsed
                        }
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON for {url}: {e}")
                else:
                    print(f"Failed to match JSON braces for {url}.")
        else:
            print(f"productV2JsonData marker not found in {url} HTML.")
            # Save dump for analysis if the marker is totally missing
            with open("failed_html_dump.txt", "w") as f:
                f.write(html)
            
    except Exception as e:
        print(f"Exception fetching {url}: {str(e)}")
        
    return None

async def build_static_catalog(urls):
    """
    Main orchestrator for concurrent extraction. Returns parsed catalog data.
    For this test, we run sequentially or with small concurrency to avoid bans.
    """
    results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Using chrome110 impersonation to spoof TLS fingerprints against Akamai
    async with AsyncSession(impersonate="chrome110", headers=headers) as session:
        tasks = [fetch_product_data(session, url) for url in urls]
        
        # We can gather concurrently, but let's do small batches
        # For this test with 3 URLs, gather is fine.
        responses = await asyncio.gather(*tasks)
        
        for res in responses:
            if res:
                results.append(res)
                
    return results

if __name__ == "__main__":
    test_urls = [
        "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp",
        "https://www.kohls.com/product/prd-2662/farberware-classic-series-4-qt-saucepot.jsp",
        "https://www.kohls.com/product/prd-3893/levis-505-regular-jeans-mens.jsp"
    ]
    
    print(f"Starting Fast Static Catalog Extractor for {len(test_urls)} products...")
    start_time = time.time()
    
    # Run the async extraction
    extracted_data = asyncio.run(build_static_catalog(test_urls))
    
    end_time = time.time()
    print(f"\nExtraction complete in {end_time - start_time:.2f} seconds.")
    print(f"Successfully extracted {len(extracted_data)}/{len(test_urls)} products.")
    
    # Save the sample data
    with open("static_catalog_sample.json", "w") as f:
        json.dump(extracted_data, f, indent=4)
        print("Sample data saved to static_catalog_sample.json")
