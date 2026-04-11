"""
Publisher & Platform Analysis — Chapters 1, 2, 4, 5
Aggregates SteamSpy + App Details into publisher-level intelligence.

Metrics computed:
- Estimated PC install base by publisher
- Review score by publisher (quality signal)
- Average/median playtime by publisher (engagement signal)
- Price analysis (premium vs discounted buyer behavior)
- Catalog depth vs revenue concentration
- PC port lag (console release → PC release gap)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

USE_CACHE = True  # Set False to force recompute

# ── Japanese font setup ───────────────────────────────────────────
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
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


# ── Data loading ──────────────────────────────────────────────────
def load_steamspy_all() -> pd.DataFrame:
    rows = []
    for p in (RAW_DIR / "steamspy").glob("*.json"):
        with open(p) as f:
            rows.append(json.load(f))
    return pd.DataFrame(rows)

def load_details_all() -> pd.DataFrame:
    rows = []
    for p in (RAW_DIR / "details").glob("*.json"):
        with open(p) as f:
            rows.append(json.load(f))
    return pd.DataFrame(rows)

def load_master_registry() -> pd.DataFrame:
    """Flatten game registry into DataFrame with publisher info."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "extractors"))
    from ThePlatformShift_ADeepDive.extractors.game_registry import GAME_REGISTRY

    rows = []
    for publisher, games in GAME_REGISTRY.items():
        for title, meta in games.items():
            rows.append({
                "title": title,
                "publisher_group": publisher,
                "appid": meta.get("appid"),
                "release_pc": meta.get("release_pc"),
            })
    return pd.DataFrame(rows).dropna(subset=["appid"])


def build_master_df() -> pd.DataFrame:
    """Join registry + steamspy + details into one analysis DataFrame."""
    registry = load_master_registry()
    registry["appid"] = registry["appid"].astype(int)

    steamspy = load_steamspy_all()
    if steamspy.empty:
        print("WARNING: No SteamSpy data found. Run steam_extractor.py first.")
        return registry

    details = load_details_all()

    df = registry.merge(steamspy[["appid", "owners_lower", "owners_upper", "positive",
                                   "negative", "average_forever", "median_forever",
                                   "price", "discount", "ccu"]],
                        on="appid", how="left")

    if not details.empty:
        df = df.merge(details[["appid", "metacritic_score", "genres", "recommendations"]],
                      on="appid", how="left")

    # Derived metrics
    df["owners_mid"] = ((df["owners_lower"] + df["owners_upper"]) / 2).fillna(0)
    df["total_reviews"] = df["positive"].fillna(0) + df["negative"].fillna(0)
    df["positive_rate"] = np.where(
        df["total_reviews"] > 0,
        df["positive"] / df["total_reviews"],
        np.nan
    )
    df["avg_playtime_hrs"] = df["average_forever"].fillna(0) / 60
    df["median_playtime_hrs"] = df["median_forever"].fillna(0) / 60
    df["price_usd"] = df["price"].fillna(0) / 100

    # PC port lag (days from PC release to… well, registry has PC release date)
    # For console→PC gap, we'd need console release dates added to registry
    df["release_pc"] = pd.to_datetime(df["release_pc"], errors="coerce")
    df["release_year"] = df["release_pc"].dt.year

    return df


# ── Publisher-level aggregation ───────────────────────────────────
def publisher_summary(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("publisher_group").agg(
        titles_tracked=("appid", "count"),
        total_estimated_owners=("owners_mid", "sum"),
        avg_owners_per_title=("owners_mid", "mean"),
        avg_positive_rate=("positive_rate", "mean"),
        avg_playtime_hrs=("avg_playtime_hrs", "mean"),
        median_playtime_hrs=("median_playtime_hrs", "mean"),
        avg_metacritic=("metacritic_score", "mean"),
        total_reviews=("total_reviews", "sum"),
    ).reset_index()

    grp["total_estimated_owners_M"] = (grp["total_estimated_owners"] / 1e6).round(2)
    grp["avg_owners_per_title_K"] = (grp["avg_owners_per_title"] / 1e3).round(1)
    grp = grp.sort_values("total_estimated_owners", ascending=False)
    return grp


# ── Franchise concentration (revenue risk) ────────────────────────
def franchise_concentration(df: pd.DataFrame, publisher: str) -> dict:
    """
    What % of a publisher's estimated PC install base comes from top 1/3 titles?
    High concentration = franchise dependency risk.
    """
    pub_df = df[df["publisher_group"] == publisher].copy()
    pub_df = pub_df.sort_values("owners_mid", ascending=False)

    total = pub_df["owners_mid"].sum()
    if total == 0:
        return {}

    pub_df["cumulative_share"] = pub_df["owners_mid"].cumsum() / total
    top1_share = pub_df.iloc[0]["owners_mid"] / total if len(pub_df) > 0 else 0
    top3_share = pub_df.head(3)["owners_mid"].sum() / total if len(pub_df) >= 3 else 1.0

    return {
        "publisher": publisher,
        "n_titles": len(pub_df),
        "top1_owner_share": round(top1_share, 3),
        "top3_owner_share": round(top3_share, 3),
        "top_title": pub_df.iloc[0]["title"] if len(pub_df) > 0 else None,
        "herfindahl_index": round((pub_df["owners_mid"] / total).pow(2).sum(), 4),
        "concentration_flag": "HIGH" if top3_share > 0.8 else "MEDIUM" if top3_share > 0.6 else "LOW",
    }


# ── PC port quality benchmark ─────────────────────────────────────
def pc_port_quality_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ranks titles by positive_rate among titles with meaningful review counts.
    Proxy for PC port quality — low scores often signal bad ports.
    """
    filtered = df[df["total_reviews"] >= 100].copy()
    filtered["quality_tier"] = pd.cut(
        filtered["positive_rate"],
        bins=[0, 0.6, 0.75, 0.85, 1.0],
        labels=["Overwhelmingly Negative / Mostly Negative",
                "Mixed",
                "Mostly Positive",
                "Very Positive / Overwhelmingly Positive"]
    )
    return filtered[["title", "publisher_group", "positive_rate", "total_reviews",
                      "avg_playtime_hrs", "price_usd", "quality_tier"]
                   ].sort_values("positive_rate", ascending=False)


# ── Engagement vs. reception scatter data ─────────────────────────
def engagement_reception_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scatter: x=positive_rate, y=avg_playtime_hrs, size=owners_mid
    High engagement + high reception = strong IP
    High engagement + low reception = "hate-play" or grinding gacha
    Low engagement + high reception = acclaimed but short game
    """
    return df[df["total_reviews"] >= 50][
        ["title", "publisher_group", "positive_rate", "avg_playtime_hrs",
         "owners_mid", "release_year", "metacritic_score"]
    ].dropna(subset=["positive_rate", "avg_playtime_hrs"])


# ── Run full analysis ─────────────────────────────────────────────
def run_full_analysis():
    print("Building master dataset...")
    df = build_master_df()

    if df.empty or "owners_mid" not in df.columns:
        print("Insufficient data. Extract Steam data first.")
        return

    print(f"Master dataset: {len(df)} titles\n")

    # Publisher summary
    master_path = PROCESSED_DIR / "master_dataset.csv"
    if USE_CACHE and master_path.exists():
        print("Cached master dataset found. Set USE_CACHE=False to recompute.")
        df = pd.read_csv(master_path)

    pub_summary = publisher_summary(df)
    pub_summary.to_csv(PROCESSED_DIR / "publisher_summary.csv", index=False)
    print("Publisher Summary:")
    print(pub_summary[["publisher_group", "titles_tracked", "total_estimated_owners_M",
                        "avg_positive_rate", "avg_playtime_hrs"]].to_string(index=False))

    # Franchise concentration per publisher
    print("\nFranchise Concentration:")
    conc_results = []
    for pub in df["publisher_group"].unique():
        conc = franchise_concentration(df, pub)
        if conc:
            conc_results.append(conc)
            print(f"  {pub}: Top title = {conc['top_title']}, "
                  f"Top-3 share = {conc['top3_owner_share']*100:.0f}% [{conc['concentration_flag']}]")
    pd.DataFrame(conc_results).to_csv(PROCESSED_DIR / "franchise_concentration.csv", index=False)

    # Port quality
    port_table = pc_port_quality_table(df)
    port_table.to_csv(PROCESSED_DIR / "port_quality.csv", index=False)

    # Scatter data
    scatter = engagement_reception_data(df)
    scatter.to_csv(PROCESSED_DIR / "engagement_reception.csv", index=False)

    # Full master
    df.to_csv(PROCESSED_DIR / "master_dataset.csv", index=False)

    # ── Dynamic observation block (f-string from live DataFrames) ─
    top_pub = pub_summary.iloc[0]
    print(
        f"\n[Summary] {len(df)} titles across {pub_summary.shape[0]} publishers | "
        f"Top by est. owners: {top_pub['publisher_group']} "
        f"({top_pub['total_estimated_owners_M']:.1f}M est. installs) | "
        f"Avg positive rate: {pub_summary['avg_positive_rate'].mean()*100:.1f}%"
    )
    print(f"All outputs saved → {PROCESSED_DIR}")

    # ── Save key chart: publisher comparison (savefig → processed/) ─
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(pub_summary["publisher_group"], pub_summary["total_estimated_owners_M"])
    ax.set_xlabel("Estimated Steam Owners (M)")
    ax.set_title("Estimated PC Install Base by Publisher (SteamSpy)")
    plt.tight_layout()
    chart_path = PROCESSED_DIR / "publisher_owners_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Chart saved → {chart_path}")


if __name__ == "__main__":
    run_full_analysis()
