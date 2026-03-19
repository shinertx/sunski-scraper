import asyncio
import xml.etree.ElementTree as ET
from curl_cffi.requests import AsyncSession

# Kohl's product sitemaps
PRODUCT_SITEMAPS = [
    f"https://www.kohls.com/sitemap_product_{i}.xml" for i in range(1, 16)
]

namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

async def fetch_sitemap(session, url):
    print(f"[*] Fetching: {url}")
    try:
        r = await session.get(url, timeout=30)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            urls = [node.text for node in root.findall('.//ns:loc', namespaces)]
            
            # Kohl's sometimes mixes non-product links. We can loosely filter for "/product/"
            # or just take all locs if we trust the sitemap naming convention.
            product_urls = [u for u in urls if "/product/" in u or "/prd-" in u]
            print(f"[+] Downloaded {len(product_urls)} products from {url}")
            return product_urls
        else:
            print(f"[-] Blocked on {url}: {r.status_code}")
            return []
    except Exception as e:
        print(f"[-] Error on {url}: {e}")
        return []

async def main():
    print("[*] Launching Asynchronous Kohl's Sitemap Extractor...")
    all_urls = []
    
    async with AsyncSession(impersonate="chrome120") as session:
        tasks = [fetch_sitemap(session, url) for url in PRODUCT_SITEMAPS]
        results = await asyncio.gather(*tasks)
        
        for batch in results:
            all_urls.extend(batch)
            
    print(f"\\n[+] Total Unique Kohl's Products Extracted: {len(set(all_urls))}")
    
    with open("kohls_master_urls.txt", "w") as f:
        for u in set(all_urls):
            f.write(u + "\\n")
            
    print("[*] Saved to kohls_master_urls.txt")

if __name__ == "__main__":
    asyncio.run(main())
