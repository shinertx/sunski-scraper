import json
import requests
from bs4 import BeautifulSoup
import time

def extract_urls_from_sitemaps():
    """Extracts product URLs from Sun & Ski sitemaps."""
    main_sitemap = "https://www.sunandski.com/sitemap.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching main sitemap: {main_sitemap}")
    response = requests.get(main_sitemap, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch main sitemap. Status: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'xml')
    sitemaps = [loc.text for loc in soup.find_all('loc') if 'productBatch' in loc.text]
    
    all_product_urls = []
    
    print(f"Found {len(sitemaps)} product sub-sitemaps. Fetching...")
    
    for sitemap_url in sitemaps:
        print(f"Fetching sub-sitemap: {sitemap_url}")
        res = requests.get(sitemap_url, headers=headers)
        if res.status_code == 200:
            sub_soup = BeautifulSoup(res.content, 'xml')
            urls = [loc.text for loc in sub_soup.find_all('loc')]
            all_product_urls.extend(urls)
            print(f"  -> Found {len(urls)} product URLs.")
        else:
            print(f"  -> Failed. Status: {res.status_code}")
        time.sleep(1) # Be polite
            
    # Deduplicate just in case
    all_product_urls = list(set(all_product_urls))
    
    output_file = "sunski_target_urls.json"
    print(f"\nTotal unique product URLs extracted: {len(all_product_urls)}")
    with open(output_file, "w") as f:
        json.dump(all_product_urls, f, indent=2)
        
    print(f"Successfully saved URLs to {output_file}")

if __name__ == "__main__":
    extract_urls_from_sitemaps()
