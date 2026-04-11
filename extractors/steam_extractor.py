"""
Steam Data Extractor — "The Platform Shift" Project
Covers: Steam Reviews API, App Details API, SteamSpy API
No API key required. Includes rate limiting + disk caching.

Usage:
    python steam_extractor.py --mode all          # extract everything
    python steam_extractor.py --mode reviews      # reviews only
    python steam_extractor.py --mode details      # app details + steamspy
    python steam_extractor.py --appid 1245620     # single title (Elden Ring)
    python steam_extractor.py --publisher sie     # one publisher
"""

import requests
import json
import time
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────
USE_CACHE = True   # Set False to force re-fetch all data

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "cache"
PROCESSED_DIR = DATA_DIR / "processed"

for d in [RAW_DIR / "reviews", RAW_DIR / "details", RAW_DIR / "steamspy",
          CACHE_DIR, PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DATA_DIR / "extraction.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Rate limits (be conservative to avoid bans)
STEAM_DELAY = 1.5       # seconds between Steam API calls
STEAMSPY_DELAY = 2.0    # SteamSpy is stricter
MAX_RETRIES = 3
CACHE_TTL_DAYS = 7      # re-fetch after 7 days


# ── Cache helpers ─────────────────────────────────────────────────
def cache_path(appid: int, data_type: str) -> Path:
    return CACHE_DIR / f"{appid}_{data_type}.json"

def load_cache(appid: int, data_type: str) -> dict | None:
    if not USE_CACHE:
        return None
    p = cache_path(appid, data_type)
    if not p.exists():
        return None
    age_days = (time.time() - p.stat().st_mtime) / 86400
    if age_days > CACHE_TTL_DAYS:
        return None
    with open(p) as f:
        return json.load(f)

def save_cache(appid: int, data_type: str, data: dict):
    with open(cache_path(appid, data_type), "w") as f:
        json.dump(data, f, ensure_ascii=False)


# ── HTTP helper ───────────────────────────────────────────────────
def get_with_retry(url: str, params: dict = None, delay: float = STEAM_DELAY) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 429:
                wait = 60 * (attempt + 1)
                log.warning(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            time.sleep(delay)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.error(f"Attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5 * (attempt + 1))
    return None


# ── App Details ───────────────────────────────────────────────────
def fetch_app_details(appid: int) -> dict | None:
    cached = load_cache(appid, "details")
    if cached:
        log.info(f"[{appid}] App details from cache")
        return cached

    log.info(f"[{appid}] Fetching app details...")
    url = "https://store.steampowered.com/api/appdetails"
    data = get_with_retry(url, params={"appids": appid, "cc": "us", "l": "en"})
    if not data or not data.get(str(appid), {}).get("success"):
        log.warning(f"[{appid}] App details returned no data")
        return None

    result = data[str(appid)]["data"]
    extracted = {
        "appid": appid,
        "name": result.get("name"),
        "type": result.get("type"),
        "short_description": result.get("short_description"),
        "release_date": result.get("release_date", {}).get("date"),
        "coming_soon": result.get("release_date", {}).get("coming_soon"),
        "developers": result.get("developers", []),
        "publishers": result.get("publishers", []),
        "genres": [g["description"] for g in result.get("genres", [])],
        "categories": [c["description"] for c in result.get("categories", [])],
        "price_usd": result.get("price_overview", {}).get("final", 0) / 100 if result.get("price_overview") else None,
        "price_formatted": result.get("price_overview", {}).get("final_formatted"),
        "metacritic_score": result.get("metacritic", {}).get("score"),
        "metacritic_url": result.get("metacritic", {}).get("url"),
        "recommendations": result.get("recommendations", {}).get("total"),
        "supported_languages": result.get("supported_languages"),
        "platforms": result.get("platforms", {}),
        "extracted_at": datetime.utcnow().isoformat(),
    }
    save_cache(appid, "details", extracted)

    out_path = RAW_DIR / "details" / f"{appid}.json"
    with open(out_path, "w") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)
    return extracted


# ── SteamSpy ──────────────────────────────────────────────────────
def fetch_steamspy(appid: int) -> dict | None:
    cached = load_cache(appid, "steamspy")
    if cached:
        log.info(f"[{appid}] SteamSpy from cache")
        return cached

    log.info(f"[{appid}] Fetching SteamSpy data...")
    url = "https://steamspy.com/api.php"
    data = get_with_retry(url, params={"request": "appdetails", "appid": appid}, delay=STEAMSPY_DELAY)
    if not data:
        return None

    extracted = {
        "appid": appid,
        "name": data.get("name"),
        "owners_range": data.get("owners"),          # e.g. "2,000,000 .. 5,000,000"
        "owners_lower": parse_owners(data.get("owners", ""))[0],
        "owners_upper": parse_owners(data.get("owners", ""))[1],
        "positive": data.get("positive"),
        "negative": data.get("negative"),
        "average_forever": data.get("average_forever"),   # minutes, all time
        "average_2weeks": data.get("average_2weeks"),     # minutes, last 2 weeks
        "median_forever": data.get("median_forever"),
        "median_2weeks": data.get("median_2weeks"),
        "ccu": data.get("ccu"),                           # peak CCU (last 24h from SteamSpy)
        "price": data.get("price"),
        "initialprice": data.get("initialprice"),
        "discount": data.get("discount"),
        "tags": data.get("tags", {}),
        "extracted_at": datetime.utcnow().isoformat(),
    }
    save_cache(appid, "steamspy", extracted)

    out_path = RAW_DIR / "steamspy" / f"{appid}.json"
    with open(out_path, "w") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)
    return extracted

def parse_owners(owners_str: str) -> tuple[int, int]:
    """Parse '2,000,000 .. 5,000,000' → (2000000, 5000000)"""
    try:
        parts = owners_str.replace(",", "").split("..")
        return int(parts[0].strip()), int(parts[1].strip())
    except Exception:
        return 0, 0


# ── Steam Reviews ─────────────────────────────────────────────────
def fetch_reviews(
    appid: int,
    max_reviews: int = 2000,
    language: str = "all",
    force_refresh: bool = False
) -> list[dict]:
    """
    Paginate through Steam Reviews API using cursor.
    Returns list of review dicts.
    """
    out_path = RAW_DIR / "reviews" / f"{appid}.json"

    # Check if we already have enough reviews
    if USE_CACHE and not force_refresh and out_path.exists():
        with open(out_path) as f:
            existing = json.load(f)
        if len(existing.get("reviews", [])) >= max_reviews:
            log.info(f"[{appid}] Reviews already cached ({len(existing['reviews'])} reviews)")
            return existing["reviews"]

    log.info(f"[{appid}] Fetching up to {max_reviews} reviews (lang={language})...")
    url = f"https://store.steampowered.com/appreviews/{appid}"

    all_reviews = []
    cursor = "*"
    page = 0

    while len(all_reviews) < max_reviews:
        params = {
            "json": 1,
            "language": language,
            "purchase_type": "all",
            "num_per_page": 100,
            "cursor": cursor,
            "filter": "recent",     # 'recent' or 'updated' — use 'all' for full history
            "review_type": "all",
        }

        data = get_with_retry(url, params=params)
        if not data or data.get("success") != 1:
            log.error(f"[{appid}] Reviews API error on page {page}")
            break

        batch = data.get("reviews", [])
        if not batch:
            log.info(f"[{appid}] No more reviews at page {page}")
            break

        # Parse each review
        for r in batch:
            all_reviews.append({
                "recommendationid": r.get("recommendationid"),
                "author_steamid": r.get("author", {}).get("steamid"),
                "author_playtime_forever": r.get("author", {}).get("playtime_forever"),  # minutes
                "author_playtime_at_review": r.get("author", {}).get("playtime_at_review"),
                "author_num_reviews": r.get("author", {}).get("num_reviews"),
                "voted_up": r.get("voted_up"),
                "votes_up": r.get("votes_up"),
                "votes_funny": r.get("votes_funny"),
                "weighted_vote_score": r.get("weighted_vote_score"),
                "timestamp_created": r.get("timestamp_created"),
                "timestamp_updated": r.get("timestamp_updated"),
                "review_text": r.get("review", ""),
                "language": r.get("language"),
                "written_during_early_access": r.get("written_during_early_access"),
                "received_for_free": r.get("received_for_free"),
            })

        new_cursor = data.get("cursor", "")
        if not new_cursor or new_cursor == cursor:
            log.info(f"[{appid}] Cursor exhausted at {len(all_reviews)} reviews")
            break
        cursor = new_cursor
        page += 1
        log.info(f"[{appid}] Page {page}: {len(all_reviews)} reviews collected")

    # Save
    output = {
        "appid": appid,
        "extracted_at": datetime.utcnow().isoformat(),
        "total_collected": len(all_reviews),
        "query_summary": data.get("query_summary", {}) if data else {},
        "reviews": all_reviews,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    log.info(f"[{appid}] Saved {len(all_reviews)} reviews → {out_path}")
    return all_reviews


# ── Batch extraction ──────────────────────────────────────────────
def extract_all(
    game_registry: dict,
    publisher_filter: str = None,
    modes: list = ["details", "steamspy", "reviews"],
    max_reviews_per_game: int = 1000,
):
    from ThePlatformShift_ADeepDive.extractors.game_registry import get_all_titles
    titles = get_all_titles()

    if publisher_filter:
        from ThePlatformShift_ADeepDive.extractors.game_registry import GAME_REGISTRY
        filtered_ids = {
            meta["appid"]
            for meta in GAME_REGISTRY.get(publisher_filter, {}).values()
            if meta.get("appid")
        }
        titles = {k: v for k, v in titles.items() if k in filtered_ids}

    log.info(f"Starting extraction: {len(titles)} titles, modes={modes}")
    results = {"details": {}, "steamspy": {}, "reviews": {}}

    for appid, info in titles.items():
        log.info(f"\n{'='*50}")
        log.info(f"Processing: {info['title']} (AppID: {appid})")

        if "details" in modes:
            results["details"][appid] = fetch_app_details(appid)

        if "steamspy" in modes:
            results["steamspy"][appid] = fetch_steamspy(appid)

        if "reviews" in modes:
            results["reviews"][appid] = fetch_reviews(appid, max_reviews=max_reviews_per_game)

    return results


# ── CLI ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    parser = argparse.ArgumentParser(description="Steam data extractor for The Platform Shift")
    parser.add_argument("--mode", choices=["all", "reviews", "details", "steamspy"], default="details")
    parser.add_argument("--appid", type=int, help="Single AppID to extract")
    parser.add_argument("--publisher", type=str, help="Filter by publisher key (e.g. 'sie', 'bandai_namco')")
    parser.add_argument("--max-reviews", type=int, default=1000, help="Max reviews per game")
    parser.add_argument("--force", action="store_true", help="Force re-fetch ignoring cache")
    args = parser.parse_args()

    modes = {
        "all": ["details", "steamspy", "reviews"],
        "reviews": ["reviews"],
        "details": ["details", "steamspy"],
        "steamspy": ["steamspy"],
    }[args.mode]

    if args.appid:
        log.info(f"Single AppID mode: {args.appid}")
        if "details" in modes:
            print(json.dumps(fetch_app_details(args.appid), indent=2))
        if "steamspy" in modes:
            print(json.dumps(fetch_steamspy(args.appid), indent=2))
        if "reviews" in modes:
            reviews = fetch_reviews(args.appid, max_reviews=args.max_reviews, force_refresh=args.force)
            print(f"Collected {len(reviews)} reviews")
    else:
        from ThePlatformShift_ADeepDive.extractors.game_registry import GAME_REGISTRY
        extract_all(GAME_REGISTRY, publisher_filter=args.publisher, modes=modes, max_reviews_per_game=args.max_reviews)
