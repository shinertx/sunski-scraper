import asyncio
import json
import re
from curl_cffi.requests import AsyncSession

OUTPUT_FILE = "kohls_national_catalog_batch1.jsonl"
INPUT_FILE = "kohls_master_urls.txt"
BATCH_SIZE = 5000 

async def fetch_product_metadata(session, url, semaphore):
    async with semaphore:
        try:
            r = await session.get(url, timeout=20)
            if r.status_code == 200:
                html = r.text
                m = re.search(r'var productV2JsonData = (\{.*?\});', html, re.DOTALL)
                if m:
                    data = json.loads(m.group(1))
                    
                    product_id = str(data.get("webID", ""))
                    if not product_id: return None
                    
                    output = {
                        "product_id": product_id,
                        "url": url,
                        "title": data.get("productTitle", ""),
                        "brand": str(data.get("brand", "")),
                        "variants": []
                    }
                    
                    upc_map = {str(upc.get("ID")): upc.get("upc") for upc in data.get("upcs", [])}
                    
                    for sku in data.get("SKUS", []):
                        sku_id = sku.get("skuId") or sku.get("skuCode")
                        if not sku_id: continue
                        
                        variant = {
                            "sku": str(sku_id),
                            "upc": upc_map.get(str(sku_id), ""),
                            "color": sku.get("color", ""),
                            "size": sku.get("size", "")
                        }
                        output["variants"].append(variant)
                    
                    return output
        except Exception:
            pass
            
        return None

async def main():
    print(f"[*] Loading Top {BATCH_SIZE} links from Master Target List ({INPUT_FILE})...")
    with open(INPUT_FILE, "r") as f:
        target_urls = [line.strip() for line in f.readlines()[:BATCH_SIZE]]
        
    print("[*] Reading independent clearance cookies from kohls_clearance_cookies.json...")
    with open("kohls_clearance_cookies.json", "r") as f:
        clearance_cookies = json.load(f)
    
    print("[*] Booting Asynchronous HTTP/TLS Streams...")
    semaphore = asyncio.Semaphore(150) # Capped to 150 concurrent workers
    
    success_count = 0
    with open(OUTPUT_FILE, "w") as out_f:
        async with AsyncSession(impersonate="chrome120") as session:
            for name, value in clearance_cookies.items():
                session.cookies.set(name, value, domain=".kohls.com")
                
            tasks = [fetch_product_metadata(session, url, semaphore) for url in target_urls]
            
            for t in asyncio.as_completed(tasks):
                result = await t
                if result:
                    success_count += 1
                    out_f.write(json.dumps(result) + "\\n")
                    if success_count % 500 == 0:
                        print(f"    [->] Embedded {success_count} isolated JSON product payloads straight from backend...")

    print(f"\\n[+] Execution Complete! Extracted metadata & exact SKU/UPC graphs for {success_count} active Kohl's products.")
    print(f"[*] Saved structured JSON outputs to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
