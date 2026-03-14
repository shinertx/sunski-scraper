import requests
from bs4 import BeautifulSoup

url = "https://www.sunandski.com/p/3461064600725/sportubes-nik-nac-pac"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"Fetching {url}")
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    with open("sample_product.html", "w") as f:
        f.write(response.text)
    print("Saved to sample_product.html")
else:
    print("Failed to fetch. Might need SeleniumBase.")
