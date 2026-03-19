import xml.etree.ElementTree as ET
from curl_cffi import requests
import json

def fetch_kohls_stores():
    print("[*] Fetching Kohl's Store Directory via TLS-Impersonation...")
    session = requests.Session(impersonate="chrome120")
    store_sitemap = "https://www.kohls.com/sitemap_store.xml"
    
    r = session.get(store_sitemap, timeout=30)
    if r.status_code == 200:
        root = ET.fromstring(r.content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        store_urls = [node.text for node in root.findall('.//ns:loc', namespaces)]
        
        store_ids = set()
        
        for url in store_urls:
            # Example: https://www.kohls.com/stores/wi/muskego-485.shtml
            filename = url.split('/')[-1]
            if '-' in filename:
                potential_id = filename.split('-')[-1].replace('.shtml', '').replace('.jsp', '')
                if potential_id.isdigit():
                    store_ids.add(potential_id)
        
        print(f"\\n[+] Successfully isolated {len(store_ids)} unique Kohl's Store IDs nationwide!")
        
        if store_ids:
            with open("kohls_store_ids.json", "w") as f:
                json.dump(list(store_ids), f, indent=2)
            print("[*] Wrote Master Store Directory to kohls_store_ids.json")
            print(f"    Examples: {list(store_ids)[:5]}")

if __name__ == "__main__":
    fetch_kohls_stores()
