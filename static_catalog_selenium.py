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

def build_static_catalog(target_urls):
    extracted_products = []
    
    with SB(uc=True, headless=True) as sb:
        print("Clearing Akamai on homepage...")
        sb.uc_open_with_reconnect("https://www.kohls.com", 5)
        time.sleep(5)
        
        # Enable CDP network interception
        sb.execute_cdp_cmd('Network.enable', {})
        
        for url in target_urls:
            print(f"\nFetching {url}...")
            
            # Start navigation
            sb.uc_open_with_reconnect(url, 5)
            time.sleep(4) # Let the page load
            
            # Retrieve all network requests logged by CDP in the current session
            logs = sb.driver.execute("getLog", {"type": "performance"})["value"]
            
            pristine_html = None
            
            for log in logs:
                message = json.loads(log["message"])["message"]
                if message["method"] == "Network.responseReceived":
                    resp = message["params"]["response"]
                    req_url = resp.get("url", "")
                    mime = resp.get("mimeType", "")
                    
                    # Look for the main document HTML response
                    if "lee-carpenter" in req_url or url.split('/')[-1] in req_url:
                        if mime == "text/html":
                            request_id = message["params"]["requestId"]
                            try:
                                body_response = sb.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                pristine_html = body_response.get('body')
                                if pristine_html:
                                    break
                            except Exception as e:
                                pass
                                
            if pristine_html:
                print(f"Intercepted pristine HTML from wire: {len(pristine_html)} bytes.")
                
                # Use our ultra-fast JSON string extraction
                start_marker = 'var productV2JsonData ='
                start_idx = pristine_html.find(start_marker)
                
                if start_idx != -1:
                    json_start = pristine_html.find('{', start_idx)
                    json_str = extract_json_object(pristine_html, json_start)
                    
                    if json_str:
                        try:
                            parsed = json.loads(json_str)
                            extracted_products.append({
                                "url": url,
                                "data": parsed
                            })
                            print(f"SUCCESS: Catalog extracted for {url.split('/')[-1]}")
                        except Exception as e:
                            print(f"JSON Parse Error: {e}")
                    else:
                        print("Failed to bracket-match the JSON.")
                else:
                    print("`var productV2JsonData` not found in pristine HTML.")
            else:
                print("Failed to intercept the HTML response via CDP.")
                
    return extracted_products

if __name__ == "__main__":
    test_urls = [
        "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp",
        "https://www.kohls.com/product/prd-2662/farberware-classic-series-4-qt-saucepot.jsp"
    ]
    
    results = build_static_catalog(test_urls)
    
    with open("static_catalog_selenium.json", "w") as f:
        json.dump(results, f, indent=4)
        print(f"\nSaved {len(results)} items to static_catalog_selenium.json")
