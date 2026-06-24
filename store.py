"""
CSV tabanli arsivleme + fark tespiti.
  latest.csv        -> her urunun en guncel hali (durum)
  price_history.csv -> sadece YENI / FIYAT DEGISIMI olaylari (zaman serisi)
CSV-first: hizli, versiyon kontrolune uygun, Excel'e gore performansli.
"""

import csv
import os

import config

HISTORY_FIELDS = [
    "scraped_at", "product_id", "title", "price",
    "in_stock", "change", "old_price", "delta", "url",
]
LATEST_FIELDS = ["product_id", "title", "price", "in_stock", "url", "scraped_at"]


def _ensure_dir():
    os.makedirs(config.DATA_DIR, exist_ok=True)


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_latest():
    """Onceki calismadan en son bilinen fiyatlari {product_id: row} olarak doner."""
    if not os.path.exists(config.LATEST_CSV):
        return {}
    out = {}
    with open(config.LATEST_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["price"] = _to_float(row.get("price"))
            out[row["product_id"]] = row
    return out


def diff(previous, current):
    """
    Her urune 'change' etiketi ekler (NEW / PRICE_CHANGE / SAME) ve
    sadece degisim olaylarinin listesini doner (arsive yazilacak olanlar).
    """
    changes = []
    for p in current:
        old = previous.get(p["product_id"])
        if old is None:
            p["change"], p["old_price"], p["delta"] = "NEW", None, None
        elif old["price"] is not None and p["price"] is not None and old["price"] != p["price"]:
            p["change"] = "PRICE_CHANGE"
            p["old_price"] = old["price"]
            p["delta"] = round(p["price"] - old["price"], 2)
        else:
            p["change"], p["old_price"], p["delta"] = "SAME", old["price"], 0.0
        if p["change"] in ("NEW", "PRICE_CHANGE"):
            changes.append(p)
    return changes


def append_history(events):
    _ensure_dir()
    exists = os.path.exists(config.HISTORY_CSV)
    with open(config.HISTORY_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HISTORY_FIELDS, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for e in events:
            w.writerow(e)


def write_latest(products):
    _ensure_dir()
    with open(config.LATEST_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LATEST_FIELDS, extrasaction="ignore")
        w.writeheader()
        for p in products:
            w.writerow(p)
