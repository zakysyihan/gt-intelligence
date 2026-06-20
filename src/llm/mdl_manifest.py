"""MDL (Modeling Definition Language) manifest for WrenAI.

Defines the semantic layer that maps business concepts to data columns.
This is the core of LLM grounding — the LLM never sees raw SQL,
only the business-meaningful model.

ponytail: This is a single dict construction. No abstractions, no
builder pattern, no config files. Just data.
"""

import base64

import orjson


def build_manifest() -> dict:
    """Build the MDL manifest for the products dataset."""
    return {
        "catalog": "gt_intelligence",
        "schema": "main",
        "dataSource": "DUCKDB",
        "models": [
            {
                "name": "products",
                "tableReference": {
                    "catalog": "gt_intelligence",
                    "schema": "main",
                    "table": "products",
                },
                "columns": [
                    {
                        "name": "timestamp",
                        "type": "varchar",
                        "expression": "timestamp",
                        "description": "When data was collected (ISO datetime)",
                    },
                    {
                        "name": "shop_location",
                        "type": "varchar",
                        "expression": "shop_location",
                        "description": "Seller city/province (Java Island only)",
                    },
                    {
                        "name": "product_name",
                        "type": "varchar",
                        "expression": "product_name",
                        "description": "Full product title from Tokopedia",
                    },
                    {
                        "name": "subcategory",
                        "type": "varchar",
                        "expression": "subcategory",
                        "description": "Product subcategory: chocolate, candy, or snacks",
                    },
                    {
                        "name": "price",
                        "type": "integer",
                        "expression": "price",
                        "description": "Price in IDR (Indonesian Rupiah)",
                    },
                    {
                        "name": "rating",
                        "type": "double",
                        "expression": "rating",
                        "description": "Average product rating (0-5 scale)",
                    },
                    {
                        "name": "sold_count",
                        "type": "integer",
                        "expression": "sold_count",
                        "description": "Monthly sales count — the primary demand signal",
                    },
                    {
                        "name": "review_count",
                        "type": "integer",
                        "expression": "review_count",
                        "description": "Number of customer reviews",
                    },
                    {
                        "name": "shop_name",
                        "type": "varchar",
                        "expression": "shop_name",
                        "description": "Seller/store name on Tokopedia",
                    },
                    {
                        "name": "shop_rating",
                        "type": "double",
                        "expression": "shop_rating",
                        "description": "Seller's overall rating",
                    },
                    {
                        "name": "product_url",
                        "type": "varchar",
                        "expression": "product_url",
                        "description": "Tokopedia product URL (for deduplication)",
                    },
                    {
                        "name": "flavor",
                        "type": "varchar",
                        "expression": "flavor",
                        "description": "Parsed from product_name (e.g., 'cokelat', 'keju', 'pedas')",
                    },
                    {
                        "name": "weight",
                        "type": "varchar",
                        "expression": "weight",
                        "description": "Parsed from product_name (e.g., '1kg', '250g')",
                    },
                    {
                        "name": "variant",
                        "type": "varchar",
                        "expression": "variant",
                        "description": "Parsed from product_name (e.g., 'large', 'pack', 'box')",
                    },
                    {
                        "name": "price_bucket",
                        "type": "varchar",
                        "expression": "price_bucket",
                        "description": "Computed: cheap (<15000), mid (15000-75000), expensive (>75000)",
                    },
                    {
                        "name": "rating_category",
                        "type": "varchar",
                        "expression": "rating_category",
                        "description": "Computed: low (<3.5), medium (3.5-4.5), high (>=4.5)",
                    },
                    # Calculated columns (virtual, computed at query time)
                    {
                        "name": "estimated_revenue",
                        "type": "double",
                        "expression": "price * sold_count",
                        "isCalculated": True,
                        "description": "Revenue proxy: price × sold_count (NOT actual profit)",
                    },
                ],
                "primaryKey": "product_url",
            }
        ],
        "views": [
            {
                "name": "top_products_by_demand",
                "statement": "SELECT product_name, subcategory, sold_count, price, shop_location FROM products ORDER BY sold_count DESC LIMIT 20",
                "description": "Top 20 products by monthly sales volume",
            },
            {
                "name": "subcategory_summary",
                "statement": "SELECT subcategory, COUNT(*) as product_count, SUM(sold_count) as total_sold, AVG(price) as avg_price, AVG(rating) as avg_rating FROM products GROUP BY subcategory ORDER BY total_sold DESC",
                "description": "Aggregated stats per subcategory",
            },
            {
                "name": "geographic_distribution",
                "statement": "SELECT shop_location, COUNT(*) as seller_count, SUM(sold_count) as total_sold, AVG(price) as avg_price FROM products GROUP BY shop_location ORDER BY seller_count DESC",
                "description": "Product distribution across Java Island cities",
            },
        ],
        "cubes": [
            {
                "name": "demand_analysis",
                "baseObject": "products",
                "description": "Demand and sales analysis",
                "measures": [
                    {"name": "total_sold", "expression": "SUM(sold_count)", "type": "integer"},
                    {"name": "avg_sold", "expression": "AVG(sold_count)", "type": "double"},
                    {"name": "product_count", "expression": "COUNT(*)", "type": "integer"},
                ],
                "dimensions": [
                    {"name": "subcategory", "expression": "subcategory", "type": "varchar"},
                    {"name": "shop_location", "expression": "shop_location", "type": "varchar"},
                    {"name": "price_bucket", "expression": "price_bucket", "type": "varchar"},
                ],
            },
            {
                "name": "revenue_analysis",
                "baseObject": "products",
                "description": "Revenue proxy analysis (price × demand)",
                "measures": [
                    {"name": "total_revenue", "expression": "SUM(price * sold_count)", "type": "double"},
                    {"name": "avg_price", "expression": "AVG(price)", "type": "double"},
                    {"name": "avg_revenue", "expression": "AVG(price * sold_count)", "type": "double"},
                ],
                "dimensions": [
                    {"name": "subcategory", "expression": "subcategory", "type": "varchar"},
                    {"name": "price_bucket", "expression": "price_bucket", "type": "varchar"},
                ],
            },
        ],
    }


def get_manifest_str() -> str:
    """Return base64-encoded MDL manifest string for WrenEngine."""
    manifest = build_manifest()
    return base64.b64encode(orjson.dumps(manifest)).decode()
