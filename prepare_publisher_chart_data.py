"""
prepare_publisher_chart_data.py — The Platform Shift
Pre-computes publisher-level chart data weighted by Steam recommendations.
Output: data/processed/NB04_publisher_chart.csv
"""

import json
import pandas as pd
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
PROCESSED    = SCRIPT_DIR / 'data' / 'processed'
RAW_DETAILS  = SCRIPT_DIR / 'data' / 'raw' / 'details'

PUBLISHER_COLORS = {
    'sie':          '#C4611A',
    'bandai_namco': '#9A7820',
    'sega_atlus':   '#2A5F9E',
    'square_enix':  '#A02828',
    'ea':           '#B04818',
    'take_two':     '#2A4A98',
    'ubisoft':      '#4A5868',
}

CHAMPION_ABBREV = {
    'God of War Ragnarök':          'GoW Ragnarök',
    'Final Fantasy VII Rebirth':    'FF7 Rebirth',
    'Persona 5 Royal':              'Persona 5 Royal',
    'Elden Ring':                   'Elden Ring',
    'Red Dead Redemption 2':        'Red Dead 2',
    'EA Sports FC 24':              'FC 24',
    "Assassin's Creed Shadows":     'AC: Shadows',
}

# ── Load feature matrix ────────────────────────────────────────────
df = pd.read_csv(
    PROCESSED / 'NB06_feature_matrix.csv',
    usecols=['appid', 'title', 'publisher_group',
             'oc_score', 'window_pos_rate', 'window_n'],
)
df = df.dropna(subset=['oc_score', 'window_pos_rate'])
df = df[df['publisher_group'].isin(PUBLISHER_COLORS)].copy()
df['oc']     = df['oc_score'].astype(float)
df['pos_rt'] = df['window_pos_rate'].astype(float)
df['n']      = df['window_n'].astype(float)

# ── Load Steam recommendations ─────────────────────────────────────
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

df['recommendations'] = df['appid'].map(recs).fillna(0).astype(int)

# ── Aggregate per publisher ────────────────────────────────────────
rows = []
for pub, grp in df.groupby('publisher_group'):
    total_recs  = grp['recommendations'].sum()
    if total_recs > 0:
        weighted_oc  = (grp['oc']     * grp['recommendations']).sum() / total_recs
        weighted_pos = (grp['pos_rt'] * grp['recommendations']).sum() / total_recs * 100
    else:
        weighted_oc  = grp['oc'].mean()
        weighted_pos = grp['pos_rt'].mean() * 100

    champ_idx    = grp['recommendations'].idxmax()
    champ_title  = grp.loc[champ_idx, 'title']
    champ_recs   = grp.loc[champ_idx, 'recommendations']
    champ_share  = champ_recs / total_recs * 100 if total_recs > 0 else 0
    champ_label  = CHAMPION_ABBREV.get(champ_title, champ_title)

    rows.append({
        'publisher_group': pub,
        'weighted_oc':     round(weighted_oc,  4),
        'weighted_pos':    round(weighted_pos, 4),
        'total_recs':      int(total_recs),
        'champion':        champ_label,
        'champion_share':  round(champ_share, 2),
    })

out_df = pd.DataFrame(rows).sort_values('publisher_group').reset_index(drop=True)

# ── Save ───────────────────────────────────────────────────────────
out_path = PROCESSED / 'NB04_publisher_chart.csv'
out_df.to_csv(out_path, index=False)
print(f'Saved → {out_path}\n')

# ── Verification table ─────────────────────────────────────────────
print(f"{'Publisher':<14} {'Wtd OC':>7} {'Wtd Pos%':>9} "
      f"{'Total recs':>12} {'Champion':<24} {'Champ%':>7}")
print('─' * 80)
for _, r in out_df.iterrows():
    print(f"{r['publisher_group']:<14} {r['weighted_oc']:>7.1f} "
          f"{r['weighted_pos']:>9.1f} {r['total_recs']:>12,} "
          f"{r['champion']:<24} {r['champion_share']:>6.1f}%")
print('─' * 80)
print(f"{'TOTAL':<14} {'':>7} {'':>9} {out_df['total_recs'].sum():>12,}\n")
