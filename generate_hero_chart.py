"""
generate_hero_chart.py — The Platform Shift
Publisher-level weighted OC score vs Steam positive rate, 7 bubbles.
Reads NB06_feature_matrix.csv → docs/hero_chart.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from pathlib import Path

import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

# ── JP font registration ───────────────────────────────────────────
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
PROCESSED  = SCRIPT_DIR / 'data' / 'processed'
OUT_DIR    = SCRIPT_DIR / 'docs'
OUT_DIR.mkdir(exist_ok=True)

# ── Design constants ───────────────────────────────────────────────
BG       = '#080B14'
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
JP_TARGETS = {'sie', 'bandai_namco', 'sega_atlus', 'square_enix'}

CHAMPION_ABBREV = {
    'God of War Ragnarök':          'GoW Ragnarök',
    'Final Fantasy VII Rebirth':    'FF7 Rebirth',
    'Persona 5 Royal':              'Persona 5 Royal',
    'Elden Ring':                   'Elden Ring',
    'Red Dead Redemption 2':        'Red Dead 2',
    'EA Sports FC 24':              'FC 24',
    "Assassin's Creed Shadows":     'AC: Shadows',
}

# ── Load & aggregate data ──────────────────────────────────────────
import sys, io, json
_out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
def _p(s=''): _out.write(s + '\n'); _out.flush()

csv_path = PROCESSED / 'NB06_feature_matrix.csv'
raw = pd.read_csv(csv_path, usecols=['appid', 'title', 'publisher_group',
                                      'oc_score', 'window_pos_rate', 'window_n'])
raw = raw.dropna(subset=['oc_score', 'window_pos_rate'])
raw = raw[raw['publisher_group'].isin(PUBLISHER_COLORS)].copy()
raw['oc']      = raw['oc_score'].astype(float)
raw['pos_rt']  = raw['window_pos_rate'].astype(float)
raw['n']       = raw['window_n'].astype(float)

# ── Load Steam recommendations from raw JSON ───────────────────────
RAW_DETAILS = SCRIPT_DIR / 'data' / 'raw' / 'details'
recs = {}
for path in RAW_DETAILS.glob('*.json'):
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        appid = d.get('appid')
        rec   = d.get('recommendations')
        if appid and rec is not None:
            recs[int(appid)] = int(rec)
    except Exception:
        pass

raw['recommendations'] = raw['appid'].map(recs).fillna(0).astype(int)

# ── Champion diagnostic ────────────────────────────────────────────
_p('\n── Champion by Steam recommendations ────────────────────────────────────────────────')
for pub in sorted(raw['publisher_group'].unique()):
    grp = raw[raw['publisher_group'] == pub].sort_values('recommendations', ascending=False)
    pub_total = grp['recommendations'].sum()
    _p(f'\n  {pub}  (total recs: {pub_total:,})')
    _p(f"  {'Title':<44} {'recs':>10} {'share':>8}")
    _p('  ' + '─' * 66)
    for _, row in grp.iterrows():
        share = row['recommendations'] / pub_total * 100 if pub_total > 0 else 0
        _p(f"  {row['title'][:43]:<44} {row['recommendations']:>10,} {share:>7.1f}%")
_p('\n' + '─' * 88 + '\n')

agg_rows = []
for pub, grp in raw.groupby('publisher_group'):
    total_n       = grp['n'].sum()
    weighted_oc   = (grp['oc']     * grp['n']).sum() / total_n
    weighted_pos  = (grp['pos_rt'] * grp['n']).sum() / total_n * 100
    # champion = title with most Steam recommendations
    champ_idx     = grp['recommendations'].idxmax()
    champ_title   = grp.loc[champ_idx, 'title']
    champ_recs    = grp.loc[champ_idx, 'recommendations']
    pub_recs      = grp['recommendations'].sum()
    champ_share   = champ_recs / pub_recs * 100 if pub_recs > 0 else 0
    champ_label   = CHAMPION_ABBREV.get(champ_title, champ_title)
    agg_rows.append({
        'publisher_group': pub,
        'weighted_oc':     weighted_oc,
        'weighted_pos':    weighted_pos,
        'total_reviews':   total_n,
        'champion':        champ_title,
        'champion_label':  champ_label,
        'champion_share':  champ_share,
    })

pub_df = pd.DataFrame(agg_rows)
pub_df['delta'] = pub_df['weighted_pos'] - pub_df['weighted_oc']

# ── Print verification table ───────────────────────────────────────
print('\n── Publisher aggregates ───────────────────────────────────────')
print(f'{"Publisher":<14} {"Wtd OC":>7} {"Wtd Pos%":>9} '
      f'{"Champion":<22} {"Champ%":>7} {"Δ":>6} {"Line"}')
print('─' * 80)
for _, r in pub_df.sort_values('publisher_group').iterrows():
    side = 'ABOVE' if r['delta'] > 0 else 'below'
    print(f'{r["publisher_group"]:<14} {r["weighted_oc"]:>7.1f} '
          f'{r["weighted_pos"]:>9.1f} {r["champion_label"]:<22} '
          f'{r["champion_share"]:>6.1f}% {r["delta"]:>+6.1f}  {side}')
print('─' * 80 + '\n')

# ── Bubble sizes ───────────────────────────────────────────────────
r_min = pub_df['total_reviews'].min()
r_max = pub_df['total_reviews'].max()
pub_df['sz'] = 400 + 1800 * (pub_df['total_reviews'] - r_min) / (r_max - r_min)

# ── Axis ranges — extra headroom for displaced labels ─────────────
XMIN = pub_df['weighted_oc'].min()  - 4
XMAX = pub_df['weighted_oc'].max()  + 11   # SIE label goes right
YMIN = pub_df['weighted_pos'].min() - 5
YMAX = pub_df['weighted_pos'].max() + 10   # upper cluster labels go up

# ── Figure ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(1200/180, 800/180), dpi=180, facecolor=BG)
ax  = fig.add_axes([0.12, 0.13, 0.81, 0.74])
ax.set_facecolor(BG)
ax.set_xlim(XMIN, XMAX)
ax.set_ylim(YMIN, YMAX)

# ── Grid & spines ──────────────────────────────────────────────────
ax.grid(axis='both', color=GRID_COL, linewidth=0.7, linestyle='-', alpha=0.9)
ax.set_axisbelow(True)
ax.tick_params(colors='#4A5A7A', labelsize=9, length=3, width=0.6)
for spine in ax.spines.values():
    spine.set_edgecolor('#1A2540')
    spine.set_linewidth(0.8)

# ── Diagonal shading ───────────────────────────────────────────────
diag_x = np.array([min(XMIN, YMIN), max(XMAX, YMAX)])
diag_y = diag_x

ax.fill_between(diag_x, diag_y, YMAX,
                color='#071420', alpha=0.4, zorder=1)
ax.fill_between(diag_x, YMIN, diag_y,
                color='#150808', alpha=0.4, zorder=1)

# ── Reference diagonal ────────────────────────────────────────────
ax.plot([XMIN, XMAX], [XMIN, XMAX],
        color='#4A6A9A', linewidth=1.5, linestyle='--',
        alpha=0.7, zorder=2)

# ── Zone labels ────────────────────────────────────────────────────
_pill = dict(boxstyle='round,pad=0.45', edgecolor='none', alpha=0.72)

ax.text(XMIN + (XMAX - XMIN) * 0.02, YMAX - (YMAX - YMIN) * 0.02,
        'overdelivered',
        fontsize=8.5, color='#7BAFD4', ha='left', va='top',
        zorder=4, bbox=dict(facecolor='#0A1828', **_pill))

ax.text(XMAX - (XMAX - XMIN) * 0.02, YMIN + (YMAX - YMIN) * 0.02,
        'underdelivered',
        fontsize=8.5, color='#D4827B', ha='right', va='bottom',
        zorder=4, bbox=dict(facecolor='#1A0808', **_pill))

# ── Per-publisher label layout ─────────────────────────────────────
# (tx, ty, ha) where ty = Y of champion line, name sits 1.9 above.
# Upper-right trio: take_two → upper-left, sega → upper-center, sie → right
# Middle pair:      square_enix → left,  bandai_namco → right
# Lower pair:       ea → left,  ubisoft → lower-right
LABEL_LAYOUT = {
    # tx, ty (bottom of % line), ha
    # sega: immediately above blue circle, left edge flush with bubble left
    'sega_atlus':   (83.02, 93.5,  'left'),
    # take_two: sits in the open space between sega and square enix labels
    'take_two':     (82.5,  85.5,  'right'),
    # sie: right of orange circle, block v-centred on bubble (ty = cy - 2.0)
    'sie':          (89.5,  86.68, 'left'),
    # square_enix: left of red circle, block v-centred on bubble
    'square_enix':  (81.0,  78.78, 'right'),
    # bandai_namco: south-east of yellow circle, just below-right
    'bandai_namco': (86.7,  74.5,  'left'),
    # ea: above orange square, flush with square's left edge
    'ea':           (76.16, 66.5,  'left'),
    # ubisoft: right of grey square, block v-centred on bubble
    'ubisoft':      (78.3,  55.66, 'left'),
}

# ── Bubbles ────────────────────────────────────────────────────────
_stroke = [pe.withStroke(linewidth=3, foreground='#080B14'), pe.Normal()]

for _, row in pub_df.iterrows():
    pub    = row['publisher_group']
    x, y   = row['weighted_oc'], row['weighted_pos']
    sz     = row['sz']
    color  = PUBLISHER_COLORS[pub]
    is_jp  = pub in JP_TARGETS
    marker = 'o' if is_jp else 's'

    # Filled bubble
    ax.scatter(x, y, s=sz, c=color, marker=marker,
               alpha=0.92, linewidths=0, zorder=5)

    # Border ring
    edge_color = '#FFFFFF' if is_jp else '#888888'
    edge_width = 2.2       if is_jp else 1.0
    edge_alpha = 0.80      if is_jp else 0.45
    ax.scatter(x, y, s=sz, c='none', marker=marker,
               edgecolors=edge_color, linewidths=edge_width,
               alpha=edge_alpha, zorder=6)

    # ── Connector line (bubble centre → label anchor) ─────────────
    tx, ty, ha = LABEL_LAYOUT[pub]
    label_mid_y = ty + 2.0   # vertical midpoint of the now-taller 4-line block
    ax.plot([x, tx], [y, label_mid_y],
            color='#2A3A5A', linewidth=0.7, linestyle=':',
            alpha=0.75, zorder=3, clip_on=False)

    # ── Label — line 1: publisher name ───────────────────────────
    display = DISPLAY_NAMES[pub]
    ax.text(tx, ty + 4.0, display,
            fontsize=10.5, color='#D0D8E8', fontweight='bold',
            ha=ha, va='bottom', zorder=10, clip_on=False,
            path_effects=_stroke)

    # ── Label — lines 2-4: most recommended / champion / share (fontsize=7) ──
    ax.text(tx, ty + 2.6, 'most recommended:',
            fontsize=7, color='#8898AA',
            ha=ha, va='bottom', zorder=10, clip_on=False,
            path_effects=_stroke)

    ax.text(tx, ty + 1.3, row['champion_label'],
            fontsize=7, color='#8898AA',
            ha=ha, va='bottom', zorder=10, clip_on=False,
            path_effects=_stroke)

    ax.text(tx, ty, f'{row["champion_share"]:.1f}%',
            fontsize=7, color='#8898AA',
            ha=ha, va='bottom', zorder=10, clip_on=False,
            path_effects=_stroke)

# ── Axes labels ────────────────────────────────────────────────────
ax.set_xlabel('OC Score', fontsize=10, color='#6A7A9A', labelpad=8)
ax.set_ylabel('Steam Positive Rate', fontsize=10, color='#6A7A9A', labelpad=8)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}'))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))

# ── Legend ─────────────────────────────────────────────────────────
legend_elements = [
    Line2D([0], [0], marker='o', color='w',
           markerfacecolor='#888888', markersize=8,
           markeredgecolor='#CCCCCC', markeredgewidth=1.2,
           label='JP publisher', linestyle='None'),
    Line2D([0], [0], marker='s', color='w',
           markerfacecolor='#888888', markersize=7,
           markeredgecolor='#AAAAAA', markeredgewidth=0.8,
           label='Western benchmark', linestyle='None'),
    Line2D([0], [0], color='#4A6A9A', linewidth=1.5,
           linestyle='--', label='Expectations line'),
]

ax.legend(
    handles=legend_elements,
    loc='lower right',
    bbox_to_anchor=(0.98, 0.06),
    fontsize=8.5,
    labelcolor='#8898AA',
    framealpha=0.30,
    facecolor='#0C1220',
    edgecolor='#1A2540',
    borderpad=0.7,
    handletextpad=0.6,
    labelspacing=0.5,
)

# ── Title ──────────────────────────────────────────────────────────
fig.text(0.5, 0.935,
         'PC Port Execution Quality',
         fontsize=14, color='#C8D4E8', ha='center', va='bottom',
         fontweight='bold')

# ── Save ───────────────────────────────────────────────────────────
out = OUT_DIR / 'hero_chart.png'
plt.savefig(out, dpi=180, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print(f'Saved → {out}')
plt.close()
