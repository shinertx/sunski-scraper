import cloudscraper

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True})

try:
    print(f"Fetching {url} using cloudscraper...")
    response = scraper.get(url)
    
    if response.status_code == 200:
        html = response.text
        print(f"Success! Status: {response.status_code}. Size: {len(html)} bytes")
        
        if "var productV2JsonData" in html:
            print("Found `productV2JsonData` in HTML!")
        else:
            print("Variable missing from HTML. Akamai might have returned a challenge page.")
    else:
        print(f"Failed. Status Code: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
