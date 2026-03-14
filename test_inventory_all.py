import asyncio
import aiohttp
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        await page.goto("https://www.sunandski.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        cookies = await context.cookies()
        auth = next((c['value'] for c in cookies if c['name'] == 'sb-sf-at-prod'), None)
        
        loc_data = await page.evaluate('''async () => {
            const res = await fetch("https://www.sunandski.com/api/commerce/storefront/locationUsageTypes/SP/locations/?sortBy=name%20asc&filter=locationType.Code%20eq%20ST&includeAttributeDefinition=true", {headers: {"Accept": "application/json"}});
            return res.json();
        }''')
        
        await browser.close()
        
    codes = [item['code'] for item in loc_data.get('items', [])]
    print(f"Got {len(codes)} codes: {codes[:5]}...")
    
    url_all = f"https://www.sunandski.com/api/commerce/catalog/storefront/products/3461064600725-0000000/locationinventory"
    url_multi = f"{url_all}?locationCodes={','.join(codes)}"
    
    async with aiohttp.ClientSession(cookies={"sb-sf-at-prod": auth}) as session:
        async with session.get(url_all, headers={"x-vol-tenant": "11961", "x-vol-site": "16493"}) as resp:
            data = await resp.json()
            items = data.get('items', [])
            print(f"No loc params returned {len(items)} stores.")
            
        async with session.get(url_multi, headers={"x-vol-tenant": "11961", "x-vol-site": "16493"}) as resp:
            data = await resp.json()
            items = data.get('items', [])
            print(f"Multi loc params returned {len(items)} stores.")            

asyncio.run(main())
