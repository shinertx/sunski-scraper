import json
from bs4 import BeautifulSoup

def examine_kibo_options():
    with open('sample_product.html', 'r') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='data-mz-preload-product')
    product_data = json.loads(script.string)
    
    variations = product_data.get('variations', [])
    if variations:
        var = variations[0]
        print(json.dumps(var.get('options', []), indent=2))
        
        # Also see if parent level has the mapping for option values
        print("\nParent options list:")
        print(json.dumps(product_data.get('options', []), indent=2))

if __name__ == "__main__":
    examine_kibo_options()
