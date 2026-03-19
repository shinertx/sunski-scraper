# Kohl's National Scale Catalog & BOPUS Scraper

This directory contains a **Massive Asynchronous Hybrid Pipeline** designed to bypass Datadome and Akamai edge proxies natively to extract the entire Kohl's product catalog (~700k items) and verify physical inventory across all 1,100+ stores simultaneously.

## Architecture (The First Principles Method)

Traditional scraping relies heavily on headless browsers (Playwright, Selenium) which are incredibly slow, RAM-heavy, and easily detected by Datadome's volumetric sensors when querying hundreds of thousands of pages.

To achieve National-scale extraction in minutes rather than weeks, this pipeline uses a decoupled hybrid approach:

1. **The Clearance Key (`job1_get_cookies.py`)**: Uses a single undetected, visible Chrome browser to natively navigate to the Kohl's homepage. By displaying a physical browser window for 5 seconds, the script proves human behavior to the edge nodes and extracts a cleared cryptographic `_abck` cookie. This token is saved to disk.
2. **The Asynchronous Engine (`job1_run_async_workers.py`)**: This is a pure Python, socket-level async script utilizing `curl_cffi` to mimic Chrome 120 TLS signatures natively. It ingests the clearance cookie and fires 150 parallel workers simultaneously against the target catalog, ripping the pristine `window.productV2JsonData` JSON payloads straight out of the HTML without evaluating Javascript.
3. **The BOPUS Auditor (`job2_check_inventory_hybrid.py`)**: Utilizes the identical async TLS architecture to ping the internal `/v1/inventory` endpoint in 10-store chunks, instantly returning local stock numbers for every SKU across the country.

## Requirements

You must install the exact TLS-impersonation dependencies to avoid Bot traps:
```bash
pip3 install curl_cffi seleniumbase
```

## How to Run

1. Generate the master URLs (Optional if you already have them):
```bash
python3 job0_extract_kohls_sitemaps.py
```

2. Extract the local Physical Store IDs (Optional if you already have them):
```bash
python3 get_kohls_stores.py
```

3. **EXTRACT THE CATALOG**:
```bash
# 1. Spawn a pop-up Chrome browser to defeat Datadome natively and grab the session key
python3 job1_get_cookies.py

# 2. RUn the massive extraction workers (No UI, just raw socket speed)
python3 job1_run_async_workers.py
```

4. Check Local Inventory matrix (You must edit script to point to your exact output files):
```bash
python3 job2_check_inventory_hybrid.py
```
