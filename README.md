# StockX Sneaker Price API – Sneaker Database (StockX, GOAT, Flight Club, Stadium Goods, KicksCrew)

[![RapidAPI](https://img.shields.io/badge/RapidAPI-Sneaker%20Database%20StockX-0055DA?logo=rapidapi&logoColor=white)](https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx)
[![Telegram support](https://img.shields.io/badge/Support-%40pintoflow-26A5E4?logo=telegram&logoColor=white)](https://t.me/pintoflow)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

> **For faster support reply, contact us on Telegram: [@pintoflow](https://t.me/pintoflow)**

**Get the API (free plan available): https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx**

A REST API for **sneaker prices, StockX market data and product details**. Look up any sneaker by **style code / SKU** (e.g. `DD1391-100`), get **live asks, bids and last sales per size**, compare **resale prices across StockX, GOAT, Flight Club and Stadium Goods**, browse **trending sneakers and new releases**, and search **KicksCrew** and **Stadium Goods** catalogs.

Use it to build sneaker price trackers, resell calculators, Discord/Telegram sneaker bots, inventory and repricing tools, release calendars, or price-comparison sites.

This repository contains the API documentation plus ready-to-run examples in **cURL**, **Node.js** and **Python**.

---

## Features

- 🔎 **StockX product by style code (SKU)**: name, brand, colorway, retail price, release date, images, 360° images
- 📈 **Live StockX market data per size**: lowest ask, highest bid, last sale, sales in the last 72 h, in 12 currencies
- 💰 **Resale price comparison per size**: StockX vs GOAT vs Flight Club vs Stadium Goods
- 🔥 **Browse StockX**: most active, new releases, price premium, best sellers, by category (sneakers, apparel, collectibles, trading cards, watches…)
- 🎨 **Colorways and related products**
- 👟 **KicksCrew and Stadium Goods** search, product details and collections
- ⚡ Server-side caching, consistent JSON errors, and clear retry rules

---

## Quick start

1. Subscribe on RapidAPI: **https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx**
2. Copy your `x-rapidapi-key`.
3. Call any endpoint:

```bash
curl --request GET \
  --url 'https://sneaker-database-stockx.p.rapidapi.com/stockx/product-by-style?styleId=DD1391-100' \
  --header 'x-rapidapi-host: sneaker-database-stockx.p.rapidapi.com' \
  --header 'x-rapidapi-key: YOUR_RAPIDAPI_KEY'
```

- **Base URL:** `https://sneaker-database-stockx.p.rapidapi.com`
- **Method:** every endpoint is `GET`
- **Auth:** send your RapidAPI headers on every call

### Which endpoint do I need?

| I have… | I want… | Use |
|---|---|---|
| A style code (SKU), e.g. `DD1391-100` | The StockX product (name, image, retail, release date) | `/stockx/product-by-style` |
| A style code | Resale prices per size on StockX, GOAT, Flight Club, Stadium Goods | `/productprice` |
| A StockX slug (`urlKey`) or product URL | Live asks/bids/last sale per size, in any currency | `/stockx/market-data` |
| A `urlKey` | Full product details (description, traits, images, sizes) | `/stockx-description` |
| A `urlKey` | Similar products | `/stockx-related` |
| A `urlKey` | Other colorways of the same model | `/stockx/colorways` |
| Nothing yet | Trending, new releases, best sellers by category | `/stockx/browse` |
| A name or keyword | A search | `/stockx/sneakers`, `/apparel/search`, `/getproducts` |

**What's a `urlKey`?** It's the last part of a StockX product URL. For `https://stockx.com/nike-dunk-low-retro-white-black-2021`, the `urlKey` is `nike-dunk-low-retro-white-black-2021`. Every endpoint that takes a `urlKey` also accepts the full StockX URL. Every search and lookup result includes the `urlKey`.

---

## Examples in this repo

| File | What it does |
|---|---|
| [`examples/curl/examples.sh`](examples/curl/examples.sh) | One cURL call for every main endpoint |
| [`examples/node/price-tracker.js`](examples/node/price-tracker.js) | Resolve a SKU once, then poll live StockX prices per size (Node.js 18+, no dependencies) |
| [`examples/node/trending.mjs`](examples/node/trending.mjs) | Print trending sneakers / new releases from StockX browse |
| [`examples/python/price_tracker.py`](examples/python/price_tracker.py) | Same price tracker in Python, with 404 handling and backoff |
| [`examples/python/resale_compare.py`](examples/python/resale_compare.py) | Compare resale prices for a SKU across StockX, GOAT, Flight Club and Stadium Goods and export to CSV |

Set your key once and run any example:

```bash
export RAPIDAPI_KEY=your_key_here

node examples/node/price-tracker.js DD1391-100
python3 examples/python/resale_compare.py HP8739
```

---

## StockX endpoints

### `GET /stockx/product-by-style`
Finds the StockX product for a style code. Dashes, spaces and case don't matter, so `DD1391-100`, `dd1391 100` and `DD1391100` all match. It covers every category, including boots, slides and mules.

| Param | Required | Example |
|---|---|---|
| `styleId` | yes | `DD1391-100` |

Returns `urlKey`, `title`, `brand`, `model`, `styleId`, `colorway`, `retailPrice`, `releaseDate`, `category`, `gender`, `description`, `image`, `images360`, `lowestAsk`, `highestBid`, `lastSale`, `url`.

### `GET /productprice`
Resale prices **per size** from StockX, GOAT, Flight Club and Stadium Goods for one style code, plus the lowest price on each site.

| Param | Required | Example |
|---|---|---|
| `styleId` | yes | `HP8739` |

This is the heaviest endpoint because it queries 4 marketplaces, so expect 3–8 s on the first call. Repeat calls within 5 minutes are served from cache. If you only need the product itself, use `/stockx/product-by-style`. If you only need StockX prices, use `/stockx/market-data`.

### `GET /stockx/market-data`
Live StockX market data for every size: lowest ask, highest bid, number of asks and bids, last sale, sales in the last 72 h, and delivery options (standard / express). Each size includes its US/UK/EU/CM/KR equivalents and its UPC/EAN barcode when StockX has one.

| Param | Required | Default | Example |
|---|---|---|---|
| `urlKey` | yes | | `nike-dunk-low-retro-white-black-2021` |
| `currency` | no | `USD` | `USD`, `EUR`, `GBP`, `CAD`, `AUD`, `JPY`, `CHF`, `KRW`, `SGD`, `HKD`, `MXN`, `NZD` |
| `country` | no | `US` | 2-letter ISO code: `US`, `GB`, `DE`, `FR`, `JP`… |

### `GET /stockx-description`
Full product page data: title, description, traits (style, colorway, retail price, release date), breadcrumbs, images (including 360°), size conversions and per-size market data.

| Param | Required | Example |
|---|---|---|
| `urlKey` | yes | `air-jordan-1-high-zoom-air-cmft-2-honeydew` |

### `GET /stockx-related`
Up to 15 products StockX shows as related, each with image, lowest ask, highest bid and last sale.

| Param | Required | Example |
|---|---|---|
| `urlKey` | yes | `air-jordan-4-retro-rare-air-tour-yellow` |

### `GET /stockx/colorways`
Other colorways of the same model, each with image and lowest ask.

| Param | Required | Default |
|---|---|---|
| `urlKey` | yes | |
| `currency` | no | `USD` |
| `country` | no | `US` |

### `GET /stockx/browse`
Ranked product lists, such as the most-active sneakers right now, the newest releases or the highest price premiums.

| Param | Required | Default | Values |
|---|---|---|---|
| `category` | no | `sneakers` | `sneakers`, `shoes`, `apparel`, `accessories`, `collectibles`, `trading-cards`, `electronics`, `watches` |
| `sort` | no | `most-active` | `featured`, `most-active`, `recent_asks`, `recent_bids`, `lowest_ask`, `highest_bid`, `release_date`, `last_sale`, `price_premium`, `deadstock_sold` |
| `query` | no | | optional keyword filter, e.g. `jordan 4` |
| `page` | no | `1` | 1–25 |
| `limit` | no | `20` | 1–40 |
| `currency` | no | `USD` | see `/stockx/market-data` |
| `country` | no | `US` | 2-letter ISO code |

### `GET /stockx/sneakers` and `GET /apparel/search`
Keyword search within sneakers or apparel.

| Param | Required | Default |
|---|---|---|
| `query` | yes | |
| `page` | no | `1` |
| `limit` | no | `40` (max 40) |
| `currency` | no | `USD` |
| `country` | no | `US` |

### `GET /getproducts` and `GET /stockxonly`
Keyword search that returns products in the classic sneaker format (style ID, retail price, release date, images, resell links).

| Endpoint | Params |
|---|---|
| `/getproducts` | `keywords` (required), `limit` (default 10), `page` (default 1) |
| `/stockxonly` | `search` (required), `perpage` (default 20), `page` (default 1) |

### `GET /mostpopular`
The current most popular products. Param: `limit` (default 10).

### `GET /searchByUrl`
The product for a StockX product URL. Param: `url`, e.g. `https://stockx.com/adidas-yeezy-desert-boot-salt`.

---

## KicksCrew endpoints

| Endpoint | Params |
|---|---|
| `GET /kc-search` | `query` (required), `hitsPerPage` (default 16), `page` (default 0) |
| `GET /kc/search/v2` | `query` (required), `hitsPerPage` (16), `page` (1), `sortBy` (`count`, `price_asc`, `price_desc`, `alpha`, `newest`), `currency` (`USD`), `region` (`US`) |
| `GET /kc-description` | `spu`: the model number / style code, e.g. `ID4126` |

## Stadium Goods endpoints

| Endpoint | Params |
|---|---|
| `GET /sg/search` | `query` (required), `page` (default 1) |
| `GET /sg/description-byurl` | `productUrl`, a Stadium Goods product URL |
| `GET /sg/collections` | `page` (default 1) |
| `GET /sg/collections/product` | `collectionsHandle`, e.g. `new-balance`; `page` (default 1) |

---

## Responses and errors

Errors always have the same shape:

```json
{ "success": false, "message": "No StockX product found for styleId 'XX0000-000'. …", "code": "NOT_FOUND", "data": null }
```

| HTTP | `code` | Meaning | What you should do |
|---|---|---|---|
| 200 | | OK | |
| 400 | `BAD_REQUEST` | A parameter is missing or invalid | Fix the request. Retrying won't help. |
| 404 | `NOT_FOUND` | The product doesn't exist on StockX | **Don't retry.** Store the miss on your side and check again in a day or so. |
| 429 | `TOO_MANY_MISSES` | You asked for the same missing product too many times | Stop requesting that product until `Retry-After` (seconds) has passed. Other products aren't affected. |
| 429 | (RapidAPI) | You hit your plan's rate limit | Slow down or upgrade your plan |
| 502 | `UPSTREAM_CHANGED` / `UPSTREAM_ERROR` | The data source changed or failed | Retry once after a few minutes. We're notified and fix these. |
| 503 | `UPSTREAM_BLOCKED` | The data source is temporarily refusing requests | Retry after 2–5 minutes, with backoff |
| 504 | `UPSTREAM_TIMEOUT` | The data source didn't answer in time | Retry after a few minutes, with backoff |

### Caching

Responses are cached to keep the API fast and stable. Calling more often than this won't get you fresher data:

| Data | Fresh for |
|---|---|
| `/productprice`, `/stockx/market-data` | 5 minutes |
| `/stockx/browse`, `/stockx/sneakers`, `/apparel/search` | 10 minutes |
| `/stockx-related`, `/stockx-description` | 30 minutes |
| `/stockx/colorways` | 1 hour |
| `/stockx/product-by-style` | 12 hours |
| "Not found" (404) answers | 30 minutes |
| Upstream errors (5xx) | 5 minutes |

`/productprice` sends an `X-Cache: HIT` or `MISS` header.

---

## Best practices

**Do**

- **Cache on your side.** Prices don't move faster than every few minutes. Keep product data (name, images, style code, retail price, release date) for days.
- **Resolve style codes once.** Call `/stockx/product-by-style` one time, save the `urlKey`, then use `/stockx/market-data` for price updates. It's faster and lighter than `/productprice`.
- **Treat 404 as a final answer** for that product, and keep a "not found" list.
- **Use exponential backoff** (e.g. 1 min → 5 min → 15 min) on 502/503/504, and honour `Retry-After`.
- **Pick the right currency and country** in `/stockx/market-data` instead of converting prices yourself. StockX fees and availability differ per market.
- **URL-encode parameters** (`jordan%204`, `dd1391%20100`).

**Don't**

- **Retry a 404 in a loop.** After 5 misses for the same product in 10 minutes, you'll get `429 TOO_MANY_MISSES` for that product, and every call still counts against your quota.
- **Retry 400 errors.** The request itself is wrong.
- **Poll the same product every few seconds.** You'll get the same cached answer.
- **Fire hundreds of parallel requests.** Keep concurrency to a few at a time.
- **Build `urlKey`s by hand from product names.** Take them from a search or lookup result.
- **Pass non-StockX URLs** to `urlKey` or `/searchByUrl`.

---

## Example flow: sneaker price tracker

1. `GET /stockx/product-by-style?styleId=DD1391-100` and save `urlKey`, `title`, `image`.
2. Every 15–60 minutes: `GET /stockx/market-data?urlKey=nike-dunk-low-retro-white-black-2021&currency=USD&country=US`.
3. Optional: once a day, `GET /productprice?styleId=DD1391-100` to compare with GOAT, Flight Club and Stadium Goods.
4. If step 1 returns 404, mark the code "not found" and check it again tomorrow, not in a loop.

A full working version is in [`examples/node/price-tracker.js`](examples/node/price-tracker.js) and [`examples/python/price_tracker.py`](examples/python/price_tracker.py).

---

## FAQ

**Is there a free StockX API?**
StockX has no public API. This API gives you StockX product and price data through RapidAPI, with a free plan to try it.

**How do I get StockX prices by SKU / style code?**
Call `/stockx/product-by-style?styleId=YOUR_SKU` for the product, then `/stockx/market-data?urlKey=...` for live per-size prices.

**Can I compare StockX vs GOAT prices?**
Yes. `/productprice?styleId=YOUR_SKU` returns per-size prices from StockX, GOAT, Flight Club and Stadium Goods.

**Which currencies are supported?**
USD, EUR, GBP, CAD, AUD, JPY, CHF, KRW, SGD, HKD, MXN and NZD.

---

## Support

> **For faster support reply, contact us on Telegram: [@pintoflow](https://t.me/pintoflow)**

- RapidAPI listing: https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx
- Or open an issue in the **Discussions** tab of the API on RapidAPI.

---

*This project is not affiliated with, endorsed by or sponsored by StockX, GOAT, Flight Club, Stadium Goods or KicksCrew. All trademarks belong to their owners.*

**Keywords:** stockx api, sneaker api, sneaker price api, stockx price api, sneaker database, goat api, flight club api, stadium goods api, kickscrew api, sneaker resale prices, sku lookup, style code lookup, sneaker bot, sneaker price tracker
