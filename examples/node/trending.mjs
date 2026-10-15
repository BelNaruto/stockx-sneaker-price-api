#!/usr/bin/env node
/**
 * Trending sneakers, new releases and best sellers from StockX (Node.js 18+)
 *
 * API:     https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/sneaker-database-stockx
 * Support: Telegram @pintoflow (fastest reply)
 *
 * Usage:
 *   export RAPIDAPI_KEY=your_key
 *   node trending.mjs                       # most active sneakers
 *   node trending.mjs release_date          # newest releases
 *   node trending.mjs price_premium apparel # apparel with the highest resale premium
 *   node trending.mjs most-active sneakers "jordan 4"
 */

const HOST = 'sneaker-database-stockx.p.rapidapi.com';
const KEY = process.env.RAPIDAPI_KEY;
if (!KEY) {
  console.error('Set RAPIDAPI_KEY first: export RAPIDAPI_KEY=your_key');
  process.exit(1);
}

const [sort = 'most-active', category = 'sneakers', query = ''] = process.argv.slice(2);

const params = new URLSearchParams({ sort, category, limit: '20', currency: 'USD', country: 'US' });
if (query) params.set('query', query);

const res = await fetch(`https://${HOST}/stockx/browse?${params}`, {
  headers: { 'x-rapidapi-host': HOST, 'x-rapidapi-key': KEY },
});
const body = await res.json();
if (!res.ok || body?.success === false) {
  console.error(`${res.status} ${body?.code || ''}: ${body?.message || 'request failed'}`);
  process.exit(1);
}

const data = body?.data ?? body;
const items = Array.isArray(data) ? data : data?.products || data?.results || data?.items || [];
const fmt = (v) => (v == null ? '-' : typeof v === 'object' ? (v.amount ?? JSON.stringify(v)) : v);

console.log(`StockX ${category} sorted by ${sort}${query ? ` matching "${query}"` : ''}\n`);
console.table(
  items.map((p, i) => ({
    '#': i + 1,
    title: (p.title || p.name || '').slice(0, 50),
    urlKey: p.urlKey,
    lowestAsk: fmt(p.lowestAsk),
    lastSale: fmt(p.lastSale),
  })),
);
console.log('\nTip: pass any urlKey to /stockx/market-data for live per-size prices.');
