import sys, json, time
from seleniumbase import SB

# Takes STDIN containing an array of SKU strings: ["94712478", "94718856"]
skus = json.load(sys.stdin)
zip_code = sys.argv[1] if len(sys.argv) > 1 else "78201"

results = {}

with SB(uc=True, headless=True) as sb:
    sb.uc_open_with_reconnect("https://www.kohls.com", 15)
    time.sleep(8) # Clear Akamai
    
    for sku in skus:
        # We loop through the internal API using the trusted browser session
        script = f"""
        var done = arguments[0]; 
        fetch('/snb/storesAvailabilitySearch?sku={sku}&limit=1&radius=50&zipCode={zip_code}', {{
            headers: {{ accept: 'application/json' }}
        }})
        .then(r => r.json())
        .then(done)
        .catch(err => done({{"error": err.toString()}}));
        """
        
        try:
            res = sb.execute_async_script(script)
            # If successful, dig down to the 'qtyAvailable' field for the first local store
            if 'allAvailableStores' in res and len(res['allAvailableStores']) > 0:
                store = res['allAvailableStores'][0]
                inventory_data = store.get("availableQuantity", 0) # This structure requires checking based on API
                results[sku] = res
        except Exception as e:
            results[sku] = {"error": str(e)}
            
        time.sleep(1) # Be polite to API

print(json.dumps(results, indent=2))
