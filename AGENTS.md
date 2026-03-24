# First Principles Automation Mandate

*This mandate acts as the core operating protocol for all AI Agents executing data extraction, web scraping, and automation tasks in this workspace.*

## 1. Eliminate the Noise Early
Be ruthlessly efficient. Filter out irrelevant data at the very first step of the pipeline. Do not scrape data you don't need. Delete and drop records that do not strictly match the hyper-specific criteria (e.g., dropping non-Shopify platforms if we only need Shopify, or dropping stores without In-Store Pickup immediately).

## 2. API & Endpoint Supremacy
Always prioritize hitting native APIs and structured JSON endpoints (e.g., Shopify's `/products.json`, WooCommerce APIs, GraphQL endpoints, explicit checkout payloads) before deploying headless browsers. Headless browsers (Playwright/Selenium) should be the *last resort*, not the first option.

## 3. Bot Protection Awareness
When dealing with enterprise sites (Nike, Academy, Walmart, Kohl's etc.), assume Akamai, Cloudflare, or Datadome bot protection is present. Skip raw `requests` and default headless instances. Immediately default to TLS-impersonation (e.g., `curl_cffi` impersonating a real Chrome signature) or authorized cookie injection (`_abck`) to bypass edge nodes cleanly.

## 4. Ground Truth Verification
Never assume a feature exists just because the front text says so. Prove it. If a store claims to have "In-Store Pickup", verify it by either parsing the cart API response, identifying the specific HTML element, or finding explicit checkout parameters.

## 5. Modularity & Reusability
Data pipelines should be broken down into discrete, reusable Python scripts (e.g., `job1_get_cookies`, `job1_run_async_workers`, `shopify_detector`). Do not build monolithic scrapers. The output of one script must cleanly pipe into the next using normalized JSON. Make it simple, make it fast, and make it modular.
