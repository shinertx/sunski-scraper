import json
import time
from seleniumbase import SB
from bs4 import BeautifulSoup

def extract_urls_from_sitemaps():
    """Uses SeleniumBase to bypass Akamai and fetch product URLs from Kohls sitemaps."""
    base_url = "https://www.kohls.com"
    sitemaps = [f"{base_url}/sitemap_product_{i}.xml" for i in range(1, 16)]
    all_product_urls = []
    
    print(f"Attempting to fetch {len(sitemaps)} sitemaps using SeleniumBase Stealth...")
    
    # We use UC (undetected_chromedriver) to bypass Akamai bot protection
    with SB(uc=True, headless=True) as sb:
        # First, go to the homepage to let Akamai set its trusted cookies
        print("Navigating to homepage to clear Akamai Challenge...")
        sb.uc_open_with_reconnect(base_url, 10)
        time.sleep(5) # Wait for challenge to pass
        
        # Now we process the first sitemap (for testing, just doing the first one)
        for sitemap_url in sitemaps[:1]:
            print(f"Fetching sitemap: {sitemap_url}")
            # Fetch the XML source natively
            sb.uc_open_with_reconnect(sitemap_url, 4)
            time.sleep(2)
            
            # The XML might be rendered inside an HTML wrapper by the browser
            # We will use JavaScript to get the raw text content or parse the DOM
            xml_content = sb.get_page_source()
            
            # Use BeautifulSoup to parse the XML out of the page source
            soup = BeautifulSoup(xml_content, 'xml') # Try parsing as strict XML first
            
            # Find all <loc> tags which contain the URLs
            loc_tags = soup.find_all('loc')
            if not loc_tags:
                # Fallback: maybe it rendered as HTML
                soup = BeautifulSoup(xml_content, 'html.parser')
                loc_tags = soup.find_all('loc')
            
            urls = [tag.text.strip() for tag in loc_tags if tag.text.strip()]
            
            print(f"Found {len(urls)} URLs in {sitemap_url.split('/')[-1]}")
            all_product_urls.extend(urls)
            time.sleep(2) # Be polite between sitemaps
            break # Just doing first one for the test
            
    # Save the urls
    output_file = "target_skus.json"
    print(f"Total URLs extracted: {len(all_product_urls)}")
    with open(output_file, "w") as f:
        json.dump(all_product_urls, f, indent=2)
        
    print(f"Successfully saved URLs to {output_file}")

if __name__ == "__main__":
    extract_urls_from_sitemaps()
