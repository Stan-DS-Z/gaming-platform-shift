# The Platform Shift — Japanese Publisher PC Strategy Analysis (2022–2025)

> *PCへの移行は、すでに強いものをもっと強くする。*
> *A platform shift amplifies what's already there. It doesn't rescue what isn't.*

---

## Central Finding

PC is an amplifier, not a rescue.

Japanese publishers who brought strong franchises and disciplined porting systems to PC gained measurable, compounding advantages. Those who treated PC as a distribution channel for whatever they were already shipping got mixed results at best — and in some cases, gave more people a faster way to find the disappointment.

**強いコンテンツはPCで花開く。弱いコンテンツはPCで早く死ぬ。**

![PC Strategy Quality Explains the Divergence](docs/hero_chart.png)
*感情スコアと収益CAGRの相関 — 46タイトル・228,776 Steamレビューより*

The data bears this out across four publishers, 46 titles, and 228,776 Steam reviews.

---

## Publisher Theses

| Publisher | Thesis | Verdict |
|-----------|--------|---------|
| **SIE** | Systematic porting is a replicable institutional capability | ✅ Confirmed — and stronger than expected |
| **Bandai Namco** | Elden Ring validated an anime IP-to-PC pipeline | ❌ Inverted — Elden Ring *masks* pipeline failure |
| **Sega/Atlus** | Persona executed the most deliberate PC globalisation arc in JP gaming | ✅ Confirmed — LAD arc even stronger than Persona |
| **Square Enix** | Franchise fatigue is visible in Steam data before IR filings | ✅ Confirmed — but variance, not decline, is the real signal |

---

## What the Data Actually Showed

### SIE — システムとしてのPC戦略
Every SIE title in the corpus scored above OC 81. Across four studios, across a compressed timeline, across genres. That's not luck — that's institutional capability. The console-to-PC window compressed from four years (God of War 2018) to under two (Ragnarök). The quality floor held.

**Finding:** The bottleneck isn't porting capability. It's release sequencing. The infrastructure exists for day-and-date.

### Bandai Namco — エルデンリングという名の幻想
Elden Ring accounts for 75.1% of Bandai Namco's total Steam recommendations. Remove it and the catalog averages 77.5% positive — a full 2 points below the headline figure. The anime IP pipeline (Tales, Gundam, Dragon Ball, SAO) has not internalised the FromSoftware lesson. Gundam Breaker 4 is the sharpest example: the worst launch fade in the corpus, a content-depth problem misread as a port quality problem.

**Finding:** フロム・ソフトウェアがいなければ、PC戦略は存在しない。
The strategy works because of FromSoftware, not because of Bandai Namco.

### Sega/Atlus — グローバル化の設計図
The Persona franchise shows sustained elite sentiment across three PC entries — not a rising arc, but a consistently high plateau with a growing Western audience visible in the language data. P4G: 44.1% English reviews. P5R: 32.2%. P3R: 43.6%. The audience is building. The Like a Dragon rebranding produced the strongest *improving* sentiment arc in the entire corpus — measurable in Steam data, invisible in IR filings until it hits revenue.

**Finding:** The Atlus globalisation playbook is documented and repeatable. It has not been applied to Sonic, Two Point, or the classic Sega catalog.

### Square Enix — ばらつきがブランドになる
The problem isn't decline. It's variance. OC range: 66.4 (Forspoken) to 91.9 (FF7 Rebirth). Standard deviation of 8.3 — widest in the corpus. The capability clearly exists: FF7 Rebirth at 77.3% positive, NieR: Automata a beloved classic. But players cannot predict what they will get from a Square Enix PC release. That unpredictability is itself the brand signal.

The Forspoken finding is the most interesting in the project: lowest critic score in the corpus (OC 66.4) but the strongest advocate-deepening playtime signal (r=+0.186). The game had a real audience. The publisher's launch execution — and PC port quality complaints — prevented them from finding each other.

**Finding:** PC amplified the wrong signal at launch and never corrected it.
「悪い作品ではなく、悪いリリースだった。」

---

## Data Architecture

| Source | Coverage | Notes |
|--------|----------|-------|
| Steam Reviews API | 228,776 reviews, 46 titles, all languages | Cursor-paginated, newest-first — launch windows undersampled for high-volume titles |
| Steam App Details API | 46/46 titles | `recommendations` field used for HHI — uncapped total positive reviews |
| OpenCritic API (RapidAPI) | 46/46 titles | Key required — free tier, ~100 req/day limit |
| IR Annual Reports | 7 publisher groups, 2022–2025 | Gaming segment level only — PC-specific revenue not disclosed |

---

## Sentiment Pipeline

Three tiers, one purpose: prove findings are model-robust, not method artifacts.

| Tier | Model | Sample | Scope |
|------|-------|--------|-------|
| 1 | VADER | 228,776 reviews | Full corpus, all languages — English-only lexicon |
| 2 | DistilBERT | 22,796 reviews | Stratified English sample — higher accuracy, known sampling artifact |
| 3 | Claude Haiku API | 2,270 reviews | Proportional multilingual sample — theme extraction + pc_specific signal |

Publisher-level rankings are consistent across all three tiers. Convergence validates the aggregate findings regardless of individual model limitations.

**The key finding from tier 3:** When players explicitly mention the PC version, negative commentary (150 reviews) outweighs positive (93) across the corpus. PC port quality is a differentiating factor — and a vulnerability.

---

## Predictive Model

**Business question:** Can early signals predict whether a PC port will achieve positive long-term reception?

**Target:** Binary — lifetime positive rate ≥ 75%
**Method:** Logistic Regression (L2, LOOCV), Decision Tree (max_depth=3, interpretable)
**Result:** LOOCV accuracy 0.80, AUC 0.79 (vs 0.717 majority-class baseline)

**Top predictors:**
1. `oc_score` — critic consensus at launch (coef +0.85)
2. `vader_compound` — player sentiment (coef +0.84)
3. `cl_pc_specific_neg_rt` — PC-specific negative commentary rate (coef −0.30)
4. `english_pct` — reflects corpus composition, not a causal claim (coef −0.79)

The model is a proof-of-concept at n=46. The feature importance is the finding, not the accuracy number.

---

## Notebook Map

| Notebook | What It Does | Key Output |
|----------|-------------|------------|
| NB01 | Steam extraction & validation | 228,776 reviews, 46 titles, 46/46 App Details |
| NB02 | IR financial extraction | Revenue CAGR by publisher group, FX-adjusted |
| NB03 | Publisher & platform analysis | Port timing cadence, SIE compression arc |
| NB04 | Sentiment deep dive | VADER + DistilBERT + Claude API three-tier pipeline |
| NB05 | Franchise intelligence | Launch delta, playtime-sentiment r, franchise arcs, HHI |
| NB06 | Predictive model | Logistic regression + decision tree, LOOCV, feature importance |
| NB07 | Recommendations | One strategic recommendation per publisher + `NB07_report.md` |
| `/dashboard` | Streamlit app | Interactive public dashboard — deploy last |

---

## Key Metrics

**Launch Quality Delta** — steady-state positive rate minus first-30-day rate. Positive = recovered after rough launch. Negative = hype faded. *Caveat: Steam's newest-first cursor means launch windows are undersampled for older high-volume titles with the 5k review cap.*

**Playtime-Sentiment Correlation** — Pearson r between `author_playtime_forever` and VADER compound per title (English reviews, 99th percentile cap on playtime). Positive r = advocates deepen. Negative r = burnout signal.

**Console→PC Gap** — days between original console release and Steam launch. Core SIE cadence metric. *Not computable for all titles — registry contains PC release dates only.*

**HHI (Franchise Concentration)** — Herfindahl index on Steam `recommendations` (total positive reviews, uncapped) per publisher. Source: `data/raw/details/{appid}.json`. Replaces review count proxy — Elden Ring's 810k+ recommendations correctly dominates Bandai Namco's HHI at 0.574.

**pc_specific Signal** — Claude API tier tags whether each review explicitly comments on the PC version (`yes_positive` / `yes_negative` / `not_mentioned`). The ratio of yes_negative to yes_positive per publisher is the port quality signal.

---

## Tracked Titles (46)

**SIE (10):** God of War (2018), God of War Ragnarök, Horizon Zero Dawn, Horizon Forbidden West, Spider-Man Remastered, Spider-Man: Miles Morales, The Last of Us Part I, Helldivers 2, Returnal, Ratchet & Clank: Rift Apart

**Bandai Namco (8):** Elden Ring, Tekken 8, Dragon Ball FighterZ, Dragon Ball: Sparking! Zero, Ace Combat 7, Tales of Arise, Gundam Breaker 4, Little Nightmares II

**Sega/Atlus (8):** Like a Dragon: Infinite Wealth, Yakuza: Like a Dragon, Persona 3 Reload, Persona 4 Golden, Persona 5 Royal, Sonic Frontiers, Sonic Superstars, Two Point Campus

**Square Enix (11):** FF7 Remake Intergrade, FF7 Rebirth, FF XVI, FF XIV Online, Dragon Quest XI S, Octopath Traveler, Octopath Traveler II, NieR: Automata, NieR Replicant, Forspoken, Marvel's Avengers

**Benchmarks (8):** EA Sports FC 24, EA Sports FC 25, Apex Legends, GTA V, Red Dead Redemption 2, Borderlands 3, Assassin's Creed Mirage, Assassin's Creed Shadows, Star Wars Outlaws

*Note: Nintendo excluded — no Steam presence. PC abstention is itself a strategic data point.*


---

## Predictive Model — Feature Importance

![Predictive Model: Feature Importance & Per-Publisher Accuracy](docs/NB06_model_chart.png)
*OC scoreとVADER感情スコアが最強の予測因子 — 出版社別LOOCVスコア内訳*

The two strongest predictors of long-term Steam reception: critic score at launch and player sentiment.
The two strongest negative predictors: PC-specific negative commentary rate, and English review share
(a corpus composition effect — high English share co-occurs with western benchmark titles in this dataset).

---

## Known Limitations

- Steam cursor newest-first: launch window reviews absent for older high-volume titles at 5k cap
- DistilBERT 50/50 stratified sampling: absolute scores unreliable, publisher rankings valid
- n=46 for predictive model: proof-of-concept, not production predictor
- IR revenue at gaming segment level: PC-specific revenue not publicly disclosed
- FX sensitivity: JPY/USD moved ~30% 2022–2024, CAGR figures directional
- Console→PC gap: registry missing console release dates
- OpenCritic RapidAPI: free tier rate limit (~100 req/day) — extraction requires two sessions

---

## Environment

```bash
conda env create -f environment.yml
conda activate platform_shift
python -m ipykernel install --user --name platform_shift --display-name "Platform Shift"
jupyter lab
```

**Dependency notes:**
- `torch==2.3.1+cpu` — do not upgrade, DLL conflicts on Windows CPU env
- `transformers==4.40.0`, `tokenizers==0.19.1`, `safetensors==0.4.3` — pin these
- Parquet skipped — pyarrow conda/pip conflict in this env; CSV throughout, no analytical impact
- OpenCritic API key: add `RAPIDAPI_KEY=your_key` to `.env` before running NB06

---

## Coding Standards

- `USE_CACHE = True` at top of every notebook
- All outputs → `../data/processed/`
- No hardcoded values in observation cells — all numbers from live DataFrames
- JP font loop: MS Gothic → Yu Gothic → Meiryo → IPAGothic
- Each notebook runs independently — load CSVs at top, no cross-notebook kernel state

---

## Differentiation vs. Matthew Ball *State of Video Gaming 2025*

Ball's report (231pp) is aggregate, Western-centric, Newzoo/Ampere/IDG data. Japanese publishers are peripheral.

This project is title-level, JP publisher lens, with Steam data Ball doesn't use:

1. **Japanese publisher focus** — SIE, Bandai Namco, Sega/Atlus, Square Enix barely appear in Ball
2. **PC port quality as measurable signal** — `pc_specific` commentary, launch delta, playtime r
3. **Franchise arc analysis** — sentiment trajectory across sequential releases
4. **Multilingual corpus** — 45–70% non-English reviews handled natively via Claude API
5. **IR × Steam cross-analysis** — Square Enix revenue decline visible in Steam data pre-earnings
6. **Predictive model** — early signals → long-term reception, interpretable features
7. **The amplifier thesis** — PC strategy quality, not volume, explains divergence

*「データはすでにそこにある。読み方を知っているかどうかだけの話だ。」*
The data was always there. It's just a question of knowing how to read it.
