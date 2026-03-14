import time
from seleniumbase import SB

url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
home = "https://www.kohls.com/"

print("Booting Selenium...")
try:
    with SB(uc=True, headless=True) as sb:
        print("Clearing Akamai on homepage with JS enabled...")
        sb.uc_open_with_reconnect(home, 5)
        time.sleep(5)
        
        print("Disabling Javascript via CDP to stop React from deleting the JSON...")
        sb.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})
        
        print(f"Fetching {url}... (with JS disabled)")
        sb.uc_open_with_reconnect(url, 5)
        time.sleep(2)
        
        html = sb.get_page_source()
        print(f"HTML size: {len(html)} bytes")
        
        if "var productV2JsonData" in html:
            print("⭐⭐⭐ SUCCESS! We defeated React Hydration! `productV2JsonData` is perfectly intact in the DOM! ⭐⭐⭐")
            with open("js_disabled_success.html", "w") as f:
                f.write(html)
        else:
            print("FAILURE: Still no JSON data.")
            if "Access Denied" in html:
                print("Wait, disabling JS caused Akamai to block us!")
            
except Exception as e:
    print(f"Error: {e}")
