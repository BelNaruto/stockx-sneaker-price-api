#!/usr/bin/env node
/**
 * StockX sneaker price tracker (Node.js 18+, no dependencies)
 *
 * 1. Resolves a style code (SKU) to a StockX product once.
 * 2. Polls live StockX market data per size on an interval.
 * 3. Treats 404 as final and backs off on 5xx, as recommended by the API.
 *
 * API:     https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx
 * Support: Telegram @pintoflow (fastest reply)
 *
 * Usage:
 *   export RAPIDAPI_KEY=your_key
 *   node price-tracker.js DD1391-100 [currency] [country] [intervalMinutes]
 *   node price-tracker.js DD1391-100 EUR DE 30
 */

const HOST = 'sneaker-database-stockx.p.rapidapi.com';
const KEY = process.env.RAPIDAPI_KEY;

if (!KEY) {
  console.error('Set RAPIDAPI_KEY first: export RAPIDAPI_KEY=your_key');
  process.exit(1);
}

const [styleId = 'DD1391-100', currency = 'USD', country = 'US', intervalArg = '30'] =
  process.argv.slice(2);
const intervalMs = Math.max(15, Number(intervalArg)) * 60 * 1000; // data is cached 5 min server-side

class ApiError extends Error {
  constructor(status, body, retryAfter) {
    super(body?.message || `HTTP ${status}`);
    this.status = status;
    this.code = body?.code;
    this.retryAfter = retryAfter;
  }
}

async function api(path, params) {
  const url = new URL(`https://${HOST}${path}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const res = await fetch(url, {
    headers: { 'x-rapidapi-host': HOST, 'x-rapidapi-key': KEY },
  });
  const body = await res.json().catch(() => null);
  if (!res.ok || body?.success === false) {
    throw new ApiError(res.status, body, Number(res.headers.get('retry-after')) || null);
  }
  return body?.data ?? body;
}

// Find the per-size list whatever the wrapper key is called.
function findSizes(data) {
  if (Array.isArray(data)) return data;
  for (const key of ['sizes', 'variants', 'market', 'data']) {
    if (Array.isArray(data?.[key])) return data[key];
  }
  return [];
}

const pick = (o, ...keys) => keys.map((k) => o?.[k]).find((v) => v !== undefined && v !== null);
const fmt = (v) => (v === undefined || v === null || v === '' ? '-' : typeof v === 'object' ? (v.amount ?? JSON.stringify(v)) : v);

async function main() {
  console.log(`Resolving ${styleId} on StockX…`);
  let product;
  try {
    product = await api('/stockx/product-by-style', { styleId });
  } catch (e) {
    if (e.status === 404) {
      console.log(`"${styleId}" is not on StockX. Save it as "not found" and try again tomorrow.`);
      return;
    }
    throw e;
  }

  console.log(`\n${product.title}`);
  console.log(`  Style:   ${product.styleId}   Colorway: ${product.colorway}`);
  console.log(`  Retail:  ${fmt(product.retailPrice)}   Released: ${fmt(product.releaseDate)}`);
  console.log(`  URL:     ${product.url}\n`);

  let backoffMin = 1;
  const tick = async () => {
    try {
      const market = await api('/stockx/market-data', { urlKey: product.urlKey, currency, country });
      const rows = findSizes(market).map((s) => ({
        size: fmt(pick(s, 'size', 'sizeUS', 'us', 'name')),
        lowestAsk: fmt(pick(s, 'lowestAsk', 'lowest_ask', 'ask')),
        highestBid: fmt(pick(s, 'highestBid', 'highest_bid', 'bid')),
        lastSale: fmt(pick(s, 'lastSale', 'last_sale')),
        sales72h: fmt(pick(s, 'salesLast72Hours', 'sales72h', 'salesLast72h')),
      }));
      console.log(`[${new Date().toLocaleTimeString()}] ${product.title} (${currency}/${country})`);
      if (rows.length) console.table(rows);
      else console.log(JSON.stringify(market, null, 2).slice(0, 2000));
      backoffMin = 1;
      setTimeout(tick, intervalMs);
    } catch (e) {
      if (e.status >= 500 || e.status === 429) {
        const wait = e.retryAfter ? e.retryAfter * 1000 : backoffMin * 60 * 1000;
        console.warn(`${e.status} ${e.code || ''}: retrying in ${Math.round(wait / 60000)} min`);
        backoffMin = Math.min(backoffMin * 5, 60); // 1 → 5 → 25 → 60 min
        setTimeout(tick, wait);
      } else {
        console.error(`Stopping: ${e.status} ${e.message}`);
      }
    }
  };

  await tick();
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
