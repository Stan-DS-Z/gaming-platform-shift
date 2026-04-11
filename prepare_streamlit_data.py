"""
prepare_streamlit_data.py
─────────────────────────────────────────────────────────────────────
Pre-Streamlit data preparation script.
Run once from the project root after all notebooks are complete.

Tasks
-----
1. Pre-aggregate NB04_vader_scores.csv (19.6 MB) → title-level summary
   Output: data/processed/NB04_vader_title_summary.csv

2. Join VADER summary into NB03_port_timeline.csv
   Fills oc_score + positive_rate placeholders.
   Output: data/processed/NB03_port_timeline.csv (updated in-place)

3. Aggregate PC-specific reception rate from NB04_claude_themes.csv
   cl_pc_specific column: 'mentioned' | 'not_mentioned'
   Output: data/processed/NB04_pc_specific_summary.csv

4. Enrich franchise fatigue with console→PC gap data
   Join NB05_franchise_fatigue.csv + NB03_port_timeline.csv on title
   Output: data/processed/NB05_franchise_fatigue_enriched.csv

Usage
-----
    cd /path/to/platform_shift
    python prepare_streamlit_data.py

    # Dry-run (prints output, does not write):
    python prepare_streamlit_data.py --dry-run

Inputs expected
---------------
    data/processed/NB03_port_timeline.csv          <- title-level with gap data
    data/processed/NB04_vader_scores.csv           <- full review-level scores
    data/processed/NB04_claude_themes.csv          <- Claude API theme extraction
    data/processed/NB05_franchise_fatigue.csv      <- franchise arc data

Hard rules
----------
    USE_CACHE = True  -- skip task if output already exists
    No hardcoded paths -- all paths derived from PROJECT_ROOT
    All outputs -> data/processed/
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# ── Config ─────────────────────────────────────────────────────────
USE_CACHE    = True
PROJECT_ROOT = Path(__file__).resolve().parent
PROCESSED    = PROJECT_ROOT / "data" / "processed"

# Inputs
INPUT_VADER         = PROCESSED / "NB04_vader_scores.csv"
INPUT_TIMELINE      = PROCESSED / "NB03_port_timeline.csv"
INPUT_CLAUDE_THEMES = PROCESSED / "NB04_claude_themes.csv"
INPUT_FATIGUE       = PROCESSED / "NB05_franchise_fatigue.csv"

# Outputs
OUTPUT_VADER_SUMMARY  = PROCESSED / "NB04_vader_title_summary.csv"
OUTPUT_TIMELINE       = PROCESSED / "NB03_port_timeline.csv"
OUTPUT_PC_SPECIFIC    = PROCESSED / "NB04_pc_specific_summary.csv"
OUTPUT_FATIGUE_ENRICH = PROCESSED / "NB05_franchise_fatigue_enriched.csv"

# ── CLI ────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Streamlit data prep")
parser.add_argument("--dry-run", action="store_true",
                    help="Print outputs without writing files")
args = parser.parse_args()

DRY_RUN = args.dry_run
if DRY_RUN:
    print("── DRY RUN mode -- no files will be written ──\n")


# ══════════════════════════════════════════════════════════════════
# TASK 1 -- Pre-aggregate VADER scores to title level
# ══════════════════════════════════════════════════════════════════
print("Task 1: NB04 VADER pre-aggregation")
print("-" * 50)

if USE_CACHE and OUTPUT_VADER_SUMMARY.exists():
    print(f"  Cache hit: {OUTPUT_VADER_SUMMARY.name} -- loading")
    vader_summary = pd.read_csv(OUTPUT_VADER_SUMMARY)
    print(f"  Rows loaded: {len(vader_summary)}")
else:
    if not INPUT_VADER.exists():
        print(f"  ERROR: {INPUT_VADER} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"  Loading {INPUT_VADER.name}...")
    vader_raw = pd.read_csv(INPUT_VADER, usecols=lambda c: c in
                            ["appid", "compound", "vader_compound", "pos", "vader_pos", "positive"])

    col_map = {}
    for expected, fallbacks in [
        ("compound", ["compound", "vader_compound"]),
        ("pos",      ["pos", "vader_pos", "positive"]),
    ]:
        for fb in fallbacks:
            if fb in vader_raw.columns:
                col_map[expected] = fb
                break
        if expected not in col_map:
            print(f"  ERROR: Cannot find column for '{expected}' in {INPUT_VADER.name}",
                  file=sys.stderr)
            print(f"  Available columns: {list(vader_raw.columns)}", file=sys.stderr)
            sys.exit(1)

    print(f"  Column mapping: {col_map}")
    print(f"  Raw rows: {len(vader_raw):,}")

    vader_raw["appid"] = pd.to_numeric(vader_raw["appid"], errors="coerce").astype("Int64")
    vader_raw.dropna(subset=["appid", col_map["compound"]], inplace=True)
    vader_raw["is_positive"] = vader_raw[col_map["compound"]] >= 0.05

    vader_summary = (
        vader_raw
        .groupby("appid")
        .agg(
            mean_compound = (col_map["compound"], "mean"),
            pct_positive  = ("is_positive",       "mean"),
            n_reviews     = (col_map["compound"],  "count"),
        )
        .reset_index()
    )
    vader_summary["mean_compound"] = vader_summary["mean_compound"].round(4)
    vader_summary["pct_positive"]  = vader_summary["pct_positive"].round(4)

    print(f"  Aggregated to {len(vader_summary)} titles")
    print(f"  mean_compound range: "
          f"{vader_summary['mean_compound'].min():.3f} - "
          f"{vader_summary['mean_compound'].max():.3f}")

    if not DRY_RUN:
        vader_summary.to_csv(OUTPUT_VADER_SUMMARY, index=False)
        print(f"  Saved: {OUTPUT_VADER_SUMMARY.name}")
    else:
        print(f"  [DRY RUN] Would save: {OUTPUT_VADER_SUMMARY.name}")

print()


# ══════════════════════════════════════════════════════════════════
# TASK 2 -- Merge VADER summary into port timeline
# ══════════════════════════════════════════════════════════════════
print("Task 2: Merge VADER scores into port timeline")
print("-" * 50)

if not INPUT_TIMELINE.exists():
    print(f"  ERROR: {INPUT_TIMELINE} not found.", file=sys.stderr)
    sys.exit(1)

timeline = pd.read_csv(INPUT_TIMELINE)
timeline["appid"] = pd.to_numeric(timeline["appid"], errors="coerce").astype("Int64")
print(f"  Timeline rows: {len(timeline)}")

merged = timeline.merge(
    vader_summary[["appid", "mean_compound", "pct_positive"]],
    on="appid", how="left", suffixes=("", "_vader"),
)
merged["oc_score"]      = merged["mean_compound"].round(4)
merged["positive_rate"] = merged["pct_positive"].round(4)
merged.drop(columns=["mean_compound", "pct_positive"], inplace=True, errors="ignore")

filled  = merged["oc_score"].notna().sum()
missing = merged["oc_score"].isna().sum()
print(f"  oc_score filled: {filled} / {len(merged)}")

if missing > 0:
    print(f"  WARNING: {missing} title(s) with no VADER match:")
    print(merged[merged["oc_score"].isna()][["appid","title","publisher_group"]].to_string(index=False))

if not DRY_RUN:
    merged.to_csv(OUTPUT_TIMELINE, index=False)
    print(f"  Saved: {OUTPUT_TIMELINE.name}")
else:
    print(f"  [DRY RUN] Would save: {OUTPUT_TIMELINE.name}")

print()


# ══════════════════════════════════════════════════════════════════
# TASK 3 -- PC-specific reception rate from Claude themes
# ══════════════════════════════════════════════════════════════════
print("Task 3: PC-specific reception rate")
print("-" * 50)

if USE_CACHE and OUTPUT_PC_SPECIFIC.exists():
    print(f"  Cache hit: {OUTPUT_PC_SPECIFIC.name} -- skipping")
    pc_summary = pd.read_csv(OUTPUT_PC_SPECIFIC)
    print(f"  Rows loaded: {len(pc_summary)}")
else:
    if not INPUT_CLAUDE_THEMES.exists():
        print(f"  ERROR: {INPUT_CLAUDE_THEMES} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"  Loading {INPUT_CLAUDE_THEMES.name}...")
    themes = pd.read_csv(INPUT_CLAUDE_THEMES)
    print(f"  Raw rows: {len(themes):,}")

    if "cl_pc_specific" not in themes.columns:
        print(f"  ERROR: 'cl_pc_specific' column not found.", file=sys.stderr)
        print(f"  Available columns: {list(themes.columns)}", file=sys.stderr)
        sys.exit(1)

    themes["pc_mentioned"] = themes["cl_pc_specific"] != "not_mentioned"

    # Publisher-level (primary -- feeds Panel 4 bar chart)
    pc_publisher = (
        themes
        .groupby("publisher_group")
        .agg(
            pc_specific_rate = ("pc_mentioned", "mean"),
            pc_mentions      = ("pc_mentioned", "sum"),
            n_reviews        = ("pc_mentioned", "count"),
        )
        .reset_index()
    )
    pc_publisher["pc_specific_rate"] = pc_publisher["pc_specific_rate"].round(4)

    # Title-level (for drill-down hover detail)
    pc_title = (
        themes
        .groupby(["appid", "title", "publisher_group"])
        .agg(
            pc_specific_rate = ("pc_mentioned", "mean"),
            pc_mentions      = ("pc_mentioned", "sum"),
            n_reviews        = ("pc_mentioned", "count"),
        )
        .reset_index()
    )
    pc_title["pc_specific_rate"] = pc_title["pc_specific_rate"].round(4)

    # Both levels in one file -- 'level' column discriminates
    pc_publisher["level"] = "publisher"
    pc_title["level"]     = "title"
    pc_summary = pd.concat([pc_publisher, pc_title], ignore_index=True)

    print(f"  Publishers: {len(pc_publisher)}")
    print(f"  Titles:     {len(pc_title)}")
    print()
    print("  Publisher-level PC-specific rates:")
    for _, row in pc_publisher.sort_values("pc_specific_rate", ascending=False).iterrows():
        bar = "#" * int(row["pc_specific_rate"] * 20)
        print(f"    {row['publisher_group']:<16} {row['pc_specific_rate']:.1%}  {bar}")

    if not DRY_RUN:
        pc_summary.to_csv(OUTPUT_PC_SPECIFIC, index=False)
        print(f"\n  Saved: {OUTPUT_PC_SPECIFIC.name}")
    else:
        print(f"\n  [DRY RUN] Would save: {OUTPUT_PC_SPECIFIC.name}")

print()


# ══════════════════════════════════════════════════════════════════
# TASK 4 -- Enrich franchise fatigue with console->PC gap data
# ══════════════════════════════════════════════════════════════════
print("Task 4: Franchise fatigue + gap enrichment")
print("-" * 50)

if USE_CACHE and OUTPUT_FATIGUE_ENRICH.exists():
    print(f"  Cache hit: {OUTPUT_FATIGUE_ENRICH.name} -- skipping")
    fatigue_enriched = pd.read_csv(OUTPUT_FATIGUE_ENRICH)
    print(f"  Rows loaded: {len(fatigue_enriched)}")
else:
    if not INPUT_FATIGUE.exists():
        print(f"  ERROR: {INPUT_FATIGUE} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"  Loading {INPUT_FATIGUE.name}...")
    fatigue = pd.read_csv(INPUT_FATIGUE)
    print(f"  Franchise entries: {len(fatigue)}")
    print(f"  Franchises:        {fatigue['franchise'].nunique()}")

    # Join gap data from port timeline (enriched by Task 2)
    # Normalise title keys before merging -- both files originate from
    # game_registry.py but may have been written with different Unicode
    # normalisation (e.g. 'ö' in Ragnarök encoded as NFC vs NFD).
    import unicodedata

    def norm(s):
        if pd.isna(s):
            return s
        return unicodedata.normalize("NFC", str(s)).strip()

    timeline_gap = pd.read_csv(INPUT_TIMELINE)[
        ["title", "release_console", "gap_days", "gap_category"]
    ].copy()
    timeline_gap["_key"] = timeline_gap["title"].map(norm)
    fatigue = fatigue.copy()
    fatigue["_key"]      = fatigue["title"].map(norm)

    fatigue_enriched = fatigue.merge(
        timeline_gap.drop(columns="title"),
        on="_key", how="left"
    ).drop(columns="_key")
    timeline_gap.drop(columns="_key", inplace=True)

    # Franchise-level trajectory delta
    # fatigue_delta = last_entry_compound - first_entry_compound
    #   > 0 : improving / globalization arc (Persona playbook)
    #   < 0 : sequel fatigue / declining
    fatigue_delta = (
        fatigue_enriched
        .sort_values("seq_idx")
        .groupby("franchise")
        .agg(
            first_compound = ("mean_compound", "first"),
            last_compound  = ("mean_compound", "last"),
            n_entries      = ("title",         "count"),
            publisher      = ("publisher_group","first"),
        )
        .reset_index()
    )
    fatigue_delta["fatigue_delta"] = (
        fatigue_delta["last_compound"] - fatigue_delta["first_compound"]
    ).round(4)
    fatigue_delta["trajectory"] = fatigue_delta["fatigue_delta"].apply(
        lambda d: "improving" if d > 0.01 else ("declining" if d < -0.01 else "stable")
    )

    gap_filled  = fatigue_enriched["gap_days"].notna().sum()
    gap_missing = fatigue_enriched["gap_days"].isna().sum()
    print(f"  gap_days filled: {gap_filled} / {len(fatigue_enriched)}")
    if gap_missing > 0:
        print(f"  WARNING: {gap_missing} entries with no gap match:")
        print(fatigue_enriched[fatigue_enriched["gap_days"].isna()][
            ["franchise","title"]].to_string(index=False))

    print()
    print("  Franchise trajectory summary (for reference):")
    for _, row in fatigue_delta.sort_values("fatigue_delta", ascending=False).iterrows():
        arrow = "^" if row["trajectory"] == "improving" else ("v" if row["trajectory"] == "declining" else "-")
        print(f"    {arrow} {row['franchise']:<26} delta={row['fatigue_delta']:+.4f}  ({row['publisher']})")

    if not DRY_RUN:
        fatigue_enriched.to_csv(OUTPUT_FATIGUE_ENRICH, index=False)
        print(f"\n  Saved: {OUTPUT_FATIGUE_ENRICH.name}")
    else:
        print(f"\n  [DRY RUN] Would save: {OUTPUT_FATIGUE_ENRICH.name}")

print()


# ══════════════════════════════════════════════════════════════════
# Final manifest
# ══════════════════════════════════════════════════════════════════
print("=" * 50)
print("Streamlit data prep complete.\n")

outputs = [
    (OUTPUT_VADER_SUMMARY,  "Layer 1+2  scatter + drill-down sentiment"),
    (OUTPUT_TIMELINE,       "Layer 2+3  port timeline with gap + oc_score"),
    (OUTPUT_PC_SPECIFIC,    "Layer 2    Panel 4 -- PC-specific reception"),
    (OUTPUT_FATIGUE_ENRICH, "Layer 3    franchise arc with gap data"),
]

print("Output manifest:")
all_ok = True
for path, description in outputs:
    if path.exists():
        size = path.stat().st_size / 1024
        print(f"  OK  {path.name:<46}  {size:>7.1f} KB  {description}")
    else:
        print(f"  !!  {path.name:<46}  MISSING      {description}")
        all_ok = False

print()
if all_ok:
    print("All outputs present. Ready to build Streamlit dashboard.")
    print()
    print("Dashboard data map:")
    print("  Layer 1  NB04_sentiment_summary.csv        (load directly, no join)")
    print("  Layer 2  NB04_sentiment_summary.csv        (Panel 1 -- sentiment)")
    print("           NB05_hhi.csv                      (Panel 2 -- concentration)")
    print("           NB05_language_dist.csv            (Panel 3 -- language dist)")
    print("           NB04_pc_specific_summary.csv      (Panel 4 -- PC reception)")
    print("  Layer 3  NB05_franchise_fatigue_enriched.csv")
    print()
    print("Before writing a line of Streamlit code, read:")
    print("  /mnt/skills/user/streamlit-plotly-dashboard/SKILL.md")
    print("  /mnt/skills/user/data-analytics-mindset/SKILL.md")
    print("  /mnt/skills/public/frontend-design/SKILL.md")
else:
    print("WARNING: Some outputs missing -- check errors above before building dashboard.")
