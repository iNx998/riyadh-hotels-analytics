# Data Dictionary — `riyadh_hotels_clean.csv`

All monetary values are in **Saudi Riyal (SAR)**.

| Column | Type | Description |
|--------|------|-------------|
| `hotel_id` | integer | Unique identifier for the hotel (primary key per hotel). |
| `hotel_name` | text | Hotel name including branding/location. |
| `source` | text | Booking source (Booking.com, Agoda.com, Expedia, brand sites, etc.). |
| `channel_type` | text | Derived: `OTA` (online travel agency) vs `Direct / Brand`. |
| `price` | float | Final price paid — base price plus taxes/service fees. |
| `base_price` | float | Room price before extra fees. Filled with `price` where originally missing. |
| `extra_fees` | float | Derived: `price − base_price`, floored at 0. |
| `currency` | text | Always `SAR`. |
| `price_per_night` | float | Derived: `price / nights`. |
| `price_tier` | category | Derived quartile band: Budget / Mid-range / Upscale / Luxury. |
| `check_in` | date | Guest check-in date. |
| `check_out` | date | Guest check-out date. |
| `nights` | integer | Derived: nights between check-in and check-out (min 1). |
| `review_count` | integer | Number of reviews. |
| `rating` | float | Quality score, 2.5–5.0. |
| `rating_band` | category | Derived bands: <3.0, 3.0–3.5, 3.5–4.0, 4.0–4.5, 4.5–5.0. |
| `has_free_breakfast` | bool | Derived from the original Info amenities list. |
| `has_free_cancellation` | bool | Derived from the original Info amenities list. |
| `amenities` | text | Pipe-separated amenities parsed from Info. |
| `latitude` | float | Hotel latitude (blank for ~40% of rows). |
| `longitude` | float | Hotel longitude (blank for ~40% of rows). |
| `has_geo` | bool | Derived: true when both coordinates are present. |

## Cleaning decisions

- **60 rows with no `price`** were dropped — they cannot support price analysis.
- **`base_price` nulls** (249) filled with `price`, assuming no separately-known fees.
- **`extra_fees`** clipped to ≥ 0 to remove negative artifacts.
- **Info** column parsed from a stringified Python list into boolean flags + a readable amenities string.
- Coordinates left blank where missing; use `has_geo` to filter the map visual.
