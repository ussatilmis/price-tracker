"""
Siteyi gezer ve ürünleri çıkarır.

İki "fetch motoru" vardır, config.TARGET['engine'] ile seçilir:
  - requests   : statik siteler için hızlı, hafif (tarayıcı açmaz)
  - playwright : JavaScript ile yüklenen siteler için (gerçek tarayıcı açar)
Motor ne olursa olsun, gerisi (parse_listing, store, report) AYNI kalır.
"""

import time
from contextlib import contextmanager
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


def _fetch_requests(url):
    """Statik sayfayı doğrudan indirir (tarayıcı yok)."""
    resp = requests.get(url, headers=HEADERS, timeout=config.TARGET["timeout"])
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp.text


@contextmanager
def open_fetcher():
    """
    Doğru motoru açar ve 'sayfa getiren bir fonksiyon' verir.
    - requests   : doğrudan indirir.
    - playwright : TEK tarayıcı açar, tüm sayfalarda tekrar kullanır, iş bitince kapatır.
    """
    engine = config.TARGET.get("engine", "requests")

    if engine == "requests":
        yield _fetch_requests

    elif engine == "playwright":
        from playwright.sync_api import sync_playwright

        wait_for = config.TARGET.get("wait_for")
        timeout_ms = config.TARGET["timeout"] * 1000

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=HEADERS["User-Agent"])

            def _fetch_playwright(url):
                page.goto(url, timeout=timeout_ms)
                if wait_for:
                    page.wait_for_selector(wait_for, timeout=timeout_ms)
                return page.content()

            try:
                yield _fetch_playwright
            finally:
                browser.close()

    else:
        raise ValueError(f"Bilinmeyen engine: {engine!r} (requests veya playwright olmali)")


def parse_price(text):
    """'£51.77' veya '$1,299.00' -> float."""
    cleaned = "".join(ch for ch in text if ch.isdigit() or ch in ".,")
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_listing(html, page_url):
    """
    Bir listeleme sayfasından ürün listesi çıkarır.
    >>> Gerçek siteye geçerken sadece buradaki CSS seçicilerini değiştir. <
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
                "product_id": href,
                "title": title,
                "price": parse_price(price_el.get_text(strip=True)),
                "in_stock": "in stock" in stock_text,
                "url": href,
            }
        )
    return products


def scrape_all():
    all_products = []
    with open_fetcher() as fetch_page:
        for page in range(1, config.TARGET["max_pages"] + 1):
            url = config.TARGET["catalogue_url"].format(page=page)
            try:
                html = fetch_page(url)
            except requests.HTTPError as exc:
                print(f"      sayfa {page} alinamadi ({exc}); duruluyor.")
                break
            items = parse_listing(html, url)
            if not items:
                break
            all_products.extend(items)
            print(f"      sayfa {page}: {len(items)} urun ({config.TARGET['engine']})")
            time.sleep(config.TARGET["request_delay"])

    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for p in all_products:
        p["scraped_at"] = scraped_at
    return all_products
