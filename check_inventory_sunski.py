import asyncio
import aiohttp
import json
import time
import os
from playwright.async_api import async_playwright

async def get_kibo_auth_and_locations():
    """
    Spawns a headless browser to acquire the guest 'sb-sf-at-prod' cookie
    AND fetches the directory of all physical store locations.
    """
    print("Launching Playwright to acquire Kibo Commerce auth token and directory...")
    start_time = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Load the page and wait for the analytics/commerce scripts to fire
        await page.goto("https://www.sunandski.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Grab cookies
        cookies = await context.cookies()
        auth_cookie_val = None
        for c in cookies:
            if c['name'] == 'sb-sf-at-prod':
                auth_cookie_val = c['value']
                break
                
        # Fetch the location directory organically
        locations_url = "https://www.sunandski.com/api/commerce/storefront/locationUsageTypes/SP/locations/?sortBy=name%20asc&filter=locationType.Code%20eq%20ST&includeAttributeDefinition=true"
        loc_data = await page.evaluate(f'''async () => {{
            const res = await fetch("{locations_url}", {{
                headers: {{ "Accept": "application/json" }}
            }});
            return res.json();
        }}''')
        
        await browser.close()
        
    duration = time.time() - start_time
    stores = loc_data.get('items', [])
    print(f"Acquired token and {len(stores)} store locations in {duration:.2f} seconds.")
    return auth_cookie_val, stores

async def check_inventory_for_variation(session, var_code):
    """
    Hits the Kibo Commerce inventory endpoint WITHOUT location parameters,
    causing it to magically return stock for ALL locations at once.
    """
    api_url = f"https://www.sunandski.com/api/commerce/catalog/storefront/products/{var_code}/locationinventory"
    stocks = {}
    try:
        async with session.get(api_url, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                items = data.get('items', [])
                for item in items:
                    loc = str(item.get('locationCode'))
                    stocks[loc] = item.get('stockAvailable', 0)
                return var_code, stocks
            else:
                raw = await response.text()
                print(f"Error fetching inventory for {var_code}: HTTP {response.status} - {raw}")
    except Exception as e:
        print(f"Exception fetching {var_code}: {e}")
        
    return var_code, stocks

async def process_batch(session, batch):
    tasks = [check_inventory_for_variation(session, var_code) for var_code in batch]
    return await asyncio.gather(*tasks)

async def main():
    # 1. Load the flat Jenni-schema catalog
    try:
        with open("sunski_catalog.json", "r") as f:
            catalog = json.load(f)
    except FileNotFoundError:
        print("sunski_catalog.json not found! Run the catalog builder script first.")
        return
        
    variation_codes = []
    for product_record in catalog:
        for var in product_record.get('variants', []):
            code = var.get('sku')
            if code:
                variation_codes.append(code)
                
    print(f"Found {len(variation_codes)} unique product variations in the catalog to check.")
    
    # 2. Grab the Authentication Token and Store Directory
    auth_token, store_directory = await get_kibo_auth_and_locations()
    if not auth_token:
        print("CRITICAL ERROR: Failed to acquire `sb-sf-at-prod` cookie.")
        return
        
    # 3. Fast bulk inventory check
    print(f"\\nStarting blazing fast API inventory checks spanning ALL {len(store_directory)} locations...")
    start_time = time.time()
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "x-vol-tenant": "11961",
        "x-vol-site": "16493"
    }
    
    cookies = {"sb-sf-at-prod": auth_token}
    connector = aiohttp.TCPConnector(limit=20)
    inventory_matrix = {} # {sku: {loc1: 5, loc2: 0}}
    
    async with aiohttp.ClientSession(headers=headers, cookies=cookies, connector=connector) as session:
        batch_size = 20
        for i in range(0, len(variation_codes), batch_size):
            batch = variation_codes[i:i + batch_size]
            results = await process_batch(session, batch)
            
            for var_code, stocks_map in results:
                if stocks_map:
                    inventory_matrix[var_code] = stocks_map
                    
            print(f"Checked {min(i + batch_size, len(variation_codes))}/{len(variation_codes)} variations...")
            
    lookup_duration = time.time() - start_time
    print(f"Inventory matrix populated in {lookup_duration:.2f} seconds.")
    
    # 4. Compile separate JSON feed files per store location
    print("\\nCompiling store-specific feeds...")
    os.makedirs("store_feeds", exist_ok=True)
    
    import copy
    
    for store in store_directory:
        code = str(store.get('code', ''))
        if not code:
            continue
            
        addr = store.get('address', {})
        geo = store.get('geo', {})
            
        store_details = {
          "provider_id": "locally",
          "retailer_store_id": code,
          "retailer_id": "sun_and_ski",
          "supplier_id": "",
          "zip": addr.get('postalOrZipCode', ''),
          "lat": geo.get('lat', 0.0),
          "lng": geo.get('lng', 0.0),
          "store_url": f"https://www.sunandski.com/locations/{addr.get('stateOrProvince', 'tx').lower()}-{addr.get('city', '').lower().replace(' ', '-')}",
          "country": addr.get('countryCode', 'US'),
          "city": addr.get('city', ''),
          "state": addr.get('stateOrProvince', ''),
          "store_name": store.get('name', ''),
          "address1": addr.get('address1', ''),
          "address2": addr.get('address2', ''),
          "contact_no1": store.get('phone', ''),
          "contact_no2": "",
          "store_dow": {}
        }
        
        feed_payload = []
        for product_record in catalog:
            record = copy.deepcopy(product_record)
            record['store_details'] = store_details
            
            parent_in_stock = False
            total_inventory = 0
            
            for var in record.get('variants', []):
                sku = var.get('sku')
                # Grab stock specifically for this store code out of the matrix
                stock = inventory_matrix.get(sku, {}).get(code, 0)
                
                var['inventory'] = str(stock)
                is_in_stock = stock > 0
                var['in_stock'] = "true" if is_in_stock else "false"
                
                if is_in_stock:
                    parent_in_stock = True
                total_inventory += stock
                    
            parent_block = record.get('products', {})
            parent_block['inventory'] = str(total_inventory)
            parent_block['in_stock'] = "true" if parent_in_stock else "false"
            
            feed_payload.append(record)
            
        filename = f"store_feeds/sunski_inventory_{code}.json"
        with open(filename, "w") as f:
            json.dump(feed_payload, f, indent=2)
            
        print(f"Generated {filename} ({len(feed_payload)} records)")
        
    print(f"\\nAll done! Successfully distributed localized catalog records across {len(store_directory)} feeds.")

if __name__ == "__main__":
    asyncio.run(main())
