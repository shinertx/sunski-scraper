import time
from seleniumbase import SB

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
home = "https://www.kohls.com/"

print("Booting Selenium...")
try:
    with SB(uc=True, headless=False) as sb:
        print("Clearing Akamai on homepage...")
        sb.uc_open_with_reconnect(home, 5)
        time.sleep(5)
        
        print(f"Fetching {url} using STANDARD open...")
        sb.open(url)
        time.sleep(5)
        
        html = sb.get_page_source()
        with open("clean_product_dump.html", "w") as f:
            f.write(html)
        print(f"Saved {len(html)} bytes to clean_product_dump.html")
        
        if "productV2JsonData" in html:
            print("Found productV2JsonData")
        elif "__NEXT_DATA__" in html:
            print("Found __NEXT_DATA__")
        else:
            print("Neither signature found.")
            
except Exception as e:
    print(f"Error: {e}")
