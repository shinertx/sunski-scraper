import time
from seleniumbase import SB

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
home = "https://www.kohls.com/"

print("Booting Selenium to gather Akamai clearance...")
try:
    with SB(uc=True, headless=True) as sb:
        sb.uc_open_with_reconnect(home, 5)
        time.sleep(5) # Let Akamai evaluate JS and set cookies
        
        print("Injecting native fetch() to grab raw unhydrated HTML...")
        
        # We fetch the exact URL requested. Since fetch follows the same origin policy, 
        # it carries all cookies and Akamai clearances natively in the C++ network stack.
        js_script = f"""
        var callback = arguments[arguments.length - 1];
        fetch("{url}")
            .then(response => response.text())
            .then(text => callback(text))
            .catch(err => callback("ERROR: " + err.toString()));
        """
        
        # execute_async_script waits for callback
        raw_html = sb.execute_async_script(js_script)
        
        if "ERROR:" in raw_html[:20]:
            print(f"Fetch failed: {raw_html}")
        else:
            print(f"Fetch Success! Size: {len(raw_html)} bytes.")
            
            if "var productV2JsonData" in raw_html:
                print("SUCCESS: `productV2JsonData` found in raw HTML payload!")
                with open("raw_html_fetch.html", "w") as f:
                    f.write(raw_html)
            else:
                print("FAILURE: JSON payload still not found in raw HTML.")
                
except Exception as e:
    print(f"Error: {e}")
