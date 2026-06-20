"""LLM-based product spec extraction.

Uses an OpenAI-compatible API (SumoPod AI / DeepSeek) to extract
flavor, weight, and variant from Indonesian product names.

Why LLM over regex:
- Indonesian product names have inconsistent formats
- "Sapi Panggang" vs "Rasa Sapi" vs "Sapi Panggang 68g" — regex misses context
- LLM understands Indonesian language nuances
- Batch processing keeps cost low (~$0.01 for 672 products)

Trade-off:
- Adds API dependency and ~2 min runtime
- Results may vary with model updates
- But accuracy >> regex (estimated 90%+ vs 60%)
"""

import json
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

SYSTEM_PROMPT = """You are a product data extractor for Indonesian food & beverage products.
Given a product name, extract these fields:

1. flavor: The taste/flavor variant (e.g., "sapi panggang", "strawberry", "keju", "balado", "original", "matcha", "cokelat"). Use Indonesian if the product uses Indonesian. Empty string if not identifiable.

2. weight: The weight/netto/volume (e.g., "68g", "100gr", "250ml", "1kg"). Include the unit. Empty string if not identifiable.

3. variant: The size/type variant (e.g., "large", "pack", "box", "jumbo", "mini", "family", "ecer", "kiloan"). Empty string if not identifiable.

Rules:
- Return ONLY a JSON object, no explanation
- Use lowercase for flavor and variant
- Keep weight as-is from the product name (including unit)
- If multiple flavors exist, return the first one
- If the product is generic (no specific flavor/weight/variant), return empty strings
- Examples of Indonesian flavors: sapi panggang, ayam bakar, balado, keju, rumput laut, pedas, original

Return format: {"flavor": "...", "weight": "...", "variant": "..."}
"""

USER_PROMPT_TEMPLATE = 'Product name: "{name}"'


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------


def _call_llm(prompt: str, client: httpx.Client, base_url: str, api_key: str, model: str) -> dict | None:
    """Make a single LLM API call."""
    try:
        resp = client.post(
            f"{base_url}/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": 100,
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()

        # Parse JSON from response (handle markdown code blocks)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)
    except (json.JSONDecodeError, KeyError, httpx.HTTPStatusError, httpx.RequestError) as e:
        return None


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


def parse_products_with_llm(products: list[dict], batch_size: int = 20) -> list[dict]:
    """Parse flavor/weight/variant for a list of products using LLM.

    Args:
        products: List of product dicts with 'product_name' key
        batch_size: Number of products per API call (for efficiency)

    Returns:
        Same list with flavor/weight/variant fields updated
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("MODEL_NAME", "gpt-4o-mini")

    if not api_key or api_key == "your-api-key-here":
        print("WARNING: No LLM API key configured. Skipping LLM parsing.")
        print("  Set OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME in .env")
        return products

    print(f"LLM Parser: {len(products)} products, model={model}")
    print(f"  Base URL: {base_url}")

    # Process in batches for efficiency
    parsed = 0
    failed = 0

    with httpx.Client(timeout=60) as client:
        for i in range(0, len(products), batch_size):
            batch = products[i : i + batch_size]

            # Build batch prompt
            names = [p["product_name"] for p in batch]
            batch_prompt = "Extract flavor, weight, and variant from each product:\n\n"
            for j, name in enumerate(names):
                batch_prompt += f'{j + 1}. "{name}"\n'
            batch_prompt += (
                '\nReturn a JSON array of objects, one per product, in order:\n'
                '[{"flavor": "...", "weight": "...", "variant": "..."}, ...]\n'
                "Return ONLY the JSON array, no explanation."
            )

            try:
                resp = client.post(
                    f"{base_url}/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": batch_prompt},
                        ],
                        "temperature": 0,
                        "max_tokens": 2000,
                    },
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()

                # Parse JSON
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()

                results = json.loads(content)

                # Apply results
                for j, result in enumerate(results):
                    if i + j < len(products):
                        p = products[i + j]
                        # Only update if LLM found something (don't overwrite existing)
                        if result.get("flavor") and not p.get("flavor"):
                            p["flavor"] = result["flavor"]
                        if result.get("weight") and not p.get("weight"):
                            p["weight"] = result["weight"]
                        if result.get("variant") and not p.get("variant"):
                            p["variant"] = result["variant"]
                        parsed += 1

            except (json.JSONDecodeError, KeyError, httpx.HTTPStatusError, httpx.RequestError) as e:
                print(f"  Batch {i // batch_size + 1} failed: {e}")
                failed += len(batch)

            # Rate limit
            if i + batch_size < len(products):
                time.sleep(1)

    print(f"  Parsed: {parsed}, Failed: {failed}")
    return products


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    import csv

    csv_path = Path("data/cleaned/products_clean.csv")
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        exit(1)

    # Read CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        products = list(reader)

    print(f"Loaded {len(products)} products from {csv_path}")

    # Parse with LLM
    products = parse_products_with_llm(products)

    # Write back
    fieldnames = list(products[0].keys())
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

    # Stats
    flavor_filled = sum(1 for p in products if p.get("flavor"))
    weight_filled = sum(1 for p in products if p.get("weight"))
    variant_filled = sum(1 for p in products if p.get("variant"))
    print(f"\nUpdated {csv_path}")
    print(f"  flavor: {flavor_filled}/{len(products)} ({100 * flavor_filled // len(products)}%)")
    print(f"  weight: {weight_filled}/{len(products)} ({100 * weight_filled // len(products)}%)")
    print(f"  variant: {variant_filled}/{len(products)} ({100 * variant_filled // len(products)}%)")
