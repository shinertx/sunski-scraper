import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
import time

async def fetch_product(session, url):
    """
    Fetches a single Sun & Ski product page and extracts the product
    metadata (GTIN, description, photos, sizes, etc.) from the embedded JSON.
    """
    try:
        async with session.get(url, timeout=20) as response:
            if response.status != 200:
                print(f"Failed to fetch {url}: HTTP {response.status}")
                return None
                
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            script_tag = soup.find('script', id='data-mz-preload-product')
            if not script_tag or not script_tag.string:
                print(f"No metadata found for {url}")
                return None
                
            product_data = json.loads(script_tag.string)
            
            product_id = product_data.get('productCode', '')
            title = product_data.get('content', {}).get('productName', '')
            desc_text = product_data.get('content', {}).get('productFullDescription', '')
            brand_name = product_data.get('content', {}).get('productBrand', '')
            price = str(product_data.get('price', {}).get('price', ''))
            upc = product_data.get('upc', '')
            
            properties = product_data.get('properties', [])
            gender_classification = ""
            for prop in properties:
                fqn = prop.get('attributeFQN', '').lower()
                if 'gender' in fqn or 'tenant~mf' in fqn:
                    vals = prop.get('values', [])
                    if vals:
                        gender_classification = vals[0].get('stringValue', vals[0].get('value', ''))
                        break
                        
            categories = product_data.get('categories', [])
            cat_names = [c.get('content', {}).get('name', '') for c in categories if c.get('content', {}).get('name')]
            category_name = " > ".join(cat_names) if cat_names else ""
            
            images = product_data.get('content', {}).get('productImages', [])
            product_images = []
            for idx, img in enumerate(images):
                raw_url = img.get('imageUrl', '')
                image_url = f"https:{raw_url}" if raw_url.startswith("//") else raw_url
                if image_url:
                    product_images.append({
                        "large_url": image_url,
                        "small_url": image_url,
                        "is_primary": "1" if idx == 0 else "0"
                    })
                    
            option_map = {}
            for opt in product_data.get('options', []):
                fqn = opt.get('attributeFQN', '')
                option_map[fqn] = {}
                for val in opt.get('values', []):
                    vid = str(val.get('value', ''))
                    vstr = str(val.get('stringValue', vid))
                    option_map[fqn][vid] = vstr
                    
            variants = []
            variations = product_data.get('variations', [])
            
            # If no variations exist, create a dummy self-variant
            if not variations:
                variants.append({
                    "sku": product_id,
                    "product_id": product_id,
                    "upc": upc,
                    "gtin": upc,
                    "title": title,
                    "price_amount": price,
                    "sale_amount": str(product_data.get('price', {}).get('salePrice', '')),
                    "in_stock": "", 
                    "inventory": "", 
                    "color": "",
                    "size": "",
                    "gender": gender_classification,
                    "gender_classification": gender_classification,
                    "option1_name": "", "option1_value": "",
                    "option2_name": "", "option2_value": "",
                    "option3_name": "", "option3_value": "",
                    "images": product_images
                })
            else:
                for var in variations:
                    var_sku = var.get('productCode', '')
                    var_upc = var.get('upc', upc)
                    var_price = str(var.get('price', price))
                    var_sale = str(var.get('salePrice', ''))
                    
                    color = ""
                    size = ""
                    option_idx = 1
                    var_options = {}
                    
                    for opt in var.get('options', []):
                        attr_name = opt.get('attributeFQN', '')
                        val_id = str(opt.get('value', ''))
                        val_str = option_map.get(attr_name, {}).get(val_id, val_id)
                        
                        clean_name = attr_name.replace('tenant~', '').title()
                        var_options[f"option{option_idx}_name"] = clean_name
                        var_options[f"option{option_idx}_value"] = val_str
                        option_idx += 1
                        
                        if 'color' in attr_name.lower():
                            color = val_str
                        elif 'size' in attr_name.lower():
                            size = val_str
                            
                    while option_idx <= 3:
                        var_options[f"option{option_idx}_name"] = ""
                        var_options[f"option{option_idx}_value"] = ""
                        option_idx += 1
                        
                    var_title = f"{title} - {color} / {size}" if color and size else title
                        
                    variants.append({
                        "sku": var_sku,
                        "product_id": product_id,
                        "upc": var_upc,
                        "gtin": var_upc,
                        "title": var_title,
                        "price_amount": var_price,
                        "sale_amount": var_sale,
                        "in_stock": "",
                        "inventory": "",
                        "color": color,
                        "size": size,
                        "gender": gender_classification,
                        "gender_classification": gender_classification,
                        **var_options,
                        "images": product_images
                    })
                
            jenni_record = {
                "products": {
                    "product_id": product_id,
                    "sku": product_id,
                    "title": title,
                    "desc_text": desc_text,
                    "desc_html": "",
                    "brand_name": brand_name,
                    "currency": "USD",
                    "external_sell_price": price,
                    "upc": upc,
                    "gtin": upc,
                    "category_name": category_name,
                    "inventory": "",
                    "in_stock": "",
                    "color": variants[0].get('color', '') if variants else "",
                    "size": variants[0].get('size', '') if variants else "",
                    "url": url,
                    "product_condition": "NewCondition",
                    "gender": gender_classification,
                    "gender_classification": gender_classification
                },
                "variants": variants,
                "product_images": product_images,
                "store_details": {}
            }
            
            return [jenni_record]
    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return None

async def process_batch(session, urls_batch):
    tasks = [fetch_product(session, url) for url in urls_batch]
    return await asyncio.gather(*tasks)

async def main():
    try:
        with open("sunski_target_urls.json", "r") as f:
            all_urls = json.load(f)
    except FileNotFoundError:
        print("sunski_target_urls.json missing! Run sitemap extractor first.")
        return
        
    # Process the entire batch of URLs
    target_urls = all_urls
    print(f"Starting async pure-HTTP extraction for {len(target_urls)} URLs...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    start_time = time.time()
    catalog_results = []
    
    # We use a TCPConnector with limits to avoid being overly aggressive
    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        
        batch_size = 5
        for i in range(0, len(target_urls), batch_size):
            batch = target_urls[i:i + batch_size]
            results = await process_batch(session, batch)
            
            for res in results:
                if res:
                    catalog_results.extend(res)
                    print(f"Scraped {len(res)} variations from {res[0].get('title', '')}")
            
            # Tiny polite delay between batches
            await asyncio.sleep(1)
            
    # Save the catalog payload
    output_file = "sunski_catalog.json"
    with open(output_file, "w") as f:
        json.dump(catalog_results, f, indent=2)
        
    duration = time.time() - start_time
    print(f"\nSaved {len(catalog_results)} complete catalog records to {output_file} in {duration:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
