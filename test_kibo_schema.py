import requests
import json
from bs4 import BeautifulSoup

url = "https://www.sunandski.com/p/03210010870002401/glyder-women-s-electric-tank-top"
headers = {"User-Agent": "Mozilla/5.0"}

html = requests.get(url, headers=headers).text
soup = BeautifulSoup(html, 'html.parser')
script = soup.find('script', id='data-mz-preload-product')
data = json.loads(script.string)

# Dump minimal fields for inspection
print("CATEGORIES:")
print(json.dumps(data.get('categories', []), indent=2))

print("\nPROPERTIES:")
print(json.dumps(data.get('properties', []), indent=2))
