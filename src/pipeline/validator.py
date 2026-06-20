"""Data quality validation for cleaned product CSV.

Runs schema, type, null, range, dedup, and geography checks.
Prints pass/fail for each check. Returns True if all critical checks pass.

ponytail: Using pandas for validation is slightly heavier than pure Python
csv module, but the type checking and aggregation functions save ~50 lines
of manual code.
"""

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Expected schema
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

# Fields that must never be null
CRITICAL_NULL_FIELDS = ["price", "sold_count", "subcategory", "shop_location"]

JAVA_ISLAND_LOCATIONS = {
    # Provinces
    "jakarta", "dki jakarta",
    "jawa barat", "jabar",
    "jawa tengah", "jateng",
    "jawa timur", "jatim",
    "banten",
    "yogyakarta", "di yogyakarta", "jogja",
    "jawa",
    # Major Java cities
    "bandung", "surabaya", "semarang", "tangerang", "bekasi",
    "depok", "bogor", "malang", "solo", "denpasar", "cirebon",
    "tasikmalaya", "purwokerto", "kediri", "blitar", "madiun",
    "jember", "probolinggo", "majalaya", "garut", "sumedang",
    "indramayu", "subang", "karawang", "purwakarta", "ciamis",
    "banjar", "cimahi", "sukabumi", "cianjur",
    "tegal", "pemalang", "purbalingga", "banjarnegara", "wonosobo",
    "magelang", "sleman", "bantul", "kulon progo", "gunung kidul",
    "gresik", "lamongan", "tuban", "bojonegoro", "nganjuk",
    "ngawi", "ponorogo", "pacitan", "trenggalek", "lumajang",
    "situbondo", "bondowoso", "banyuwangi", "pasuruan", "bangil",
    "mojokerto", "jombang", "tulungagung", "batu",
}

# Minimum rows expected
MIN_ROWS = 500


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------


def validate(csv_path: Path) -> dict:
    """Run all validation checks. Returns dict of check_name -> passed."""
    results = {}

    if not csv_path.exists():
        print(f"FAIL: File not found: {csv_path}")
        return {"file_exists": False}

    df = pd.read_csv(csv_path, encoding="utf-8")
    total_rows = len(df)
    print(f"\n{'=' * 50}")
    print(f"Data Validation Report")
    print(f"File: {csv_path}")
    print(f"Total rows: {total_rows}")
    print(f"{'=' * 50}")

    # 1. Schema check
    missing = [f for f in REQUIRED_FIELDS if f not in df.columns]
    passed = len(missing) == 0
    results["schema"] = passed
    if passed:
        print(f"PASS: Schema — all {len(REQUIRED_FIELDS)} fields present")
    else:
        print(f"FAIL: Schema — missing fields: {missing}")

    # 2. Type checks
    type_checks = {
        "price": "int",
        "rating": "float",
        "sold_count": "int",
        "review_count": "int",
        "shop_rating": "float",
    }
    all_types_ok = True
    for field, expected_type in type_checks.items():
        if field not in df.columns:
            continue
        if expected_type == "int":
            try:
                pd.to_numeric(df[field], errors="raise").astype(int)
                print(f"PASS: Type — {field} is numeric (int)")
            except (ValueError, TypeError):
                all_types_ok = False
                print(f"FAIL: Type — {field} is not numeric")
        elif expected_type == "float":
            try:
                pd.to_numeric(df[field], errors="raise").astype(float)
                print(f"PASS: Type — {field} is numeric (float)")
            except (ValueError, TypeError):
                all_types_ok = False
                print(f"FAIL: Type — {field} is not numeric")
    results["types"] = all_types_ok

    # 3. Null checks
    null_issues = []
    for field in CRITICAL_NULL_FIELDS:
        if field not in df.columns:
            null_issues.append(f"{field} (missing column)")
            continue
        null_count = df[field].isna().sum() + (df[field].astype(str).str.strip() == "").sum()
        if null_count > 0:
            null_issues.append(f"{field}: {null_count} nulls")
        else:
            print(f"PASS: Nulls — {field} has 0 nulls")
    results["nulls"] = len(null_issues) == 0
    if null_issues:
        print(f"FAIL: Nulls — issues: {null_issues}")
    else:
        print("PASS: Nulls — all critical fields have 0 nulls")

    # 4. Range checks
    range_issues = []
    if "price" in df.columns:
        prices = pd.to_numeric(df["price"], errors="coerce")
        bad_price = (prices <= 0).sum()
        if bad_price > 0:
            range_issues.append(f"price: {bad_price} values <= 0")
        else:
            print(f"PASS: Range — price > 0 for all rows")

    if "rating" in df.columns:
        ratings = pd.to_numeric(df["rating"], errors="coerce")
        bad_rating = ((ratings < 1) | (ratings > 5) | ratings.isna()).sum()
        if bad_rating > 0:
            range_issues.append(f"rating: {bad_rating} values outside 1-5")
        else:
            print(f"PASS: Range — rating 1-5 for all rows")

    if "sold_count" in df.columns:
        sold = pd.to_numeric(df["sold_count"], errors="coerce")
        bad_sold = (sold < 0).sum()
        if bad_sold > 0:
            range_issues.append(f"sold_count: {bad_sold} values < 0")
        else:
            print(f"PASS: Range — sold_count >= 0 for all rows")

    results["ranges"] = len(range_issues) == 0
    if range_issues:
        print(f"FAIL: Range — issues: {range_issues}")
    else:
        print("PASS: Range — all values within expected ranges")

    # 5. Dedup check
    if "product_url" in df.columns:
        dupes = df["product_url"].duplicated().sum()
        results["dedup"] = dupes == 0
        if dupes == 0:
            print(f"PASS: Dedup — 0 duplicate product_url")
        else:
            print(f"FAIL: Dedup — {dupes} duplicate product_url values")
    else:
        results["dedup"] = False
        print(f"FAIL: Dedup — product_url column not found")

    # 6. Geography check
    if "shop_location" in df.columns:
        non_java = 0
        for loc in df["shop_location"].dropna():
            loc_lower = str(loc).lower().strip()
            if not any(java in loc_lower for java in JAVA_ISLAND_LOCATIONS):
                non_java += 1
        results["geography"] = non_java == 0
        if non_java == 0:
            print(f"PASS: Geography — all shop_locations in Java Island")
        else:
            print(f"FAIL: Geography — {non_java} locations outside Java Island")
    else:
        results["geography"] = False
        print(f"FAIL: Geography — shop_location column not found")

    # 7. Row count check
    results["row_count"] = total_rows >= MIN_ROWS
    if total_rows >= MIN_ROWS:
        print(f"PASS: Row count — {total_rows} >= {MIN_ROWS}")
    else:
        print(f"WARN: Row count — {total_rows} < {MIN_ROWS} (below minimum)")

    # Summary
    passed_count = sum(1 for v in results.values() if v)
    total_checks = len(results)
    print(f"\n{'=' * 50}")
    print(f"Summary: {passed_count}/{total_checks} checks passed")

    if all(results.values()):
        print("RESULT: ALL CHECKS PASSED ✓")
    elif results.get("row_count") is False and all(
        v for k, v in results.items() if k != "row_count"
    ):
        print("RESULT: ALL CRITICAL CHECKS PASSED (row count warning)")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"RESULT: FAILED checks: {failed}")
    print(f"{'=' * 50}\n")

    return results


if __name__ == "__main__":
    csv_path = Path("data/cleaned/products_clean.csv")
    validate(csv_path)
