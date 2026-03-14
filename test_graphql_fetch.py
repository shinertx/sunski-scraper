import time
from seleniumbase import SB
import json

print("Booting Selenium...")
try:
    with SB(uc=True, headless=True) as sb:
        print("Clearing Akamai on homepage...")
        sb.uc_open_with_reconnect("https://www.kohls.com/", 5)
        time.sleep(5)
        
        print("Injecting GraphQL fetch query for Product Data...")
        
        # We try to mimic a real Kohl's frontend GraphQL request
        js_script = """
        var callback = arguments[arguments.length - 1];
        
        const payload = {
            "operationName": "getProducts",
            "variables": {
                "skus": ["2868971", "1107"]
            },
            "query": "query getProducts($skus: [String]) { products(skus: $skus) { id title description images { url } } }"
        };
        
        // This is an exploratory GraphQL payload, if they use GraphQL on /graphql
        fetch("https://www.kohls.com/graphql", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.text())
        .then(text => callback(text))
        .catch(err => callback("ERROR: " + err.toString()));
        """
        
        result = sb.execute_async_script(js_script)
        
        print("GraphQL Fetch Result:")
        print(result[:1000])
        
        with open("graphql_test_result.txt", "w") as f:
            f.write(result)
            
except Exception as e:
    print(f"Error: {e}")
