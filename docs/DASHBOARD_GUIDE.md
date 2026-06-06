# Power BI Dashboard — Step-by-Step Build Guide

This guide builds the **Riyadh Hotels** dashboard from scratch in **Power BI Desktop** (free on Windows). Follow it top to bottom; every click is listed.

> Before you start, run `python scripts/clean_data.py` so that
> `data/processed/riyadh_hotels_clean.csv` exists.

---

## Step 0 — Install Power BI Desktop

Download from the Microsoft Store (search "Power BI Desktop") or from
`https://powerbi.microsoft.com/desktop/`. Install and open it. Close the
start-up splash screen.

---

## Step 1 — Apply the theme first

Doing this before adding visuals means everything is styled correctly from the start.

1. Go to the **View** ribbon.
2. Click **Themes** → the small dropdown arrow → **Browse for themes**.
3. Select `powerbi/riyadh_desert_theme.json`.
4. You should see a confirmation that the *Riyadh Desert Hospitality* theme was imported.

### Why this theme for Riyadh

| Color | Hex | Meaning |
|-------|-----|---------|
| Palm green (primary) | `#1A5632` | Saudi national green; oases & palm groves |
| Desert gold (accent) | `#C9A227` | Luxury hospitality, brass, dates |
| Najdi clay | `#B5651D` | Traditional Riyadh mud-brick architecture |
| Sage / sand neutrals | `#4A7C59` `#D9B382` `#E8DCC4` | Desert landscape, warm canvas |
| Off-white canvas | `#FAF6EF` | Soft, premium feel (no harsh white) |

Green = "good", red-clay `#A23B2D` = "bad" for conditional formatting, gold = highlight.

---

## Step 2 — Load the data

1. **Home** ribbon → **Get data** → **Text/CSV**.
2. Browse to `data/processed/riyadh_hotels_clean.csv` → **Open**.
3. In the preview window, check the encoding is **65001: Unicode (UTF-8)**.
4. Click **Transform Data** (not "Load") to open Power Query and verify types.

### In Power Query, confirm these column types

| Column | Type |
|--------|------|
| `hotel_id` | Whole Number |
| `price`, `base_price`, `extra_fees`, `price_per_night` | Decimal Number |
| `check_in`, `check_out` | Date |
| `nights`, `review_count` | Whole Number |
| `rating` | Decimal Number |
| `latitude`, `longitude` | Decimal Number |
| `has_free_breakfast`, `has_free_cancellation`, `has_geo` | True/False |
| everything else | Text |

To change a type: click the small icon left of the column name and pick the type.
When done, **Home → Close & Apply**.

---

## Step 3 — Create the measures

In the **Data** pane, right-click the table `riyadh_hotels_clean` → **New measure**. Paste each of the following (one measure at a time), then press Enter.

```DAX
Hotels = DISTINCTCOUNT('riyadh_hotels_clean'[hotel_id])
```
```DAX
Total Listings = COUNTROWS('riyadh_hotels_clean')
```
```DAX
Avg Price = AVERAGE('riyadh_hotels_clean'[price])
```
```DAX
Avg Price Per Night = AVERAGE('riyadh_hotels_clean'[price_per_night])
```
```DAX
Avg Rating = AVERAGE('riyadh_hotels_clean'[rating])
```
```DAX
Avg Fee % =
DIVIDE(
    SUM('riyadh_hotels_clean'[extra_fees]),
    SUM('riyadh_hotels_clean'[base_price])
)
```

Format the money measures as currency:
select the measure → **Measure tools** ribbon → **Format: Currency**, or set
**Format = "0"** with no symbol and just label cards "SAR" (since the symbol ﷼
can render oddly). Set **Avg Fee %** to **Percentage, 1 decimal**.

---

## Step 4 — Set the page up

1. With nothing selected, open the **Format** pane (paint-roller icon) → **Canvas settings** → **Type: 16:9**.
2. Insert a title: **Insert** ribbon → **Text box**. Type
   `RIYADH HOTELS — PRICE & RATING OVERVIEW`. Make it bold, size ~20, color `#1A3C24`. Place it across the top.

Target layout:

```
┌─────────────────────────────────────────────────────────────┐
│  RIYADH HOTELS — PRICE & RATING OVERVIEW                      │
├───────────┬───────────┬───────────┬───────────┬─────────────┤
│ Hotels    │ Avg Price │ Avg /night│ Avg Rating│  Avg Fee %  │  ← KPI cards
├───────────┴───────────┴─────┬─────┴───────────┴─────────────┤
│  Avg price by source (bar)  │     Map of hotels (bubbles)    │
├─────────────────────────────┼────────────────────────────────┤
│  Price vs Rating (scatter)  │   Top hotels by rating (table) │
└─────────────────────────────┴────────────────────────────────┘
   Slicers along the very top or left: source • channel_type • price_tier • rating_band • check_in
```

---

## Step 5 — KPI cards (the top row)

For each of the 5 cards:

1. Click an empty area → in **Visualizations**, choose the **Card** visual.
2. Drag the measure into the **Fields** well:
   - Card 1 → `Hotels`
   - Card 2 → `Avg Price`
   - Card 3 → `Avg Price Per Night`
   - Card 4 → `Avg Rating`
   - Card 5 → `Avg Fee %`
3. Resize each to a small rectangle and line them up across the top row.
4. (Optional) Format → **Callout value** color `#1A5632`; **Category label** "Avg Price (SAR)" etc.

---

## Step 6 — Bar chart: Average price by source

1. Click empty area → choose **Clustered bar chart**.
2. **Y-axis** = `source`.
3. **X-axis** = `Avg Price`.
4. **Legend** (optional) = `channel_type` (colors OTA vs Direct/Brand).
5. Sort: click the visual's **… (more options)** → **Sort axis → Avg Price → Ascending**, so the cheapest source is at the top.
6. Format → **Data labels: On**.

This visual directly answers "which booking channel is cheapest."

---

## Step 7 — Map: hotels by location

1. Click empty area → choose the **Map** (bubble) visual. (If maps are disabled, enable in **File → Options → Global → Security → uncheck/relevant map setting**, or use **Azure Map**.)
2. **Latitude** = `latitude`, **Longitude** = `longitude`.
3. **Bubble size** = `Avg Price` (or `price`).
4. **Legend** = `price_tier` (Budget→Luxury get different colors).
5. **Filter the map to rows that have coordinates:** drag `has_geo` into the visual's **Filters on this visual** → check **True**. (~40% of rows have no coordinates.)

---

## Step 8 — Scatter: price vs rating

1. Click empty area → choose **Scatter chart**.
2. **X-axis** = `Avg Price`.
3. **Y-axis** = `Avg Rating`.
4. **Values** (the points/details) = `hotel_name`.
5. **Size** = `Total Listings` or sum of `review_count`.
6. Format → turn **X/Y axis titles On**.

How to read it: hotels in the **lower-right** = high rating for low price = best value. Upper-left = expensive but lower rated.

---

## Step 9 — Table: top hotels

1. Click empty area → choose the **Table** visual.
2. Add fields in order: `hotel_name`, `Avg Rating`, `Avg Price`, `price_tier`, `has_free_breakfast`, `has_free_cancellation`.
3. Sort by **Avg Rating** descending (click the column header).
4. (Optional) Filter to **Top N**: visual filter on `hotel_name` → **Top N = 10 by Avg Rating**.
5. Format → **Style preset: Minimal**; header fill uses the theme green automatically.

---

## Step 10 — Slicers (interactivity)

Add a **Slicer** visual for each of these (one field each):

- `source`
- `channel_type`
- `price_tier`
- `rating_band`
- `check_in` (this becomes a date-range slider)

Place them along the top or down the left side. Selecting any value filters every visual on the page. To make a slicer a dropdown: its **… → Slicer settings / the dropdown caret** at the top-right of the slicer.

---

## Step 11 — Polish & save

1. **View → Page background / Wallpaper**: the theme already sets `#FAF6EF`.
2. Align visuals: select multiple (Ctrl-click) → **Format ribbon → Align**.
3. Give each visual a clear title (Format → **Title**).
4. **File → Save as** → `powerbi/riyadh_hotels_dashboard.pbix`.
5. To share online: **Home → Publish** (needs a free Power BI account) → opens in the Power BI Service (web).

---

## Step 12 — Take a screenshot for the README

Once it looks good, press **Win + Shift + S** (Snip) or export the page, save it as
`assets/dashboard_preview.png`, and add it near the top of `README.md`:

```markdown
![Dashboard preview](assets/dashboard_preview.png)
```

---

## Quick troubleshooting

| Problem | Fix |
|---------|-----|
| Map shows no bubbles | Confirm `latitude`/`longitude` are **Decimal Number** and **Data category** = Latitude/Longitude (Column tools → Data category). Filter `has_geo = True`. |
| Prices look like text | In Power Query set `price` etc. to **Decimal Number**. |
| Arabic/special chars look broken | Re-load CSV with encoding **65001 UTF-8**. |
| Currency symbol looks odd | Label cards manually as "SAR" instead of using the ﷼ symbol. |
| Theme didn't apply | View → Themes → Browse → re-select the JSON; restart Power BI if needed. |
