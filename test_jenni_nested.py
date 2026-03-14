import json
from bs4 import BeautifulSoup

def examine_jenni_nested():
    with open('sample_product.html', 'r') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='data-mz-preload-product')
    product_data = json.loads(script.string)
    
    product_id = product_data.get('productCode', '')
    title = product_data.get('content', {}).get('productName', '')
    desc_text = product_data.get('content', {}).get('productFullDescription', '')
    brand_name = product_data.get('content', {}).get('productBrand', '')
    price = str(product_data.get('price', {}).get('price', ''))
    upc = product_data.get('upc', '')
    url = f"https://www.sunandski.com/p/{product_id}" # Close enough fallback
    
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
                "small_url": image_url, # Sub in if needed
                "is_primary": "1" if idx == 0 else "0"
            })
            
    # Build Option Value map from parent to get human-readable strings
    # Looks like: {"tenant~color": {"23": "Black", "9": "White"}, "tenant~size": {"5": "M"}}
    option_map = {}
    for opt in product_data.get('options', []):
        fqn = opt.get('attributeFQN', '')
        option_map[fqn] = {}
        for val in opt.get('values', []):
            vid = str(val.get('value', ''))
            vstr = str(val.get('stringValue', vid))
            option_map[fqn][vid] = vstr
            
    variants = []
    for var in product_data.get('variations', []):
        var_sku = var.get('productCode', '')
        var_upc = var.get('upc', upc)
        var_price = str(var.get('price', price)) # If variant has specific price
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
                
        # Fill missing options to match schema expectation (usually up to 3)
        while option_idx <= 3:
            var_options[f"option{option_idx}_name"] = ""
            var_options[f"option{option_idx}_value"] = ""
            option_idx += 1
            
        var_title = f"{title} - {color} / {size}" if color and size else title
            
        variants.append({
            "sku": var_sku,
            "product_id": product_id,
            "upc": var_upc,
            "gtin": var_upc, # Sun & Ski tends to use UPC
            "title": var_title,
            "price_amount": var_price,
            "sale_amount": var_sale,
            "in_stock": "", # Added later by inventory checker
            "inventory": "", # Added later by inventory checker
            "color": color,
            "size": size,
            "gender": gender_classification,
            "gender_classification": gender_classification,
            **var_options,
            "images": product_images # Can inherit parent images
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
            "inventory": "", # Added later
            "in_stock": "", # Added later
            "color": variants[0].get('color', '') if variants else "",
            "size": variants[0].get('size', '') if variants else "",
            "url": url,
            "product_condition": "NewCondition",
            "gender": gender_classification,
            "gender_classification": gender_classification
        },
        "variants": variants,
        "product_images": product_images,
        "store_details": {} # Will be populated by the inventory scraper
    }
    
    print(json.dumps([jenni_record], indent=2))

if __name__ == "__main__":
    examine_jenni_nested()
