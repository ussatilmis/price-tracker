"""
Calistirmak icin:  python main.py
Akis: siteyi tara -> onceki veriyle karsilastir -> CSV arsivini guncelle -> Excel rapor uret.
Her calistirmada sadece DEGISEN fiyatlar arsive eklenir.
"""

import config
import report
import scraper
import store


def run():
    print(f"Hedef: {config.TARGET['name']}")

    print("1/4  Site taraniyor...")
    products = scraper.scrape_all()
    print(f"      toplam {len(products)} urun cekildi.")
    if not products:
        print("      urun bulunamadi; secicileri (parse_listing) kontrol et.")
        return

    print("2/4  Onceki veriyle karsilastiriliyor...")
    previous = store.load_latest()
    changes = store.diff(previous, products)
    new = sum(1 for c in changes if c["change"] == "NEW")
    moved = sum(1 for c in changes if c["change"] == "PRICE_CHANGE")
    print(f"      {new} yeni urun, {moved} fiyat degisimi.")

    print("3/4  CSV arsivi guncelleniyor...")
    if changes:
        store.append_history(changes)
    store.write_latest(products)

    print("4/4  Excel rapor uretiliyor...")
    path = report.build_report()
    print(f"      rapor hazir: {path}")
    print("Bitti.")


if __name__ == "__main__":
    run()
