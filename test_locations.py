import asyncio
from playwright.async_api import async_playwright

async def get_locations():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Navigating to homepage to acquire guest authentication tokens...")
        await page.goto("https://www.sunandski.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        locations_url = "https://www.sunandski.com/api/commerce/storefront/locationUsageTypes/SP/locations/?sortBy=name%20asc&filter=locationType.Code%20eq%20ST&includeAttributeDefinition=true"
        print("Fetching Locations API via Playwright context...")
        
        loc_data = await page.evaluate(f'''async () => {{
            const res = await fetch("{locations_url}", {{
                headers: {{ "Accept": "application/json" }}
            }});
            return res.json();
        }}''')
        
        items = loc_data.get('items', [])
        print(f"Found {len(items)} locations.")
        for item in items:
            name = item.get('name', '')
            code = item.get('code', '')
            print(f"STORE: {name} (Code: {code})")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_locations())
