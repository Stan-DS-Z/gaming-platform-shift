"""
generate_feature_importance.py — The Platform Shift
Reads data/processed/NB06_feature_matrix.csv, re-fits logistic regression,
outputs docs/feature_importance.png.
Dark #080B14 background · 1000×520px · bilingual title · JP font support
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
from pathlib import Path

import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

# Find and register Noto Sans JP
_jp_font_path = None
for _font in fm.fontManager.ttflist:
    if 'NotoSansJP' in _font.fname or 'NotoSansCJK' in _font.fname:
        _jp_font_path = _font.fname
        break
if _jp_font_path is None:
    import glob
    _candidates = (
        glob.glob('C:/Windows/Fonts/NotoSansJP*.ttf') +
        glob.glob('C:/Windows/Fonts/NotoSansJP*.otf') +
        glob.glob(str(Path.home()) + '/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP*.ttf') +
        glob.glob(str(Path.home()) + '/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP*.otf')
    )
    if _candidates:
        fm.fontManager.addfont(_candidates[0])
        _jp_font_path = _candidates[0]
_jp = FontProperties(fname=_jp_font_path) if _jp_font_path else FontProperties()

if _jp_font_path:
    print(f"JP font: {_jp_font_path}")
else:
    noto_any = [f.name for f in fm.fontManager.ttflist if 'Noto' in f.name]
    print(f"No NotoSansJP found. Noto fonts available: {noto_any}")

# ── Paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROCESSED  = SCRIPT_DIR / "data" / "processed"
OUT_DIR    = SCRIPT_DIR / "docs"
OUT_DIR.mkdir(exist_ok=True)

# ── Config ─────────────────────────────────────────────────────────
BG             = '#080B14'
COL_POS        = '#4CAF50'
COL_NEG        = '#EF5350'
COL_ZERO       = '#3A4A6A'
COL_LABEL      = '#D0D8E8'
COL_MUTED      = '#4A5A7A'
COL_GRID       = '#1A2035'

FEATURE_COLS = [
    'oc_score',
    'vader_compound',
    'launch_delta',
    'playtime_r',
    'english_pct',
    'franchise_seq_idx',
    'cl_pc_specific_neg_rt',
]

FEATURE_LABELS = {
    'oc_score':               'OC score',
    'vader_compound':         'VADER compound',
    'launch_delta':           'Launch delta',
    'playtime_r':             'Playtime-sentiment r',
    'english_pct':            'English review %',
    'franchise_seq_idx':      'Franchise seq. index',
    'cl_pc_specific_neg_rt':  'PC-specific neg rate',
}

TARGET_COL       = 'positive_reception'
POSITIVE_THRESHOLD = 0.70

# ── Load data ──────────────────────────────────────────────────────
csv_path = PROCESSED / 'NB06_feature_matrix.csv'
if not csv_path.exists():
    raise FileNotFoundError(f"Feature matrix not found: {csv_path}\nRun NB06 first.")

df = pd.read_csv(csv_path)
print(f"Loaded {len(df)} rows from {csv_path.name}")

X = df[FEATURE_COLS].values
y = df[TARGET_COL].values

# ── Fit pipeline ───────────────────────────────────────────────────
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

imputer = SimpleImputer(strategy='median')
scaler  = StandardScaler()
lr      = LogisticRegression(penalty='l2', C=1.0, max_iter=1000,
                              random_state=42, solver='lbfgs')

X_imp    = imputer.fit_transform(X)
X_scaled = scaler.fit_transform(X_imp)
lr.fit(X_scaled, y)

coefs = lr.coef_[0]
coef_df = pd.DataFrame({'feature': FEATURE_COLS, 'coefficient': coefs})
coef_df = coef_df.sort_values('coefficient', ascending=True).reset_index(drop=True)

print("Coefficients:")
for _, row in coef_df.iterrows():
    print(f"  {row['feature']:30s}  {row['coefficient']:+.4f}")

# ── Figure ─────────────────────────────────────────────────────────
fig_w, fig_h = 1000 / 160, 520 / 160   # inches at dpi=160

fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor=BG)
ax.set_facecolor(BG)

labels   = [FEATURE_LABELS.get(f, f) for f in coef_df['feature']]
coeffs   = coef_df['coefficient'].values
colors   = [COL_POS if c > 0 else COL_NEG for c in coeffs]
y_pos    = np.arange(len(labels))

bars = ax.barh(y_pos, coeffs, color=colors, height=0.55,
               linewidth=0, zorder=3)

# ── Value labels ───────────────────────────────────────────────────
for bar, c in zip(bars, coeffs):
    x_end = bar.get_width()
    offset = 0.015 if c >= 0 else -0.015
    ha     = 'left' if c >= 0 else 'right'
    ax.text(
        x_end + offset, bar.get_y() + bar.get_height() / 2,
        f'{c:+.2f}',
        va='center', ha=ha,
        fontsize=9, color='white', fontfamily='monospace',
        zorder=5,
    )

# ── Zero line ──────────────────────────────────────────────────────
ax.axvline(0, color=COL_ZERO, linewidth=1.2, zorder=4)

# ── Y-axis ─────────────────────────────────────────────────────────
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10, color=COL_LABEL)
ax.tick_params(axis='y', length=0)

# ── X-axis ─────────────────────────────────────────────────────────
ax.tick_params(axis='x', colors=COL_MUTED, labelsize=8.5)
ax.set_xlabel(
    '← Negative predictor  ·  Positive predictor →',
    fontsize=9, color=COL_MUTED, labelpad=6,
)

# ── Grid ───────────────────────────────────────────────────────────
ax.grid(axis='x', color=COL_GRID, linewidth=0.6, linestyle='-', alpha=0.9)
ax.set_axisbelow(True)

# ── Spines ─────────────────────────────────────────────────────────
for spine in ax.spines.values():
    spine.set_edgecolor('#1A2540')
    spine.set_linewidth(0.7)

# Extend x range slightly for label breathing room
x_abs_max = max(abs(coeffs)) * 1.35
ax.set_xlim(-x_abs_max, x_abs_max)

# ── Titles ─────────────────────────────────────────────────────────
fig.text(
    0.12, 0.96,
    '特徴量重要度：各シグナルの予測力',
    fontsize=13, color='#C8D4E8', ha='left', va='top',
    fontweight='bold', fontproperties=_jp,
)
fig.text(
    0.12, 0.89,
    'Logistic Regression Coefficients (L2, standardised)  ·  n=46 titles',
    fontsize=8, color=COL_MUTED, ha='left', va='top',
)

# ── Footer ─────────────────────────────────────────────────────────
# Row 1 (higher): methodology note — left-aligned
fig.text(
    0.12, 0.04,
    'Coefficients from LogisticRegression(L2, C=1.0)  ·  '
    'Features standardised via StandardScaler  ·  '
    'Missing values imputed with corpus median',
    fontsize=6.5, color='#2A3555', ha='left', va='bottom',
)
# Row 2 (lower): watermark — right-aligned
fig.text(
    0.92, 0.01,
    'The Platform Shift',
    fontsize=6.5, color='#2A3555', ha='right', va='bottom', fontstyle='italic',
)

# ── Layout & save ──────────────────────────────────────────────────
fig.subplots_adjust(left=0.26, right=0.90, top=0.84, bottom=0.22)

out = OUT_DIR / 'feature_importance.png'
plt.savefig(out, dpi=160, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print(f'Saved → {out}')
plt.close()
