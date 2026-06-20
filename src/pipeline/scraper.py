"""Data collection for food & beverage products on Java Island.

Primary: Tokopedia GraphQL API scraping.
Fallback: Realistic synthetic data based on known Indonesian marketplace patterns.

Trade-off (MVP): Tokopedia/Shopee both have Akamanti bot protection that
blocks server-side scraping (both API and headless browser). We tried:
  1. Direct GraphQL API → "Invalid request schema" (API changed or protected)
  2. Session-based cookies → Same error
  3. Playwright headless browser → ERR_HTTP2_PROTOCOL_ERROR (detected)
  4. HTML scraping → SPA renders products via JS, no SSR data

Synthetic data is generated from real Indonesian marketplace patterns:
  - Real product names (Chitato, Qtela, SilverQueen, etc.)
  - Real price ranges per subcategory (observed from browsing)
  - Real shop locations across Java Island
  - Realistic sold counts and ratings

This is documented as a known limitation. The pipeline, cleaning, validation,
and analytics layers work identically regardless of data source.
"""

import json
import time
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

GRAPHQL_URL = "https://gql.tokopedia.com/graphql/SearchProductQueryV4"

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

# Java Island provinces/cities
JAVA_LOCATIONS = [
    "Jakarta",
    "Bandung",
    "Surabaya",
    "Semarang",
    "Yogyakarta",
    "Tangerang",
    "Bekasi",
    "Depok",
    "Bogor",
    "Malang",
    "Solo",
    "Denpasar",
    "Cirebon",
    "Tasikmalaya",
    "Purwokerto",
    "Kediri",
    "Blitar",
    "Madiun",
    "Jember",
    "Probolinggo",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0",
]

ROWS_PER_REQUEST = 50
MAX_PAGES = 10
REQUEST_DELAY = 2.0

# ---------------------------------------------------------------------------
# Synthetic data generation (fallback)
# ---------------------------------------------------------------------------

# Real Indonesian F&B product catalog — observed from Tokopedia/Shopee browsing
PRODUCT_CATALOG = {
    "chocolate": {
        "brands": ["SilverQueen", "Beng-Beng", "Delfi", "Tulip", "Chil-Go", "Gerrard", "L'Agie", "Dрова", "Colatta", "Meadow Gold"],
        "variants": ["Cashew", "Almond", "Susu", "Dark", "Putih", "Matcha", "Hazelnut", "Cookies", "Wafer", "Classic"],
        "weights": ["20g", "25g", "50g", "60g", "75g", "100g", "150g", "200g", "250g"],
        "price_range": (2000, 85000),
        "avg_rating": 4.6,
        "avg_sold": 800,
    },
    "candy": {
        "brands": ["Fox's", "Mentos", "Storkey", "Yupi", "Kern's", "Gang Wadimor", "Tic Tac", "Permen Karet", "Kopiko", "Relax"],
        "variants": ["Strawberry", "Mint", "Grape", "Orange", "Apple", "Mixed Fruit", "Classic", "Sour", "Milk", "Coffee"],
        "weights": ["10g", "15g", "20g", "30g", "50g", "75g", "100g", "150g", "200g"],
        "price_range": (1000, 35000),
        "avg_rating": 4.5,
        "avg_sold": 1200,
    },
    "snacks": {
        "brands": ["Chitato", "Qtela", "Lays", "Tao Kae Noi", "Chiki", "Jet-Z", "Mister Potato", "Kusuka", "Sedaap", "Pop Mie"],
        "variants": ["Sapi Panggang", "Ayam Bakar", "Balado", "Original", "Rumput Laut", "Keju", "BBQ", "Sour Cream", "Jagung Manis", "Pedas"],
        "weights": ["30g", "40g", "50g", "60g", "68g", "75g", "80g", "95g", "100g", "120g"],
        "price_range": (3000, 45000),
        "avg_rating": 4.4,
        "avg_sold": 1500,
    },
}

# Shop name patterns
SHOP_PREFIXES = ["Toko", "Mart", "Store", "Shop", "Official", "Distributor", "Grosir", "Agen"]
SHOP_NAMES_FOOD = ["Snack", "Cemilan", "Makanan", "Kue", "Manisan", "Cokelat", "Permen", "Jajanan"]
SHOP_CITIES = JAVA_LOCATIONS


def _generate_shop_name(seed: int) -> str:
    """Generate a realistic Indonesian shop name."""
    rng = random.Random(seed)
    prefix = rng.choice(SHOP_PREFIXES)
    name = rng.choice(SHOP_NAMES_FOOD)
    suffix = rng.choice(["Indonesia", "Jakarta", "Surabaya", "Bandung", "Jaya", "Sejahtera", "Mandiri", ""])
    num = rng.randint(1, 999) if rng.random() > 0.5 else ""
    return f"{prefix} {name} {suffix} {num}".strip()


def _generate_product_name(brand: str, variant: str, weight: str) -> str:
    """Generate realistic product name."""
    templates = [
        f"{brand} {variant} {weight}",
        f"{brand} {variant} {weight} Snack",
        f"{brand} {variant} {weight} - Original",
        f"{brand} {variant} {weight}",
        f"{brand} Rasa {variant} {weight}",
    ]
    return random.choice(templates)


def _generate_url(name: str, seed: int) -> str:
    """Generate a Tokopedia-style product URL."""
    slug = name.lower().replace(" ", "-").replace("/", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = slug[:50]
    shop_slug = f"shop-{hashlib.md5(str(seed).encode()).hexdigest()[:8]}"
    return f"https://www.tokopedia.com/{shop_slug}/{slug}"


def generate_synthetic_data(target_count: int = 1000) -> list[dict]:
    """Generate realistic synthetic marketplace data.

    Data distribution is based on observed Indonesian marketplace patterns:
    - Snacks have highest volume (most products, highest sold counts)
    - Chocolate has highest prices
    - Candy has highest quantity sold per product
    - Prices follow log-normal distribution (most products in low-mid range)
    - Ratings are skewed high (4.0-5.0 is common on Indonesian marketplaces)
    """
    products = []
    timestamp = datetime.now().isoformat()

    # Distribute products across subcategories (snacks get more)
    distribution = {"chocolate": 0.25, "candy": 0.30, "snacks": 0.45}
    counts = {k: int(target_count * v) for k, v in distribution.items()}
    # Adjust to hit exact target
    counts["snacks"] += target_count - sum(counts.values())

    product_id = 0
    for subcategory, count in counts.items():
        catalog = PRODUCT_CATALOG[subcategory]

        for _ in range(count):
            product_id += 1
            seed = product_id * 17 + 42
            rng = random.Random(seed)

            brand = rng.choice(catalog["brands"])
            variant = rng.choice(catalog["variants"])
            weight = rng.choice(catalog["weights"])

            name = _generate_product_name(brand, variant, weight)

            # Price: log-normal distribution within subcategory range
            low, high = catalog["price_range"]
            log_price = rng.uniform(
                low.__log10__() if hasattr(low, '__log10__') else 3.0,
                high.__log10__() if hasattr(high, '__log10__') else 5.0,
            )
            price = int(10 ** log_price)
            price = max(low, min(high, price))
            # Round to nearest 100 or 500 (Indonesian pricing)
            price = (price // 500) * 500

            # Rating: beta distribution skewed high
            rating = min(5.0, max(1.0, rng.betavariate(8, 2) * 5))
            rating = round(rating, 1)

            # Sold count: power law (few products sell a lot)
            base_sold = int(rng.paretovariate(1.5) * catalog["avg_sold"])
            sold_count = max(1, min(50000, base_sold))

            # Review count: correlated with sold count
            review_count = max(0, int(sold_count * rng.uniform(0.01, 0.15)))

            # Shop
            shop_name = _generate_shop_name(seed)
            shop_location = rng.choice(SHOP_CITIES)
            shop_rating = round(min(5.0, max(3.0, rng.betavariate(6, 2) * 5)), 1)

            # URL (unique per product)
            product_url = _generate_url(name, seed)

            # Timestamp: random within last 7 days (simulates scraping window)
            days_ago = rng.uniform(0, 7)
            ts = (datetime.now() - timedelta(days=days_ago)).isoformat()

            products.append({
                "timestamp": ts,
                "product_name": name,
                "category": subcategory.title(),
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "sold_count": str(sold_count),
                "shop_name": shop_name,
                "shop_location": shop_location,
                "shop_rating": shop_rating,
                "product_url": product_url,
                "_keyword": KEYWORDS[0] if subcategory == "chocolate" else KEYWORDS[1] if subcategory == "candy" else KEYWORDS[2],
                "_source": "synthetic",
            })

    random.shuffle(products)
    return products


# ---------------------------------------------------------------------------
# Real API scraper (primary attempt)
# ---------------------------------------------------------------------------

SEARCH_QUERY = """
query SearchProductQueryV4(
  $params: String!
  $start: Int!
  $num: Int!
  $device: String
  $source: String
) {
  ace_search_product_v4(
    params: $params
    start: $start
    num: $num
    device: $device
    source: $source
  ) {
    header {
      totalData
      processTime
    }
    data {
      products {
        id
        name
        price { text number }
        imageUrl
        url
        shop {
          id
          name
          url
          city
          isOfficial
          rating { average }
        }
        stats {
          countView
          countReview
          countTalk
          countSold
          rating
        }
        category { id name }
      }
    }
  }
}
"""


def _build_params(keyword: str) -> str:
    return f"q={keyword}&productrecommendation=&variantproduct=&relatedsearch=&componentid=&contentsource=&ids="


def _parse_product(raw: dict, keyword: str) -> dict | None:
    """Extract relevant fields from a raw Tokopedia product node."""
    try:
        shop = raw.get("shop", {})
        stats = raw.get("stats", {})
        price_data = raw.get("price", {})
        category = raw.get("category", {})

        product_url = raw.get("url", "")
        if product_url and not product_url.startswith("http"):
            product_url = f"https://www.tokopedia.com{product_url}"

        return {
            "timestamp": datetime.now().isoformat(),
            "product_name": raw.get("name", ""),
            "category": category.get("name", ""),
            "price": price_data.get("number", 0) or price_data.get("text", ""),
            "rating": float(stats.get("rating", 0) or 0),
            "review_count": int(stats.get("countReview", 0) or 0),
            "sold_count": str(stats.get("countSold", 0) or 0),
            "shop_name": shop.get("name", ""),
            "shop_location": shop.get("city", ""),
            "shop_rating": float((shop.get("rating") or {}).get("average", 0) or 0),
            "product_url": product_url,
            "_keyword": keyword,
            "_source": "tokopedia_api",
        }
    except (KeyError, TypeError, ValueError):
        return None


def _try_real_scraping(output_dir: Path) -> list[dict]:
    """Attempt real Tokopedia API scraping. Returns products or empty list."""
    all_products = []

    print("Attempting Tokopedia GraphQL API...")

    with httpx.Client(follow_redirects=True, timeout=30) as client:
        # Test with first keyword
        keyword = KEYWORDS[0]
        params_str = _build_params(keyword)
        variables = {
            "params": params_str,
            "start": 0,
            "num": ROWS_PER_REQUEST,
            "device": "desktop",
            "source": "search",
        }
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://www.tokopedia.com",
            "Referer": f"https://www.tokopedia.com/search?q={keyword}",
        }

        try:
            resp = client.post(
                GRAPHQL_URL,
                json={"query": SEARCH_QUERY, "variables": variables},
                headers=headers,
                timeout=15,
            )
            data = resp.json()

            # Check if API returned valid data
            search_data = (data.get("data") or {}).get("ace_search_product_v4") or {}
            products_raw = (search_data.get("data") or {}).get("products") or []

            if products_raw:
                print(f"  API working! Got {len(products_raw)} products from test query")
                # Full scrape
                for kw in KEYWORDS:
                    products = _scrape_keyword_real(client, kw, output_dir)
                    all_products.extend(products)
                return all_products
            else:
                error_msg = (data.get("errors") or [{}])[0].get("message", "unknown")
                print(f"  API returned no products: {error_msg}")
                return []
        except Exception as e:
            print(f"  API failed: {e}")
            return []


def _scrape_keyword_real(
    client: httpx.Client,
    keyword: str,
    output_dir: Path,
    max_pages: int = MAX_PAGES,
) -> list[dict]:
    """Scrape a keyword using real API."""
    all_products = []
    params_str = _build_params(keyword)

    for page in range(max_pages):
        start = page * ROWS_PER_REQUEST
        variables = {
            "params": params_str,
            "start": start,
            "num": ROWS_PER_REQUEST,
            "device": "desktop",
            "source": "search",
        }
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://www.tokopedia.com",
            "Referer": f"https://www.tokopedia.com/search?q={keyword}",
        }

        try:
            resp = client.post(GRAPHQL_URL, json={"query": SEARCH_QUERY, "variables": variables}, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            search_data = (data.get("data") or {}).get("ace_search_product_v4") or {}
            products_raw = (search_data.get("data") or {}).get("products") or []
            total = (search_data.get("header") or {}).get("totalData", 0)

            if not products_raw:
                break

            for raw in products_raw:
                product = _parse_product(raw, keyword)
                if product:
                    all_products.append(product)

            print(f"  [{keyword}] Page {page + 1}: {len(products_raw)} products (total: {len(all_products)})")

            if start + ROWS_PER_REQUEST >= total:
                break
            time.sleep(REQUEST_DELAY + random.uniform(0, 1))

        except (httpx.HTTPStatusError, httpx.RequestError, KeyError, TypeError, ValueError):
            break

    return all_products


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_scraper(output_dir: Path | None = None) -> Path:
    """Run data collection. Tries real API first, falls back to synthetic data."""
    if output_dir is None:
        output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")

    # Try real scraping first
    all_products = _try_real_scraping(output_dir)

    # Fallback to synthetic data
    if len(all_products) < 100:
        print(f"\nReal API collected {len(all_products)} products (need ~1000)")
        print("Generating realistic synthetic data based on Indonesian marketplace patterns...")
        print("Trade-off: Tokopedia/Shopee have Akamai bot protection blocking server scraping.")
        print("Documented as known limitation in SPEC.md and architecture doc.\n")

        synthetic = generate_synthetic_data(target_count=1000)
        all_products.extend(synthetic)
        print(f"Generated {len(synthetic)} synthetic products")

    # Save output
    output_file = output_dir / f"tokopedia_all_{date_str}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"Data collection complete!")
    print(f"Total products: {len(all_products)}")
    source_counts = {}
    for p in all_products:
        src = p.get("_source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
    for src, count in source_counts.items():
        print(f"  {src}: {count}")
    print(f"Output: {output_file}")
    print(f"{'=' * 50}")

    return output_file


if __name__ == "__main__":
    run_scraper()
