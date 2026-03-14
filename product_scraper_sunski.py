import asyncio
import json
import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def scrape_product(page, url):
    """
    Navigates to a Sun & Ski product page, extracts product data embedded in
    data-mz-preload-product, and fetches BOPIS inventory directly from the
    Kibo Commerce API using the generated guest auth tokens.
    """
    print(f"Loading {url}")
    await page.goto(url, wait_until="domcontentloaded")
    
    # Wait for the product script tag to be available
    try:
        await page.wait_for_selector('script#data-mz-preload-product', state='attached', timeout=10000)
    except Exception as e:
        print(f"Failed to load product page or find metadata: {e}")
        return None
        
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract product metadata
    product_data = None
    script_tag = soup.find('script', id='data-mz-preload-product')
    if script_tag and script_tag.string:
        try:
            product_data = json.loads(script_tag.string)
        except json.JSONDecodeError:
            print("Failed to parse product JSON")
            return None
            
    if not product_data:
        print("No product data found in HTML")
        return None
        
    # Get the parent GTIN or Variation Code
    product_code = product_data.get('productCode')
    
    # Create the BOPIS request using Playwright's page context
    try:
        location_codes = "4,3,82,6,8,11,22,96,90,98,93,25,28,10,42,40,17,16,87,88,32,15,35,50,51,77,86,68,64,66"
        variations = product_data.get('variations', [])
        
        # We fetch BOPIS per variation code
        for var in variations:
            var_code = var.get('productCode')
            api_url = f"https://www.sunandski.com/api/commerce/catalog/storefront/products/{var_code}/locationinventory?locationCodes={location_codes}"
            
            var_inv = await page.evaluate(f'''async () => {{
                try {{
                    const res = await fetch("{api_url}", {{ headers: {{ "Accept": "application/json" }} }});
                    return res.json();
                }} catch(e) {{
                    return null;
                }}
            }}''')
            
            var['bopis_inventory'] = var_inv

    except Exception as e:
        print(f"Failed to fetch inventory API: {e}")
        
    # Compile the final parsed dictionary
    result = {
        "url": url,
        "productCode": product_code,
        "upc": product_data.get('upc'),
        "brand": product_data.get('content', {}).get('productBrand'), # if available
        "productName": product_data.get('content', {}).get('productName'),
        "description": product_data.get('content', {}).get('productFullDescription'),
        "images": [img.get('imageUrl') for img in product_data.get('content', {}).get('productImages', [])],
        "options": product_data.get('options', []),
        "variations": variations, # Now contains bopis_inventory nested
        "price": product_data.get('price', {}).get('price'),
        "salePrice": product_data.get('price', {}).get('salePrice')
    }
    
    return result

async def main():
    # Load target URLs from the sitemap extraction
    try:
        with open("sunski_target_urls.json", "r") as f:
            all_urls = json.load(f)
    except FileNotFoundError:
        print("sunski_target_urls.json not found. Run the sitemap extractor first.")
        return
        
    # Process only a small batch for testing first principles
    target_urls = all_urls[:5]
    print(f"Starting scraper for {len(target_urls)} URLs...")
    
    scraped_data = []
    
    async with async_playwright() as p:
        # Launch real browser in headless
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # First visit homepage to let Kibo set guest cookies
        print("Navigating to homepage to acquire guest authentication tokens...")
        await page.goto("https://www.sunandski.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        for url in target_urls:
            data = await scrape_product(page, url)
            if data:
                print(f"Successfully scraped: {data['productName']}")
                scraped_data.append(data)
            await page.wait_for_timeout(2000) # Polite delay
            
        await browser.close()
        
    # Save the output
    output_file = "sunski_scraped_data.json"
    with open(output_file, "w") as f:
        json.dump(scraped_data, f, indent=2)
    print(f"\nSaved {len(scraped_data)} records to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
