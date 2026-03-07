#!/usr/bin/env python3
"""
Hybrid GCP Product Scraper - 100% complete coverage
Uses HTTP requests for speed, Playwright for categories that need it
"""

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import time


def get_featured_descriptions():
    """Get featured product descriptions from main page."""
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
    
    try:
        resp = session.get("https://cloud.google.com/products", timeout=30)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        featured = {}
        for card in soup.find_all('a', class_='xVzQV'):
            name_div = card.find('div', class_='owa4Ee')
            desc_div = card.find('div', class_='z5liZ')
            if name_div and desc_div:
                featured[name_div.get_text(strip=True)] = desc_div.get_text(strip=True)
        
        return featured
    except:
        return {}


def scrape_via_http(category_code, featured_descriptions):
    """Scrape category using HTTP requests."""
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    url = f"https://cloud.google.com/products?pds={category_code}"
    
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        products = []
        
        for card in soup.find_all('a', class_='hfCetc'):
            name_div = card.find('div', class_='owa4Ee')
            if not name_div:
                continue
            
            name = name_div.get_text(strip=True)
            desc_div = card.find('div', class_='z5liZ')
            
            if desc_div:
                desc = desc_div.get_text(strip=True)
            elif name in featured_descriptions:
                desc = featured_descriptions[name]
            else:
                continue
            
            if name and desc and len(desc) > 10:
                products.append({"ProductName": name, "Description": desc})
        
        return products, None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            return None, "500_error"
        return None, str(e)
    except Exception as e:
        return None, str(e)


def scrape_via_browser(category_name):
    """Scrape category using Playwright when HTTP fails."""
    print(f"    Using browser automation...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            page.goto("https://cloud.google.com/products", wait_until="domcontentloaded", timeout=45000)
            time.sleep(3)
            
            button = page.locator(f"button:has-text('{category_name}')").first
            button.click(timeout=10000)
            time.sleep(3)
            
            page.wait_for_selector("a.hfCetc", timeout=10000)
            time.sleep(2)
            
            products = []
            product_links = page.locator("a.hfCetc").all()
            
            for link in product_links:
                try:
                    name = link.locator("div.owa4Ee").first.text_content(timeout=3000).strip()
                    
                    try:
                        desc = link.locator("div.z5liZ").first.text_content(timeout=3000).strip()
                    except:
                        desc = None
                    
                    if name and desc and len(desc) > 10:
                        products.append({"ProductName": name, "Description": desc})
                except:
                    continue
            
            browser.close()
            return products, None
            
        except Exception as e:
            browser.close()
            return None, str(e)


def google_product_scraper():
    """Main scraper - tries HTTP first, uses browser for failures."""
    
    print("=" * 70)
    print("Hybrid GCP Product Scraper - Complete Coverage")
    print("=" * 70)
    print()
    
    categories = {
        "AI/ML": "CAE",
        "Infrastructure": "CAQ",
        "Databases and analytics": "CAc",
        "Developer tools": "CAg",
        "App development": "CAk",
        "Integration services": "CAo",
        "Management tools": "CAs",
        "Security and identity": "CAw",
        "Web and app hosting": "CA0",
        "Productivity and collaboration": "CA4",
        "Industry": "CA8"
    }
    
    print("Fetching featured product descriptions...")
    featured_descriptions = get_featured_descriptions()
    print(f"  ✓ Found {len(featured_descriptions)} featured descriptions\n")
    
    all_data = []
    
    for category_name, category_code in categories.items():
        print(f"Scraping: {category_name}...")
        
        # Try HTTP first
        products, error = scrape_via_http(category_code, featured_descriptions)
        
        # If HTTP failed with 500, try browser
        if error == "500_error":
            print(f"    HTTP returned 500, trying browser...")
            products, error = scrape_via_browser(category_name)
        
        if products:
            # Remove duplicates within category
            seen = set()
            unique = []
            for p in products:
                if p['ProductName'] not in seen:
                    seen.add(p['ProductName'])
                    unique.append(p)
            
            all_data.append({
                "Product Section": category_name,
                "Services": sorted(unique, key=lambda x: x['ProductName'])
            })
            print(f"  ✓ Found {len(unique)} products")
        else:
            print(f"  ✗ Failed: {error}")
        
        time.sleep(2)
    
    return all_data


if __name__ == "__main__":
    try:
        scraped_data = google_product_scraper()
        
        if not scraped_data:
            print("\n⚠️  No data collected")
            exit(1)
        
        total = sum(len(s["Services"]) for s in scraped_data)
        unique = len(set(p["ProductName"] for s in scraped_data for p in s["Services"]))
        
        print()
        print("=" * 70)
        print(f"✓ {total} product entries across {len(scraped_data)} categories")
        print(f"✓ {unique} unique products")
        print("=" * 70)
        
        print("\nBreakdown:")
        for section in scraped_data:
            print(f"  • {section['Product Section']}: {len(section['Services'])} products")
        
        with open("GCP_Products.json", "w", encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=4, ensure_ascii=False)
        
        print(f"\n✓ Data written to GCP_Products.json")
        
        if len(scraped_data) < 11:
            print(f"\n⚠️  WARNING: Only {len(scraped_data)}/11 categories")
            exit(1)
        else:
            print(f"\n✓ ALL 11 CATEGORIES COMPLETE!")
        
        print()
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
