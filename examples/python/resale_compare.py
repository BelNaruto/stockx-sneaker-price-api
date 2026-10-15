#!/usr/bin/env python3
"""
Compare sneaker resale prices: StockX vs GOAT vs Flight Club vs Stadium Goods

Calls /productprice for one or more style codes (SKUs) and writes the result
to a CSV you can open in Excel / Google Sheets.

API:     https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx
Support: Telegram @pintoflow (fastest reply)

Usage:
    pip install requests
    export RAPIDAPI_KEY=your_key
    python3 resale_compare.py HP8739 DD1391-100 --csv prices.csv
"""
import argparse
import csv
import json
import os
import sys
import time

import requests

HOST = "sneaker-database-stockx.p.rapidapi.com"
KEY = os.environ.get("RAPIDAPI_KEY")
SITES = ("stockX", "goat", "flightClub", "stadiumGoods")


def get_prices(style_id):
    r = requests.get(
        f"https://{HOST}/productprice",
        params={"styleId": style_id},
        headers={"x-rapidapi-host": HOST, "x-rapidapi-key": KEY},
        timeout=60,  # first call queries 4 marketplaces: 3-8 s
    )
    body = r.json() if r.content else {}
    if r.status_code == 404:
        return None
    if not r.ok or (isinstance(body, dict) and body.get("success") is False):
        raise RuntimeError(f"{r.status_code} {body.get('code', '')}: {body.get('message', 'request failed')}")
    print(f"  {style_id}: X-Cache {r.headers.get('X-Cache', '-')}")
    return body.get("data", body) if isinstance(body, dict) else body


def flatten(style_id, data):
    """Turn the response into rows of (styleId, field, value).

    Writes every price-like field it finds, so the CSV stays useful even if
    you only care about a few marketplaces.
    """
    rows = []

    def walk(prefix, v):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(f"{prefix}.{k}" if prefix else k, x)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(f"{prefix}[{i}]", x)
        else:
            rows.append({"styleId": style_id, "field": prefix, "value": v})

    walk("", data)
    return rows


def main():
    p = argparse.ArgumentParser(description="Compare resale prices across StockX, GOAT, Flight Club, Stadium Goods")
    p.add_argument("style_ids", nargs="*", default=["HP8739"])
    p.add_argument("--csv", default="resale_prices.csv")
    a = p.parse_args()
    if not KEY:
        sys.exit("Set RAPIDAPI_KEY first: export RAPIDAPI_KEY=your_key")

    all_rows = []
    for sid in a.style_ids:
        data = get_prices(sid)
        if data is None:
            print(f"  {sid}: not found (404). Don't retry today.")
            continue

        # Lowest price per marketplace, if the response includes it
        lowest = data.get("lowestResellPrice") if isinstance(data, dict) else None
        if lowest:
            print(f"\n{data.get('shoeName') or data.get('title') or sid}")
            for site in SITES:
                if site in lowest:
                    print(f"  {site:<14} lowest: {lowest[site]}")
        else:
            print(json.dumps(data, indent=2)[:1500])

        all_rows += flatten(sid, data)
        time.sleep(1)  # be gentle: a few requests at a time

    with open(a.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["styleId", "field", "value"])
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nSaved {len(all_rows)} rows to {a.csv}")


if __name__ == "__main__":
    main()
