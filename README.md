# rogue-kepler (Retail Scraper & Inventory Tools)

This repository contains a collection of Python scripts designed to extract product catalogs and check real-time inventory from various Kibo Commerce and custom storefronts. 

It was primarily developed to work with the Sunski brand (handling complex product variations, acquiring location directories, and querying matrix inventory across all retail stores) but also includes experiments for scraping other retail endpoints.

**[👉 Click Here to Download the Extracted Data & Store Feeds (v1.0.0) 👈](https://github.com/shinertx/sunski-scraper/releases/tag/v1.0.0)**

## Features

- **Store Location Extraction**: Spawns headless browsers via Playwright to mimic natural requests and gather physical store location codes and coordinates.
- **Deep Catalog Extraction**: Crawls sitemaps, extracts hidden GraphQL / Next.js JSON state blocks, and compiles comprehensive product catalogs with full nested variation logic (Colors -> Sizes).
- **Blazing Fast Inventory Checks**: Uses asynchronous networking (`aiohttp`) to bypass rate limits and concurrently check matrix-level stock across all physical store locations simultaneously.
- **Store-Specific localized Feeds**: Generates standardized, nested JSON payload schemas compatible with external inventory tracking platforms, distributed into individual feeds based on the retail store.

## Installation

1. Verify you have Python 3.10+ installed.
2. Clone this repository.
3. Install the dependencies. You may wish to use a virtual environment.

```bash
pip install aiohttp playwright bs4 lxml
playwright install chromium
```

## Basic Usage (Sunski Flow)

The Sunski workflow is split into two asynchronous scripts:

### 1. Build the Master Catalog
First, extract the complete product catalog. This scours the website, parsing nested state objects to build a master JSON file of all products and their valid variants (colors/sizes).

```bash
python build_catalog_sunski.py
```
*Note: This process may take a while depending on the size of the sitemap. It generates `sunski_catalog.json` (very large, excluded from Git) and `catalog_extraction.log` for debugging.*

### 2. Check Inventory and Build Store Feeds
Once you have the localized schema built in step 1, run the inventory checker. This will perform rapid asynchronous checks for all variants and locations, building out individual feed payloads per-store.

```bash
python check_inventory_sunski.py
```
*Outputs will be placed in the `store_feeds/` directory.*

### 3. Downloading the Data Directly
Because the resulting catalog and store feeds are quite large (hundreds of megabytes), they are excluded from this git repository to prevent bloat.

Instead of running the scripts yourself, you can download a `.zip` archive containing the most recent `sunski_catalog.json` and the complete `store_feeds/` directory from the Releases tab:
[Download Latest Data Release](https://github.com/shinertx/sunski-scraper/releases/tag/v1.0.0)

## Understanding the Output JSON
If you are looking to extract GTINs (UPCs) and stock levels, you will want to look at the individual JSON files generated inside integer-named files in the `store_feeds/` directory (e.g., `sunski_inventory_17.json`).

Each store feed contains a JSON array of product objects. Inside each product object, look at the `variants` array:

```json
{
  "title": "Example Product",
  "variants": [
    {
      "color": "Black",
      "size": "Medium",
      "upc": "840000000000",        // <--- THIS IS THE GTIN
      "inventory": "5",             // <--- THIS IS THE INVENTORY LEVEL FOR THIS SPECIFIC STORE
      "in_stock": "true",
      "price": "19.99"
    }
  ]
}
```

## Project Structure (Key Files)

- `build_catalog_sunski.py` — The core crawler building the product schema from the sitemap.
- `check_inventory_sunski.py` — The fast, asynchronous matrix inventory fetcher mapping variants against Kibo Commerce APIs.
- `sitemap_extractor_sunski.py` / `product_scraper_sunski.py` — Utility scripts for specific extraction tasks.

*(Other files like `test_*.py` and `*kohl*.py` are experimental or test harness files targeting specific headless capabilities or logic validation.)*

---
**Disclaimer**: This is a proof-of-concept repository. It is intended for educational purposes or authorized integrations. Ensure you are respecting standard rate limits, terms of service, and utilizing organic headers/cookies where possible.
