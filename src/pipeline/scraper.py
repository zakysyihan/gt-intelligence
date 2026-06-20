"""Tokopedia scraper using tokopaedi library.

Scrapes real product data from Tokopedia's mobile API via user-agent spoofing.
Collects food & beverage products from Java Island sellers.

Trade-off: Uses the tokopaedi library which spoofs mobile user-agents to bypass
Akamai's heaviest protections. If Tokopedia hardens their mobile API, this would
need updating. The library is actively maintained (last update Aug 2025).
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path

from tokopaedi import search

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Food & beverage keywords targeting younger/teenager audience
KEYWORDS = [
    "cokelat",
    "permen",
    "snack",
    "camilan",
    "keripik",
    "biskuit",
    "wafer",
    "chocolate",
    "candy",
]

# Java Island locations for seller filtering
JAVA_ISLAND = {
    "jakarta", "dki jakarta", "jawa barat", "jabar", "jawa tengah", "jateng",
    "jawa timur", "jatim", "banten", "yogyakarta", "di yogyakarta", "jogja",
    "jawa", "bandung", "surabaya", "semarang", "tangerang", "bekasi",
    "depok", "bogor", "malang", "solo", "cirebon", "tasikmalaya",
    "purwokerto", "kediri", "blitar", "madiun", "jember", "probolinggo",
}

# Keyword to subcategory mapping
KEYWORD_TO_SUBCATEGORY = {
    "cokelat": "chocolate", "chocolate": "chocolate",
    "permen": "candy", "candy": "candy",
    "snack": "snacks", "camilan": "snacks", "keripik": "snacks",
    "biskuit": "snacks", "wafer": "snacks",
}


def _is_java_location(city: str | None) -> bool:
    """Check if a shop city is in Java Island."""
    if not city:
        return False
    return any(loc in city.lower() for loc in JAVA_ISLAND)


def _product_to_dict(p, keyword: str) -> dict | None:
    """Convert tokopaedi ProductData to our schema dict."""
    try:
        shop = p.shop
        city = shop.city if shop else ""
        shop_name = shop.name if shop else ""
        shop_type = shop.shop_type if shop else ""

        # Filter Java Island
        if not _is_java_location(city):
            return None

        return {
            "timestamp": datetime.now().isoformat(),
            "product_name": p.product_name or "",
            "category": p.category or "",
            "subcategory": KEYWORD_TO_SUBCATEGORY.get(keyword, "snacks"),
            "price": int(p.price or 0),
            "price_text": p.price_text or "",
            "price_original": p.price_original or "",
            "discount_percentage": p.discount_percentage or "",
            "rating": float(p.rating or 0),
            "sold_count": int(p.sold_count or 0),
            "review_count": int(p.review_count or 0),
            "shop_name": shop_name,
            "shop_location": city,
            "shop_type": shop_type,
            "product_url": p.url or "",
            "weight": p.weight or "",
            "weight_unit": p.weight_unit or "",
            "total_stock": int(p.total_stock or 0) if p.total_stock else 0,
            "_keyword": keyword,
            "_source": "tokopedia_mobile_api",
        }
    except (AttributeError, TypeError, ValueError):
        return None


def run_scraper(output_dir: Path | None = None, target_count: int = 1000) -> Path:
    """Run scraper across all keywords. Returns path to output JSON."""
    if output_dir is None:
        output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    all_products: list[dict] = []
    seen_urls: set[str] = set()

    per_keyword = max(target_count // len(KEYWORDS), 100)

    print(f"Starting Tokopedia scraper — {len(KEYWORDS)} keywords")
    print(f"Target: ~{target_count} products ({per_keyword} per keyword)")
    print(f"Output: {output_dir}\n")

    for i, keyword in enumerate(KEYWORDS):
        remaining = target_count - len(all_products)
        if remaining <= 0:
            break

        max_results = min(per_keyword + 50, remaining + 50)  # overshoot to account for Java filter
        print(f"[{i + 1}/{len(KEYWORDS)}] Scraping: '{keyword}' (max {max_results})")

        try:
            results = search(keyword, max_result=max_results, debug=False)
            added = 0
            for p in results:
                if len(all_products) >= target_count:
                    break
                d = _product_to_dict(p, keyword)
                if d and d["product_url"] not in seen_urls:
                    seen_urls.add(d["product_url"])
                    all_products.append(d)
                    added += 1
            print(f"  Got {len(results)} results, {added} from Java Island (total: {len(all_products)})")
        except Exception as e:
            print(f"  Error: {e}")

        # Rate limit between keywords
        if i < len(KEYWORDS) - 1:
            delay = random.uniform(2, 5)
            print(f"  Waiting {delay:.1f}s...")
            time.sleep(delay)

    # Save output
    output_file = output_dir / f"tokopedia_all_{date_str}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Scraping complete!")
    print(f"Total products: {len(all_products)}")
    print(f"Source: Tokopedia mobile API (tokopaedi library)")
    print(f"Output: {output_file}")

    # Subcategory breakdown
    subcats = {}
    for p in all_products:
        sc = p.get("subcategory", "unknown")
        subcats[sc] = subcats.get(sc, 0) + 1
    for sc, count in sorted(subcats.items()):
        print(f"  {sc}: {count}")

    # Location breakdown
    cities = {}
    for p in all_products:
        c = p.get("shop_location", "unknown")
        cities[c] = cities.get(c, 0) + 1
    print(f"\n  Top cities:")
    for city, count in sorted(cities.items(), key=lambda x: -x[1])[:10]:
        print(f"    {city}: {count}")

    print(f"{'=' * 50}")
    return output_file


if __name__ == "__main__":
    run_scraper()
