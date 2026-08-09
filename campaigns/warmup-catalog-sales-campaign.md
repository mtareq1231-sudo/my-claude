# Warmup — Catalog Sales Campaign (WhatsApp + Calls)

**Store:** Warmup — warmupjo.com (Jordan, JOD, EEST)
**Requested:** Sales campaign, Shopify catalog, message destination to Calls and WhatsApp
**Status:** ⛔ Blocked on owner setup (§7). Structure and decisions are locked; build starts as soon as setup lands.

## Decisions taken

| Decision | Choice |
|---|---|
| Ad account | **New JOD account** under `warmup_jo` — matches store currency, avoids permanent reporting mismatch |
| Catalog source | **Shopify Facebook & Instagram sales channel** — continuous price/stock sync |
| Catalog scope | **All 69 active products** |
| Pixel | **`1527928829106094`** — the only dataset actually firing (see §6b) |

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

Scope: **all 69 active products** (decided). The `meta-sync` tag on 17 of them is not used as a filter.

**Two products will fail Meta catalog validation — fix in Shopify before syncing:**

| Product | Problem |
|---|---|
| `ارضيات فوم (2.5cm)` (`ارضيات-فوم-2-5cm`) | price is **0.000 JOD** — Meta rejects zero-price items |
| `بنش متحرك ثقيل` (`بنش-متحرك-ثقيل`) | **0 inventory** — syncs as `out of stock`, never serves |

## 5. Still needed from you

- Daily budget (campaign-level, CBO)
- WhatsApp Business number to receive messages
- Phone number for the call ads

## 6. Reference — account inventory

| Ad account | ID | Currency | Payment method | Business |
|---|---|---|---|---|
| warmup jordan | 1040996508411644 | EGP | ✗ | warmup_jo |
| Tareq | 1380005700498127 | EGP | ✓ | جريشه لبلاط الديكور |
| Classy Travel | 1451173459641632 | CAD | ✓ | horus_store16 |
| Atelier Salma Elsareef | 1223373786443814 | EGP | ✓ | Atelier Salma Elsareef |
| (unnamed) | 1819698555145882 | USD | ✓ | leader.jo__official |
| (unnamed) | 1932190657582170 | USD | ✓ | — |

### 6b. Datasets (pixels) under warmup_jo — needs cleanup

Five datasets exist for one business. Only **one is receiving events**:

| Dataset | ID | Last fired |
|---|---|---|
| warmup_jo's pixel | **1527928829106094** | **2026-08-09 — live, use this one** |
| warmup_jo's pixel | 1375770671113797 | 2026-08-04 |
| warmup_jo's pixel | 28143430988679834 | never |
| warmup_jo's pixel | 2235806020157388 | never |
| warmup jordan | 1054515230383520 | never |

Five pixels on one store fragments conversion signal and weakens optimisation. Point the Shopify
sales channel at `1527928829106094` and remove the three that have never fired.

## 7. Owner setup checklist (blocks the build)

1. **Create a Warmup Facebook Page** — required for both WhatsApp and call ads. Connect the WhatsApp
   Business number to it (Page → Settings → WhatsApp).
2. **Create a JOD ad account** under business `warmup_jo` in Business Settings, and add a payment
   method. Currency is permanent — confirm JOD at creation.
3. **Install the Facebook & Instagram sales channel** in Shopify admin; connect it to `warmup_jo`,
   the new Page, and pixel `1527928829106094`. This creates and syncs the catalog.
4. **Fix the two products** in §4.
5. Send me the new ad account ID, Page ID, daily budget, WhatsApp number, and call phone number.
