"""
Google Trends integration for Indonesian food keywords.

Fetches search interest data via pytrends (Google Trends unofficial API)
and caches results locally to avoid rate limits.

Caching strategy:
- Results written to data/trends_cache.json with a timestamp.
- TTL is 24 hours: if the cache file exists and is fresh, skip fetching.
- If pytrends fails (rate limit, network), return stale cache rather than None.
- If pytrends is not installed at all, return None gracefully.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# -----------

KEYWORDS = [
    "snack Indonesia",
    "cokelat Indonesia",
    "permen Indonesia",
    "makanan ringan",
]

CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "trends_cache.json"
CACHE_TTL_HOURS = 24
FETCH_DELAY_S = 1          # seconds between keyword fetches
RETRY_WAIT_S = 60           # seconds to wait on 429 before retry

# -------------- internal helpers --------------

def _load_cache() -> dict | None:
    """Return cached data if the file exists, else None."""
    if not CACHE_PATH.exists():
        return None
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _cache_is_fresh(cache: dict) -> bool:
    """Return True if cache was written within the last CACHE_TTL_HOURS."""
    ts = cache.get("fetched_at")
    if not ts:
        return False
    try:
        fetched = datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return False
    return datetime.now() - fetched < timedelta(hours=CACHE_TTL_HOURS)


def _save_cache(data: dict) -> None:
    """Write *data* (including a fetched_at timestamp) to the cache file."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now().isoformat(),
        "data": data,
    }
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[trends] Cache saved to {CACHE_PATH}")


def _fetch_keyword(pytrends, keyword: str) -> list[dict]:
    """Fetch interest-over-time for a single keyword.

    Returns a list of ``{"date": "YYYY-MM-DD", "interest": int}`` dicts.
    Handles rate limiting (429) with a single retry after a wait.
    """
    from pytrends.exceptions import ResponseError

    for attempt in (1, 2):
        try:
            pytrends.build_payload(
                kw_list=[keyword],
                timeframe="today 12-m",
                geo="",  # worldwide (filters by keyword mentioning Indonesia)
            )
            df = pytrends.interest_over_time()

            if df.empty:
                print(f"[trends] No data for '{keyword}'")
                return []

            series = df[keyword]
            return [
                {"date": ts.strftime("%Y-%m-%d"), "interest": int(val)}
                for ts, val in series.items()
            ]

        except ResponseError as exc:
            if exc.response.status_code == 429 and attempt == 1:
                print(f"[trends] 429 rate limit on '{keyword}', waiting {RETRY_WAIT_S}s …")
                time.sleep(RETRY_WAIT_S)
                continue
            print(f"[trends] Error fetching '{keyword}': {exc}")
            return []
        except Exception as exc:
            print(f"[trends] Unexpected error fetching '{keyword}': {exc}")
            return []

    return []

# -------------- public API --------------

def get_trends_data() -> dict | None:
    """Return Google Trends interest-over-time for Indonesian food keywords.

    Returns
    -------
    dict or None
        ``{keyword: [{"date": "YYYY-MM-DD", "interest": int}, …]}``
        Returns ``None`` when pytrends is unavailable or all fetches fail.

    Behaviour
    ---------
    1. If a fresh cache (< 24 h) exists, return it immediately.
    2. Otherwise, fetch each keyword one-by-one (with delays to respect
       the ~10 req/min rate limit).
    3. If a fetch fails, fall back to whatever was cached (even if stale).
    4. If everything fails and there is no cache at all, return None.
    """
    # ---- check cache first ----
    cache = _load_cache()
    if cache and _cache_is_fresh(cache):
        print("[trends] Returning fresh cached data")
        return cache["data"]

    # ---- attempt live fetch ----
    try:
        from pytrends.request import TrendReq  # noqa: F811
    except ImportError:
        print("[trends] pytrends not installed — returning cached data if available")
        return cache["data"] if cache else None

    print("[trends] Fetching live data from Google Trends …")
    pytrends = TrendReq(hl="en-US", tz=480)  # WIB (UTC+7, approx)
    result: dict[str, list[dict]] = {}

    for i, kw in enumerate(KEYWORDS):
        if i > 0:
            time.sleep(FETCH_DELAY_S)
        result[kw] = _fetch_keyword(pytrends, kw)

    # ---- decide what to return ----
    any_has_data = any(len(v) > 0 for v in result.values())
    if any_has_data:
        _save_cache(result)
        return result

    print("[trends] All fetches returned empty — falling back to cache")
    return cache["data"] if cache else None


if __name__ == "__main__":
    data = get_trends_data()
    if data:
        for kw, points in data.items():
            print(f"\n{kw}: {len(points)} data points")
            for p in points[:3]:
                print(f"  {p['date']}: {p['interest']}")
    else:
        print("No trends data available")
