"""
app.py — The Platform Shift: A Deep Dive
Japanese Publisher PC Strategy 2022–2025

Bilingual: EN / 日本語
Font stack: Plus Jakarta Sans (EN) + Noto Sans JP (JP) + IBM Plex Mono (numbers)

4-tab architecture:
  1. Thesis & Verdicts   — hero scatter + verdict cards (click to drill)
  2. Title Explorer      — 46-title sortable table + detail panels
  3. Publisher Deep Dive  — 4-panel profile + title-level bar
  4. Predictive Model    — feature importance + calibration + per-publisher accuracy
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
# 0. Page config
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="The Platform Shift",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════
# 1. Paths
# ══════════════════════════════════════════════════════════════════
ROOT = Path(__file__).parent
PROC = ROOT / "data" / "processed"

# ══════════════════════════════════════════════════════════════════
# 2. Design tokens
# ══════════════════════════════════════════════════════════════════
C = {
    "bg":       "#F7F8FA",
    "surface":  "#FFFFFF",
    "panel":    "#FAFBFC",
    "border":   "#E8EAEE",
    "border2":  "#D4D8E0",
    "text":     "#1A1D2E",
    "muted":    "#6B7280",
    "ghost":    "#B0B8C8",
    "gold":     "#9A7820",
    "gold_dim": "#C8A840",
    "up":       "#1D6A3A",
    "down":     "#8A1F1F",
    "warn":     "#8A6010",
    "highlight":"#FDF6E3",
}

PUBLISHER_COLORS = {
    "sie":          "#C4611A",
    "bandai_namco": "#9A7820",
    "sega_atlus":   "#2A5F9E",
    "square_enix":  "#A02828",
    "ea":           "#B04818",
    "take_two":     "#2A4A98",
    "ubisoft":      "#4A5868",
}

DISPLAY_NAMES = {
    "sie":          "SIE",
    "bandai_namco": "Bandai Namco",
    "sega_atlus":   "Sega/Atlus",
    "square_enix":  "Square Enix",
    "ea":           "EA",
    "take_two":     "Take-Two",
    "ubisoft":      "Ubisoft",
}

JP_TARGETS = ["sie", "bandai_namco", "sega_atlus", "square_enix"]
BENCHMARKS = ["ea", "take_two", "ubisoft"]
ALL_PUBS   = JP_TARGETS + BENCHMARKS

LANG_COLORS = {
    "english":    "#2A5F9E", "japanese":   "#C4611A",
    "schinese":   "#A02828", "russian":    "#6A3A9A",
    "tchinese":   "#9A7820", "korean":     "#1A7A4A",
    "brazilian":  "#1A7878", "spanish":    "#B86820",
    "german":     "#2A5888", "french":     "#6A3A88",
    "portuguese": "#1A8878", "other":      "#B0B8C8",
}

MONO = "'IBM Plex Mono', monospace"
SANS = "'Plus Jakarta Sans', 'Noto Sans JP', 'DM Sans', sans-serif"

FEATURE_COLS = [
    'oc_score', 'vader_compound', 'launch_delta', 'playtime_r',
    'english_pct', 'franchise_seq_idx', 'cl_pc_specific_neg_rt',
]

FEATURE_LABELS = {
    "oc_score":               "OpenCritic score",
    "vader_compound":         "VADER compound",
    "launch_delta":           "Launch delta",
    "playtime_r":             "Playtime-sentiment r",
    "english_pct":            "English review %",
    "franchise_seq_idx":      "Franchise seq. index",
    "cl_pc_specific_neg_rt":  "PC-specific neg rate",
}

FEATURE_LABELS_JA = {
    "oc_score":               "OC スコア",
    "vader_compound":         "VADER 複合値",
    "launch_delta":           "ローンチΔ",
    "playtime_r":             "プレイ時間-感情 r",
    "english_pct":            "英語レビュー%",
    "franchise_seq_idx":      "フランチャイズ順序",
    "cl_pc_specific_neg_rt":  "PC特有ネガ率",
}

# ══════════════════════════════════════════════════════════════════
# 3. Translations
# ══════════════════════════════════════════════════════════════════
T = {
    "en": {
        # Header
        "eyebrow":          "Deep dive · Gaming industry analysis",
        "subtitle":         "Japanese publisher PC strategy 2022–2025 · 46 titles · 228,776 Steam reviews · 4 JP publishers + 3 Western benchmarks",
        "finding_label":    "Central finding",
        "finding_body":     "PC is an amplifier, not a rescue. Strong franchises compound on PC — weak execution gets amplified in the wrong direction. Port <em>volume</em> (R²&thinsp;≈&thinsp;0.01) does not predict revenue trajectory. Port <em>quality</em> does.",
        # Tabs
        "tab_thesis":       "Thesis & verdicts",
        "tab_titles":       "Title explorer",
        "tab_publisher":    "Publisher deep dive",
        "tab_model":        "Predictive model",
        # Tab 1 — Thesis
        "chart_scatter":    "Steam sentiment vs revenue CAGR · volume doesn't explain trajectory, quality does",
        "caption_scatter":  "Steam reviews · IR filings 2022–2025 · VADER sentiment · Bubble size ∝ total Steam reviews · ● JP target  ■ Western benchmark",
        "axis_sentiment":   "VADER compound sentiment  (publisher average)",
        "axis_cagr":        "Revenue CAGR 2022–2025  (%)",
        "quad_ls_hg":       "low sentiment · high growth",
        "quad_hs_hg":       "high sentiment · high growth",
        "quad_ls_dc":       "low sentiment · declining",
        "quad_hs_dc":       "high sentiment · declining",
        "section_verdicts": "Publisher verdicts — click to drill into titles",
        # Tab 2 — Title Explorer
        "section_titles":   "Title explorer — every game in the corpus",
        "filter_pub":       "Filter by publisher",
        "all_filter":       "All",
        "select_title":     "Select title for detail",
        "col_title":        "Title",
        "col_publisher":    "Publisher",
        "col_oc":           "OC Score",
        "col_vader":        "VADER",
        "col_pos":          "Pos %",
        "col_reviews":      "Reviews",
        "col_gap":          "Gap (days)",
        "col_launch_d":     "Launch Δ",
        "col_playtime_r":   "Playtime r",
        "col_pc_neg":       "PC Neg %",
        "col_pred":         "Pred.",
        "detail_header":    "Title detail",
        "launch_delta_lbl": "Launch delta",
        "playtime_r_lbl":   "Playtime-sentiment r",
        "pc_neg_lbl":       "PC-specific negative rate",
        "recovered":        "recovered after rough launch",
        "hype_faded":       "launch hype faded",
        "advocate_signal":  "advocates deepen over time",
        "burnout_signal":   "playtime burnout signal",
        "high_pc_neg":      "high PC port complaints",
        "low_pc_neg":       "few PC-specific complaints",
        # Tab 3 — Publisher Deep Dive
        "select_publisher": "Select publisher",
        "section_peers":    "Sentiment vs peers",
        "section_hhi":      "Portfolio concentration  (HHI)",
        "section_language": "Review language distribution",
        "section_pc":       "PC-specific mentions",
        "section_title_bar":"Title-level sentiment — the real picture behind the aggregate",
        "metric_sentiment": "VADER sentiment",
        "metric_positive":  "Positive rate",
        "metric_cagr":      "Revenue CAGR",
        "metric_reviews":   "Steam reviews",
        "vs_avg":           "vs avg",
        "avg_label":        "avg",
        "caption_lang":     "reviews · all {pub} titles",
        "above":            "above",
        "below":            "below",
        "concentrated":     "Concentrated",
        "moderate":         "Moderate",
        "diversified":      "Diversified",
        # Tab 4 — Model
        "section_model":    "Can early signals predict long-term reception?",
        "model_desc":       "Logistic regression (L2, LOOCV) predicting lifetime positive rate ≥ 75%. n=46 — proof-of-concept. The feature importance is the finding, not the accuracy number.",
        "feat_importance":  "Feature importance — logistic regression coefficients (scaled)",
        "per_pub_acc":      "Per-publisher LOOCV accuracy",
        "calibration":      "Predicted probability vs actual positive rate",
        "misclassified":    "Misclassified titles",
        "model_acc":        "LOOCV accuracy",
        "model_auc":        "AUC-ROC",
        "model_baseline":   "Majority baseline",
        "model_n":          "Titles",
        "model_features":   "Features",
        # Verdict
        "confirmed":        "Confirmed",
        "inverted":         "Inverted",
        "verdict_sie":      "Strong franchises compound on PC",
        "verdict_sega":     "Persona & Like a Dragon arc",
        "verdict_sqenix":   "Variance is the signal, not decline",
        "verdict_bandai":   "Elden Ring masks pipeline failure",
        "card_cagr":        "CAGR",
        "card_sent":        "VADER",
        "card_pos":         "Pos%",
        "card_titles":      "titles",
        # Footer
        "footer":           "The Platform Shift: A Deep Dive · 7 notebooks · 228,776 Steam reviews · 46 titles ·",
    },
    "ja": {
        "eyebrow":          "深掘り分析 · ゲーム産業分析",
        "subtitle":         "日本パブリッシャーのPC戦略 2022–2025 · 46タイトル · 228,776件のSteamレビュー · JP4社＋欧米3社ベンチマーク",
        "finding_label":    "中心的な発見",
        "finding_body":     "PCは救済ではなく、増幅器だ。強いフランチャイズはPCで複利的に成長する——実行力が弱ければ、逆方向に増幅される。移植の「量」（R²≈0.01）は収益軌道を予測しない。移植の「質」が予測する。",
        "tab_thesis":       "仮説と評価",
        "tab_titles":       "タイトル一覧",
        "tab_publisher":    "パブリッシャー詳細",
        "tab_model":        "予測モデル",
        "chart_scatter":    "Steam感情値 vs 売上CAGR · 量ではなく質が軌道を決定する",
        "caption_scatter":  "Steamレビュー · IR開示資料 2022–2025 · VADER感情分析 · バブルサイズ∝レビュー数 · ● JPターゲット  ■ 欧米ベンチマーク",
        "axis_sentiment":   "VADER複合感情値（パブリッシャー平均）",
        "axis_cagr":        "売上CAGR 2022–2025（%）",
        "quad_ls_hg":       "低感情 · 高成長",
        "quad_hs_hg":       "高感情 · 高成長",
        "quad_ls_dc":       "低感情 · 減収",
        "quad_hs_dc":       "高感情 · 減収",
        "section_verdicts": "パブリッシャー評価 — クリックでタイトル詳細へ",
        "section_titles":   "タイトル一覧 — コーパス内の全ゲーム",
        "filter_pub":       "パブリッシャーでフィルター",
        "all_filter":       "全て",
        "select_title":     "タイトルを選択して詳細表示",
        "col_title":        "タイトル",
        "col_publisher":    "パブリッシャー",
        "col_oc":           "OCスコア",
        "col_vader":        "VADER",
        "col_pos":          "ポジ%",
        "col_reviews":      "レビュー数",
        "col_gap":          "ギャップ日数",
        "col_launch_d":     "ローンチΔ",
        "col_playtime_r":   "プレイ時間r",
        "col_pc_neg":       "PCネガ%",
        "col_pred":         "予測",
        "detail_header":    "タイトル詳細",
        "launch_delta_lbl": "ローンチΔ",
        "playtime_r_lbl":   "プレイ時間-感情相関",
        "pc_neg_lbl":       "PC特有ネガティブ率",
        "recovered":        "ラフなローンチから回復",
        "hype_faded":       "ローンチ時のハイプが減退",
        "advocate_signal":  "時間とともに支持が深化",
        "burnout_signal":   "プレイ時間バーンアウト信号",
        "high_pc_neg":      "PC移植への不満が多い",
        "low_pc_neg":       "PC特有の不満が少ない",
        "select_publisher": "パブリッシャーを選択",
        "section_peers":    "同業比較",
        "section_hhi":      "ポートフォリオ集中度（HHI）",
        "section_language": "レビュー言語分布",
        "section_pc":       "PC特有の言及",
        "section_title_bar":"タイトル別感情値 — 集計値の裏にある実態",
        "metric_sentiment": "VADER感情値",
        "metric_positive":  "ポジティブ率",
        "metric_cagr":      "売上CAGR",
        "metric_reviews":   "Steamレビュー数",
        "vs_avg":           "平均比",
        "avg_label":        "平均",
        "caption_lang":     "件のレビュー · {pub}全タイトル",
        "above":            "上回る",
        "below":            "下回る",
        "concentrated":     "集中型",
        "moderate":         "中程度",
        "diversified":      "分散型",
        "section_model":    "初期シグナルで長期受容を予測できるか？",
        "model_desc":       "ロジスティック回帰（L2、LOOCV）でライフタイムポジティブ率≧75%を予測。n=46 — 概念実証。精度よりも特徴量重要度が発見。",
        "feat_importance":  "特徴量重要度 — ロジスティック回帰係数（標準化）",
        "per_pub_acc":      "パブリッシャー別LOOCV精度",
        "calibration":      "予測確率 vs 実際のポジティブ率",
        "misclassified":    "誤分類タイトル",
        "model_acc":        "LOOCV精度",
        "model_auc":        "AUC-ROC",
        "model_baseline":   "多数決ベースライン",
        "model_n":          "タイトル数",
        "model_features":   "特徴量数",
        "confirmed":        "確認済み",
        "inverted":         "逆説的",
        "verdict_sie":      "強いフランチャイズがPCで複利成長",
        "verdict_sega":     "ペルソナ＆龍が如くの成長弧",
        "verdict_sqenix":   "分散が信号——衰退ではない",
        "verdict_bandai":   "エルデンリングがパイプライン失敗を隠蔽",
        "card_cagr":        "CAGR",
        "card_sent":        "VADER",
        "card_pos":         "ポジ%",
        "card_titles":      "タイトル",
        "footer":           "The Platform Shift: A Deep Dive · ノートブック7冊 · 228,776件のSteamレビュー · 46タイトル ·",
    },
}

VERDICTS = {
    "sie":          ("✓", "confirmed", "verdict_sie"),
    "sega_atlus":   ("✓", "confirmed", "verdict_sega"),
    "square_enix":  ("✓", "confirmed", "verdict_sqenix"),
    "bandai_namco": ("⚠", "inverted",  "verdict_bandai"),
}

# ══════════════════════════════════════════════════════════════════
# 4. Language state + helpers
# ══════════════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0
if "drill_pub" not in st.session_state:
    st.session_state.drill_pub = None

# Clear stale query params from previous HTML-link approach
if st.query_params:
    st.query_params.clear()
# Clear stale query params from previous HTML toggle approach
if st.query_params.get("lang"):
    st.query_params.clear()

def t(key):
    d = T["ja"] if st.session_state.lang == "日本語" else T["en"]
    return d.get(key, T["en"].get(key, key))

def conc_label(raw):
    m = {"concentrated": t("concentrated"), "moderate": t("moderate"),
         "diversified": t("diversified")}
    return m.get(str(raw).lower(), str(raw).title())

def feat_label(col):
    if st.session_state.lang == "日本語":
        return FEATURE_LABELS_JA.get(col, col)
    return FEATURE_LABELS.get(col, col)

# ══════════════════════════════════════════════════════════════════
# 5. Chart helpers
# ══════════════════════════════════════════════════════════════════
def _base(h=400):
    return dict(
        height=h,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=C["panel"],
        font=dict(family=SANS, color=C["text"], size=12),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=C["surface"],
            bordercolor=C["border2"],
            font=dict(family=SANS, color=C["text"], size=12),
        ),
    )

def _xax(**kw):
    d = dict(
        gridcolor=C["border"], gridwidth=1,
        zerolinecolor=C["border2"], zerolinewidth=1,
        linecolor=C["border2"], tickcolor=C["ghost"],
        tickfont=dict(family=MONO, color=C["muted"], size=12),
    )
    d.update(kw)
    return d

def _yax(**kw):
    d = dict(
        gridcolor=C["border"], gridwidth=1,
        zerolinecolor=C["border2"], zerolinewidth=1,
        linecolor=C["border2"], tickcolor=C["ghost"],
        tickfont=dict(family=MONO, color=C["muted"], size=12),
    )
    d.update(kw)
    return d

def _section_label(text):
    st.markdown(
        f"<p style='font-family:{SANS};font-size:12px;font-weight:500;"
        f"color:{C['muted']};letter-spacing:0.06em;text-transform:uppercase;"
        f"border-bottom:1px solid {C['border']};padding-bottom:8px;"
        f"margin-bottom:14px;'>{text}</p>",
        unsafe_allow_html=True,
    )

def _insight_box(html):
    st.markdown(
        f"<div style='background:{C['highlight']};border:1px solid #E8D9A0;"
        f"border-radius:4px;padding:14px 18px;font-family:{SANS};"
        f"font-size:13px;color:{C['text']};line-height:1.6;margin:12px 0;'>"
        f"{html}</div>",
        unsafe_allow_html=True,
    )

def _explain(text):
    """Muted explanatory text below charts/sections — for the recruiter audience."""
    st.markdown(
        f"<p style='font-family:{SANS};font-size:13px;color:{C['muted']};"
        f"line-height:1.7;margin:4px 0 20px 0;max-width:900px;'>{text}</p>",
        unsafe_allow_html=True,
    )

def _explain_bi(en, ja):
    _explain(ja if st.session_state.lang == "日本語" else en)

def _metric_card(label, value, delta=None, delta_color=None):
    delta_html = ""
    if delta is not None:
        dc = delta_color or C["muted"]
        delta_html = (
            f"<div style='font-family:{MONO};font-size:12px;"
            f"color:{dc};margin-top:2px;'>{delta}</div>"
        )
    st.markdown(
        f"<div style='background:{C['surface']};border:1px solid {C['border']};"
        f"border-radius:4px;padding:16px 18px;text-align:center;'>"
        f"<div style='font-family:{MONO};font-size:26px;font-weight:500;"
        f"color:{C['text']};'>{value}</div>"
        f"<div style='font-size:11px;color:{C['muted']};font-weight:500;"
        f"text-transform:uppercase;letter-spacing:0.08em;margin-top:4px;"
        f"font-family:{SANS};'>{label}</div>"
        f"{delta_html}</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# 6. Data loaders
# ══════════════════════════════════════════════════════════════════
@st.cache_data
def load_sentiment():
    p = PROC / "NB04_sentiment_summary.csv"
    return pd.read_csv(str(p)) if p.exists() else pd.DataFrame()

@st.cache_data
def load_hhi():
    p = PROC / "NB05_hhi.csv"
    return pd.read_csv(str(p)) if p.exists() else pd.DataFrame()

@st.cache_data
def load_language_dist():
    p = PROC / "NB05_language_dist.csv"
    return pd.read_csv(str(p)) if p.exists() else pd.DataFrame()

@st.cache_data
def load_pc_specific():
    p = PROC / "NB04_pc_specific_summary.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(str(p))
    return df[df["level"] == "publisher"].copy().reset_index(drop=True)

@st.cache_data
def load_feature_matrix():
    p = PROC / "NB06_feature_matrix.csv"
    return pd.read_csv(str(p)) if p.exists() else pd.DataFrame()

@st.cache_data
def load_logreg_results():
    p = PROC / "NB06_logreg_results.csv"
    return pd.read_csv(str(p)) if p.exists() else pd.DataFrame()

@st.cache_data
def load_port_timeline():
    p = PROC / "NB03_port_timeline.csv"
    return pd.read_csv(str(p)) if p.exists() else pd.DataFrame()

@st.cache_data
def load_franchise():
    p = PROC / "NB05_franchise_fatigue_enriched.csv"
    return pd.read_csv(str(p)) if p.exists() else pd.DataFrame()

@st.cache_data
def build_title_table():
    """Join feature matrix + logreg results + port timeline into
    a single title-level table for the Title Explorer."""
    feat = load_feature_matrix()
    if feat.empty:
        return pd.DataFrame()

    results = load_logreg_results()
    timeline = load_port_timeline()

    df = feat.copy()

    # Join predictions
    if not results.empty and "logreg_proba" in results.columns:
        pred_cols = ["appid", "logreg_pred", "logreg_proba", "correct"]
        pred_cols = [c for c in pred_cols if c in results.columns]
        df = df.merge(results[pred_cols], on="appid", how="left")

    # Join gap_days from port timeline
    if not timeline.empty and "gap_days" in timeline.columns:
        gap_cols = ["appid", "gap_days"]
        gap_cols = [c for c in gap_cols if c in timeline.columns]
        if "appid" in timeline.columns:
            df = df.merge(timeline[gap_cols], on="appid", how="left")

    return df

@st.cache_data
def compute_model_coefficients():
    """Recompute logistic regression coefficients from feature matrix.
    n=46 is instant. This avoids needing a separate coefficients CSV."""
    feat = load_feature_matrix()
    if feat.empty:
        return pd.DataFrame()
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.impute import SimpleImputer
        from sklearn.model_selection import LeaveOneOut

        available_cols = [c for c in FEATURE_COLS if c in feat.columns]
        if not available_cols or "positive_reception" not in feat.columns:
            return pd.DataFrame()

        X = feat[available_cols].copy()
        y = feat["positive_reception"].values

        # Impute + scale
        imp = SimpleImputer(strategy="median")
        X_imp = imp.fit_transform(X)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_imp)

        # Fit on all data (coefficients for display)
        clf = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                                 random_state=42, solver="lbfgs")
        clf.fit(X_scaled, y)

        coef_df = pd.DataFrame({
            "feature":     available_cols,
            "coefficient": clf.coef_[0],
            "abs_coef":    np.abs(clf.coef_[0]),
        }).sort_values("abs_coef", ascending=False)

        return coef_df

    except ImportError:
        return pd.DataFrame()

# Load all data
sentiment_df = load_sentiment()
hhi_df       = load_hhi()
lang_df      = load_language_dist()
pc_df        = load_pc_specific()
feat_df      = load_feature_matrix()
results_df   = load_logreg_results()
timeline_df  = load_port_timeline()
title_df     = build_title_table()
coef_df      = compute_model_coefficients()

# ══════════════════════════════════════════════════════════════════
# 7. CSS
# ══════════════════════════════════════════════════════════════════
st.markdown(
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP'
    ':wght@300;400;500;600&family=Plus+Jakarta+Sans:wght@300;400;500;600'
    '&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

_CSS = f"""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {{
    background-color: {C['bg']} !important;
}}
[data-testid="stHeader"], [data-testid="stDecoration"],
[data-testid="stToolbar"] {{ display: none !important; }}

.stTabs [data-baseweb="tab-list"],
.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

[data-testid="stRadio"] > div {{
    flex-direction: row !important;
    gap: 0 !important;
    background: transparent !important;
    border-bottom: 2px solid {C['border']} !important;
    padding: 0 !important;
    margin-bottom: 32px !important;
    width: 100% !important;
}}
[data-testid="stRadio"] label {{
    padding: 14px 24px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    color: {C['ghost']} !important;
    font-family: {SANS} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    background: transparent !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    color: {C['gold']} !important;
    border-bottom: 2px solid {C['gold']} !important;
}}
[data-testid="stRadio"] label p {{ color: inherit !important; }}
[data-testid="stRadio"] input[type="radio"] {{
    position: absolute; opacity: 0; width: 0; height: 0;
}}

[data-testid="stSelectbox"] > div > div {{
    background: {C['surface']} !important;
    border: 1px solid {C['border2']} !important;
    border-radius: 4px !important;
    color: {C['text']} !important;
    font-size: 14px !important;
}}
[data-testid="stSelectbox"] label p {{
    color: {C['muted']} !important;
    font-size: 12px !important;
    font-family: {SANS} !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}}

[data-testid="metric-container"] {{
    background: {C['surface']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 4px !important;
    padding: 18px 20px 16px !important;
}}
[data-testid="stMetricLabel"] p {{
    color: {C['muted']} !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-family: {SANS} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: {MONO} !important;
    color: {C['text']} !important;
    font-size: 26px !important;
    font-weight: 500 !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: {MONO} !important;
    font-size: 12px !important;
}}

hr {{ border-color: {C['border']} !important; margin: 24px 0 !important; }}

[data-testid="stCaptionContainer"] p {{
    color: {C['ghost']} !important;
    font-size: 12px !important;
    font-family: {MONO} !important;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid {C['border']} !important;
    border-radius: 4px !important;
}}

/* Language toggle pills */
[data-testid="stPills"] {{
    justify-content: flex-end !important;
}}
[data-testid="stPills"] > div {{
    gap: 0 !important;
    justify-content: flex-end !important;
}}
[data-testid="stPills"] button {{
    font-family: {SANS} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 5px 14px !important;
    border-radius: 4px !important;
    border: 1px solid {C['border2']} !important;
    color: {C['ghost']} !important;
    background: transparent !important;
    min-height: 0 !important;
}}
[data-testid="stPills"] button[aria-checked="true"] {{
    background: {C['text']} !important;
    border-color: {C['text']} !important;
    color: {C['surface']} !important;
}}
[data-testid="stPills"] button:hover {{
    color: {C['muted']} !important;
    border-color: {C['muted']} !important;
}}
[data-testid="stPills"] button[aria-checked="true"]:hover {{
    color: {C['surface']} !important;
    border-color: {C['text']} !important;
}}

::-webkit-scrollbar       {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {C['border2']}; border-radius: 2px; }}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 8. Header + language toggle
# ══════════════════════════════════════════════════════════════════
hdr_col, toggle_col = st.columns([8, 1])

with toggle_col:
    st.markdown("<div style='padding-top:48px;'></div>", unsafe_allow_html=True)
    lang_choice = st.pills(
        "",
        options=["EN", "日本語"],
        default=st.session_state.get("lang", "EN"),
        key="lang_pills",
        label_visibility="collapsed",
    )
    if lang_choice is not None and lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

with hdr_col:
    st.markdown(f"""
<div style="padding:44px 0 0 0;">
  <div style="font-family:{SANS};font-size:12px;font-weight:500;color:{C['muted']};
              letter-spacing:0.16em;text-transform:uppercase;margin-bottom:12px;">
    {t("eyebrow")}
  </div>
  <h1 style="font-family:{SANS};font-size:42px;font-weight:600;color:{C['text']};
             letter-spacing:-0.02em;margin:0 0 8px 0;line-height:1.05;">
    The Platform Shift
  </h1>
  <p style="font-family:{SANS};font-size:16px;color:{C['muted']};
            margin:0 0 0 0;line-height:1.6;font-weight:400;">
    {t("subtitle")}
  </p>
</div>
""", unsafe_allow_html=True)

# Finding callout — full width, outside columns
st.markdown(f"""
<div style="border-left:3px solid {C['gold']};background:{C['surface']};
            border:1px solid {C['border']};border-left:3px solid {C['gold']};
            padding:20px 28px;margin:36px 0 44px 0;border-radius:0 4px 4px 0;">
  <div style="font-family:{SANS};font-size:11px;font-weight:600;color:{C['gold']};
              letter-spacing:0.16em;text-transform:uppercase;margin-bottom:10px;">
    {t("finding_label")}
  </div>
  <p style="font-family:{SANS};font-size:16px;color:{C['text']};
            margin:0;line-height:1.7;font-weight:400;">
    {t("finding_body")}
  </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 9. Tab navigation — 4 tabs, index-based
# ══════════════════════════════════════════════════════════════════
_tab_labels = [t("tab_thesis"), t("tab_titles"), t("tab_publisher"), t("tab_model")]
_selected = st.radio(
    "", _tab_labels,
    index=st.session_state.active_tab,
    horizontal=True,
    label_visibility="collapsed",
    key="tab_nav",
)
_new_idx = _tab_labels.index(_selected)
if _new_idx != st.session_state.active_tab:
    st.session_state.active_tab = _new_idx
    st.rerun()


# ══════════════════════════════════════════════════════════════════
# TAB 1 — Thesis & Verdicts
# ══════════════════════════════════════════════════════════════════
if st.session_state.active_tab == 0:
    if sentiment_df.empty:
        st.error("NB04_sentiment_summary.csv not found in data/processed/")
        st.stop()

    valid   = sentiment_df.dropna(subset=["revenue_cagr", "vader_compound"])
    x_arr   = valid["vader_compound"].values.astype(float)
    y_arr   = valid["revenue_cagr"].values.astype(float)
    z       = np.polyfit(x_arr, y_arr, 1)
    p_fit   = np.poly1d(z)
    y_pred  = p_fit(x_arr)
    ss_res  = np.sum((y_arr - y_pred) ** 2)
    ss_tot  = np.sum((y_arr - y_arr.mean()) ** 2)
    r2      = round(1 - ss_res / ss_tot, 3) if ss_tot > 0 else 0
    pearson = round(float(np.corrcoef(x_arr, y_arr)[0, 1]), 3)

    X_MID = 0.17
    y_min = float(y_arr.min()) - 6
    y_max = float(y_arr.max()) + 6

    fig1 = go.Figure()

    # Quadrant shading
    for x0, x1, y0, y1 in [
        (X_MID, 0.275, 0, y_max), (0.065, X_MID, 0, y_max),
        (X_MID, 0.275, y_min, 0), (0.065, X_MID, y_min, 0),
    ]:
        fig1.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                       xref="x", yref="y", fillcolor=C["border"],
                       opacity=0.5, line_width=0, layer="below")

    fig1.add_vline(x=X_MID, line=dict(color=C["border2"], width=1, dash="dot"))
    fig1.add_hline(y=0,     line=dict(color=C["border2"], width=1, dash="dot"))

    # Trend line
    x_line = np.linspace(x_arr.min() - 0.01, x_arr.max() + 0.01, 120)
    fig1.add_trace(go.Scatter(
        x=x_line, y=p_fit(x_line), mode="lines",
        line=dict(color=C["ghost"], width=1.5, dash="dash"),
        showlegend=False, hoverinfo="skip",
    ))

    # Benchmark squares
    for pub in BENCHMARKS:
        row = sentiment_df[sentiment_df["publisher_group"] == pub]
        if row.empty:
            continue
        r    = row.iloc[0]
        size = max(12, min(38, float(r["vader_reviews"]) / 900))
        fig1.add_trace(go.Scatter(
            x=[r["vader_compound"]], y=[r["revenue_cagr"]],
            mode="markers",
            marker=dict(size=size, color=C["bg"], opacity=1.0,
                        line=dict(color=PUBLISHER_COLORS[pub], width=2),
                        symbol="square"),
            name=DISPLAY_NAMES[pub],
            customdata=[[r["vader_reviews"], r["pct_positive"], r["revenue_cagr"]]],
            hovertemplate=(
                f"<b>{DISPLAY_NAMES[pub]}</b><br>"
                f"{t('metric_sentiment')}  %{{x:.3f}}<br>"
                f"{t('metric_cagr')}  %{{customdata[2]:+.1f}}%<br>"
                f"{t('metric_positive')}  %{{customdata[1]:.1%}}<br>"
                f"{t('metric_reviews')}  %{{customdata[0]:,.0f}}<br>"
                "<extra></extra>"
            ),
        ))

    # JP target circles
    for pub in JP_TARGETS:
        row = sentiment_df[sentiment_df["publisher_group"] == pub]
        if row.empty:
            continue
        r    = row.iloc[0]
        size = max(24, min(64, float(r["vader_reviews"]) / 900))
        fig1.add_trace(go.Scatter(
            x=[r["vader_compound"]], y=[r["revenue_cagr"]],
            mode="markers",
            marker=dict(size=size, color=PUBLISHER_COLORS[pub], opacity=0.82,
                        line=dict(color=C["surface"], width=2), symbol="circle"),
            name=DISPLAY_NAMES[pub],
            customdata=[[r["vader_reviews"], r["pct_positive"], r["revenue_cagr"]]],
            hovertemplate=(
                f"<b>{DISPLAY_NAMES[pub]}</b><br>"
                f"{t('metric_sentiment')}  %{{x:.3f}}<br>"
                f"{t('metric_cagr')}  %{{customdata[2]:+.1f}}%<br>"
                f"{t('metric_positive')}  %{{customdata[1]:.1%}}<br>"
                f"{t('metric_reviews')}  %{{customdata[0]:,.0f}}<br>"
                "<extra></extra>"
            ),
        ))

    # Labels
    label_nudge = {
        "sie":          (0.012, 3.5), "sega_atlus":   (0.008, -3.0),
        "square_enix":  (0.008, 3.5), "bandai_namco": (0.008,  2.5),
        "ea":           (0.004,  1.5), "take_two":     (0.004,  1.5),
        "ubisoft":      (0.004,  1.5),
    }
    for pub in ALL_PUBS:
        row = sentiment_df[sentiment_df["publisher_group"] == pub]
        if row.empty:
            continue
        r      = row.iloc[0]
        dx, dy = label_nudge.get(pub, (0.004, 1.4))
        is_jp  = pub in JP_TARGETS
        icon   = VERDICTS[pub][0] if pub in VERDICTS else ""
        label  = f"{DISPLAY_NAMES[pub]}{' ' + icon if is_jp else ''}"
        fig1.add_annotation(
            x=float(r["vader_compound"]) + dx, y=float(r["revenue_cagr"]) + dy,
            text=label, showarrow=False, xanchor="left",
            font=dict(family=SANS, size=13 if is_jp else 11,
                      color=PUBLISHER_COLORS[pub] if is_jp else C["muted"]),
        )

    # Quadrant labels
    for qx, qy, qk in [
        (0.068, y_max * 0.90, "quad_ls_hg"),
        (X_MID + 0.003, y_max * 0.90, "quad_hs_hg"),
        (0.068, y_min * 0.82, "quad_ls_dc"),
        (X_MID + 0.003, y_min * 0.82, "quad_hs_dc"),
    ]:
        fig1.add_annotation(x=qx, y=qy, text=t(qk), showarrow=False, xanchor="left",
                            font=dict(family=SANS, size=10, color=C["ghost"]))

    # R² annotation
    fig1.add_annotation(
        x=0.99, y=0.02, xref="paper", yref="paper",
        text=f"R² = {r2:.2f} &nbsp;·&nbsp; r = {pearson:+.2f}",
        showarrow=False, align="right",
        font=dict(family=MONO, size=12, color=C["muted"]),
    )

    fig1.update_layout(**_base(h=540))
    fig1.update_layout(
        xaxis=_xax(title=dict(text=t("axis_sentiment"),
                              font=dict(size=13, color=C["muted"])),
                   range=[0.065, 0.275]),
        yaxis=_yax(title=dict(text=t("axis_cagr"),
                              font=dict(size=13, color=C["muted"]))),
        showlegend=False,
        margin=dict(l=65, r=65, t=30, b=60),
    )

    st.markdown(
        f"<p style='font-family:{SANS};font-size:12px;font-weight:500;"
        f"color:{C['muted']};letter-spacing:0.04em;text-transform:uppercase;"
        f"margin-bottom:8px;'>{t('chart_scatter')}</p>",
        unsafe_allow_html=True,
    )
    _explain_bi(
        "Each bubble is a publisher's PC game portfolio. <strong>Right = better-received games</strong> (higher VADER sentiment from Steam reviews). <strong>Up = stronger revenue growth</strong> (CAGR from IR filings). Bubble size reflects total Steam reviews — a proxy for audience reach. The near-flat dashed trend line (R² ≈ 0.01) is the thesis: shipping <em>more</em> PC ports doesn't drive revenue. The <em>quality</em> of those ports does.",
        "各バブルはパブリッシャーのPCゲームポートフォリオを表す。<strong>右＝高評価</strong>（Steamレビューからの VADER感情値）。<strong>上＝収益成長</strong>（IR資料からのCAGR）。バブルサイズはSteamレビュー数に比例。点線の近似直線（R²≈0.01）が仮説を証明する：PCへの移植「数」は収益を予測しない。移植の「質」が予測する。",
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(t("caption_scatter"))

    # ── Verdict cards ──
    _section_label(t("section_verdicts"))
    _explain_bi(
        "Four hypotheses about Japanese publisher PC strategy, tested against 228,776 Steam reviews and public IR filings. <strong>Confirmed</strong> = the data supports the thesis. <strong>Inverted</strong> = the data tells the opposite story. Select any card's publisher in the Title Explorer tab to see the individual games behind these numbers.",
        "日本パブリッシャーのPC戦略に関する4つの仮説を、228,776件のSteamレビューとIR資料で検証。<strong>確認済み</strong>＝データが仮説を支持。<strong>逆説的</strong>＝データが逆の結果を示す。タイトル一覧タブで各パブリッシャーの個別タイトルを確認可能。",
    )
    v_cols = st.columns(4, gap="small")
    for i, pub in enumerate(JP_TARGETS):
        icon, status_key, detail_key = VERDICTS[pub]
        col   = PUBLISHER_COLORS[pub]
        row   = sentiment_df[sentiment_df["publisher_group"] == pub]
        cagr  = f"{row.iloc[0]['revenue_cagr']:+.1f}%" if not row.empty else "—"
        comp  = f"{row.iloc[0]['vader_compound']:.3f}"  if not row.empty else "—"
        ppos  = f"{row.iloc[0]['pct_positive']:.1%}"    if not row.empty else "—"
        s_col = C["up"] if status_key == "confirmed" else C["warn"]

        # Count titles for this publisher
        n_titles = len(title_df[title_df["publisher_group"] == pub]) if not title_df.empty else "?"

        with v_cols[i]:
            st.markdown(f"""
<div style="border-left:3px solid {col};background:{C['surface']};
            border:1px solid {C['border']};border-left:3px solid {col};
            padding:18px 18px 16px;border-radius:0 4px 4px 0;height:100%;">
  <div style="font-family:{SANS};font-size:16px;font-weight:600;
              color:{col};margin-bottom:6px;">{DISPLAY_NAMES[pub]}</div>
  <div style="font-family:{SANS};font-size:11px;font-weight:600;color:{s_col};
              letter-spacing:0.06em;margin-bottom:8px;">
    {icon} {t(status_key).upper()}
  </div>
  <div style="font-family:{SANS};font-size:13px;color:{C['muted']};
              margin-bottom:14px;line-height:1.55;">{t(detail_key)}</div>
  <div style="font-family:{MONO};font-size:12px;color:{C['muted']};line-height:2.0;">
    {t('card_cagr')} &nbsp;&nbsp;{cagr}<br>
    {t('card_sent')} &nbsp;&nbsp;{comp}<br>
    {t('card_pos')} &nbsp;&nbsp;{ppos}<br>
    {n_titles} {t('card_titles')}
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 2 — Title Explorer
# ══════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 1:
    if title_df.empty:
        st.warning("NB06_feature_matrix.csv not found — run NB06 first.")
        st.stop()

    _section_label(t("section_titles"))
    _explain_bi(
        "All 46 PC titles in the corpus with their key performance signals. <strong>OC Score</strong> = OpenCritic aggregate (critic consensus at launch). <strong>VADER</strong> = average sentiment from Steam reviews. <strong>Pos %</strong> = share of positive reviews. <strong>Gap</strong> = days between console and PC release. <strong>Launch Δ</strong> = how reception changed after launch (positive = recovered). <strong>PC Neg %</strong> = share of reviews that specifically criticize the PC port. <strong>Pred.</strong> = model-predicted probability of positive long-term reception. Sort by any column. Select a title below the table to see its full analytical profile.",
        "コーパス内の全46タイトルと主要指標。<strong>OCスコア</strong>＝OpenCritic集計（ローンチ時の批評家合意）。<strong>VADER</strong>＝Steamレビューの平均感情値。<strong>ポジ%</strong>＝ポジティブレビューの割合。<strong>ギャップ日数</strong>＝コンソール→PCリリースまでの日数。<strong>ローンチΔ</strong>＝ローンチ後の受容変化（正＝回復）。<strong>PCネガ%</strong>＝PC版を具体的に批判するレビューの割合。<strong>予測</strong>＝長期的なポジティブ受容のモデル予測確率。任意の列でソート可能。テーブル下のセレクタでタイトル詳細を表示。",
    )

    # ── Publisher filter ──
    pub_options = [t("all_filter")] + [DISPLAY_NAMES[p] for p in ALL_PUBS
                                        if p in title_df["publisher_group"].values]
    reverse_pub = {DISPLAY_NAMES[p]: p for p in ALL_PUBS}

    filter_pub = st.selectbox(
        t("filter_pub"), pub_options,
        index=0, key="title_pub_filter",
        label_visibility="visible",
    )

    if filter_pub == t("all_filter"):
        filtered = title_df.copy()
    else:
        pk = reverse_pub.get(filter_pub, "")
        filtered = title_df[title_df["publisher_group"] == pk].copy()

    # ── Build display table ──
    display_cols = {}
    display_cols[t("col_title")]     = filtered["title"]
    display_cols[t("col_publisher")] = filtered["publisher_group"].map(DISPLAY_NAMES)

    if "oc_score" in filtered.columns:
        display_cols[t("col_oc")] = filtered["oc_score"].round(1)
    if "vader_compound" in filtered.columns:
        display_cols[t("col_vader")] = filtered["vader_compound"].round(3)
    if "window_pos_rate" in filtered.columns:
        display_cols[t("col_pos")] = (filtered["window_pos_rate"] * 100).round(1)
    if "window_n" in filtered.columns:
        display_cols[t("col_reviews")] = filtered["window_n"].astype(int)
    if "gap_days" in filtered.columns:
        display_cols[t("col_gap")] = filtered["gap_days"]
    if "launch_delta" in filtered.columns:
        display_cols[t("col_launch_d")] = filtered["launch_delta"].round(3)
    if "playtime_r" in filtered.columns:
        display_cols[t("col_playtime_r")] = filtered["playtime_r"].round(3)
    if "cl_pc_specific_neg_rt" in filtered.columns:
        display_cols[t("col_pc_neg")] = (filtered["cl_pc_specific_neg_rt"] * 100).round(1)
    if "logreg_proba" in filtered.columns:
        display_cols[t("col_pred")] = filtered["logreg_proba"].round(2)

    disp_df = pd.DataFrame(display_cols)
    # Sort by OC score descending if available
    oc_col = t("col_oc")
    if oc_col in disp_df.columns:
        disp_df = disp_df.sort_values(oc_col, ascending=False)

    st.dataframe(
        disp_df,
        use_container_width=True,
        hide_index=True,
        height=min(460, 38 + len(disp_df) * 35),
    )
    st.caption(f"{len(filtered)} titles")

    # ── Title detail drill-down ──
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    _section_label(t("detail_header"))

    title_options = filtered["title"].sort_values().tolist()
    if title_options:
        selected_title = st.selectbox(
            t("select_title"), title_options,
            index=0, key="title_detail_select",
        )

        row = filtered[filtered["title"] == selected_title].iloc[0]
        pub = row["publisher_group"]
        pub_color = PUBLISHER_COLORS.get(pub, C["muted"])

        # Title header
        oc_str = f"{row['oc_score']:.1f}" if pd.notna(row.get("oc_score")) else "—"
        st.markdown(f"""
<div style="border-left:3px solid {pub_color};background:{C['surface']};
            border:1px solid {C['border']};border-left:3px solid {pub_color};
            padding:18px 24px;border-radius:0 4px 4px 0;margin-bottom:20px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <div style="font-family:{SANS};font-size:22px;font-weight:600;
                  color:{C['text']};margin-bottom:4px;">{selected_title}</div>
      <div style="font-family:{SANS};font-size:13px;color:{C['muted']};">
        {DISPLAY_NAMES.get(pub, pub)} · OC {oc_str}
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:{MONO};font-size:28px;color:{pub_color};">
        {row['vader_compound']:.3f}
      </div>
      <div style="font-family:{SANS};font-size:11px;color:{C['muted']};
                  text-transform:uppercase;letter-spacing:0.06em;">
        {t('metric_sentiment')}
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # KPI row
        k1, k2, k3, k4 = st.columns(4, gap="small")
        with k1:
            pos_rate = row.get("window_pos_rate", None)
            val = f"{pos_rate:.1%}" if pd.notna(pos_rate) else "—"
            _metric_card(t("metric_positive"), val)
        with k2:
            n_rev = row.get("window_n", None)
            val = f"{int(n_rev):,}" if pd.notna(n_rev) else "—"
            _metric_card(t("metric_reviews"), val)
        with k3:
            gap = row.get("gap_days", None)
            val = f"{int(gap)}" if pd.notna(gap) else "—"
            _metric_card(t("col_gap"), val)
        with k4:
            pred = row.get("logreg_proba", None)
            if pd.notna(pred):
                pred_color = C["up"] if pred >= 0.5 else C["down"]
                _metric_card(t("col_pred"), f"{pred:.2f}",
                            delta="✓" if pred >= 0.5 else "✗",
                            delta_color=pred_color)
            else:
                _metric_card(t("col_pred"), "—")

        # Analytical signals row
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3, gap="small")
        with s1:
            ld = row.get("launch_delta", None)
            if pd.notna(ld):
                ld_color = C["up"] if ld > 0 else C["down"]
                ld_desc  = t("recovered") if ld > 0 else t("hype_faded")
                _metric_card(t("launch_delta_lbl"), f"{ld:+.3f}",
                            delta=ld_desc, delta_color=ld_color)
            else:
                _metric_card(t("launch_delta_lbl"), "—", delta="insufficient data")
        with s2:
            pr = row.get("playtime_r", None)
            if pd.notna(pr):
                pr_color = C["up"] if pr > 0 else C["down"]
                pr_desc  = t("advocate_signal") if pr > 0 else t("burnout_signal")
                _metric_card(t("playtime_r_lbl"), f"{pr:+.3f}",
                            delta=pr_desc, delta_color=pr_color)
            else:
                _metric_card(t("playtime_r_lbl"), "—")
        with s3:
            pcn = row.get("cl_pc_specific_neg_rt", None)
            if pd.notna(pcn):
                pcn_color = C["down"] if pcn > 0.10 else C["up"]
                pcn_desc  = t("high_pc_neg") if pcn > 0.10 else t("low_pc_neg")
                _metric_card(t("pc_neg_lbl"), f"{pcn:.1%}",
                            delta=pcn_desc, delta_color=pcn_color)
            else:
                _metric_card(t("pc_neg_lbl"), "—")

        _explain_bi(
            "<strong>How to read these signals:</strong> Launch delta compares early reviews against the lifetime average — positive means the game overcame a rough start. Playtime-sentiment correlation (Pearson r) measures whether players who invest more hours rate the game higher — the strongest indicator of a loyal, deepening audience. PC-specific negative rate comes from Claude API semantic analysis of the full multilingual review corpus — it isolates complaints about the PC port itself, separate from the game's quality.",
            "<strong>指標の読み方：</strong> ローンチΔはローンチ初期と生涯平均のレビューを比較 — 正の値はラフなスタートからの回復を示す。プレイ時間-感情相関（ピアソンr）はプレイ時間が長いほど評価が高いかを測定 — 忠実で深化する支持層の最強指標。PC特有ネガティブ率はClaude APIによる多言語レビューの意味解析から — ゲーム品質とは別に、PC移植自体への不満を分離する。",
        )


# ══════════════════════════════════════════════════════════════════
# TAB 3 — Publisher Deep Dive
# ══════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 2:
    if sentiment_df.empty:
        st.error("Data not found.")
        st.stop()

    pub_options      = {DISPLAY_NAMES[p]: p for p in ALL_PUBS}
    selected_display = st.selectbox(
        t("select_publisher"),
        options=list(pub_options.keys()),
        index=0, key="pub_selector",
    )
    selected_pub = pub_options[selected_display]
    pub_color    = PUBLISHER_COLORS[selected_pub]

    s_row = sentiment_df[sentiment_df["publisher_group"] == selected_pub]
    if s_row.empty:
        st.warning(f"No data for {selected_display}.")
        st.stop()
    s = s_row.iloc[0]

    # KPI row
    m1, m2, m3, m4 = st.columns(4, gap="small")
    all_mean = float(sentiment_df["vader_compound"].mean())
    all_pos  = float(sentiment_df["pct_positive"].mean())
    with m1:
        st.metric(t("metric_sentiment"), f"{s['vader_compound']:.3f}",
                  delta=f"{s['vader_compound'] - all_mean:+.3f} {t('vs_avg')}")
    with m2:
        st.metric(t("metric_positive"), f"{s['pct_positive']:.1%}",
                  delta=f"{s['pct_positive'] - all_pos:+.1%} {t('vs_avg')}")
    with m3:
        st.metric(t("metric_cagr"), f"{s['revenue_cagr']:+.1f}%")
    with m4:
        st.metric(t("metric_reviews"), f"{int(s['vader_reviews']):,}")

    # Verdict banner
    if selected_pub in VERDICTS:
        icon, status_key, detail_key = VERDICTS[selected_pub]
        s_col = C["up"] if status_key == "confirmed" else C["warn"]
        st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};
            border-left:3px solid {pub_color};border-radius:0 4px 4px 0;
            padding:14px 22px;margin:14px 0 28px 0;
            display:flex;align-items:center;gap:24px;">
  <span style="font-family:{SANS};font-size:11px;font-weight:600;color:{s_col};
               letter-spacing:0.10em;text-transform:uppercase;white-space:nowrap;">
    {icon} {t(status_key)}
  </span>
  <span style="font-family:{SANS};font-size:14px;color:{C['muted']};">
    {t(detail_key)}
  </span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='margin-bottom:28px;'></div>", unsafe_allow_html=True)

    # ── NEW: Title-level sentiment bar ──
    if not title_df.empty:
        pub_titles = title_df[title_df["publisher_group"] == selected_pub].copy()
        if not pub_titles.empty and "vader_compound" in pub_titles.columns:
            _section_label(t("section_title_bar"))
            _explain_bi(
                "Each bar is one game in this publisher's PC catalog. The dotted line marks the publisher average. Games above it are pulling the portfolio up; games below reveal where execution fell short. The gap between best and worst tells you how consistent the publisher's PC strategy is.",
                "各バーはこのパブリッシャーのPCカタログ内の1タイトル。点線はパブリッシャー平均。上回るタイトルがポートフォリオを牽引し、下回るタイトルが実行力の課題を示す。最高と最低の差がPC戦略の一貫性を物語る。",
            )
            pub_titles = pub_titles.sort_values("vader_compound", ascending=True)
            fig_tb = go.Figure(go.Bar(
                x=pub_titles["vader_compound"],
                y=pub_titles["title"],
                orientation="h",
                marker_color=[pub_color] * len(pub_titles),
                marker_line_width=0,
                text=[f"{v:.3f}" for v in pub_titles["vader_compound"]],
                textposition="outside",
                textfont=dict(family=MONO, size=11, color=C["muted"]),
                customdata=pub_titles[["window_pos_rate", "window_n"]].values
                    if "window_pos_rate" in pub_titles.columns else None,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"{t('metric_sentiment')}  %{{x:.3f}}<br>"
                    "<extra></extra>"
                ),
            ))
            mean_pub = float(pub_titles["vader_compound"].mean())
            fig_tb.add_vline(
                x=mean_pub, line=dict(color=C["border2"], width=1, dash="dot"),
                annotation_text=f"{t('avg_label')} {mean_pub:.3f}",
                annotation_font=dict(family=MONO, size=11, color=C["muted"]),
                annotation_position="top",
            )
            fig_tb.update_layout(**_base(h=max(200, len(pub_titles) * 38 + 50)))
            fig_tb.update_layout(
                xaxis=_xax(range=[0, float(pub_titles["vader_compound"].max()) * 1.25]),
                yaxis=_yax(automargin=True),
                margin=dict(l=8, r=68, t=28, b=30),
            )
            st.plotly_chart(fig_tb, use_container_width=True)

    # ── 4-panel layout ──
    col_l, col_r = st.columns(2, gap="medium")

    with col_l:
        _section_label(t("section_peers"))
        _explain_bi(
            "VADER compound sentiment averaged across all titles in each publisher's PC catalog. The dotted line is the 7-publisher average. Position relative to peers reveals competitive standing.",
            "各パブリッシャーのPC全タイトルのVADER複合感情値の平均。点線は7社平均。競合との相対的な位置が競争力を示す。",
        )
        sent_s = sentiment_df.sort_values("vader_compound", ascending=True).copy()
        sent_s["display"] = sent_s["publisher_group"].map(DISPLAY_NAMES)
        fig_s = go.Figure(go.Bar(
            x=sent_s["vader_compound"], y=sent_s["display"], orientation="h",
            marker_color=[pub_color if r["publisher_group"] == selected_pub
                          else C["border"] for _, r in sent_s.iterrows()],
            marker_line_width=0,
            customdata=sent_s[["pct_positive","vader_reviews","revenue_cagr"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{t('metric_sentiment')}  %{{x:.3f}}<br>"
                f"{t('metric_positive')}  %{{customdata[0]:.1%}}<br>"
                f"{t('metric_reviews')}  %{{customdata[1]:,.0f}}<br>"
                f"{t('metric_cagr')}  %{{customdata[2]:+.1f}}%<br>"
                "<extra></extra>"
            ),
        ))
        mean_s = float(sentiment_df["vader_compound"].mean())
        fig_s.add_vline(x=mean_s, line=dict(color=C["border2"], width=1, dash="dot"),
                        annotation_text=f"{t('avg_label')} {mean_s:.3f}",
                        annotation_font=dict(family=MONO, size=11, color=C["muted"]),
                        annotation_position="top")
        fig_s.update_layout(**_base(h=270))
        fig_s.update_layout(xaxis=_xax(range=[0.06, 0.26]), yaxis=_yax(),
                            margin=dict(l=8, r=48, t=8, b=30))
        st.plotly_chart(fig_s, use_container_width=True)

    with col_r:
        _section_label(t("section_hhi"))
        _explain_bi(
            "The HHI (Herfindahl-Hirschman Index) measures how concentrated a publisher's Steam presence is across their titles. Green zone (< 0.15) = healthy spread. Red zone (> 0.25) = one or two titles dominate. A publisher dependent on a single hit has a fragile PC strategy.",
            "HHI（ハーフィンダール指数）はSteamでの存在感がタイトル間でどれだけ集中しているかを測定。緑（< 0.15）＝健全な分散。赤（> 0.25）＝1〜2タイトルに依存。単一ヒットに依存するパブリッシャーのPC戦略は脆弱。",
        )
        if not hhi_df.empty:
            h_row = hhi_df[hhi_df["publisher_group"] == selected_pub]
            if not h_row.empty:
                h = h_row.iloc[0]
                fig_h = go.Figure(go.Indicator(
                    mode="gauge+number", value=float(h["hhi"]),
                    number=dict(font=dict(family=MONO, size=36, color=pub_color),
                                valueformat=".3f"),
                    gauge=dict(
                        axis=dict(range=[0, 1],
                                  tickvals=[0, 0.15, 0.25, 0.5, 1.0],
                                  ticktext=["0", ".15", ".25", ".50", "1"],
                                  tickfont=dict(family=MONO, size=10, color=C["muted"])),
                        bar=dict(color=pub_color, thickness=0.22),
                        bgcolor="rgba(0,0,0,0)",
                        bordercolor=C["border"], borderwidth=1,
                        steps=[
                            dict(range=[0,    0.15], color="#EDF7ED"),
                            dict(range=[0.15, 0.25], color="#FDF6E3"),
                            dict(range=[0.25, 1.0],  color="#FDF0F0"),
                        ],
                    ),
                ))
                fig_h.update_layout(**_base(h=210))
                fig_h.update_layout(margin=dict(l=24, r=24, t=24, b=8))
                st.plotly_chart(fig_h, use_container_width=True)
                titles_word = "タイトル" if st.session_state.lang == "日本語" else "titles"
                st.markdown(
                    f"<div style='background:{C['surface']};border:1px solid "
                    f"{C['border']};border-radius:4px;padding:12px 16px;'>"
                    f"<span style='font-family:{SANS};font-size:14px;font-weight:600;"
                    f"color:{pub_color};'>{h['top_title']}</span>"
                    f"<span style='font-family:{MONO};font-size:12px;"
                    f"color:{C['muted']};'>"
                    f" · {float(h['top_title_share']):.1%}"
                    f" · {conc_label(h['concentration'])}"
                    f" · {int(h['n_titles'])} {titles_word}"
                    f"</span></div>",
                    unsafe_allow_html=True,
                )

    col_l2, col_r2 = st.columns(2, gap="medium")

    with col_l2:
        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        _section_label(t("section_language"))
        _explain_bi(
            "Language distribution reveals who the audience actually is. A high Japanese share signals domestic loyalty. Growing English and Chinese shares indicate successful globalisation. This is why the project uses multilingual sentiment analysis — English-only tools miss 45–70% of the corpus depending on publisher.",
            "言語分布はオーディエンスの実態を示す。日本語比率が高ければ国内ロイヤリティ、英語・中国語の増加はグローバル化の成功を意味する。英語のみの分析ツールはパブリッシャーにより45〜70%のコーパスを見逃すため、本プロジェクトでは多言語感情分析を採用。",
        )
        if not lang_df.empty:
            pub_lang    = lang_df[lang_df["publisher_group"] == selected_pub].copy()
            lang_totals = pub_lang.groupby("language")["count"].sum().reset_index()
            total_r     = int(lang_totals["count"].sum())
            lang_totals["pct"] = lang_totals["count"] / total_r if total_r > 0 else 0
            top7 = lang_totals.nlargest(7, "count").copy()
            other = max(0.0, 1.0 - top7["pct"].sum())
            if other > 0.005:
                other_label = "その他" if st.session_state.lang == "日本語" else "other"
                top7 = pd.concat([
                    top7,
                    pd.DataFrame([{"language": other_label, "count": 0, "pct": other}]),
                ], ignore_index=True)
            top7 = top7.sort_values("pct", ascending=True)

            lang_label_map = {
                "english":  "英語" if st.session_state.lang == "日本語" else "English",
                "japanese": "日本語" if st.session_state.lang == "日本語" else "Japanese",
                "schinese": "中国語(簡)" if st.session_state.lang == "日本語" else "Chinese (S)",
                "tchinese": "中国語(繁)" if st.session_state.lang == "日本語" else "Chinese (T)",
                "russian":  "ロシア語" if st.session_state.lang == "日本語" else "Russian",
                "korean":   "韓国語" if st.session_state.lang == "日本語" else "Korean",
                "brazilian":"PT (BR)",
                "spanish":  "スペイン語" if st.session_state.lang == "日本語" else "Spanish",
                "german":   "ドイツ語" if st.session_state.lang == "日本語" else "German",
                "french":   "フランス語" if st.session_state.lang == "日本語" else "French",
                "portuguese":"ポルトガル語" if st.session_state.lang == "日本語" else "Portuguese",
            }
            _ll = lambda l: lang_label_map.get(l, l.title())

            fig_l = go.Figure(go.Bar(
                x=top7["pct"], y=top7["language"].map(_ll), orientation="h",
                marker_color=[LANG_COLORS.get(l, C["border"]) for l in top7["language"]],
                marker_line_width=0,
                text=[f"{p:.1%}" for p in top7["pct"]],
                textposition="outside",
                textfont=dict(family=MONO, size=11, color=C["muted"]),
                hovertemplate="%{y}: %{x:.1%}<extra></extra>",
            ))
            fig_l.update_layout(**_base(h=290))
            fig_l.update_layout(
                xaxis=_xax(tickformat=".0%",
                           range=[0, float(top7["pct"].max()) * 1.38]),
                yaxis=_yax(), margin=dict(l=8, r=58, t=8, b=30),
            )
            st.plotly_chart(fig_l, use_container_width=True)
            cap = t("caption_lang").format(pub=selected_display)
            st.caption(f"{total_r:,} {cap}")

    with col_r2:
        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        _section_label(t("section_pc"))
        _explain_bi(
            "When players explicitly mention the PC version in their review, is the commentary positive or negative? This signal — extracted by Claude API from the full multilingual corpus — isolates port quality from game quality. A publisher with high PC-specific negativity has a porting problem, not necessarily a game problem.",
            "レビューでPC版に明示的に言及する際、その内容はポジティブかネガティブか？ このシグナルはClaude APIが多言語コーパスから抽出 — 移植品質をゲーム品質から分離する。PC特有のネガティブ率が高いパブリッシャーは、ゲームではなく移植に問題がある。",
        )
        if not pc_df.empty:
            pc_s   = pc_df.sort_values("pc_specific_rate", ascending=True).copy()
            pc_s["display"] = pc_s["publisher_group"].map(DISPLAY_NAMES)
            avg_pc = float(pc_df["pc_specific_rate"].mean())
            fig_pc = go.Figure(go.Bar(
                x=pc_s["pc_specific_rate"], y=pc_s["display"], orientation="h",
                marker_color=[pub_color if r["publisher_group"] == selected_pub
                              else C["border"] for _, r in pc_s.iterrows()],
                marker_line_width=0,
                text=[f"{r:.1%}" for r in pc_s["pc_specific_rate"]],
                textposition="outside",
                textfont=dict(family=MONO, size=11, color=C["muted"]),
                customdata=pc_s[["pc_mentions","n_reviews"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>%{x:.1%}<br>"
                    "%{customdata[0]:,.0f} / %{customdata[1]:,.0f}<br>"
                    "<extra></extra>"
                ),
            ))
            fig_pc.add_vline(
                x=avg_pc, line=dict(color=C["border2"], width=1, dash="dot"),
                annotation_text=f"{t('avg_label')} {avg_pc:.1%}",
                annotation_font=dict(family=MONO, size=11, color=C["muted"]),
                annotation_position="top",
            )
            fig_pc.update_layout(**_base(h=290))
            fig_pc.update_layout(
                xaxis=_xax(tickformat=".0%",
                           range=[0, float(pc_s["pc_specific_rate"].max()) * 1.42]),
                yaxis=_yax(), margin=dict(l=8, r=58, t=8, b=55),
            )
            st.plotly_chart(fig_pc, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 4 — Predictive Model
# ══════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 3:
    _section_label(t("section_model"))
    _explain_bi(
        "If you knew a game's critic score, player sentiment, and PC port quality at launch — could you predict whether it would achieve strong long-term reception on Steam? This logistic regression model answers that question using 7 features derived from the pipeline. At n=46, it's a proof-of-concept, not a production predictor. But the feature importance ranking below reveals which signals matter most — and that's the real finding.",
        "ローンチ時の批評家スコア、プレイヤー感情、PC移植品質がわかっていれば、Steamでの長期的な好評を予測できるか？ このロジスティック回帰モデルはパイプラインから得た7つの特徴量でその問いに答える。n=46は概念実証であり本番予測器ではない。しかし以下の特徴量重要度ランキングがどのシグナルが最も重要かを明らかにする — それが真の発見。",
    )

    if results_df.empty:
        st.warning("NB06_logreg_results.csv not found — run NB06 first.")
        st.stop()

    # ── Model KPIs ──
    y_true = results_df["positive_reception"].values
    y_pred = results_df["logreg_pred"].values
    loocv_acc = float((y_true == y_pred).mean())
    baseline  = max(float(y_true.mean()), 1 - float(y_true.mean()))

    # AUC
    try:
        from sklearn.metrics import roc_auc_score
        loocv_auc = float(roc_auc_score(y_true, results_df["logreg_proba"].values))
    except Exception:
        loocv_auc = 0.0

    k1, k2, k3, k4 = st.columns(4, gap="small")
    with k1:
        _metric_card(t("model_acc"), f"{loocv_acc:.2f}",
                    delta=f"vs {baseline:.3f} baseline",
                    delta_color=C["up"] if loocv_acc > baseline else C["down"])
    with k2:
        _metric_card(t("model_auc"), f"{loocv_auc:.2f}")
    with k3:
        _metric_card(t("model_n"), str(len(results_df)))
    with k4:
        n_feats = len([c for c in FEATURE_COLS if c in feat_df.columns]) if not feat_df.empty else 7
        _metric_card(t("model_features"), str(n_feats))

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    _explain_bi(
        "<strong>LOOCV</strong> (Leave-One-Out Cross-Validation) trains the model on 45 titles and predicts the 46th, repeated for every title — the most honest accuracy estimate at small sample sizes. <strong>AUC-ROC</strong> measures how well the model separates positive from negative outcomes regardless of threshold. <strong>Majority baseline</strong> is what you'd get by always predicting the most common class — the model must beat this to be useful.",
        "<strong>LOOCV</strong>（Leave-One-Out交差検証）は45タイトルで学習し残り1タイトルを予測、全タイトルで繰り返す — 小サンプルで最も誠実な精度推定。<strong>AUC-ROC</strong>は閾値に依らずポジティブ/ネガティブの分離能力を測定。<strong>多数決ベースライン</strong>は最頻クラスを常に予測した場合の精度 — モデルはこれを上回る必要がある。",
    )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Feature importance bar chart ──
    if not coef_df.empty:
        _section_label(t("feat_importance"))
        _explain_bi(
            "Each bar shows how strongly a feature pushes the prediction toward positive (green, right) or negative (red, left) reception. Coefficients are standardised, so their magnitudes are directly comparable. Longer bars = stronger predictors.",
            "各バーは特徴量が予測をポジティブ（緑・右）またはネガティブ（赤・左）にどれだけ押すかを示す。係数は標準化されているため大きさを直接比較可能。長いバー＝強い予測因子。",
        )
        coef_sorted = coef_df.sort_values("coefficient", ascending=True)

        fig_coef = go.Figure(go.Bar(
            x=coef_sorted["coefficient"],
            y=coef_sorted["feature"].map(feat_label),
            orientation="h",
            marker_color=[C["up"] if c > 0 else C["down"]
                          for c in coef_sorted["coefficient"]],
            marker_line_width=0,
            text=[f"{c:+.2f}" for c in coef_sorted["coefficient"]],
            textposition="outside",
            textfont=dict(family=MONO, size=12, color=C["muted"]),
            hovertemplate="<b>%{y}</b><br>Coefficient: %{x:+.3f}<extra></extra>",
        ))
        fig_coef.add_vline(x=0, line=dict(color=C["border2"], width=1))
        fig_coef.update_layout(**_base(h=max(220, len(coef_sorted) * 36 + 50)))
        fig_coef.update_layout(
            xaxis=_xax(title=dict(text="Coefficient (scaled)",
                                  font=dict(size=12, color=C["muted"]))),
            yaxis=_yax(),
            margin=dict(l=8, r=68, t=8, b=40),
        )
        st.plotly_chart(fig_coef, use_container_width=True)

        _insight_box(
            "<strong>Interpretation:</strong> "
            "OC score and VADER compound are the strongest positive predictors — "
            "critic consensus and player sentiment both matter. "
            "PC-specific negative rate is a drag: port quality is a measurable liability. "
            "English % is a corpus composition effect (high English share co-occurs with "
            "Western benchmarks), not a causal claim."
            if st.session_state.lang != "日本語" else
            "<strong>解釈：</strong> "
            "OCスコアとVADER複合値が最も強い正の予測因子 — 批評家の合意とプレイヤー感情の両方が重要。"
            "PC特有ネガティブ率はマイナス要因：移植品質は測定可能な負債。"
            "英語%はコーパス構成効果（高い英語シェアは欧米ベンチマークと共起）であり、因果的主張ではない。"
        )

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Two-panel: per-publisher accuracy + calibration scatter ──
    col_l, col_r = st.columns(2, gap="medium")

    with col_l:
        _section_label(t("per_pub_acc"))
        _explain_bi(
            "How well does the model predict each publisher's titles? Numbers in parentheses show title count. Publishers with high variance (like Square Enix) are harder to predict.",
            "パブリッシャーごとのモデル予測精度。括弧内はタイトル数。分散の大きいパブリッシャー（スクエニ等）は予測困難。",
        )
        pub_acc = (
            results_df.groupby("publisher_group")["correct"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "accuracy", "count": "n_titles"})
        )
        pub_acc["display"] = pub_acc["publisher_group"].map(DISPLAY_NAMES)
        pub_acc = pub_acc.sort_values("accuracy", ascending=True)

        fig_pa = go.Figure(go.Bar(
            x=pub_acc["accuracy"],
            y=pub_acc["display"],
            orientation="h",
            marker_color=[PUBLISHER_COLORS.get(p, C["muted"])
                          for p in pub_acc["publisher_group"]],
            marker_line_width=0,
            text=[f"{a:.0%} ({n})" for a, n in
                  zip(pub_acc["accuracy"], pub_acc["n_titles"])],
            textposition="outside",
            textfont=dict(family=MONO, size=11, color=C["muted"]),
            hovertemplate=(
                "<b>%{y}</b><br>Accuracy: %{x:.0%}<br>"
                "<extra></extra>"
            ),
        ))
        fig_pa.add_vline(x=loocv_acc,
                         line=dict(color=C["border2"], width=1, dash="dot"),
                         annotation_text=f"overall {loocv_acc:.0%}",
                         annotation_font=dict(family=MONO, size=11, color=C["muted"]),
                         annotation_position="top")
        fig_pa.update_layout(**_base(h=280))
        fig_pa.update_layout(
            xaxis=_xax(tickformat=".0%", range=[0, 1.15]),
            yaxis=_yax(),
            margin=dict(l=8, r=68, t=8, b=30),
        )
        st.plotly_chart(fig_pa, use_container_width=True)

    with col_r:
        _section_label(t("calibration"))
        _explain_bi(
            "Each dot is one game. The diagonal = perfect prediction. Dots above the line exceeded expectations; dots below underperformed. Misclassified titles (✗) show where the model's assumptions break down — hover for details.",
            "各ドットは1タイトル。対角線＝完全な予測。線の上＝期待以上、線の下＝期待以下。誤分類タイトル（✗）はモデルの前提が崩れた箇所 — ホバーで詳細表示。",
        )
        fig_cal = go.Figure()

        # 45-degree reference line
        fig_cal.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines",
            line=dict(color=C["ghost"], width=1, dash="dash"),
            showlegend=False, hoverinfo="skip",
        ))

        # Each title as a dot
        for _, r in results_df.iterrows():
            pub = r["publisher_group"]
            correct = r.get("correct", 1)
            fig_cal.add_trace(go.Scatter(
                x=[r["logreg_proba"]],
                y=[r["window_pos_rate"]],
                mode="markers",
                marker=dict(
                    size=10 if correct == 0 else 8,
                    color=PUBLISHER_COLORS.get(pub, C["muted"]),
                    opacity=0.85,
                    line=dict(color=C["down"] if correct == 0 else C["surface"],
                              width=2 if correct == 0 else 1),
                    symbol="x" if correct == 0 else "circle",
                ),
                name=r["title"],
                showlegend=False,
                hovertemplate=(
                    f"<b>{r['title']}</b><br>"
                    f"{DISPLAY_NAMES.get(pub, pub)}<br>"
                    f"Predicted: %{{x:.2f}}<br>"
                    f"Actual: %{{y:.1%}}<br>"
                    f"{'✗ Misclassified' if correct == 0 else '✓ Correct'}"
                    "<extra></extra>"
                ),
            ))

        # Label misclassified
        mis = results_df[results_df["correct"] == 0]
        for _, r in mis.iterrows():
            fig_cal.add_annotation(
                x=float(r["logreg_proba"]) + 0.03,
                y=float(r["window_pos_rate"]),
                text=r["title"],
                showarrow=True, arrowhead=0, arrowwidth=0.5,
                arrowcolor=C["down"], ax=40, ay=-10,
                font=dict(family=SANS, size=10, color=C["down"]),
                xanchor="left",
            )

        fig_cal.update_layout(**_base(h=280))
        fig_cal.update_layout(
            xaxis=_xax(title=dict(text="Predicted probability",
                                  font=dict(size=12, color=C["muted"])),
                       range=[-0.05, 1.05]),
            yaxis=_yax(title=dict(text="Actual positive rate",
                                  font=dict(size=12, color=C["muted"])),
                       range=[-0.05, 1.05]),
            margin=dict(l=55, r=20, t=8, b=50),
        )
        st.plotly_chart(fig_cal, use_container_width=True)

    # ── Misclassified titles table ──
    if len(mis) > 0:
        _section_label(t("misclassified"))
        mis_display = mis[["title", "publisher_group", "positive_reception",
                           "logreg_proba", "window_pos_rate"]].copy()
        mis_display["publisher_group"] = mis_display["publisher_group"].map(DISPLAY_NAMES)
        mis_display.columns = [
            t("col_title"), t("col_publisher"), "Target",
            t("col_pred"), t("col_pos"),
        ]
        st.dataframe(mis_display, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# Footer
# ══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:56px;'></div>", unsafe_allow_html=True)
st.markdown(
    f"<p style='font-family:{MONO};font-size:12px;color:{C['ghost']};"
    f"text-align:center;padding:16px 0;border-top:1px solid {C['border']};'>"
    f"{t('footer')} "
    f"<a href='https://github.com/Stan-DS-Z/gaming-platform-shift' "
    f"style='color:{C['gold']};text-decoration:none;'>"
    f"github.com/Stan-DS-Z/gaming-platform-shift</a>"
    f"</p>",
    unsafe_allow_html=True,
)
