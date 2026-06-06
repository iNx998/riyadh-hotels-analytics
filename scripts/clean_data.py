"""
Clean and prepare the Riyadh Hotels dataset for Power BI.

Input : data/raw/Riyadh_Hotels.xlsx
Output: data/processed/riyadh_hotels_clean.csv

Run:  python scripts/clean_data.py
"""

import ast
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Riyadh_Hotels.xlsx"
OUT = ROOT / "data" / "processed" / "riyadh_hotels_clean.csv"

# All prices are in Saudi Riyal (SAR)
CURRENCY = "SAR"


def parse_info(value):
    """The Info column holds a stringified Python list of amenities."""
    if pd.isna(value):
        return []
    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []


def main():
    df = pd.read_excel(RAW)

    # --- Standardise column names -------------------------------------------
    df = df.rename(
        columns={
            "SOURCE": "source",
            "checkIn": "check_in",
            "checkOut": "check_out",
            "count": "review_count",
            "Info": "info",
        }
    )

    # --- Types --------------------------------------------------------------
    df["check_in"] = pd.to_datetime(df["check_in"], errors="coerce")
    df["check_out"] = pd.to_datetime(df["check_out"], errors="coerce")

    # --- Prices -------------------------------------------------------------
    # base_price missing -> assume equal to final price (no extra fees known)
    df["base_price"] = df["base_price"].fillna(df["price"])
    # extra fees (taxes/service); never negative
    df["extra_fees"] = (df["price"] - df["base_price"]).clip(lower=0)
    df["currency"] = CURRENCY

    # Drop rows with no price at all -> cannot be used in price analysis
    before = len(df)
    df = df.dropna(subset=["price"]).copy()
    dropped = before - len(df)

    # --- Length of stay -----------------------------------------------------
    df["nights"] = (df["check_out"] - df["check_in"]).dt.days.clip(lower=1)
    df["price_per_night"] = (df["price"] / df["nights"]).round(2)

    # --- Amenities flags ----------------------------------------------------
    info_lists = df["info"].apply(parse_info)
    df["has_free_breakfast"] = info_lists.apply(
        lambda x: any("breakfast" in i.lower() for i in x)
    )
    df["has_free_cancellation"] = info_lists.apply(
        lambda x: any("cancellation" in i.lower() for i in x)
    )
    df["amenities"] = info_lists.apply(lambda x: " | ".join(x))

    # --- Geo flag (some rows lack coordinates) ------------------------------
    df["has_geo"] = df["latitude"].notna() & df["longitude"].notna()

    # --- Rating band (for slicers) ------------------------------------------
    df["rating_band"] = pd.cut(
        df["rating"],
        bins=[0, 3.0, 3.5, 4.0, 4.5, 5.0],
        labels=["<3.0", "3.0-3.5", "3.5-4.0", "4.0-4.5", "4.5-5.0"],
        include_lowest=True,
    )

    # --- Price tier (quartile-based) ----------------------------------------
    df["price_tier"] = pd.qcut(
        df["price"],
        q=[0, 0.25, 0.5, 0.75, 1.0],
        labels=["Budget", "Mid-range", "Upscale", "Luxury"],
    )

    # --- Channel type (OTA vs direct/brand) ---------------------------------
    otas = {
        "Booking.com", "Agoda.com", "Expedia", "MakeMyTrip",
        "Vio.com", "Prestigia.com", "Hotels.com", "Trip.com",
    }
    df["channel_type"] = df["source"].apply(
        lambda s: "OTA" if s in otas else "Direct / Brand"
    )

    # --- Final column order -------------------------------------------------
    cols = [
        "hotel_id", "hotel_name", "source", "channel_type",
        "price", "base_price", "extra_fees", "currency",
        "price_per_night", "price_tier",
        "check_in", "check_out", "nights",
        "review_count", "rating", "rating_band",
        "has_free_breakfast", "has_free_cancellation", "amenities",
        "latitude", "longitude", "has_geo",
    ]
    df = df[cols].sort_values(["hotel_name", "source"]).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"Rows in : {before}")
    print(f"Dropped (no price): {dropped}")
    print(f"Rows out: {len(df)}")
    print(f"Unique hotels: {df['hotel_name'].nunique()}")
    print(f"Sources: {df['source'].nunique()}")
    print(f"Saved -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
