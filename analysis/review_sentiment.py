"""
Review Sentiment Analyzer — Chapter 3: What Players Actually Think

Key analyses:
1. Launch quality score (first 30 days vs steady state)
2. Playtime-to-positive correlation
3. PC port quality decay/recovery pattern
4. Language distribution (regional demand proxy)
5. Review velocity (launch momentum)

Requires: pip install pandas textblob langdetect matplotlib seaborn
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import warnings
warnings.filterwarnings("ignore")
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

USE_CACHE = True  # Set False to force reprocess

# ── Japanese font setup (matches Masstige Moment standard) ────────
def get_jp_font():
    candidates = ["MS Gothic", "Yu Gothic", "Meiryo", "IPAGothic"]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            return font
    return None

JP_FONT = get_jp_font()
if JP_FONT:
    plt.rcParams["font.family"] = JP_FONT

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_REVIEWS_DIR = DATA_DIR / "raw" / "reviews"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


# ── Load reviews ──────────────────────────────────────────────────
def load_reviews(appid: int) -> pd.DataFrame:
    path = RAW_REVIEWS_DIR / f"{appid}.json"
    if not path.exists():
        raise FileNotFoundError(f"No reviews found for appid {appid}. Run steam_extractor.py first.")

    with open(path) as f:
        data = json.load(f)

    df = pd.DataFrame(data["reviews"])
    df["appid"] = appid

    # Parse timestamps
    df["date"] = pd.to_datetime(df["timestamp_created"], unit="s", utc=True)
    df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
    df["year_month"] = df["date"].dt.to_period("M")

    # Playtime in hours
    df["playtime_at_review_hrs"] = df["author_playtime_at_review"].fillna(0) / 60
    df["playtime_total_hrs"] = df["author_playtime_forever"].fillna(0) / 60

    return df


# ── Core metrics ──────────────────────────────────────────────────
def compute_launch_quality(df: pd.DataFrame, release_date_str: str, window_days: int = 30) -> dict:
    """
    Launch quality = positive rate in first N days vs steady state.
    A big drop signals PC port issues (e.g. TLOU Part I).
    """
    release_date = pd.Timestamp(release_date_str, tz="UTC")
    cutoff = release_date + pd.Timedelta(days=window_days)

    launch = df[df["date"] <= cutoff]
    post_launch = df[df["date"] > cutoff]

    def positive_rate(subset):
        if len(subset) == 0:
            return None
        return subset["voted_up"].mean()

    launch_score = positive_rate(launch)
    post_score = positive_rate(post_launch)

    delta = None
    if launch_score is not None and post_score is not None:
        delta = post_score - launch_score  # positive = improved after launch

    return {
        "launch_n": len(launch),
        "post_launch_n": len(post_launch),
        "launch_positive_rate": round(launch_score, 4) if launch_score else None,
        "post_launch_positive_rate": round(post_score, 4) if post_score else None,
        "delta_post_minus_launch": round(delta, 4) if delta else None,
        "port_quality_flag": "POOR_LAUNCH" if (delta and delta > 0.05) else
                             "STRONG_LAUNCH" if (delta and delta < -0.02) else "STABLE",
    }


def compute_playtime_sentiment_correlation(df: pd.DataFrame) -> dict:
    """
    Does more playtime = more positive reviews?
    High correlation suggests players who invest time become advocates.
    Low/negative suggests burnout (common in live service games).
    """
    # Cap outliers at 99th percentile for cleaner correlation
    cap = df["playtime_at_review_hrs"].quantile(0.99)
    filtered = df[df["playtime_at_review_hrs"] <= cap].copy()

    corr = filtered["playtime_at_review_hrs"].corr(filtered["voted_up"].astype(float))

    # Playtime buckets
    bins = [0, 1, 5, 20, 50, 100, float("inf")]
    labels = ["<1h", "1-5h", "5-20h", "20-50h", "50-100h", "100h+"]
    filtered["playtime_bucket"] = pd.cut(filtered["playtime_at_review_hrs"], bins=bins, labels=labels)
    bucket_stats = filtered.groupby("playtime_bucket", observed=True)["voted_up"].agg(
        positive_rate="mean", count="count"
    ).round(4).to_dict()

    return {
        "playtime_sentiment_corr": round(corr, 4) if not np.isnan(corr) else None,
        "interpretation": (
            "Advocates grow with investment" if corr > 0.15 else
            "Burnout risk" if corr < -0.1 else
            "Weak relationship"
        ),
        "bucket_stats": bucket_stats,
    }


def compute_language_distribution(df: pd.DataFrame) -> dict:
    """Language field from Steam = regional demand proxy (not perfect but directional)."""
    lang_counts = df["language"].value_counts()
    lang_pct = (lang_counts / len(df) * 100).round(2)

    top_10 = lang_pct.head(10).to_dict()

    # Regional aggregation
    english_regions = ["english"]
    japanese = ["japanese"]
    cjk = ["japanese", "schinese", "tchinese", "koreana"]
    european = ["german", "french", "spanish", "italian", "portuguese", "russian"]

    return {
        "total_reviews": len(df),
        "unique_languages": lang_counts.shape[0],
        "top_10_pct": top_10,
        "english_pct": lang_pct.get("english", 0),
        "japanese_pct": lang_pct.get("japanese", 0),
        "cjk_combined_pct": sum(lang_pct.get(l, 0) for l in cjk),
        "western_pct": sum(lang_pct.get(l, 0) for l in english_regions + european),
    }


def compute_review_velocity(df: pd.DataFrame) -> pd.DataFrame:
    """Daily review count — shows launch spike, content update bumps, sale spikes."""
    velocity = df.groupby("date_str").agg(
        total_reviews=("recommendationid", "count"),
        positive_reviews=("voted_up", "sum"),
    ).reset_index()
    velocity["negative_reviews"] = velocity["total_reviews"] - velocity["positive_reviews"]
    velocity["daily_positive_rate"] = (velocity["positive_reviews"] / velocity["total_reviews"]).round(4)
    return velocity.sort_values("date_str")


# ── Full analysis for one title ────────────────────────────────────
def analyze_title(appid: int, title_info: dict) -> dict:
    """
    Run all analyses for a single title.
    title_info should have: title, publisher, release_pc
    """
    print(f"\nAnalyzing: {title_info['title']} ({appid})")

    try:
        df = load_reviews(appid)
    except FileNotFoundError as e:
        print(f"  SKIP: {e}")
        return {"appid": appid, "error": str(e)}

    print(f"  Loaded {len(df)} reviews")

    release_date = title_info.get("release_pc", "2022-01-01")

    result = {
        "appid": appid,
        "title": title_info["title"],
        "publisher": title_info["publisher"],
        "release_pc": release_date,
        "total_reviews_in_sample": len(df),
        "overall_positive_rate": round(df["voted_up"].mean(), 4),
        "median_playtime_at_review_hrs": round(df["playtime_at_review_hrs"].median(), 1),
        "mean_playtime_at_review_hrs": round(df["playtime_at_review_hrs"].mean(), 1),
        "launch_quality": compute_launch_quality(df, release_date),
        "playtime_sentiment": compute_playtime_sentiment_correlation(df),
        "language_distribution": compute_language_distribution(df),
        "analyzed_at": datetime.utcnow().isoformat(),
    }

    # Save processed result
    out_path = PROCESSED_DIR / f"{appid}_analysis.json"

    # USE_CACHE: skip reprocessing if output already exists
    if USE_CACHE and out_path.exists():
        print(f"  Cached result found → {out_path}")
        with open(out_path) as f:
            return json.load(f)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save velocity data separately (for time series viz)
    velocity = compute_review_velocity(df)
    velocity_path = PROCESSED_DIR / f"{appid}_velocity.csv"
    velocity.to_csv(velocity_path, index=False)

    # ── Dynamic observation block (f-string from live data) ───────
    lq = result["launch_quality"]
    ps = result["playtime_sentiment"]
    ld = result["language_distribution"]
    print(
        f"  [{result['title']}] "
        f"n={result['total_reviews_in_sample']:,} | "
        f"positive={result['overall_positive_rate']*100:.1f}% | "
        f"launch_flag={lq['port_quality_flag']} | "
        f"playtime_corr={ps['playtime_sentiment_corr']} ({ps['interpretation']}) | "
        f"JP={ld['japanese_pct']:.1f}% CJK={ld['cjk_combined_pct']:.1f}%"
    )
    print(f"  Saved → {out_path}")

    return result


def analyze_all_available():
    """Run analysis on all downloaded review files."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "extractors"))
    from ThePlatformShift_ADeepDive.extractors.game_registry import get_all_titles

    titles = get_all_titles()
    available = [p.stem for p in RAW_REVIEWS_DIR.glob("*.json")]
    available_ids = {int(x) for x in available if x.isdigit()}

    results = []
    for appid, info in titles.items():
        if appid in available_ids:
            result = analyze_title(appid, info)
            results.append(result)

    # Master summary
    summary_df = pd.DataFrame([
        {k: v for k, v in r.items() if not isinstance(v, (dict, list))}
        for r in results if "error" not in r
    ])
    summary_path = PROCESSED_DIR / "all_titles_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"\nSummary saved → {summary_path}")
    return results


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "extractors"))

    if len(sys.argv) > 1:
        appid = int(sys.argv[1])
        from ThePlatformShift_ADeepDive.extractors.game_registry import get_all_titles
        titles = get_all_titles()
        info = titles.get(appid, {"title": f"AppID {appid}", "publisher": "unknown", "release_pc": "2022-01-01"})
        analyze_title(appid, info)
    else:
        analyze_all_available()
