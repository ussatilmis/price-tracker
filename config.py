"""
Tüm ayarlar burada. Başka bir siteye geçmek istediğinde:
  1) Buradaki TARGET sözlüğünü güncelle
  2) scraper.py içindeki parse_listing() seçicilerini güncelle
Gerisi (arşivleme, fark tespiti, Excel) olduğu gibi çalışır.
"""

TARGET = {
    "name": "books_toscrape",
    "catalogue_url": "http://books.toscrape.com/catalogue/page-{page}.html",
    "max_pages": 5,
    "request_delay": 1.0,
    "timeout": 20,

    # --- Fetch motoru ---
    # "requests"  : statik siteler için hızlı, hafif (tarayıcı açmaz)
    # "playwright": JavaScript ile içerik yükleyen siteler için (gerçek tarayıcı)
    "engine": "requests",
    # playwright modunda: bu element çizilene kadar BEKLE (JS'in içeriği oluşturmasını bekle)
    "wait_for": "article.product_pod",
}

DATA_DIR = "data"
HISTORY_CSV = "data/price_history.csv"
LATEST_CSV = "data/latest.csv"
REPORT_XLSX = "data/price_report.xlsx"
