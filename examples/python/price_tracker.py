#!/usr/bin/env python3
"""
StockX sneaker price tracker (Python 3.8+, needs `requests`)

1. Resolves a style code (SKU) to a StockX product once.
2. Polls live StockX market data per size on an interval.
3. Treats 404 as final and backs off on 5xx / 429, as recommended by the API.

API:     https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx
Support: Telegram @pintoflow (fastest reply)

Usage:
    pip install requests
    export RAPIDAPI_KEY=your_key
    python3 price_tracker.py DD1391-100 --currency EUR --country DE --every 30
"""
import argparse
import os
import sys
import time
from datetime import datetime

import requests

HOST = "sneaker-database-stockx.p.rapidapi.com"
KEY = os.environ.get("RAPIDAPI_KEY")


class ApiError(Exception):
    def __init__(self, status, body, retry_after=None):
        body = body or {}
        super().__init__(body.get("message") or f"HTTP {status}")
        self.status = status
        self.code = body.get("code")
        self.retry_after = retry_after


def api(path, **params):
    r = requests.get(
        f"https://{HOST}{path}",
        params=params,
        headers={"x-rapidapi-host": HOST, "x-rapidapi-key": KEY},
        timeout=30,
    )
    try:
        body = r.json()
    except ValueError:
        body = None
    if not r.ok or (isinstance(body, dict) and body.get("success") is False):
        ra = r.headers.get("Retry-After")
        raise ApiError(r.status_code, body if isinstance(body, dict) else None, int(ra) if ra and ra.isdigit() else None)
    return body.get("data", body) if isinstance(body, dict) else body


def find_sizes(data):
    if isinstance(data, list):
        return data
    for key in ("sizes", "variants", "market", "data"):
        if isinstance(data, dict) and isinstance(data.get(key), list):
            return data[key]
    return []


def pick(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            v = d[k]
            return v.get("amount", v) if isinstance(v, dict) else v
    return "-"


def main():
    p = argparse.ArgumentParser(description="Track StockX prices for a sneaker SKU")
    p.add_argument("style_id", nargs="?", default="DD1391-100")
    p.add_argument("--currency", default="USD")
    p.add_argument("--country", default="US")
    p.add_argument("--every", type=int, default=30, help="minutes between checks (min 15)")
    p.add_argument("--once", action="store_true", help="check once and exit")
    a = p.parse_args()

    if not KEY:
        sys.exit("Set RAPIDAPI_KEY first: export RAPIDAPI_KEY=your_key")

    try:
        product = api("/stockx/product-by-style", styleId=a.style_id)
    except ApiError as e:
        if e.status == 404:
            print(f'"{a.style_id}" is not on StockX. Save it as "not found" and try again tomorrow.')
            return
        raise

    print(f"\n{product['title']}")
    print(f"  Style:  {product.get('styleId')}   Colorway: {product.get('colorway')}")
    print(f"  Retail: {product.get('retailPrice')}   Released: {product.get('releaseDate')}")
    print(f"  URL:    {product.get('url')}\n")

    backoff_min = 1
    while True:
        try:
            market = api("/stockx/market-data", urlKey=product["urlKey"], currency=a.currency, country=a.country)
            sizes = find_sizes(market)
            print(f"[{datetime.now():%H:%M:%S}] {product['title']} ({a.currency}/{a.country})")
            print(f"{'Size':<8}{'Lowest ask':>12}{'Highest bid':>13}{'Last sale':>11}")
            for s in sizes:
                print(
                    f"{str(pick(s, 'size', 'sizeUS', 'us', 'name')):<8}"
                    f"{str(pick(s, 'lowestAsk', 'lowest_ask', 'ask')):>12}"
                    f"{str(pick(s, 'highestBid', 'highest_bid', 'bid')):>13}"
                    f"{str(pick(s, 'lastSale', 'last_sale')):>11}"
                )
            backoff_min = 1
            if a.once:
                return
            time.sleep(max(15, a.every) * 60)  # server cache is 5 min; no point polling faster
        except ApiError as e:
            if e.status >= 500 or e.status == 429:
                wait = e.retry_after or backoff_min * 60
                print(f"{e.status} {e.code or ''}: retrying in {wait // 60} min", file=sys.stderr)
                backoff_min = min(backoff_min * 5, 60)  # 1 -> 5 -> 25 -> 60 min
                time.sleep(wait)
            else:
                sys.exit(f"Stopping: {e.status} {e}")


if __name__ == "__main__":
    main()
