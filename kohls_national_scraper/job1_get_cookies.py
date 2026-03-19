import json
import time
from seleniumbase import SB

def get_akamai_clearance():
    print("[*] Spawning Visible Stealth Browser to bypass Datadome natively...")
    clearance_cookies = {}
    
    with SB(uc=True, headless=False) as sb:
        sb.uc_open_with_reconnect("https://www.kohls.com/", 6)
        time.sleep(7) 
        
        for cookie in sb.driver.get_cookies():
            clearance_cookies[cookie['name']] = cookie['value']
            
    if '_abck' in clearance_cookies:
        print(f"[+] Sensor Cleared. Extracted _abck proxy token: {clearance_cookies['_abck'][:20]}...")
        with open("kohls_clearance_cookies.json", "w") as f:
            json.dump(clearance_cookies, f)
        print("[+] Wrote cookies to kohls_clearance_cookies.json")
    else:
        print("[-] Failed to capture _abck cookie!")

if __name__ == "__main__":
    get_akamai_clearance()
