#!/usr/bin/env bash
# Sneaker Database – StockX API: cURL examples
# Get your key: https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx
# Support (fastest reply): Telegram @pintoflow
#
# Usage: RAPIDAPI_KEY=your_key bash examples.sh

set -euo pipefail
: "${RAPIDAPI_KEY:?Set RAPIDAPI_KEY first: export RAPIDAPI_KEY=your_key}"

HOST="sneaker-database-stockx.p.rapidapi.com"
BASE="https://${HOST}"

call() {
  echo -e "\n=== GET $1 ==="
  curl -sS --get "${BASE}$1" "${@:2}" \
    -H "x-rapidapi-host: ${HOST}" \
    -H "x-rapidapi-key: ${RAPIDAPI_KEY}" | head -c 1500
  echo
}

# 1. StockX product by style code (SKU)
call /stockx/product-by-style --data-urlencode "styleId=DD1391-100"

# 2. Live StockX market data per size, in EUR for Germany
call /stockx/market-data --data-urlencode "urlKey=nike-dunk-low-retro-white-black-2021" \
  --data-urlencode "currency=EUR" --data-urlencode "country=DE"

# 3. Resale prices per size: StockX vs GOAT vs Flight Club vs Stadium Goods
call /productprice --data-urlencode "styleId=HP8739"

# 4. Trending sneakers right now
call /stockx/browse --data-urlencode "category=sneakers" --data-urlencode "sort=most-active" \
  --data-urlencode "limit=10"

# 5. Newest releases filtered by keyword
call /stockx/browse --data-urlencode "sort=release_date" --data-urlencode "query=jordan 4"

# 6. Other colorways of a model
call /stockx/colorways --data-urlencode "urlKey=nike-dunk-low-retro-white-black-2021"

# 7. Related products
call /stockx-related --data-urlencode "urlKey=air-jordan-4-retro-rare-air-tour-yellow"

# 8. Full product details
call /stockx-description --data-urlencode "urlKey=air-jordan-1-high-zoom-air-cmft-2-honeydew"

# 9. Keyword search (sneakers / apparel)
call /stockx/sneakers --data-urlencode "query=yeezy 350" --data-urlencode "limit=5"
call /apparel/search --data-urlencode "query=supreme box logo" --data-urlencode "limit=5"

# 10. KicksCrew search v2, cheapest first
call /kc/search/v2 --data-urlencode "query=samba" --data-urlencode "sortBy=price_asc"

# 11. Stadium Goods search
call /sg/search --data-urlencode "query=new balance 550"
