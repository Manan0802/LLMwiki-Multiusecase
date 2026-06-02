---
name: seller-spec-creator
description: Use this skill when you want to create product specifications for a category on an Indian B2B marketplace. Triggers for any request involving product specification creation, category attribute mapping, or seller form field generation — even if phrased as "give me specs for X", "what are the attributes for Y", "create a spec sheet for Z", or "define product fields for W".
---

# Seller Spec Creator

This skill help in creating the finalised product specifications for a given product category on an Indian B2B marketplace. These specs serve two purposes:
1. **Seller product addition form** — sellers fill these specs when listing their products
2. **Buyer-facing filters and display** — buyers use these to search, filter, compare, and evaluate products

Every spec must reflect how **real Indian B2B buyers and sellers** actually talk about, search for, and transact on products.

---

## Specification Naming

- Use the most common name used by sellers and buyers in the **Indian B2B market**
- Spec names must be in **Title Case** (with stopwords like "of", "on", "in", "and", "to" in lowercase)
- Exception: Industry-standard acronyms remain uppercase (ISO, IS, BIS, ISI, PVC, RPM, MDF, UV, LED, TSA, PP, ABS, PC)
- **Examples:** "Number of Doors", "Nominal Diameter", "ISO Certification"
- No units in spec names — units belong on option values only

---

## Specification Classification

Classify each specification into **ONE of three tiers**:

### Primary Specs — MIN 2, MAX 3

The **first things a buyer asks about** when inquiring. These specs:
- Have the highest impact on pricing
- Are the first filter a buyer applies on a marketplace
- Make two listings directly comparable
- Without these, the listing is commercially useless

**Ask yourself:**
- In the first 60 seconds of a buyer inquiry, is this one of the 2–3 things they ask about?
- Do sellers include this spec in their product listing titles (not just descriptions)?
- Would the listing be unsearchable or incomparable without this spec?

**Examples:**
- Steel Rod → "Diameter" is Primary (everyone searches "12mm steel rod")
- Fire Extinguisher → "Capacity" is Primary ("2kg fire extinguisher")
- Industrial Fan → "Sweep Size" is Primary ("24 inch exhaust fan")

**Prefer `radio_button` in Primary.** `multi_select` only if the category genuinely requires multiple simultaneous values.

---

### Secondary Specs — MIN 2, MAX 3

**Functional performance specs** that define technical suitability. These specs:
- Are checked after primary specs to confirm fit for purpose
- Help buyers compare products with the same primary spec values
- If the wrong value is selected, the product becomes technically unsuitable for the buyer's application

**Ask yourself:**
- What spec, if it had the wrong value, would make this product the wrong choice for the buyer's application?
- Is this spec required for technical compatibility (voltage, thread size, connector type)?
- Does this spec relate to compliance/safety that buyers must verify before purchase?

**Examples:**
- Motor → "Voltage" is Secondary (must match power supply)
- Pipe Fitting → "Thread Type" is Secondary (must match existing system)
- Safety Helmet → "ISI Certification" is Secondary (compliance requirement)

---

### Tertiary Specs — MAX 4

**Supporting details** that complete the listing without driving the purchase decision. These specs:
- Do not independently drive purchase decisions
- Add credibility and completeness to the listing
- Are useful for niche buyers with specific requirements

**Ask yourself:**
- Would this spec change the buying decision on its own, or does it just add detail?
- Is this something a seller would mention to make their listing stand out, not to qualify it?

**Examples:**
- LED Bulb → "Color Temperature" (preference)
- Water Pump → "Cable Length" (convenience)
- Motor → "Efficiency Class" (additional technical detail)
- Steel Almirah → "Color" (aesthetic)

---

## Tier Overflow Rule

If more than 3 specs qualify for Primary or Secondary, use this tiebreaker:

> **Which spec's value change causes a bigger price difference in the Indian B2B market?**
> → Higher price impact = higher tier
> → Lower price impact = drop to next tier

If more than 4 specs qualify for Tertiary, drop the least commercially impactful ones entirely.

---

## Single-Value Specifications

If a spec has only ONE value across the entire category → **Do NOT include it.**

**Exception:** Include in Tertiary ONLY if it's a regulatory/certification requirement that buyers need to verify.

**DO NOT include:**
- Category: CO2 Fire Extinguisher → Spec: Extinguisher Type → value is always "CO2" → skip
- Category: Stainless Steel Sink → Spec: Material → value is always "Stainless Steel" → skip

**INCLUDE in Tertiary:**
- Category: Industrial Safety Helmet → Spec: ISI Certification → buyers must verify → keep

---

## Input Type Determination

### `radio_button`
Use when the product has **exactly one value** for this spec — the values are mutually exclusive.
- ✅ Use for: Size, Material, Grade, Shell Type, Capacity, Thickness, Diameter

### `multi_select`
Use when a product can **genuinely have multiple values for this spec simultaneously**.

**Use ONLY when ALL THREE conditions are true:**

1. **Physical/Technical Reality** — Product genuinely carries multiple attributes at once
   - ✅ Tile Usage → one tile IS used in "Bathroom, Kitchen, Outdoor" simultaneously
   - ❌ Steel Grade → a rod cannot be "IS 2062 AND SS 304" simultaneously

2. **Typical Selection Count** — Real products have 2–4 values, not all options
   - ✅ Safety Features → Helmet has "Chin Strap, Adjustable Headband, Ventilation"
   - ❌ Applications → if most sellers select all 10 options → use `radio_button` instead

3. **Not Gameable** — Options are objectively verifiable, not marketing claims
   - ✅ Certifications → "ISI, CE, ISO 9001" (documentable)
   - ❌ Features → "Durable, High Quality, Long Lasting" (all subjective)

**Default:** When uncertain, prefer `radio_button` for cleaner data.

### `text_input`
Use **only** when values are truly free-form and no meaningful fixed option list is possible.
- ✅ Use for: Brand Name, Model Number, Custom Dimensions, Part Number
- ⚠️ Last resort — always prefer `radio_button` or `multi_select` when a fixed list is possible

---

## Specification Rules

### VALID Specifications Must:
1. Be technically applicable to the category
2. Be commercially meaningful in Indian B2B marketplaces
3. Help buyers compare or differentiate products
4. Avoid duplication — if two terms exist for the same thing, use only the most common one

### INVALID Specifications:
- Specs that don't logically apply to the product (e.g., "Engine Type" for "Granite Tile")
- Duplicate specs under different names (e.g., don't include both "Weight" and "Mass")
- Specs with only one universal value (see Single-Value rule above)

---

## Option Rules

### 1. Character Limit
Every option value must be **under 25 characters** including spaces, units, and symbols.

### 2. Maximum 10 Options
Include the **top 10 most commercially popular** choices only. Drop long-tail, rarely-used options.

### 3. Option Ordering
List options by **commercial popularity** — what buyers actively search for and sellers commonly stock.

Priority order:
1. Highest buyer demand and seller inventory volume
2. BIS/ISI/ISO standard values where applicable
3. Buyer search frequency

**Never order by:** physical size (small→large), alphabetical, IS standard numbering, or price.


### 4. Unit Consistency & Placement — CRITICAL

**Units MUST be attached to option values, NEVER to spec names.**

- Use the **primary legally standard Indian unit** (per BIS/government standards)
- If a secondary unit is commonly spoken in the trade, include it in parentheses
- Always attach the unit directly to the number — no separation

**Correct:**
- Spec Name: `Door Height` → Options: `2100 mm (7 ft)`, `2400 mm (8 ft)`

**Incorrect:**
- Spec Name: `Door Height (mm)` ← WRONG
- Options: `2100`, `2400` ← WRONG

**Mixed units (rare):** attach unit to EACH value individually:
- Spec Name: `Capacity` → Options: `500 ml`, `1 L`, `5 L`, `20 L`

### 5. Options Reality Check
Before including any option, confirm:
> *"Would a real Indian B2B seller have listed this exact value on their product in the last 12 months?"*
- **High confidence** → include
- **Medium confidence** (appears in catalogues but not in active trade) → include only if also referenced in active buyer searches
- **Low confidence** (rare or theoretical) → exclude, even if technically valid

### 6. No Vague or Placeholder Options
Permanently banned: `Custom`, `Other`, `As Required`, `As per Requirement`, `Unbranded`, `Not Applicable`, `N/A`, `Various`, `Standard`

Every option must be specific, product-relevant, and actionable — a buyer must be able to self-select it on a marketplace form.

### 7. No Duplicate Options
Merge options that represent the same value. Keep the most common form, put the alternate in parentheses.
- ✅ `Stainless Steel (SS)` — not both separately
- ✅ `PP (Polypropylene)` — not both separately

### 8. Avoid Unnecessary Ranges
Use fixed discrete values wherever possible. Use a range **only** when the industry genuinely represents that spec as an interval.
- ❌ `Small, Medium, Large` when standard sizes exist
- ✅ `551–650 kg/m³` when density class intervals are the industry standard

### 9. Consistent Format Within a Spec
All options for a given spec must follow the same format — same unit, same case style.

### 10. Preserve Source Format — Non-Negotiable
Option values must use the EXACT format found in the source data.
for example:
- If wiki shows a range → output as range: `4–14 inch` not `Up to 14 inch`
- If wiki shows a fixed value → output as fixed value: `20 in` not `Up to 20 in`
- Never convert, interpret, or rephrase the format of a value
- "Up to", "upto", "maximum", "minimum" prefixes are BANNED
  unless the source data itself uses that exact phrasing

—

## 4 Option Purity Rule

Each attribute must represent **exactly one spec dimension**. Never mix values that answer different questions into the same attribute.

**Before adding any option to an attribute, ask:**
> "Do all options in this attribute answer the same question?"

If the answer is **no** — split them into separate attributes.

**Common violation patterns to reject:**

| ❌ Bad (mixed) | ✅ Fix (split) |
|---|---|
| Size: `20"`, `24"`, `Set of 2`, `Set of 3` | **Size:** `20"`, `24"`, `28"` + **Pack:** `Single`, `Set of 2`, `Set of 3` |
| Color: `Red`, `Blue`, `Pack of 6` | **Color:** `Red`, `Blue` + **Pack Size:** `Pack of 6` |
| Material: `Cotton`, `Unisex`, `XL` | **Material:** `Cotton` + **Gender:** `Unisex` + **Size:** `XL` |

**Rule:** Options within a single attribute must be:
- **Mutually exclusive** — a product can only be one of them at a time
- **Same type** — all sizes, OR all pack counts, OR all colors — never mixed

If a value would require a **different question to elicit it** than the other values in the attribute, it belongs in a **separate attribute**.

—

## Brand Specification — Special Rules

1. **Is brand a meaningful differentiator in this category?**
   - Power tools → YES (Bosch, Makita, DeWalt matter)
   - Generic nuts and bolts → NO (buyers don't care)
2. **If YES** → Determine input type based on market structure:
   - **5 or fewer dominant brands** exist in this category → `radio_button` with those brand names as options, ordered by market share
   - **More than 10 brands / highly fragmented market** → `text_input` with empty options `[]`

3. **If NO** → Do NOT include "Brand" as a spec.

**NEVER include:** "Unbranded", "Generic", "No Brand", "OEM", "Local Make"

---

## Symbols & Formatting

| Symbol | Correct | Wrong |
|--------|---------|-------|
| Degrees | `°C` | `C`, `deg C` |
| Square | `m²`, `cm²` | `m2`, `cm2` |
| Cubic | `m³`, `cm³` | `m3`, `cm3` |
| Range | `15–20 kg` (en dash) | `15-20 kg` (hyphen) |
| Rate | `m³/hr`, `kg/cm²` | `m3/hr`, `kg/cm2` |
| Tolerance | `±0.5 mm` | `+/-0.5 mm` |
| Micro | `µm` | `um`, `micron` |

---

## Pre-Output Quality Checklist

**Tiers**
- [ ] Primary has MIN 2, MAX 3 specs
- [ ] Secondary has MIN 2, MAX 3 specs
- [ ] Tertiary has MAX 4 specs
- [ ] No spec appears in more than one tier
- [ ] Single-value specs only in Tertiary, and only if regulatory

**Spec Names**
- [ ] Title Case with stopwords lowercase
- [ ] No spec name contains units
- [ ] No two specs mean the same thing
- [ ] Every spec is applicable to this category

**Options**
- [ ] Every option reality-checked for Indian B2B market relevance
- [ ] Every option under 25 characters
- [ ] No vague or placeholder options
- [ ] No duplicate options within a spec
- [ ] Units attached with correct symbols (see table above)
- [ ] Options ordered by commercial popularity, not size or alphabetical
- [ ] Maximum 10 options per spec
- [ ] Ranges use en dash `–` not hyphen `-`
- [ ] Superscripts: `m²` not `m2`, `m³` not `m3`

**Input Types**
- [ ] `radio_button` for mutually exclusive single-value specs
- [ ] `multi_select` only when all three conditions are met
- [ ] `text_input` only when no fixed list is possible

---

## Final Quality Check

Before outputting, answer both questions:

1. *"If a real Indian B2B buyer used these specs as marketplace filters, would they find exactly what they are looking for — and nothing irrelevant?"*
2. *"If an Indian seller filled in these specs for their product listing, would the listing be complete, accurate, and competitive against other sellers in this category?"*

Both **yes** → output. Either **no** → revise first.

---

## Output Format

Return **ONE valid JSON object only**.
No markdown fences. No text before or after. Starts with `{`, ends with `}`.

{
  "category_name": "<string>",
  "finalized_specs": {
    "finalized_primary_specs": {
      "specs": [
        {
          "spec_name": "<string>",
          "options": ["<val1>", "<val2>", "..."],
          "input_type": "radio_button | multi_select | text_input"
        }
      ]
    },
    "finalized_secondary_specs": {
      "specs": [
        {
          "spec_name": "<string>",
          "options": ["<val1>", "<val2>", "..."],
          "input_type": "radio_button | multi_select | text_input"
        }
      ]
    },
    "finalized_tertiary_specs": {
      "specs": [
        {
          "spec_name": "<string>",
          "options": ["<val1>", "<val2>", "..."],
          "input_type": "radio_button | multi_select | text_input"
        }
      ]
    }
  }
}
