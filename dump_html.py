import time
from seleniumbase import SB

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"

print(f"Fetching {url} with SeleniumBase...")
try:
    with SB(uc=True, headless=True) as sb:
        sb.uc_open_with_reconnect(url, 5)
        time.sleep(5)
        html = sb.get_page_source()
        with open("selenium_dump.html", "w") as f:
            f.write(html)
        print("Done. Saved to selenium_dump.html")
except Exception as e:
    print(f"Error: {e}")
