import time
from seleniumbase import SB
from bs4 import BeautifulSoup
import json

with SB(uc=True, headless=True) as sb:
    sb.uc_open_with_reconnect("https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp", 10)
    time.sleep(5)
    html = sb.get_page_source()
    
soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

print(f"Total scripts: {len(scripts)}")
for i, script in enumerate(scripts):
    if script.string and "sku" in script.string.lower() and "description" in script.string.lower():
        print(f"\n--- Found potential match in script {i} ---")
        print(script.string[:500] + "...\n")
        
        # Try to save the full text of matching scripts to analyze
        with open(f"script_match_{i}.txt", "w") as f:
            f.write(script.string)
