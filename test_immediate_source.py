import time
from seleniumbase import SB

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
home = "https://www.kohls.com/"

print("Booting Selenium...")
try:
    with SB(uc=True, headless=True, page_load_strategy="none") as sb:
        print("Clearing Akamai on homepage...")
        sb.uc_open_with_reconnect(home, 5)
        time.sleep(5)
        
        print(f"Fetching {url} and capturing IMMEDIATELY...")
        # Using standard open since we already cleared Akamai
        sb.driver.get(url)
        
        # We don't sleep! We grab the source immediately.
        time.sleep(0.5)
        raw_html = sb.driver.page_source
        
        print(f"HTML Length: {len(raw_html)} bytes.")
        
        if "var productV2JsonData =" in raw_html:
            print("SUCCESS! JSON payload found before React hydration!")
        else:
            print("FAILURE: JSON payload not found. We might be too early or too late.")
            with open("immediate_dump.html", "w") as f:
                f.write(raw_html)
                
except Exception as e:
    print(f"Error: {e}")
