"""Data cleaning and transformation for scraped marketplace products.

Reads raw JSON from staging, normalizes fields, parses product specs,
and outputs a clean CSV ready for analytics.

ponytail: Regex-heavy parsing is intentionally simple. A production system
would use NLP/NER for product spec extraction — for MVP, regex covers ~70%
of cases which is acceptable.
"""

import json
import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Schema — all fields + computed columns
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "timestamp",
    "shop_location",
    "shop_city",
    "shop_province",
    "product_name",
    "category",
    "subcategory",
    "price",
    "rating",
    "sold_count",
    "review_count",
    "shop_name",
    "shop_rating",
    "product_url",
    "flavor",
    "weight",
    "variant",
]


# ---------------------------------------------------------------------------
# City → Province mapping (official Indonesian admin divisions)
# ---------------------------------------------------------------------------
# Source: https://en.wikipedia.org/wiki/List_of_regencies_and_cities_of_Indonesia
# "Kab." = Kabupaten (regency), "Kota" = city — they are different admin regions.
# "Kab. Bandung" (regency) ≠ "Bandung" (city), even though both are in West Java.

CITY_TO_PROVINCE = {
    # DKI Jakarta
    "Jakarta Barat": "DKI Jakarta",
    "Jakarta Pusat": "DKI Jakarta",
    "Jakarta Selatan": "DKI Jakarta",
    "Jakarta Timur": "DKI Jakarta",
    "Jakarta Utara": "DKI Jakarta",
    # Banten
    "Tangerang": "Banten",
    "Tangerang Selatan": "Banten",
    "Kab. Tangerang": "Banten",
    # Jawa Barat
    "Bandung": "Jawa Barat",
    "Kab. Bandung": "Jawa Barat",
    "Kab. Bandung Barat": "Jawa Barat",
    "Bekasi": "Jawa Barat",
    "Kab. Bekasi": "Jawa Barat",
    "Bogor": "Jawa Barat",
    "Kab. Bogor": "Jawa Barat",
    "Cirebon": "Jawa Barat",
    "Kab. Cirebon": "Jawa Barat",
    "Depok": "Jawa Barat",
    "Tasikmalaya": "Jawa Barat",
    "Kab. Tasikmalaya": "Jawa Barat",
    "Cimahi": "Jawa Barat",
    "Sukabumi": "Jawa Barat",
    "Kab. Sukabumi": "Jawa Barat",
    "Garut": "Jawa Barat",
    "Kab. Garut": "Jawa Barat",
    "Sumedang": "Jawa Barat",
    "Kab. Sumedang": "Jawa Barat",
    "Indramayu": "Jawa Barat",
    "Kab. Indramayu": "Jawa Barat",
    "Karawang": "Jawa Barat",
    "Kab. Karawang": "Jawa Barat",
    "Purwakarta": "Jawa Barat",
    "Kab. Purwakarta": "Jawa Barat",
    "Subang": "Jawa Barat",
    "Kab. Subang": "Jawa Barat",
    "Majalaya": "Jawa Barat",
    "Ciamis": "Jawa Barat",
    "Kab. Ciamis": "Jawa Barat",
    "Banjar": "Jawa Barat",
    "Cianjur": "Jawa Barat",
    "Kab. Cianjur": "Jawa Barat",
    # Jawa Tengah
    "Semarang": "Jawa Tengah",
    "Kab. Semarang": "Jawa Tengah",
    "Solo": "Jawa Tengah",
    "Surakarta": "Jawa Tengah",
    "Tegal": "Jawa Tengah",
    "Kab. Tegal": "Jawa Tengah",
    "Pemalang": "Jawa Tengah",
    "Kab. Pemalang": "Jawa Tengah",
    "Purbalingga": "Jawa Tengah",
    "Kab. Purbalingga": "Jawa Tengah",
    "Banjarnegara": "Jawa Tengah",
    "Kab. Banjarnegara": "Jawa Tengah",
    "Wonosobo": "Jawa Tengah",
    "Kab. Wonosobo": "Jawa Tengah",
    "Magelang": "Jawa Tengah",
    "Kab. Magelang": "Jawa Tengah",
    "Purwokerto": "Jawa Tengah",
    "Banyumas": "Jawa Tengah",
    "Kab. Banyumas": "Jawa Tengah",
    # DI Yogyakarta
    "Yogyakarta": "DI Yogyakarta",
    "Sleman": "DI Yogyakarta",
    "Kab. Sleman": "DI Yogyakarta",
    "Bantul": "DI Yogyakarta",
    "Kab. Bantul": "DI Yogyakarta",
    "Kulon Progo": "DI Yogyakarta",
    "Kab. Kulon Progo": "DI Yogyakarta",
    "Gunung Kidul": "DI Yogyakarta",
    "Kab. Gunung Kidul": "DI Yogyakarta",
    # Jawa Timur
    "Surabaya": "Jawa Timur",
    "Malang": "Jawa Timur",
    "Kab. Malang": "Jawa Timur",
    "Kediri": "Jawa Timur",
    "Kab. Kediri": "Jawa Timur",
    "Blitar": "Jawa Timur",
    "Kab. Blitar": "Jawa Timur",
    "Madiun": "Jawa Timur",
    "Kab. Madiun": "Jawa Timur",
    "Probolinggo": "Jawa Timur",
    "Kab. Probolinggo": "Jawa Timur",
    "Jember": "Jawa Timur",
    "Kab. Jember": "Jawa Timur",
    "Banyuwangi": "Jawa Timur",
    "Kab. Banyuwangi": "Jawa Timur",
    "Pasuruan": "Jawa Timur",
    "Kab. Pasuruan": "Jawa Timur",
    "Mojokerto": "Jawa Timur",
    "Kab. Mojokerto": "Jawa Timur",
    "Jombang": "Jawa Timur",
    "Kab. Jombang": "Jawa Timur",
    "Tulungagung": "Jawa Timur",
    "Kab. Tulungagung": "Jawa Timur",
    "Gresik": "Jawa Timur",
    "Kab. Gresik": "Jawa Timur",
    "Lamongan": "Jawa Timur",
    "Kab. Lamongan": "Jawa Timur",
    "Tuban": "Jawa Timur",
    "Kab. Tuban": "Jawa Timur",
    "Bojonegoro": "Jawa Timur",
    "Kab. Bojonegoro": "Jawa Timur",
    "Nganjuk": "Jawa Timur",
    "Kab. Nganjuk": "Jawa Timur",
    "Ngawi": "Jawa Timur",
    "Kab. Ngawi": "Jawa Timur",
    "Ponorogo": "Jawa Timur",
    "Kab. Ponorogo": "Jawa Timur",
    "Pacitan": "Jawa Timur",
    "Kab. Pacitan": "Jawa Timur",
    "Trenggalek": "Jawa Timur",
    "Kab. Trenggalek": "Jawa Timur",
    "Lumajang": "Jawa Timur",
    "Kab. Lumajang": "Jawa Timur",
    "Situbondo": "Jawa Timur",
    "Kab. Situbondo": "Jawa Timur",
    "Bondowoso": "Jawa Timur",
    "Kab. Bondowoso": "Jawa Timur",
    "Bangil": "Jawa Timur",
    "Batu": "Jawa Timur",
}


def normalize_city(raw_location: str) -> str:
    """Normalize city name: trim whitespace, keep 'Kab.' prefix as-is.

    "Kab. Bandung" and "Bandung" are different admin regions (regency vs city).
    We keep the original distinction but normalize whitespace.
    """
    if not raw_location:
        return ""
    return raw_location.strip()


def get_province(city: str) -> str:
    """Map city name to province using official Indonesian admin data.

    Returns empty string if city is not in the mapping.
    """
    if not city:
        return ""
    # Try exact match first
    if city in CITY_TO_PROVINCE:
        return CITY_TO_PROVINCE[city]
    # Try without "Kab. " prefix for fuzzy match
    stripped = re.sub(r"^Kab\.\s*", "", city)
    if stripped in CITY_TO_PROVINCE:
        return CITY_TO_PROVINCE[stripped]
    # Try case-insensitive
    city_lower = city.lower()
    for k, v in CITY_TO_PROVINCE.items():
        if k.lower() == city_lower:
            return v
    return ""


# ---------------------------------------------------------------------------
# Keyword → subcategory mapping
# ---------------------------------------------------------------------------

KEYWORD_TO_SUBCATEGORY = {
    "cokelat": "chocolate",
    "chocolate": "chocolate",
    "permen": "candy",
    "candy": "candy",
    "snack": "snacks",
    "camilan": "snacks",
    "keripik": "snacks",
    "biskuit": "snacks",
    "wafer": "snacks",
}


# ---------------------------------------------------------------------------
# Product spec parsing
# ---------------------------------------------------------------------------

FLAVOR_KEYWORDS = [
    "sapi panggang", "ayam bakar", "balado", "original", "strawberry",
    "cokelat", "chocolate", "keju", "cheese", "vanilla", "mocca", "mocha",
    "greentea", "green tea", "matcha", "taro", "durian", "mangga", "mango",
    "jeruk", "orange", "lemon", "anggur", "grape", "nanas", "pineapple",
    "pisang", "banana", "jambu", "guava", "susu", "milk", "kopi", "coffee",
    "madu", "honey", "pedas", "spicy", "rumput laut", "seaweed", "udang",
    "shrimp", "BBQ", "barbecue", "bbq", "sapi lada hitam", "black pepper",
    "sweet corn", "jagung manis", "ayam", "chicken", "sapi", "beef", "ikan", "fish",
]

WEIGHT_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(g|gr|gram|ml|mL|liter|ltr|l|kg|kilogram)\b",
    re.IGNORECASE,
)

VARIANT_KEYWORDS = [
    "large", "big", "small", "mini", "pack", "box", "pouch", "sachet",
    "tube", "bag", "wrapper", "cup", "bottle", "botol", "kaleng", "can",
    "jar", "toples", "rex", "jumbo", "family", "sharing", "single", "multi",
]


def parse_flavor(product_name: str) -> str:
    name_lower = product_name.lower()
    for flavor in FLAVOR_KEYWORDS:
        if flavor.lower() in name_lower:
            return flavor.lower().replace(" ", "_")
    return ""


def parse_weight(product_name: str) -> str:
    match = WEIGHT_PATTERN.search(product_name)
    if match:
        value = match.group(1).replace(",", ".")
        unit = match.group(2).lower()
        if unit in ("gr", "gram"):
            unit = "g"
        elif unit in ("liter", "ltr", "l"):
            unit = "ml"
        elif unit in ("kilogram",):
            unit = "kg"
        return f"{value}{unit}"
    return ""


def parse_variant(product_name: str) -> str:
    name_lower = product_name.lower()
    for variant in VARIANT_KEYWORDS:
        if variant in name_lower:
            return variant
    return ""


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize_price(price) -> int:
    if isinstance(price, (int, float)):
        return int(price)
    if not price:
        return 0
    s = str(price)
    s = re.sub(r"[Rp\s.]", "", s, flags=re.IGNORECASE)
    s = s.replace(",", "")
    try:
        return int(s)
    except ValueError:
        return 0


def normalize_sold_count(sold) -> int:
    if isinstance(sold, (int, float)):
        return int(sold)
    if not sold:
        return 0
    s = str(sold).lower().strip()
    s = s.replace("+", "").strip()
    s = s.replace(".", "")
    try:
        if "jt" in s or "juta" in s:
            num = float(s.replace("jt", "").replace("juta", "").strip())
            return int(num * 1_000_000)
        elif "rb" in s or "ribu" in s:
            num = float(s.replace("rb", "").replace("ribu", "").strip())
            return int(num * 1_000)
        else:
            return int(float(s))
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Main cleaning pipeline
# ---------------------------------------------------------------------------


def clean_products(staging_dir: Path, output_path: Path) -> pd.DataFrame:
    """Read staging JSONs, clean, and output CSV."""
    all_raw = []
    for json_file in staging_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                all_raw.extend(data)
            else:
                all_raw.append(data)

    if not all_raw:
        print("WARNING: No data found in staging directory")
        return pd.DataFrame(columns=REQUIRED_FIELDS)

    print(f"Loaded {len(all_raw)} raw records from staging")

    df = pd.DataFrame(all_raw)
    initial_count = len(df)

    # --- Map API fields to our schema ---
    if "_keyword" in df.columns:
        df["subcategory"] = df["_keyword"].map(KEYWORD_TO_SUBCATEGORY).fillna("snacks")
    else:
        df["subcategory"] = "snacks"

    # Carry category from staging JSON (e.g., "Makanan & Minuman")
    if "category" not in df.columns:
        df["category"] = ""

    # Ensure all required fields exist
    for field in REQUIRED_FIELDS:
        if field not in df.columns:
            df[field] = ""

    print(f"After field mapping: {len(df)} records")

    # --- Deduplication by product_url ---
    df = df.drop_duplicates(subset=["product_url"], keep="first")
    print(f"After dedup: {len(df)} records (removed {initial_count - len(df)} dupes)")

    # --- Remove rows with missing critical fields ---
    before = len(df)
    df = df.dropna(subset=["price", "sold_count"])
    df = df[df["price"].astype(str).str.strip() != ""]
    df = df[df["sold_count"].astype(str).str.strip() != ""]
    print(f"After null removal: {len(df)} records (removed {before - len(df)})")

    # --- Normalize numeric fields ---
    df["price"] = df["price"].apply(normalize_price)
    df["sold_count"] = df["sold_count"].apply(normalize_sold_count)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").fillna(0).astype(int)
    df["shop_rating"] = pd.to_numeric(df["shop_rating"], errors="coerce").fillna(0.0)

    # --- Location normalization ---
    # No geo filter — keep all locations for analytics
    df["shop_city"] = df["shop_location"].apply(normalize_city)
    df["shop_province"] = df["shop_city"].apply(get_province)

    province_counts = df["shop_province"].value_counts()
    unmapped = (df["shop_province"] == "").sum()
    print(f"Locations: {len(df)} total, {unmapped} unmapped to province")
    print(f"  Provinces: {dict(province_counts)}")

    # --- Parse product specs ---
    df["flavor"] = df["product_name"].apply(parse_flavor)
    df["weight"] = df["product_name"].apply(parse_weight)
    df["variant"] = df["product_name"].apply(parse_variant)

    # --- Computed columns ---
    df["price_bucket"] = _compute_price_buckets(df)
    df["rating_category"] = df["rating"].apply(_rating_category)

    # --- Final cleanup ---
    df = df[df["price"] > 0]
    df["price"] = df["price"].astype(int)
    df["sold_count"] = df["sold_count"].astype(int)

    # Select and order columns
    output_fields = REQUIRED_FIELDS + ["price_bucket", "rating_category"]
    for col in output_fields:
        if col not in df.columns:
            df[col] = ""
    df = df[output_fields]

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nCleaned data saved to: {output_path}")
    print(f"Final record count: {len(df)}")

    return df


def _compute_price_buckets(df: pd.DataFrame) -> pd.Series:
    buckets = pd.Series("mid", index=df.index)
    for subcat in df["subcategory"].unique():
        mask = df["subcategory"] == subcat
        median = df.loc[mask, "price"].median()
        if median == 0:
            continue
        low_threshold = median * 0.6
        high_threshold = median * 1.5
        buckets[mask & (df["price"] < low_threshold)] = "cheap"
        buckets[mask & (df["price"] >= low_threshold) & (df["price"] <= high_threshold)] = "mid"
        buckets[mask & (df["price"] > high_threshold)] = "expensive"
    return buckets


def _rating_category(rating: float) -> str:
    if rating >= 4.5:
        return "high"
    elif rating >= 3.5:
        return "medium"
    else:
        return "low"


if __name__ == "__main__":
    staging_dir = Path("data/staging")
    output_path = Path("data/cleaned/products_clean.csv")
    clean_products(staging_dir, output_path)
