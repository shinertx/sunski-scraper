import json
import requests
from bs4 import BeautifulSoup
import hashlib

def test_jenni_mapping():
    url = "https://www.sunandski.com/p/03210010870002401/glyder-women-s-electric-tank-top"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='data-mz-preload-product')
    product_data = json.loads(script.string)
    
    # Extract properties
    properties = product_data.get('properties', [])
    gender_classification = ""
    for prop in properties:
        fqn = prop.get('attributeFQN', '').lower()
        if 'gender' in fqn or 'tenant~mf' in fqn:
            vals = prop.get('values', [])
            if vals:
                gender_classification = vals[0].get('stringValue', vals[0].get('value', ''))
                break
                
    # Categories
    categories = product_data.get('categories', [])
    full_category = ""
    sub_category = ""
    if categories:
        # Just grab the first leaf category's name and its parent
        leaf = categories[0]
        sub_category = leaf.get('content', {}).get('name', '')
        # Usually Kibo categories have a hierarchy, but we can just use the product's primary categories
        
    parent_product_id = product_data.get('productCode', '')
    title = product_data.get('content', {}).get('productName', '')
    desc_text = product_data.get('content', {}).get('productFullDescription', '')
    brand_name = product_data.get('content', {}).get('productBrand', '')
    
    images = product_data.get('content', {}).get('productImages', [])
    image_url = images[0].get('imageUrl') if images else ""
    
    variations = product_data.get('variations', [])
    variant_count = len(variations)
    
    jenni_records = []
    
    for var in variations:
        var_code = var.get('productCode')
        upc = var.get('upc')
        
        # Color and Size from options
        color = ""
        size = ""
        for opt in var.get('options', []):
            attr_name = opt.get('attributeFQN', '').lower()
            val = opt.get('value', '')
            if 'color' in attr_name:
                color = str(val)
            elif 'size' in attr_name:
                size = str(val)
                
        # Fallback to product upc if variation has none
        final_upc = upc if upc else product_data.get('upc', '')
        
        # Generate a jenni_product_id (can be a hash of variation code or just the code itself)
        jenni_product_id = var_code
        
        record = {
            "jenni_product_id": jenni_product_id,
            "title": title,
            "desc_text": desc_text,
            "upc": final_upc,
            "brand_name": brand_name,
            "parent_product_id": parent_product_id,
            "variant_count": variant_count,
            "color": color,
            "size": size,
            "full_category": full_category, # Might be empty, we can improve
            "sub_category": sub_category,
            "gender_classification": gender_classification,
            "image_url": image_url
        }
        jenni_records.append(record)
        
    print(json.dumps(jenni_records[:2], indent=2))

if __name__ == "__main__":
    test_jenni_mapping()
