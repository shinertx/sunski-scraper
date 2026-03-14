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
        
        print("Injecting JS hook via CDP to steal JSON before GC...")
        script_to_inject = """
        // Intercept '__NEXT_DATA__' and 'productV2JsonData'
        let stolenNextData = null;
        let stolenV2 = null;
        
        Object.defineProperty(window, '__NEXT_DATA__', {
            set: function(val) {
                stolenNextData = val;
                window._STOLEN_NEXT_DATA = JSON.parse(JSON.stringify(val));
                this._nd = val;
            },
            get: function() { return this._nd; }
        });
        
        Object.defineProperty(window, 'productV2JsonData', {
            set: function(val) {
                stolenV2 = val;
                window._STOLEN_V2_DATA = JSON.parse(JSON.stringify(val));
                this._v2 = val;
            },
            get: function() { return this._v2; },
            configurable: true
        });
        """
        sb.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script_to_inject})
        
        print(f"Loading {url}...")
        sb.uc_open_with_reconnect(url, 5)
        time.sleep(5)
        
        print("Checking if the Hook caught anything...")
        stolen_v2 = sb.execute_script("return window._STOLEN_V2_DATA;")
        stolen_next = sb.execute_script("return window._STOLEN_NEXT_DATA;")
        
        if stolen_v2:
            print("⭐⭐ SUCCESS! Stole productV2JsonData! ⭐⭐")
            with open("stolen_v2.json", "w") as f:
                json.dump(stolen_v2, f, indent=4)
        elif stolen_next:
            print("⭐⭐ SUCCESS! Stole __NEXT_DATA__! ⭐⭐")
            with open("stolen_next.json", "w") as f:
                json.dump(stolen_next, f, indent=4)
        else:
            print("FAILURE: Hook didn't catch anything. The data might not be assigned to 'window' at all.")
            
except Exception as e:
    print(f"Error: {e}")
