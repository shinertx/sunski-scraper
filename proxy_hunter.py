import asyncio
from curl_cffi.requests import AsyncSession
import aiohttp

async def fetch_proxies():
    print("Downloading massive free proxy list...")
    # This repo updates every few hours with thousands of scraped HTTP proxies
    url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    proxies = [line.strip() for line in text.split('\n') if line.strip()]
                    print(f"Downloaded {len(proxies)} public proxies!")
                    return proxies
    except Exception as e:
        print(f"Failed to download list: {e}")
    return []

async def test_proxy(proxy_str, target_url, sem):
    async with sem:
        # Format the proxy for curl_cffi
        proxy = {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }
        
        try:
            # We use chrome110 impersonate to dodge the TLS bot checks
            async with AsyncSession(impersonate="chrome110", proxies=proxy, headers=headers) as session:
                # small timeout because public proxies are slow/unreliable
                resp = await session.get(target_url, timeout=10)
                
                # If we get a 200 and the HTML length isn't the tiny 483 byte Akamai block
                if resp.status_code == 200 and len(resp.text) > 10000:
                    print(f"\n[WINNER] Found working proxy! {proxy_str} - Passed Akamai! HTML size: {len(resp.text)}")
                    return proxy_str
        except Exception:
            # Proxy was dead or timed out or Akamai blocked it
            pass
            
    return None

async def proxy_hunter():
    proxies = await fetch_proxies()
    if not proxies:
        return
        
    target = "https://www.kohls.com/product/prd-1107/lee-carpenter-jeans.jsp"
    
    # We will test 50 proxies concurrently to find one fast
    sem = asyncio.Semaphore(50)
    
    print("Testing proxies to find an Akamai bypass (this may take a minute)...")
    
    # Let's take the top 500 to test
    tasks = [test_proxy(p, target, sem) for p in proxies[:500]]
    
    # We will use asyncio.as_completed so we can stop as soon as we find ONE winner
    for future in asyncio.as_completed(tasks):
        winner = await future
        if winner:
            print(f"Successfully secured proxy {winner}. Saving to functional_proxies.txt")
            with open("functional_proxies.txt", "w") as f:
                f.write(winner + "\n")
            
            # Keep hunting for a few more or stop here? Let's just exit so we can test it immediately
            return winner
            
    print("No functional proxies found in the first batch. The IP bans are very strict.")
    return None

if __name__ == "__main__":
    asyncio.run(proxy_hunter())
