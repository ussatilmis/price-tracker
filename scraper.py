"""
Siteyi gezer ve ürünleri çıkarır.
Bir başka siteye geçerken DEĞİŞTİRECEĞİN TEK YER: parse_listing().
JS ile yüklenen siteler için requests yerine Playwright'a geçilir (README'ye bak).
"""

import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch(url):
    resp = requests.get(url, headers=HEADERS, timeout=config.TARGET["timeout"])
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp.text


def parse_price(text):
    """'£51.77' veya '$1,299.00' -> float. Para birimi sembolünü atar."""
    cleaned = "".join(ch for ch in text if ch.isdigit() or ch in ".,")
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_listing(html, page_url):
    """
    Bir listeleme sayfasından ürün listesi çıkarır.
    >>> Gerçek siteye geçerken sadece buradaki CSS seçicilerini değiştir. <<<
    Her ürün için kararlı bir 'product_id' şart (burada ürün URL'si kullanıldı).
    """
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for card in soup.select("article.product_pod"):
        title_el = card.select_one("h3 a")
        price_el = card.select_one("p.price_color")
        stock_el = card.select_one("p.availability")
        if not (title_el and price_el):
            continue
        title = title_el.get("title") or title_el.get_text(strip=True)
        href = urljoin(page_url, title_el.get("href", ""))
        stock_text = stock_el.get_text(strip=True).lower() if stock_el else ""
        products.append(
            {
                "product_id": href,  # benzersiz, kararlı anahtar
                "title": title,
                "price": parse_price(price_el.get_text(strip=True)),
                "in_stock": "in stock" in stock_text,
                "url": href,
            }
        )
    return products


def scrape_all():
    all_products = []
    for page in range(1, config.TARGET["max_pages"] + 1):
        url = config.TARGET["catalogue_url"].format(page=page)
        try:
            html = fetch(url)
        except requests.HTTPError as exc:
            print(f"      sayfa {page} alinamadi ({exc}); duruluyor.")
            break
        items = parse_listing(html, url)
        if not items:
            break
        all_products.extend(items)
        print(f"      sayfa {page}: {len(items)} urun")
        time.sleep(config.TARGET["request_delay"])

    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for p in all_products:
        p["scraped_at"] = scraped_at
    return all_products
