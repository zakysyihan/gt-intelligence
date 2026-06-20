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
# Schema — all 14 fields + computed columns
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "timestamp",
    "shop_location",
    "product_name",
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

# Java Island provinces and cities for filtering
JAVA_ISLAND_LOCATIONS = {
    # Provinces
    "jakarta", "dki jakarta",
    "jawa barat", "jabar",
    "jawa tengah", "jateng",
    "jawa timur", "jatim",
    "banten",
    "yogyakarta", "di yogyakarta", "jogja",
    "jawa",
    # Major Java cities (used in marketplace seller locations)
    "bandung", "surabaya", "semarang", "tangerang", "bekasi",
    "depok", "bogor", "malang", "solo", "denpasar", "cirebon",
    "tasikmalaya", "purwokerto", "kediri", "blitar", "madiun",
    "jember", "probolinggo", "majalaya", "garut", "sumedang",
    "indramayu", "subang", "karawang", "purwakarta", "ciamis",
    "banjar", "cimahi", "sukabumi", "cianjur", "purwakarta",
    "tegal", "pemalang", "purbalingga", "banjarnegara", "wonosobo",
    "magelang", "sleman", "bantul", "kulon progo", "gunung kidul",
    "gresik", "lamongan", "tuban", "bojonegoro", "nganjuk",
    "ngawi", "ponorogo", "pacitan", "trenggalek", "lumajang",
    "situbondo", "bondowoso", "banyuwangi", "pasuruan", "bangil",
    "mojokerto", "jombang", "tulungagung", "blitar", "kediri",
    "batu",
}


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

# Common Indonesian/English flavor keywords
FLAVOR_KEYWORDS = [
    "sapi panggang",
    "ayam bakar",
    "balado",
    "original",
    "strawberry",
    "cokelat",
    "chocolate",
    "keju",
    "cheese",
    "vanilla",
    "mocca",
    "mocha",
    "greentea",
    "green tea",
    "matcha",
    "taro",
    "durian",
    "mangga",
    "mango",
    "jeruk",
    "orange",
    "lemon",
    "anggur",
    "grape",
    "nanas",
    "pineapple",
    "pisang",
    "banana",
    "jambu",
    "guava",
    "susu",
    "milk",
    "kopi",
    "coffee",
    "madu",
    "honey",
    "pedas",
    "spicy",
    "original",
    "rumput laut",
    "seaweed",
    "udang",
    "shrimp",
    "BBQ",
    "barbecue",
    "bbq",
    "sapi lada hitam",
    "black pepper",
    "rumah",
    "balado",
    "sweet corn",
    "jagung manis",
    "ayam",
    "chicken",
    "sapi",
    "beef",
    "ikan",
    "fish",
]

# Weight patterns: 68g, 100gr, 250ml, 1.5kg, etc.
WEIGHT_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(g|gr|gram|ml|mL|liter|ltr|l|kg|kilogram)\b",
    re.IGNORECASE,
)

# Variant keywords
VARIANT_KEYWORDS = [
    "large",
    "big",
    "small",
    "mini",
    "pack",
    "box",
    "pouch",
    "sachet",
    "tube",
    "bag",
    "wrapper",
    "cup",
    "bottle",
    "botol",
    "kaleng",
    "can",
    "jar",
    "toples",
    "rex",
    "bagus",
    "jumbo",
    "family",
    "sharing",
    "single",
    "multi",
    "variant",
]


def parse_flavor(product_name: str) -> str:
    """Extract flavor from product name using keyword matching."""
    name_lower = product_name.lower()
    for flavor in FLAVOR_KEYWORDS:
        if flavor.lower() in name_lower:
            return flavor.lower().replace(" ", "_")
    return ""


def parse_weight(product_name: str) -> str:
    """Extract weight/netto from product name using regex."""
    match = WEIGHT_PATTERN.search(product_name)
    if match:
        value = match.group(1).replace(",", ".")
        unit = match.group(2).lower()
        # Normalize unit
        if unit in ("gr", "gram"):
            unit = "g"
        elif unit in ("liter", "ltr", "l"):
            unit = "ml"
        elif unit in ("kilogram",):
            unit = "kg"
        return f"{value}{unit}"
    return ""


def parse_variant(product_name: str) -> str:
    """Extract variant from product name using keyword matching."""
    name_lower = product_name.lower()
    for variant in VARIANT_KEYWORDS:
        if variant in name_lower:
            return variant
    return ""


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize_price(price) -> int:
    """Normalize price to integer IDR.
    Handles: 'Rp 50.000', 'Rp50000', 50000, '50.000', etc.
    """
    if isinstance(price, (int, float)):
        return int(price)
    if not price:
        return 0
    s = str(price)
    # Remove Rp prefix, whitespace, dots
    s = re.sub(r"[Rp\s.]", "", s, flags=re.IGNORECASE)
    # Remove commas used as decimal separator (Indonesian style)
    s = s.replace(",", "")
    try:
        return int(s)
    except ValueError:
        return 0


def normalize_sold_count(sold) -> int:
    """Normalize sold_count string to integer.
    Handles: '1rb+' → 1000, '10rb+' → 10000, '100rb+' → 100000,
             '1jt+' → 1000000, '500+' → 500
    """
    if isinstance(sold, (int, float)):
        return int(sold)
    if not sold:
        return 0
    s = str(sold).lower().strip()
    # Remove '+' and whitespace
    s = s.replace("+", "").strip()
    # Remove dots (thousand separator)
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


def is_java_location(location: str) -> bool:
    """Check if shop location is in Java Island."""
    if not location:
        return False
    loc_lower = location.lower().strip()
    return any(java_loc in loc_lower for java_loc in JAVA_ISLAND_LOCATIONS)


# ---------------------------------------------------------------------------
# Main cleaning pipeline
# ---------------------------------------------------------------------------


def clean_products(staging_dir: Path, output_path: Path) -> pd.DataFrame:
    """Read staging JSONs, clean, and output CSV."""
    # Load all JSON files from staging
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
    # The scraper already outputs mostly matching fields
    # Map keyword to subcategory
    if "_keyword" in df.columns:
        df["subcategory"] = df["_keyword"].map(KEYWORD_TO_SUBCATEGORY).fillna("snacks")
    elif "category" in df.columns:
        # Fallback: try to map from category name
        df["subcategory"] = df["category"].apply(
            lambda c: _category_to_subcategory(str(c))
        )
    else:
        df["subcategory"] = "snacks"

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

    # --- Filter Java Island ---
    before = len(df)
    df = df[df["shop_location"].apply(is_java_location)]
    print(f"After Java Island filter: {len(df)} records (removed {before - len(df)})")

    # --- Parse product specs ---
    df["flavor"] = df["product_name"].apply(parse_flavor)
    df["weight"] = df["product_name"].apply(parse_weight)
    df["variant"] = df["product_name"].apply(parse_variant)

    # --- Computed columns ---
    df["price_bucket"] = _compute_price_buckets(df)
    df["rating_category"] = df["rating"].apply(_rating_category)

    # --- Final cleanup ---
    # Remove rows with zero price (invalid)
    df = df[df["price"] > 0]

    # Ensure correct types
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


def _category_to_subcategory(category: str) -> str:
    """Map Tokopedia category name to our subcategory."""
    cat_lower = category.lower()
    if any(w in cat_lower for w in ["chocolate", "cokelat", "coklat"]):
        return "chocolate"
    elif any(w in cat_lower for w in ["candy", "permen", "candy"]):
        return "candy"
    elif any(w in cat_lower for w in ["snack", "camilan", "keripik", "biskuit", "wafer"]):
        return "snacks"
    return "snacks"


def _compute_price_buckets(df: pd.DataFrame) -> pd.Series:
    """Assign price_bucket based on subcategory median."""
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
    """Categorize rating into low/medium/high."""
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
