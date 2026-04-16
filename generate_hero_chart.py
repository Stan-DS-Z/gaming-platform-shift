"""
generate_hero_chart.py — The Platform Shift
Standalone script. Reads NB04_sentiment_summary.csv, outputs docs/hero_chart.png.
Dark #080B14 background · 3-layer glow · heavy quadrant shading · bilingual · 1200×675
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
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

# ── Paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROCESSED  = SCRIPT_DIR / "data" / "processed"
OUT_DIR    = SCRIPT_DIR / "docs"
OUT_DIR.mkdir(exist_ok=True)

# ── Design constants ───────────────────────────────────────────────
BG       = '#080B14'
PANEL    = '#080B14'
GRID_COL = '#1A2035'

PUBLISHER_COLORS = {
    'sie':          '#C4611A',
    'bandai_namco': '#9A7820',
    'sega_atlus':   '#2A5F9E',
    'square_enix':  '#A02828',
    'ea':           '#B04818',
    'take_two':     '#2A4A98',
    'ubisoft':      '#4A5868',
}
DISPLAY_NAMES = {
    'sie':          'SIE',
    'bandai_namco': 'Bandai Namco',
    'sega_atlus':   'Sega/Atlus',
    'square_enix':  'Square Enix',
    'ea':           'EA',
    'take_two':     'Take-Two',
    'ubisoft':      'Ubisoft',
}
JP_TARGETS = ['sie', 'bandai_namco', 'sega_atlus', 'square_enix']
BENCHMARKS = ['ea', 'take_two', 'ubisoft']

# Verdict symbols for JP targets
VERDICTS = {
    'sie':          '✓',
    'bandai_namco': '✗',
    'sega_atlus':   '✓',
    'square_enix':  '✓',
}

# ── Load data ──────────────────────────────────────────────────────
# Publisher-level aggregates from NB04 / NB02
# Fallback to hardcoded actuals if CSV missing
csv_path = PROCESSED / 'NB04_sentiment_summary.csv'

publishers = {
    'sie':          {'sentiment': 0.218, 'cagr': 14.2, 'oc': 88, 'reviews': 91_000, 'group': 'jp_target'},
    'bandai_namco': {'sentiment': 0.152, 'cagr':  6.1, 'oc': 84, 'reviews': 78_000, 'group': 'jp_target'},
    'sega_atlus':   {'sentiment': 0.219, 'cagr': 11.3, 'oc': 86, 'reviews': 46_000, 'group': 'jp_target'},
    'square_enix':  {'sentiment': 0.208, 'cagr': -6.8, 'oc': 80, 'reviews': 61_000, 'group': 'jp_target'},
    'ea':           {'sentiment': 0.093, 'cagr': 13.1, 'oc': 73, 'reviews': 21_000, 'group': 'benchmark'},
    'take_two':     {'sentiment': 0.211, 'cagr': 29.3, 'oc': 85, 'reviews': 18_000, 'group': 'benchmark'},
    'ubisoft':      {'sentiment': 0.096, 'cagr':  2.8, 'oc': 69, 'reviews': 13_000, 'group': 'benchmark'},
}

if csv_path.exists():
    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            pub = row.get('publisher_group', '')
            if pub in publishers:
                publishers[pub]['sentiment'] = float(row.get('vader_compound', publishers[pub]['sentiment']))
                publishers[pub]['cagr']      = float(row.get('revenue_cagr',  publishers[pub]['cagr']))
        print(f"Loaded {csv_path.name}")
    except Exception as e:
        print(f"CSV load failed ({e}), using hardcoded actuals")
else:
    print(f"CSV not found at {csv_path}, using hardcoded actuals")

# ── Figure ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 6.75), facecolor=BG)
ax  = fig.add_axes([0.09, 0.13, 0.84, 0.74])
ax.set_facecolor(BG)

# ── Data ranges ────────────────────────────────────────────────────
xs = [d['sentiment'] for d in publishers.values()]
ys = [d['cagr']      for d in publishers.values()]

x_pad = 0.025
y_pad = 4
x_min, x_max = min(xs) - x_pad, max(xs) + x_pad + 0.015
y_min, y_max = min(ys) - y_pad, max(ys) + y_pad + 3

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

# Cross-hair at median x, y=0
x_mid = np.median(xs)
y_mid = 0

# ── Grid ───────────────────────────────────────────────────────────
ax.grid(axis='both', color=GRID_COL, linewidth=0.7, linestyle='-', alpha=0.9)
ax.set_axisbelow(True)
ax.axhline(y_mid, color='#2A3555', linewidth=1.2, zorder=2)
ax.axvline(x_mid, color='#2A3555', linewidth=1.2, zorder=2, linestyle='--', alpha=0.7)

# ── Quadrant shading ───────────────────────────────────────────────
ax.axhspan(y_mid, y_max, xmin=0, xmax=1, color='#071420', alpha=0.55, zorder=1)  # growth zone — blue tint
ax.axhspan(y_min, y_mid, xmin=0, xmax=1, color='#150808', alpha=0.55, zorder=1)  # decline zone — red tint

# ── Quadrant labels ────────────────────────────────────────────────
# Corner-anchored, dark pill background, readable contrast
_pill = dict(boxstyle='round,pad=0.45', edgecolor='none', alpha=0.72)

# Growth zone labels — blue-tinted text on dark blue pill
_q_growth = dict(fontsize=8.5, color='#7BAFD4',
                 bbox=dict(facecolor='#0A1828', **_pill))
# Decline zone labels — red-tinted text on dark red pill
_q_decline = dict(fontsize=8.5, color='#D4827B',
                  bbox=dict(facecolor='#1A0808', **_pill))

Q_MX = 0.005   # x margin in data units
Q_MY = 1.5     # y margin in CAGR % units

ax.text(x_min + Q_MX, y_max - Q_MY,
        'low sentiment · high growth\n低感情・高成長',
        ha='left', va='top', fontproperties=_jp, **_q_growth)

ax.text(x_max - Q_MX, y_max - Q_MY,
        'high sentiment · high growth\n高感情・高成長',
        ha='right', va='top', fontproperties=_jp, **_q_growth)

ax.text(x_min + Q_MX, y_min + Q_MY,
        'low sentiment · declining\n低感情・減収',
        ha='left', va='bottom', fontproperties=_jp, **_q_decline)

ax.text(x_max - Q_MX, y_min + Q_MY,
        'high sentiment · declining\n高感情・減収',
        ha='right', va='bottom', fontproperties=_jp, **_q_decline)

# ── OLS trend line ─────────────────────────────────────────────────
x_arr = np.array(xs)
y_arr = np.array(ys)
m, b  = np.polyfit(x_arr, y_arr, 1)
r     = np.corrcoef(x_arr, y_arr)[0, 1]
r2    = r ** 2

x_fit = np.linspace(x_min, x_max, 100)
ax.plot(x_fit, m * x_fit + b,
        color='#4A6A9A', linewidth=1.5, linestyle='--', alpha=0.65, zorder=3)

# ── Bubbles ────────────────────────────────────────────────────────
for pub_key, d in publishers.items():
    x      = d['sentiment']
    y      = d['cagr']
    color  = PUBLISHER_COLORS[pub_key]
    marker = 'o' if d['group'] == 'jp_target' else 's'
    size   = (d['oc'] / 100) ** 2 * 3800

    is_jp = d['group'] == 'jp_target'

    # Clean single marker — no glow
    ax.scatter(x, y, s=size, c=color, marker=marker,
               alpha=0.92, linewidths=0, zorder=5)

    # Crisp border ring — white for JP targets, muted for benchmarks
    edge_color = '#FFFFFF' if is_jp else '#888888'
    edge_width = 2.2      if is_jp else 1.0
    edge_alpha = 0.80     if is_jp else 0.45
    ax.scatter(x, y, s=size, c='none', marker=marker,
               edgecolors=edge_color, linewidths=edge_width,
               alpha=edge_alpha, zorder=6)

# ── Publisher labels ───────────────────────────────────────────────
label_offsets = {
    'sie':          ( 0.0085,  0.5),
    'bandai_namco': ( 0.0,     1.8),
    'sega_atlus':   ( 0.009,  -1.5),
    'square_enix':  ( 0.007,  -1.8),
    'ea':           ( 0.007,   0.5),
    'take_two':     ( 0.008,   0.5),
    'ubisoft':      ( 0.007,   0.5),
}

for pub_key, d in publishers.items():
    x  = d['sentiment']
    y  = d['cagr']
    dx, dy = label_offsets.get(pub_key, (0.007, 0.5))

    name = DISPLAY_NAMES[pub_key]
    if pub_key in VERDICTS:
        name = f"{name} {VERDICTS[pub_key]}"

    txt = ax.text(
        x + dx, y + dy, name,
        fontsize=9.5, color='#D0D8E8', ha='left', va='bottom',
        fontweight='semibold',
        path_effects=[
            pe.withStroke(linewidth=3, foreground='#080B14'),
            pe.Normal(),
        ],
        zorder=10,
    )

# ── Legend ─────────────────────────────────────────────────────────
# Placed at upper-left corner with bbox_to_anchor — sits in the figure margin
# above the quadrant label which is now at 55% height, not the ceiling.
legend_elements = [
    Line2D([0], [0], marker='o', color='w',
           markerfacecolor='#888888', markersize=8,
           markeredgecolor='#CCCCCC', markeredgewidth=1.0,
           label='JP target', linestyle='None'),
    Line2D([0], [0], marker='s', color='w',
           markerfacecolor='#888888', markersize=7,
           markeredgecolor='#AAAAAA', markeredgewidth=0.8,
           label='Western benchmark', linestyle='None'),
    Line2D([0], [0], color='#4A6A9A', linewidth=1.4,
           linestyle='--', label=f'OLS trend  (R² = {r2:.2f})'),
]

leg = ax.legend(
    handles=legend_elements,
    loc='upper left',
    bbox_to_anchor=(0.0, 1.0),
    fontsize=8.5,
    labelcolor='#8898AA',
    framealpha=0.30,
    facecolor='#0C1220',
    edgecolor='#1A2540',
    borderpad=0.7,
    handletextpad=0.6,
    labelspacing=0.5,
)

# ── R² annotation — bottom-right interior, below zero line ────────
# Placed at a fixed data coordinate that stays clear of Square Enix
ax.text(x_max - 0.002, y_mid - (y_mid - y_min) * 0.3,
        f'R² = {r2:.2f}   ·   r = {r:+.2f}',
        fontsize=8.5, color='#4A5A7A', ha='right', va='center',
        fontfamily='monospace')

# ── Axes styling ───────────────────────────────────────────────────
ax.tick_params(colors='#4A5A7A', labelsize=9, length=3, width=0.6)
for spine in ax.spines.values():
    spine.set_edgecolor('#1A2540')
    spine.set_linewidth(0.8)

ax.set_xlabel('VADER compound sentiment  (publisher average)',
              fontsize=10, color='#6A7A9A', labelpad=8)
ax.set_ylabel('Revenue CAGR 2022–2025  (%)',
              fontsize=10, color='#6A7A9A', labelpad=8)

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:+.0f}%' if v != 0 else '0%'))

# ── Titles ─────────────────────────────────────────────────────────
fig.text(0.09, 0.935,
         'PCプラットフォームへの移行：感情スコアと収益軌道',
         fontsize=14, color='#C8D4E8', ha='left', va='bottom',
         fontweight='bold', fontproperties=_jp)

fig.text(0.09, 0.900,
         f'Steam sentiment vs revenue CAGR 2022–2025  ·  46 titles  ·  228,776 reviews  ·  7 publishers',
         fontsize=8.5, color='#4A5A7A', ha='left', va='bottom')

# ── Footer ─────────────────────────────────────────────────────────
fig.text(0.09, 0.03,
         'Sentiment: VADER compound (all reviews, multilingual corpus)  ·  '
         'CAGR: IR gaming segment, FX-adjusted  ·  '
         '46 titles · 228,776 Steam reviews · 2022–2025',
         fontsize=7, color='#2A3555', ha='left', va='bottom')

fig.text(0.93, 0.03,
         'The Platform Shift',
         fontsize=7, color='#2A3555', ha='right', va='bottom', fontstyle='italic')

# ── Save ───────────────────────────────────────────────────────────
out = OUT_DIR / 'hero_chart.png'
plt.savefig(out, dpi=180, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print(f'Saved → {out}')
plt.close()
