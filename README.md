# Shako Cricket Records

A small, fast storefront for the two self-published Test-cricket reference books
by **Ramnarine "Shako" Sambhudat** — both forewarded by West Indies great
**Lance Gibbs**. The site is a single, self-contained page anchored by an
animated "shot-tracker" hero (a bat strikes the ball and a broadcast-style
trajectory arcs toward the boundary).

## What's here

| Path | Purpose |
|---|---|
| `index.html` | The entire website — one file (HTML + CSS + a little JS), no build step |
| `assets/` | Web-optimized cover images (WebP + JPEG), generated from the source photos |
| `robots.txt`, `sitemap.xml` | Basic SEO; update the domain before going live |
| `hero_prototype.html` | The original standalone hero animation (kept for reference) |
| `book_metadata.json`, `book_catalog_sheet.md` | Source product data (titles, ISBNs, prices, descriptions, JSON-LD) |
| `website_action_plan.md` | The longer-term CTO plan (Next.js + Stripe) this page is the quick first cut of |
| `0*_*.png` / `0*_*.jpg` | Original high-res cover/studio photos (source for `assets/`) |

## Preview locally

It's a static page, so just open it:

```bash
# either open the file directly…
open index.html            # macOS  (xdg-open on Linux)

# …or serve it (recommended, so relative asset paths + fonts behave)
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploy

Drop the repo onto any static host — **GitHub Pages, Netlify, Vercel, or
Cloudflare Pages** all work with zero configuration. No server or build is
required.

The site's canonical domain is **`https://www.sambhudat.org/`** (used in the
`index.html` canonical/Open Graph/JSON-LD tags, `robots.txt`, and `sitemap.xml`).
The domain is registered at **Namecheap**; no `CNAME` file is needed in the repo
because Vercel/Cloudflare manage the domain from their dashboard.

### Custom domain — Vercel

1. Import this GitHub repo as a Vercel project (Framework preset: **Other**, no
   build command — it's a static site).
2. Project → **Settings → Domains**: add both `www.sambhudat.org` and
   `sambhudat.org`, and set `www` as primary (Vercel will 308-redirect the apex
   to `www`, matching the Namecheap redirect).
3. At **Namecheap → Advanced DNS** (delete the apex URL-redirect record first, it
   conflicts):
   - **CNAME** — Host `www` → Value `cname.vercel-dns.com.`
   - **A** — Host `@` → Value `76.76.21.21`
4. Vercel issues the HTTPS certificate automatically once DNS resolves.

### Custom domain — Cloudflare Pages (alternative)

1. Create a Pages project from this repo (no build command; output dir = repo
   root).
2. Pages project → **Custom domains** → add `www.sambhudat.org`.
3. Easiest path: move the domain's nameservers from Namecheap to Cloudflare
   (Cloudflare dashboard → Add site → it lists the records and gives you the two
   nameservers to paste into **Namecheap → Domain → Nameservers → Custom DNS**).
   Cloudflare then manages DNS and flattens the apex automatically. If you keep
   DNS at Namecheap instead, add a **CNAME** `www` → `<project>.pages.dev`.

DNS changes can take anywhere from a few minutes to a few hours to propagate.

## Payments (Stripe)

Checkout uses **Stripe Payment Links** — hosted by Stripe, so no card data and
no API keys ever touch this site. Turning it on is two steps:

1. In the [Stripe dashboard → Payment Links](https://dashboard.stripe.com/payment-links),
   create one link per book:
   - **WI in Test Matches** — $29.95
   - **Test Cricket Records** — $33.90

   For each link, turn on **shipping address collection**, optionally enable
   **Stripe Tax**, add a shipping rate, and (optional) set the after-payment
   behaviour to **redirect** to `https://YOUR-DOMAIN/?checkout=success` — the
   page shows a thank-you toast when it sees that parameter.

2. Paste the two URLs into the `STRIPE_LINKS` config near the bottom of
   `index.html`:

   ```js
   var STRIPE_LINKS = {
     wi:  "https://buy.stripe.com/xxxxxxxx",   // WI in Test Matches
     tcr: "https://buy.stripe.com/yyyyyyyy"    // Test Cricket Records
   };
   ```

That's it — the "Buy now" buttons immediately switch from the marketplace
fallback to hosted Stripe checkout. (Prefer a custom `/api/checkout` serverless
function with the Stripe SDK instead? That's the alternative in
`website_action_plan.md`; Payment Links are the lower-maintenance choice for two
SKUs.)

## Sections

- **Hero** — animated, respects `prefers-reduced-motion`, dims on mobile.
- **The Books** — both titles with cover galleries (click the thumbnail to flip
  to the back cover; click the cover itself to open a details modal), specs,
  descriptions, prices and buy buttons.
- **Inside the Book** — one section per title (`#inside-wi`, `#inside-tcr`) with
  the Lance Gibbs foreword, the cover/story legend and the full table of
  contents. The cover-click modal reuses this same markup, so each book keeps a
  single source of truth.
- **About Shako** — author bio and an at-a-glance stats panel.
- **Contact** — email, phone and website.

## Decisions made for this quick first cut

- **Buy buttons** use hosted **Stripe Payment Links** (see *Payments* above).
  Until the two links are pasted in, they fall back to the live **Amazon** /
  **eBay** listings so checkout is never dead. "Order direct" `mailto:` remains
  as a secondary option.
- **Contact** is consolidated to one email + one phone (per the catalog sheet's
  recommendation). Confirm/replace these before launch if a dedicated business
  line is preferred.
- **Images** were down-scaled to ~1000px and re-encoded to WebP/JPEG (the
  originals are 7–8 MB each, far too heavy to ship); everything below the hero
  is lazy-loaded.
- **SEO** — per-book `Book` JSON-LD, Open Graph/Twitter tags, a favicon,
  `robots.txt` and `sitemap.xml` are all in place.

## Regenerating the optimized images

If you replace the source photos, re-run the optimizer (requires `Pillow`):

```bash
pip install Pillow
python3 optimize_images.py
```
