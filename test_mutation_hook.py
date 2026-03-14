import time
import json
from seleniumbase import SB

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
home = "https://www.kohls.com/"

print("Booting Selenium...")
try:
    with SB(uc=True, headless=True) as sb:
        print("Clearing Akamai on homepage...")
        sb.uc_open_with_reconnect(home, 5)
        time.sleep(5)
        
        print("Injecting MutationObserver via CDP...")
        script_to_inject = """
        window._STOLEN_SCRIPT = null;
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                for (const node of mutation.removedNodes) {
                    if (node.tagName === 'SCRIPT' && node.innerHTML) {
                        if (node.innerHTML.includes('productV2JsonData') || node.innerHTML.includes('__NEXT_DATA__')) {
                            window._STOLEN_SCRIPT = node.innerHTML;
                        }
                    }
                }
            }
        });
        // We must observe document.documentElement once it exists, or just document
        observer.observe(document, { childList: true, subtree: true });
        """
        sb.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script_to_inject})
        
        print(f"Loading {url}...")
        sb.uc_open_with_reconnect(url, 5)
        time.sleep(5)
        
        print("Checking if the MutationObserver caught the script tag...")
        stolen_html = sb.execute_script("return window._STOLEN_SCRIPT;")
        
        if stolen_html:
            print(f"⭐⭐ SUCCESS! Stole script contents before deletion! Size: {len(stolen_html)} bytes ⭐⭐")
            with open("stolen_script.txt", "w") as f:
                f.write(stolen_html)
        else:
            print("FAILURE: MutationObserver didn't catch anything.")
            
            # Alternative: What if the script text is in the original HTML response? 
            # Let's search document.documentElement.innerHTML just in case it's STILL THERE and just hidden
            current_html = sb.get_page_source()
            with open("working_page.html", "w") as f:
                f.write(current_html)
            print(f"Saved {len(current_html)} bytes to working_page.html")
except Exception as e:
    print(f"Error: {e}")
