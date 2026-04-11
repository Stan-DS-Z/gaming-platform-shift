# The Platform Shift — Strategic Analysis Report
## Japanese Publisher PC Strategy 2022-2025

> *While global gaming stagnated 2022-2024, Japanese publishers executed
> divergent PC strategies with results visible in Steam data but invisible
> in IR filings alone.*

**Data:** 46 titles | 228,776 Steam reviews | 7 publishers | 46 OC scores
**Sentiment:** VADER (228,776) + DistilBERT (22,796, EN) + Claude API (2,270, multilingual)
**Model:** Logistic Regression, LOOCV acc=0.80, AUC=0.79, n=46 titles
**HHI source:** Steam App Details recommendations (uncapped) — Bandai Namco most concentrated, Square Enix most diversified

---

## Publisher Profile

Publisher           SIE Bandai Namco Sega/Atlus Square Enix
Titles               10            8          8          11
Rev CAGR          13.2%         6.4%      10.9%       -2.0%
OC Score           87.5         84.8       84.0        83.0
VADER Compound   +0.211       +0.158     +0.219      +0.210
% Positive        88.7%        79.2%      89.0%       80.8%
PC Neg Rate        7.7%         3.6%       3.8%        9.0%
HHI               0.424        0.574      0.225       0.177
Top Title Share   63.2%        75.1%      32.7%       31.6%
English %         46.4%        44.2%      48.2%       46.3%
Model Acc           80%          75%        88%         91%

---

## Recommendations

### 1 — Sony Interactive Entertainment
- OC: 87.5 | Positive: 88.7% | HHI: 0.424 (moderately concentrated)
- GoW arc: +0.026 | Horizon arc: -0.023 (stable franchise sentiment)
- Best: Marvel's Spider-Man Remastered (96.0%) | Worst: Helldivers 2 (73.6%)
- **Rec:** Accelerate console-to-PC cadence toward day-and-date releases.
- **Risk:** Worst title (Helldivers 2) shows system not infallible at compressed timelines.

### 2 — Bandai Namco Entertainment
- OC: 84.8 | Positive: 79.2% | HHI: 0.574 (most concentrated JP target)
- Elden Ring = 75.1% of total Steam recommendations (OC 95.1)
- Non-Elden Ring catalog avg: 77.5% positive | Dragon Ball arc: -0.005
- **Rec:** Apply Elden Ring porting standard to anime IP catalog. Start with Tekken.
- **Risk:** Port quality may not fix underlying game design issues in anime titles.

### 3 — Sega/Atlus
- OC: 84.0 | Positive: 89.0% | HHI: 0.225 (moderately concentrated)
- Persona: sustained elite sentiment (+0.143 to +0.201) across 8+ years
- English share growing: P4G 44.1% -> P5R 32.2% -> P3R 43.6%
- LAD arc: +0.064 (strongest improving arc in corpus) | Sonic: 83.7% / 68.6%
- **Rec:** Extend Atlus globalisation model to one Sega IP. Metaphor: ReFantazio.
- **Risk:** Playbook is necessary but not sufficient — game quality (OC avg 84.0) is primary.

### 4 — Square Enix
- OC: 83.0 (range 66.4-91.9, std 8.3) | Positive: 80.8%
- PC neg rate: 9.0% (highest JP target) | HHI: 0.177 (most diversified JP target)
- Forspoken: OC 66.4, playtime r=+0.186 (advocate-deepening despite poor launch)
- Revenue CAGR: -2.0% (weakest JP target) — visible in Steam before IR filings
- **Rec:** Establish minimum PC release standard: no Denuvo >12mo, ultrawide/FPS unlock,
  90-day patch commitment, max 12-month console-to-PC window at portfolio level.
- **Risk:** Structural problems (franchise fatigue, asset sales) need different interventions.

---

## Limitations (key flags)

- Steam cursor newest-first: launch window undersampled for high-volume titles
- DistilBERT 50/50 stratification: absolute scores unreliable, rankings valid
- HHI uses Steam App Details recommendations (uncapped) — niche/JP titles may still
  underrepresent relative to playtime-based engagement vs install base
- n=46: LOOCV acc=0.80 is meaningful but model is proof-of-concept only
- FX: JPY/USD ~30% move 2022-2024 affects CAGR figures
- Console-to-PC gap excluded: registry missing console release dates
- English bias: VADER/DistilBERT unreliable for EA (~29.6% English)
- Nintendo excluded: no Steam presence — PC abstention is the data point
