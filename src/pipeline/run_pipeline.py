"""Main pipeline orchestrator.

Runs the full ETL pipeline:
  1. Scrape Tokopedia → data/raw/
  2. Stage (backup) → data/staging/
  3. Clean → data/cleaned/products_clean.csv
  4. LLM Parse → enrich flavor/weight/variant via LLM
  5. Validate → pass/fail report
  6. Curate → data/analytics/products.db (SQLite)

Usage:
  python -m src.pipeline.run_pipeline              # full pipeline
  python -m src.pipeline.run_pipeline --skip-scrape  # skip scraping, use existing staging
  python -m src.pipeline.run_pipeline --skip-llm     # skip LLM parsing (faster, less accurate)
"""

import argparse
import shutil
import sqlite3
import sys
from pathlib import Path

import pandas as pd


def run_pipeline(skip_scrape: bool = False, skip_llm: bool = False):
    """Execute the full data pipeline."""
    # Resolve paths relative to project root
    project_root = Path(__file__).resolve().parent.parent.parent
    raw_dir = project_root / "data" / "raw"
    staging_dir = project_root / "data" / "staging"
    cleaned_dir = project_root / "data" / "cleaned"
    analytics_dir = project_root / "data" / "analytics"

    cleaned_csv = cleaned_dir / "products_clean.csv"
    db_path = analytics_dir / "products.db"

    print("=" * 60)
    print("BANGUNINDO ANALYTICS MVP — Data Pipeline")
    print("=" * 60)

    # --- Step 1: Scrape ---
    if not skip_scrape:
        print("\n[Step 1/6] Scraping Tokopedia...")
        from src.pipeline.scraper import run_scraper
        run_scraper(raw_dir)
    else:
        print("\n[Step 1/6] Scraping SKIPPED (--skip-scrape)")

    # --- Step 2: Stage (backup raw → staging) ---
    print("\n[Step 2/6] Staging raw data...")
    staging_dir.mkdir(parents=True, exist_ok=True)
    raw_files = list(raw_dir.glob("*.json"))
    if raw_files:
        for f in raw_files:
            dest = staging_dir / f.name
            shutil.copy2(f, dest)
            print(f"  Copied: {f.name} → staging/")
        print(f"  Staged {len(raw_files)} file(s)")
    else:
        print("  WARNING: No raw files to stage")
        staging_files = list(staging_dir.glob("*.json"))
        if staging_files:
            print(f"  Using {len(staging_files)} existing staging file(s)")

    # --- Step 3: Clean ---
    print("\n[Step 3/6] Cleaning data...")
    from src.pipeline.cleaner import clean_products
    df = clean_products(staging_dir, cleaned_csv)

    # --- Step 4: LLM Parse (enrich flavor/weight/variant) ---
    if not skip_llm:
        print("\n[Step 4/6] LLM parsing product specs...")
        from src.pipeline.llm_parser import parse_products_with_llm
        import csv

        # Read CSV as list of dicts
        with open(cleaned_csv, "r", encoding="utf-8") as f:
            products = list(csv.DictReader(f))

        # Parse with LLM
        products = parse_products_with_llm(products)

        # Write back
        fieldnames = list(products[0].keys())
        with open(cleaned_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)

        # Stats
        total = len(products)
        flavor_n = sum(1 for p in products if p.get("flavor"))
        weight_n = sum(1 for p in products if p.get("weight"))
        variant_n = sum(1 for p in products if p.get("variant"))
        print(f"  Updated: flavor {flavor_n}/{total}, weight {weight_n}/{total}, variant {variant_n}/{total}")
    else:
        print("\n[Step 4/6] LLM parsing SKIPPED (--skip-llm)")

    # --- Step 5: Validate ---
    print("\n[Step 5/6] Validating data quality...")
    from src.pipeline.validator import validate
    results = validate(cleaned_csv)

    # --- Step 6: Curate (write to SQLite) ---
    print("\n[Step 6/6] Writing to SQLite...")
    analytics_dir.mkdir(parents=True, exist_ok=True)

    if cleaned_csv.exists():
        df = pd.read_csv(cleaned_csv, encoding="utf-8")

        conn = sqlite3.connect(str(db_path))
        df.to_sql("products", conn, if_exists="replace", index=False)

        # Add indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subcategory ON products(subcategory)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_shop_location ON products(shop_location)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_shop_province ON products(shop_province)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON products(category)")

        row_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"  Written {row_count} rows to {db_path}")

        # Summary stats
        print(f"\n  Summary stats:")
        print(f"    Subcategories: {df['subcategory'].nunique()}")
        print(f"    Avg price: Rp {df['price'].mean():,.0f}")
        print(f"    Avg rating: {df['rating'].mean():.2f}")
        print(f"    Total sold (sum): {df['sold_count'].sum():,}")
        print(f"    Unique shops: {df['shop_name'].nunique()}")

        # Derived field stats
        for field in ["flavor", "weight", "variant"]:
            filled = (df[field].notna() & (df[field] != "")).sum()
            print(f"    {field}: {filled}/{row_count} ({100 * filled // row_count}%)")

        # Show subcategory breakdown
        print(f"\n  By subcategory:")
        for subcat, group in df.groupby("subcategory"):
            print(f"    {subcat}: {len(group)} products, avg Rp {group['price'].mean():,.0f}")

        conn.close()
    else:
        print(f"  ERROR: {cleaned_csv} not found — skipping SQLite write")

    # --- Final summary ---
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print(f"  Raw data:   {raw_dir}")
    print(f"  Staging:    {staging_dir}")
    print(f"  Cleaned:    {cleaned_csv}")
    print(f"  Database:   {db_path}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the data pipeline")
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip scraping step, use existing staging data",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM parsing step (faster, less accurate specs)",
    )
    args = parser.parse_args()
    run_pipeline(skip_scrape=args.skip_scrape, skip_llm=args.skip_llm)
