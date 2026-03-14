from seleniumbase import SB
import time
import json

def dump_auth_data():
    url = "https://www.sunandski.com/p/3461064600725/sportubes-nik-nac-pac"
    with SB(uc=True, headless=True) as sb:
        sb.uc_open_with_reconnect("https://www.sunandski.com", 10)
        time.sleep(5)
        
        sb.open(url)
        time.sleep(5)
        
        cookies = sb.driver.get_cookies()
        
        local_store = sb.execute_script("return window.localStorage;")
        session_store = sb.execute_script("return window.sessionStorage;")
        
        # Let's also check the global standard Mozu objects
        mozu_context = sb.execute_script("return window.require ? window.require.s.contexts._.config : null;")
        
        data = {
            "cookies": cookies,
            "localStorage": local_store,
            "sessionStorage": session_store,
            "mozu_config": mozu_context
        }
        
        with open("auth_dump.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("Successfully dumped auth data!")

dump_auth_data()
