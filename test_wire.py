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

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"

try:
    print(f"Fetching {url} with Selenium Wire Mode...")
    with SB(uc=True, headless=True, wire=True) as sb:
        sb.uc_open_with_reconnect(url, 5)
        time.sleep(5)
        
        # In wire mode, we can iterate over intercepted requests
        pristine_html = None
        for request in sb.driver.requests:
            if request.response and request.url == url:
                if 'text/html' in request.response.headers.get('Content-Type', ''):
                    try:
                        from seleniumwire.utils import decode
                        body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                        pristine_html = body.decode('utf-8', errors='ignore')
                        break
                    except Exception as e:
                        print(f"Error decoding wire response: {e}")

        if pristine_html:
            print(f"Success! Captured wire HTML: {len(pristine_html)} bytes")
            if "var productV2JsonData" in pristine_html:
                print("FOUND the JSON string in wire bytes!")
                
                start_marker = 'var productV2JsonData ='
                start_idx = pristine_html.find(start_marker)
                
                if start_idx != -1:
                    json_start = pristine_html.find('{', start_idx)
                    json_str = extract_json_object(pristine_html, json_start)
                    
                    if json_str:
                        parsed = json.loads(json_str)
                        print(f"SUCCESS: Parsed the JSON dictionary! Length: {len(str(parsed))}")
                    else:
                        print("JSON brace matching failed.")
            else:
                print("Missing from HTML even in wire mode.")
        else:
            print("Failed to intercept the main document request.")
except Exception as e:
    print(f"Exception: {e}")
