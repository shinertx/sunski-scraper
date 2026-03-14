import asyncio
from curl_cffi.requests import AsyncSession
import json

async def test_tor():
    url = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
    
    # Route through local Tor proxy
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    print("Testing Kohl's through Tor Onion Proxy...")
    try:
        async with AsyncSession(impersonate="chrome110", proxies=proxies, headers=headers) as session:
            
            # Check IP first
            ip_resp = await session.get("https://api.ipify.org?format=json", timeout=15)
            print(f"Tor Exit Node IP: {ip_resp.json()['ip']}")
            
            # Test Kohls
            resp = await session.get(url, timeout=30)
            
            print(f"\nResponse Status: {resp.status_code}")
            print(f"Response Size: {len(resp.text)} bytes")
            
            if resp.status_code == 200 and len(resp.text) > 10000:
                print("⭐⭐⭐ HUGE SUCCESS! Tor bypassed the Akamai IP Ban! ⭐⭐⭐")
                with open("tor_success_dump.html", "w") as f:
                    f.write(resp.text)
                
                if "var productV2JsonData =" in resp.text:
                    print("JSON data perfectly intact in the source!")
                else:
                    print("JSON missing - we might need Tor + Selenium.")
            else:
                print("FAILURE. Akamai blocked this Tor exit node too.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tor())
