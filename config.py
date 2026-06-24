"""
Tüm ayarlar burada. Başka bir siteye geçmek istediğinde:
  1) Buradaki TARGET sözlüğünü güncelle
  2) scraper.py içindeki parse_listing() seçicilerini güncelle
Gerisi (arşivleme, fark tespiti, Excel) olduğu gibi çalışır.
"""

TARGET = {
    "name": "books_toscrape",
    # Demo hedefi: scraping pratiği için kurulmuş, izinli bir site.
    # Gerçek bir e-ticaret sitesine geçince sadece bu URL'leri + parser'ı değiştir.
    "catalogue_url": "http://books.toscrape.com/catalogue/page-{page}.html",
    "max_pages": 5,        # kaç listeleme sayfası gezilecek
    "request_delay": 1.0,  # saniye — siteye saygı + ban riskini azaltır
    "timeout": 20,
}

DATA_DIR = "data"
HISTORY_CSV = "data/price_history.csv"  # sadece DEĞİŞİM olaylarını tutan zaman serisi
LATEST_CSV = "data/latest.csv"          # her ürünün en güncel hali
REPORT_XLSX = "data/price_report.xlsx"  # paylaşılabilir Excel rapor
