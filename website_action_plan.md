# Shako Cricket Records — Website Build: CTO Action Plan

**Goal:** a small, fast, trustworthy storefront selling two self-published Test-cricket reference books, anchored by a memorable animated hero. Scope is deliberately tiny (2 SKUs, one seller) — the engineering priority is *reliability of checkout/shipping* and *craft of the first impression*, not platform complexity. Over-building is the main risk; resist it.

Companion assets already produced: edited cover photos (`edited_photos/`), `book_metadata.json` (incl. ready-to-paste JSON-LD), `book_catalog_sheet.md`, and a working hero (`hero_prototype.html`).

---

## 1. Stack recommendation

**Primary (recommended): Next.js (App Router) + Stripe Checkout, deployed on Vercel.**
Rationale: full control over the custom animated hero and design system; the prototype drops in as a React component; Stripe handles payments, tax and fraud so we don't touch card data; Vercel gives us image optimization, edge CDN and a free/cheap tier appropriate to this volume.

| Layer | Choice | Notes |
|---|---|---|
| Framework | Next.js 14+ (App Router, RSC) | Static-export-friendly; 5–6 routes total |
| Styling | CSS variables + CSS Modules (or Tailwind if team prefers) | Tokens in §3; keep it lean |
| Payments | **Stripe Checkout** + Stripe Tax | Hosted, PCI-offloaded; webhook → order email |
| Email | Resend / Postmark | Order confirmation + ship notice |
| Images | `next/image`, AVIF/WebP | Source = our edited PNG/JPG covers |
| Hosting | Vercel | Analytics + Speed Insights on |
| CMS | None to start (content in repo/MDX) | 2 products rarely change |

**Alternative (no-code): Shopify Basic.** If the author wants to self-manage inventory/orders without a developer long-term, Shopify is the pragmatic call — it solves shipping/tax/payments out of the box, and our hero ships as a custom Liquid section (same HTML/CSS/JS). Trade-off: less design freedom, ~$39/mo. **Decision owner: CTO — pick before Phase 1.** Recommendation: launch on Next.js+Stripe; revisit Shopify only if order ops become a burden.

---

## 2. Information architecture

```
/                Home — hero, featured books, about teaser, reviews, CTA
/books           Shop — 2 product cards
/books/[slug]    Product — gallery, description, price, buy, JSON-LD
/about           About Shako (bio, photo, Lance Gibbs foreword note)
/contact         Contact form / email / phone
/cart → Stripe   Checkout (hosted)
/policies/*      Shipping, Returns, Privacy (required for trust + Stripe)
```

Slugs: `wi-in-test-matches-1928-2013`, `test-cricket-records-1877-2019`. Keep the nav to 4 items max (The Books · About · Contact · Shop) — fewer choices = faster decisions.

---

## 3. Design system (the "pleasing & easy to use" decisions, made explicit)

The aesthetic is **heritage sports almanac**: deep pitch green, bone/cream paper, West-Indies maroon, gold, cherry-red ball. It's warm, editorial, and distinctly cricket — not generic SaaS. All values below are in the prototype already; lift them into `tokens.css`.

**Color tokens**
```
--pitch:#0d3a2c  --pitch-2:#082a20      /* backgrounds */
--bone:#f3ead6   --bone-dim:#cdc4b1     /* text on dark */
--maroon:#82243a --gold:#d9a94c         /* brand accents */
--cherry:#bb3326                         /* ball / focal pops */
--ink:#0c1b16                            /* text on light, buttons */
```
Rule: one dominant color (pitch green) + sharp accents (gold/cherry). Avoid evenly distributed palettes — they read as timid.

**Typography:** Display = **Fraunces** (characterful serif, gives the "almanac" feel); Body/UI = **Hanken Grotesk**. Pairing a distinctive serif with a clean grotesque creates hierarchy without effort. Body 16–18px, line-height 1.6, measure capped ~32em for readability.

**Spacing & shape:** 8px base scale (8/16/24/40/64). Generous negative space around the headline and a single, obvious primary action per screen. Card radius 6–10px; pill buttons (999px) for a friendly, tappable feel.

**Human-factors checklist (apply on every view):**
- **One primary action**, visually dominant (gold "Shop the books"); secondary actions are ghost buttons. Don't make people choose between two equally loud buttons.
- **Visual hierarchy follows reading order** (eyebrow → headline → lede → CTA), an F/Z scan path; price and "Add to cart" always above the fold on product pages.
- **Tap targets ≥ 44×44px** (Fitts's law); ample hit areas on mobile.
- **Feedback on every interaction**: hover lift on buttons, focus rings, add-to-cart confirmation, loading states on checkout.
- **Reduce cognitive load**: short copy, scannable specs (pages, ISBN, price as a small spec table), no jargon walls.
- **Consistency**: same button shapes, spacing rhythm, and motion easing everywhere.

**Accessibility (non-negotiable, AA):** color contrast ≥ 4.5:1 for body text (verify bone-on-pitch and ink-on-gold); visible keyboard focus; semantic landmarks; descriptive `alt` on covers; the entire hero animation is decorative (`aria-hidden`) and must respect `prefers-reduced-motion`.

---

## 4. Hero animation spec (the bat-hits-ball "shot tracker")

A working reference is in **`hero_prototype.html`** — open it in a browser to see the intended motion. Port it into a self-contained React component `<HeroShot/>`.

**What it does:** a cricket bat in the lower-left swings, strikes the cherry-red ball at the contact point, an impact burst + spark fire, and the ball launches on a broadcast-style **drawn trajectory arc** that wraps up and over the headline toward a glowing boundary rope at top-right — then loops (≈4.2s).

**Technique (keep it GPU-cheap, no JS animation loop required):**
- Scene is a single inline **SVG** (`viewBox 0 0 1200 700`, `preserveAspectRatio="xMidYMid slice"`).
- **Bat** = SVG group rotated via CSS `@keyframes swing` about a handle pivot (`transform-box:view-box`).
- **Ball** rides a CSS **`offset-path`** (the flight curve); `offset-distance` keyframes hold it at rest, then sweep 0→100%.
- **Trajectory** is the same path, revealed with `stroke-dashoffset` (the "tracker" line drawing in), then fading.
- **Impact** = a scaling stroked ring + four spark lines timed to the contact frame (~62% of the loop).
- All four animations share the **same duration and timing** so they stay in lockstep across loops.

**Constraints:**
- Animate only `transform`/`opacity`/`offset-distance`/`stroke-dashoffset` — no layout-triggering properties. Target 60fps; the hero must not regress LCP.
- `@media (prefers-reduced-motion: reduce)` → freeze on a tasteful struck pose (ball mid-arc, tracker partially drawn), no looping.
- On mobile, dim the animation (`opacity:.5`) so text stays the priority; consider pausing it off-screen via `IntersectionObserver`.
- Decorative only: wrap in `aria-hidden="true"`; never block interaction (`pointer-events:none`).

---

## 5. Commerce & fulfillment

- **Checkout:** Stripe Checkout (hosted). Enable **Stripe Tax** and **address collection**. Webhook (`checkout.session.completed`) → send order email to author + buyer.
- **Shipping:** *Action — weigh one copy of each book* (a 551/561pp 6×9 paperback ≈ 1.7–2.1 lb). Then set either a simple flat rate (domestic/intl) or USPS Media Mail (eligible — books) for low cost. Decide domestic-only vs international at launch.
- **Inventory:** volume is low; manual stock counts are fine. Add a simple "sold out / pre-order" toggle per product.
- **Pricing:** list at the printed prices ($29.95 WI / $33.90 Test Records) unless undercutting the existing Amazon/eBay listings is a deliberate strategy.
- **Trust signals:** real cover photos (done), the Lance Gibbs foreword, the 5★ Amazon review, clear policies, author bio with origin story.

---

## 6. SEO, performance & analytics

- **Structured data:** paste the per-book **JSON-LD** from `book_metadata.json` into each product page (`<script type="application/ld+json">`) for Google rich results (price, ISBN, availability).
- **Meta/OG:** unique title+description per page; use the **studio cover shots** as OG/Twitter images.
- **Sitemap + robots**, canonical URLs, and submit to Google Search Console.
- **Performance budget:** LCP < 2.5s. The hero is inline SVG (cheap); covers via `next/image` (AVIF), below-the-fold lazy-loaded. Subset the two Google fonts and `font-display:swap`.
- **Analytics:** Vercel Analytics + a simple funnel (view product → begin checkout → purchase).

---

## 7. Phased plan

**Phase 0 — Decisions & assets (0.5 day)**
- [ ] Confirm stack (Next.js+Stripe vs Shopify)
- [ ] Register domain; create Stripe account
- [ ] Weigh both books; decide shipping zones & price
- [ ] Confirm one business email + phone (keep personal numbers private)

**Phase 1 — Foundation (1–2 days)**
- [ ] Next.js + Vercel skeleton, routes from §2
- [ ] `tokens.css` + typography; base layout, nav, footer
- [ ] Port `<HeroShot/>` from the prototype; verify reduced-motion + mobile

**Phase 2 — Content & commerce (2–3 days)**
- [ ] Product pages from `book_metadata.json`; galleries from `edited_photos/`
- [ ] Stripe Checkout + Tax + webhook → order emails
- [ ] About + Contact + policy pages

**Phase 3 — Polish & launch (1–2 days)**
- [ ] JSON-LD, meta/OG, sitemap, Search Console
- [ ] a11y pass (contrast, keyboard, focus, alt)
- [ ] Lighthouse ≥ 90 across the board; cross-browser/device QA
- [ ] Test-mode purchase end-to-end → go live

**Total: ~1 working week** for one developer.

---

## 8. Definition of done

- A buyer can discover, view, and purchase either book on mobile and desktop, receiving a confirmation email.
- Hero animation runs at 60fps, loops cleanly, and degrades gracefully under reduced-motion.
- Lighthouse: Performance/Best-Practices/SEO/Accessibility ≥ 90; LCP < 2.5s.
- Each product page emits valid Book JSON-LD and unique OG tags.
- All covers use the corrected studio/flat images; no raw phone photos anywhere.
