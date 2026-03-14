import time
from seleniumbase import SB
import requests

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
home = "https://www.kohls.com/"

print("Booting Selenium to gather Akamai clearance cookies...")
try:
    with SB(uc=True, headless=True) as sb:
        sb.uc_open_with_reconnect(home, 5)
        time.sleep(5) # Let Akamai evaluate JS and set cookies
        
        # Get cookies
        selenium_cookies = sb.driver.get_cookies()
        
        # Format cookies for requests
        session = requests.Session()
        for cookie in selenium_cookies:
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
            
        print("Cookies gathered! Now performing high-speed pure HTTP request for the raw HTML...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        res = session.get(url, headers=headers)
        
        if res.status_code == 200:
            html = res.text
            print(f"HTTP GET Success! Size: {len(html)} bytes.")
            
            if "var productV2JsonData" in html:
                print("SUCCESS: `productV2JsonData` found in raw HTML payload!")
                with open("raw_html_success.html", "w") as f:
                    f.write(html)
            else:
                print("FAILURE: JSON payload still not found in raw HTML. Akamai might have blocked it silently or returned a challenge page.")
                with open("raw_html_fail.html", "w") as f:
                    f.write(html)
        else:
            print(f"HTTP GET Failed with status {res.status_code}")
            
except Exception as e:
    print(f"Error: {e}")
