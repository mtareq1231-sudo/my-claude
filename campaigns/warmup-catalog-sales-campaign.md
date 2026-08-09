# Warmup — Catalog Sales Campaign (WhatsApp + Calls)

**Store:** Warmup — warmupjo.com (Jordan, JOD, EEST)
**Requested:** Sales campaign, Shopify catalog, message destination to Calls and WhatsApp
**Status:** ⛔ Blocked — cannot launch yet. Prerequisites below.

---

## 1. What blocks launch

These are account-level items only the account owner can fix.

| # | Blocker | Detail | Who fixes |
|---|---------|--------|-----------|
| B1 | **No Facebook Page for Warmup** | The only Page available on this login is `جريشة للبلاط - Grisha Tiles` (id `106064670890356`) — a different business. WhatsApp click-to-message ads **and** call ads both require a Page. | Owner |
| B2 | **No Meta catalog for Warmup** | Business `warmup_jo` (`1978048349559384`) has zero catalogs. The only two catalogs on the login belong to `جريشه لبلاط الديكور`. | Owner / setup |
| B3 | **No payment method** | Ad account `warmup jordan` (`1040996508411644`) has `has_payment_method: false`. | Owner |
| B4 | **Currency mismatch** | That ad account is set to **EGP**, but the store sells in **JOD** in Jordan. Ad account currency cannot be changed after creation. | Owner decision |

## 2. Platform constraints (not fixable — the plan works around them)

- **C1 — Sales objective does not support the Calls goal.** Meta's `OUTCOME_SALES` accepts
  `OFFSITE_CONVERSIONS, VALUE, LANDING_PAGE_VIEWS, IMPRESSIONS, POST_ENGAGEMENT, REACH, LINK_CLICKS, CONVERSATIONS`.
  `QUALITY_CALL` is **not** among them — calls require `OUTCOME_LEADS` (or Traffic/Engagement).
  → Calls need their own campaign; they cannot sit under the Sales campaign.
- **C2 — One destination per ad set.** WhatsApp and Calls can never share an ad set, so they are separate ad sets regardless.
- **C3 — Catalog ads and messaging destinations are different products.** Advantage+ catalog (dynamic) ads render from the
  catalog and drive to Website/Shop. Click-to-WhatsApp ads use standard image/carousel creative. The catalog powers
  retargeting and the website ad set; the WhatsApp and Calls ad sets run manual creative built from catalog products.

## 3. Proposed structure

```
Campaign A — "Warmup | Sales | Catalog"        objective: OUTCOME_SALES     (CBO)
  ├─ Ad set A1  "WhatsApp — Broad JO"          destination: WHATSAPP
  │                                            goal: CONVERSATIONS
  │                                            promoted_object: { page_id }
  └─ Ad set A2  "Website — Catalog Retargeting" destination: WEBSITE
                                               goal: OFFSITE_CONVERSIONS
                                               promoted_object: { pixel_id, custom_event_type: PURCHASE }
                                               product_set: from Warmup catalog

Campaign B — "Warmup | Leads | Calls"          objective: OUTCOME_LEADS     (CBO)
  └─ Ad set B1  "Calls — Broad JO"             destination: PHONE_CALL
                                               goal: QUALITY_CALL
                                               promoted_object: { page_id }
```

Targeting for all ad sets: `{"geo_locations":{"countries":["JO"]}}`, broad (no invented interest IDs),
Advantage+ Audience on. All entities are created **PAUSED** for review before any spend.

## 4. Catalog source — recommendation

Prefer the **Facebook & Instagram sales channel app** in Shopify admin over an API-built catalog:

- continuously syncs price, stock, and new products — an API/CSV catalog is a snapshot that goes stale immediately
- creates the catalog under the correct business and links the Meta pixel/dataset in the same flow
- fixes B2 and gives the pixel needed for ad set A2 in one step

Catalog scope to decide: **all 69 active products**, or the **17 tagged `meta-sync`**.
The `meta-sync` tag looks like a deliberate subset, so it is the safer default.

Note: `ارضيات فوم (2.5cm)` is priced at **0.000 JOD** and `بنش متحرك ثقيل` has **0 inventory** —
both would be rejected or suppressed by Meta catalog validation. Fix before syncing.

## 5. Open decisions

1. Which ad account — `warmup jordan` (EGP, no payment method), or a different/new JOD account?
2. Catalog via Shopify sales channel (recommended) or API-built now?
3. Catalog scope — all 69 active, or the 17 `meta-sync` products?
4. Daily budget, WhatsApp business number, and the phone number for call ads.

## 6. Reference — account inventory

| Ad account | ID | Currency | Payment method | Business |
|---|---|---|---|---|
| warmup jordan | 1040996508411644 | EGP | ✗ | warmup_jo |
| Tareq | 1380005700498127 | EGP | ✓ | جريشه لبلاط الديكور |
| Classy Travel | 1451173459641632 | CAD | ✓ | horus_store16 |
| Atelier Salma Elsareef | 1223373786443814 | EGP | ✓ | Atelier Salma Elsareef |
| (unnamed) | 1819698555145882 | USD | ✓ | leader.jo__official |
| (unnamed) | 1932190657582170 | USD | ✓ | — |
