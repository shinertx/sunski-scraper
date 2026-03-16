import sys, json, time, re
from seleniumbase import SB

urls = json.load(sys.stdin)
results = []

with SB(uc=True, headless=True) as sb:
    if not urls: sys.exit(0)
    
    # 1. Clear Akamai
    sb.uc_open_with_reconnect(urls[0], 15)
    time.sleep(8)
    
    # 2. Iterate and steal full context
    for u in urls:
        sb.open(u)
        time.sleep(3)
        html = sb.get_page_source()
        
        m = re.search(r'var productV2JsonData = (\{.*?\});', html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                
                # Extract ONLY WHAT WE NEED for the SKU graph (First Principles)
                output = {
                    "product_id": str(data.get("webID", "")),
                    "url": u,
                    "title": data.get("productTitle", ""),
                    "brand": str(data.get("brand", "")),
                    "description": data.get("description", {}).get("longDescription", ""),
                    "images": [img.get("url", "") for img in data.get("images", [])],
                    "categories": data.get("breadcrumbs", []),
                    "variants": []
                }
                
                # Map UPCs quickly
                upc_map = {str(upc.get("ID")): upc.get("upc") for upc in data.get("upcs", [])}
                
                for sku in data.get("SKUS", []):
                    sku_id = sku.get("skuId") or sku.get("skuCode")
                    if not sku_id: continue
                    
                    variant = {
                        "sku": str(sku_id),
                        "upc": upc_map.get(str(sku_id), ""),
                        "color": sku.get("color", ""),
                        "size": sku.get("size", ""),
                        "retail_price": str(sku.get("price", {}).get("regularPrice", ""))
                    }
                    output["variants"].append(variant)
                
                results.append(output)
            except Exception as e:
                pass

print(json.dumps(results, indent=2))
