import time
import json
from seleniumbase import SB

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
home = "https://www.kohls.com/"

print("Booting Selenium...")
try:
    with SB(uc=True, headless=True) as sb:
        print("Clearing Akamai on homepage...")
        sb.uc_open_with_reconnect(home, 5)
        time.sleep(5)
        
        print(f"Loading {url}...")
        sb.uc_open_with_reconnect(url, 5)
        time.sleep(8) # Let Akamai clear and React fully hydrate
        
        print("Attempting to read variable directly from JS memory...")
        # Check if the variable is still in global scope
        data = sb.execute_script("""
            if (typeof productV2JsonData !== 'undefined') {
                return productV2JsonData;
            } else if (typeof window.__NEXT_DATA__ !== 'undefined') {
                return window.__NEXT_DATA__;
            } else {
                return null;
            }
        """)
        
        if data:
            print("⭐⭐⭐ HUGE SUCCESS! Captured JSON directly from live Javascript memory! ⭐⭐⭐")
            print(f"Keys found: {list(data.keys())[:10]}")
            
            with open("memory_extracted_product.json", "w") as f:
                json.dump(data, f, indent=4)
        else:
            print("FAILURE: Variable was completely Garbage Collected from JS memory.")
            
            # As a fallback, what if we inject a MutationObserver BEFORE the page loads to steal `<script>` tags?
            
except Exception as e:
    print(f"Error: {e}")
