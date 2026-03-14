import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Add basic anti-bot headers/agent if needed, though PW usually works for simple clicks
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        api_calls = []

        page.on("request", lambda request: api_calls.append(request) if "inventory" in request.url.lower() or "storefront" in request.url.lower() else None)

        print("Navigating to Sun&Ski...")
        await page.goto("https://www.sunandski.com/p/3461064600725/sportubes-nik-nac-pac", wait_until="domcontentloaded")
        
        # Wait a bit
        await page.wait_for_timeout(5000)
        
        print("Clicking store locator...")
        
        # Try finding the map marker
        marker = page.locator('span.icon--map-marker-alt')
        if await marker.count() > 0:
            await marker.first.click()
            await page.wait_for_timeout(2000)
            
            print("Typing zip...")
            await page.locator('input[placeholder*="Zip"]').fill("78201")
            await page.locator('button', has_text="Search").click()
            await page.wait_for_timeout(3000)
            
            print("Clicking store...")
            store_btns = page.locator('button', has_text="Store")
            if await store_btns.count() > 0:
                await store_btns.first.click()
                await page.wait_for_timeout(3000)
                print("Store selected!")
        else:
            print("Could not find map marker.")

        print("\n--- Intercepted APIs ---")
        for req in api_calls:
            print(f"URL: {req.url}")
            print(f"Headers: {req.headers}")
            print("---")

        cookies = await context.cookies()
        print(f"\nCookies: {[c['name'] for c in cookies]}")

        await browser.close()

asyncio.run(main())
