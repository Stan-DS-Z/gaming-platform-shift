# The Platform Shift

![PC Strategy Quality Explains the Divergence](docs/hero_chart.png)

> **PCへの移行は、すでに強いものをもっと強くする。弱いものは、もっと早く見つかるだけだ。**
>
> *A platform shift amplifies what's already there. It doesn't rescue what isn't.*

<p align="center">
  <a href="https://ss-gaming-platform-shift.streamlit.app/">
    <img src="https://img.shields.io/badge/%F0%9F%8E%AE_ダッシュボード-ss--gaming--platform--shift.streamlit.app-9A7820?style=for-the-badge" alt="Dashboard">
  </a>
</p>

<p align="center">
  46タイトル · 228,776件のSteamレビュー · 日本パブリッシャー4社＋欧米ベンチマーク3社 · 2022–2025<br>
  <em>46 titles · 228,776 Steam reviews · 4 JP publishers + 3 Western benchmarks · 2022–2025</em>
</p>

---

## 🇯🇵 日本語

### 中心的な発見

PCは救済ではなく、**増幅器**だ。

強いフランチャイズと規律あるポーティング体制をPCに持ち込んだ日本パブリッシャーは、測定可能で複利的な優位性を得た。PCを「出していたものを流すだけのチャンネル」として扱ったパブリッシャーは、良くて結果はまちまち——悪ければ、失望をより早く、より多くの人に届けただけだった。

PC移植の「量」（R²≈0.01）は収益軌道を予測しない。移植の「質」が予測する。

### パブリッシャー仮説と評価

| パブリッシャー | 仮説 | 評価 |
|------------|------|------|
| **SIE** | 組織的なポーティングは再現可能な制度的能力である | ✅ 確認 — 予想以上に強い |
| **バンダイナムコ** | エルデンリングがアニメIP→PCパイプラインを証明した | ❌ 逆説的 — エルデンリングがパイプラインの失敗を*隠蔽* |
| **セガ/アトラス** | ペルソナは日本ゲーム業界で最も計画的なPCグローバル化を実行した | ✅ 確認 — 龍が如くの弧はペルソナ以上 |
| **スクウェア・エニックス** | フランチャイズ疲弊がIR開示前にSteamデータで可視化できる | ✅ 確認 — ただし衰退ではなくばらつきが真のシグナル |

### データが示したもの

**SIE — システムとしてのPC戦略**
コーパス内の全SIEタイトルがOC 81以上。4スタジオ、圧縮されたタイムライン、ジャンル横断で。これは偶然ではなく、制度的能力だ。コンソール→PCの窓は4年（God of War 2018）から2年未満（Ragnarök）に圧縮された。品質の底が維持された。

**バンダイナムコ — エルデンリングという名の幻想**
エルデンリングはバンダイナムコのSteam総推薦数の75.1%を占める。これを除くとカタログ平均は77.5% — 見出しの数字より2ポイント低い。アニメIPパイプライン（テイルズ、ガンダム、ドラゴンボール）はフロム・ソフトウェアの教訓を内在化していない。

**セガ/アトラス — グローバル化の設計図**
ペルソナは3つのPC作品で持続的な高評価を示す。龍が如くのリブランディングはコーパス全体で最も強い*改善*感情弧を生み出した — Steamデータで測定可能、IR開示では収益に反映されるまで不可視。

**スクウェア・エニックス — ばらつきがブランドになる**
問題は衰退ではない。ばらつきだ。OC範囲：66.4（Forspoken）〜91.9（FF7 Rebirth）。標準偏差8.3 — コーパス最大。プレイヤーはスクエニのPCリリースで何が得られるか予測できない。その予測不能性自体がブランドシグナルだ。

### 分析パイプライン

| 層 | モデル | サンプル | 目的 |
|----|--------|---------|------|
| 1 | VADER | 228,776件 | 全コーパス・全言語 — 英語のみの辞書 |
| 2 | DistilBERT | 22,796件 | 層化英語サンプル — 高精度、サンプリングアーティファクトあり |
| 3 | Claude Haiku API | 2,270件 | 比例多言語サンプル — テーマ抽出＋PC特有シグナル |

3層による検証：パブリッシャーランキングは全モデルで一貫。個別モデルの限界に関わらず集計結果の妥当性を保証。

### 予測モデル

ビジネス問い：初期シグナルでPC移植の長期的受容を予測できるか？

ロジスティック回帰（L2、LOOCV）。精度0.80、AUC 0.79（多数決ベースライン0.717に対して）。n=46は概念実証 — 精度ではなく**特徴量重要度**が発見。

最強の正の予測因子：OCスコア（批評家合意）とVADER複合値（プレイヤー感情）。最強の負の予測因子：PC特有ネガティブ率（移植品質は測定可能な負債）。

---

## 🇬🇧 English

### Central Finding

PC is an amplifier, not a rescue.

Japanese publishers who brought strong franchises and disciplined porting systems to PC gained measurable, compounding advantages. Those who treated PC as a distribution channel for whatever they were already shipping got mixed results at best — and in some cases, gave more people a faster way to find the disappointment.

Port *volume* (R² ≈ 0.01) does not predict revenue trajectory. Port *quality* does.

### Publisher Theses

| Publisher | Thesis | Verdict |
|-----------|--------|---------|
| **SIE** | Systematic porting is a replicable institutional capability | ✅ Confirmed — stronger than expected |
| **Bandai Namco** | Elden Ring validated an anime IP-to-PC pipeline | ❌ Inverted — Elden Ring *masks* pipeline failure |
| **Sega/Atlus** | Persona executed the most deliberate PC globalisation arc in JP gaming | ✅ Confirmed — LAD arc even stronger than Persona |
| **Square Enix** | Franchise fatigue is visible in Steam data before IR filings | ✅ Confirmed — but variance, not decline, is the real signal |

### What the Data Showed

**SIE — Porting as institutional capability.**
Every SIE title in the corpus scored above OC 81. Across four studios, a compressed timeline, and multiple genres. The console-to-PC window compressed from four years (God of War 2018) to under two (Ragnarök). The quality floor held.

**Bandai Namco — The Elden Ring illusion.**
Elden Ring accounts for 75.1% of Bandai Namco's total Steam recommendations. Remove it and the catalog averages 77.5% positive — 2 points below the headline figure. The anime IP pipeline (Tales, Gundam, Dragon Ball) has not internalised the FromSoftware lesson.

**Sega/Atlus — The globalisation blueprint.**
Persona shows sustained elite sentiment across three PC entries. The Like a Dragon rebranding produced the strongest *improving* sentiment arc in the entire corpus — measurable in Steam data, invisible in IR filings until it hits revenue.

**Square Enix — Variance is the brand.**
The problem isn't decline. It's variance. OC range: 66.4 (Forspoken) to 91.9 (FF7 Rebirth). Standard deviation of 8.3 — widest in the corpus. Players cannot predict what they will get from a Square Enix PC release. That unpredictability is itself the brand signal.

The Forspoken finding is the most interesting in the project: lowest critic score in the corpus but the strongest advocate-deepening playtime signal (r = +0.186). The game had a real audience. The publisher's launch execution prevented them from finding each other.

### Sentiment Pipeline

Three tiers, one purpose: prove findings are model-robust, not method artifacts.

| Tier | Model | Sample | Scope |
|------|-------|--------|-------|
| 1 | VADER | 228,776 reviews | Full corpus, all languages — English-only lexicon |
| 2 | DistilBERT | 22,796 reviews | Stratified English sample — higher accuracy, known sampling artifact |
| 3 | Claude Haiku API | 2,270 reviews | Proportional multilingual sample — theme extraction + pc_specific signal |

Publisher-level rankings are consistent across all three tiers. Convergence validates the aggregate findings regardless of individual model limitations.

### Predictive Model

**Business question:** Can early signals predict whether a PC port will achieve positive long-term reception?

Logistic Regression (L2, LOOCV). Accuracy 0.80, AUC 0.79 (vs 0.717 majority-class baseline). n=46 is a proof-of-concept — the **feature importance** is the finding, not the accuracy number.

Top positive predictors: OC score (critic consensus at launch) and VADER compound (player sentiment). Top negative predictor: PC-specific negative commentary rate — port quality is a measurable liability.

![Predictive Model: Feature Importance & Per-Publisher Accuracy](docs/NB06_model_chart.png)
*OC scoreとVADER感情スコアが最強の予測因子 — 出版社別LOOCVスコア内訳*

---

## Data Architecture

| Source | Coverage | Notes |
|--------|----------|-------|
| Steam Reviews API | 228,776 reviews, 46 titles, all languages | Cursor-paginated, newest-first — launch windows undersampled for high-volume titles |
| Steam App Details API | 46/46 titles | `recommendations` field used for HHI — uncapped total positive reviews |
| OpenCritic API (RapidAPI) | 46/46 titles | Key required — free tier, ~100 req/day limit |
| IR Annual Reports | 7 publisher groups, 2022–2025 | Gaming segment level only — PC-specific revenue not disclosed |

---

## Key Metrics

**Launch Quality Delta** — steady-state positive rate minus first-30-day rate. Positive = recovered after rough launch. Negative = hype faded.

**Playtime-Sentiment Correlation** — Pearson r between `author_playtime_forever` and VADER compound per title (English reviews, 99th percentile cap). Positive r = advocates deepen. Negative r = burnout signal.

**Console→PC Gap** — days between original console release and Steam launch. Core SIE cadence metric.

**HHI (Franchise Concentration)** — Herfindahl index on Steam `recommendations` per publisher. Elden Ring's 810k+ recommendations drive Bandai Namco's HHI to 0.574.

**pc_specific Signal** — Claude API tier tags whether each review explicitly comments on the PC version. The ratio of negative to positive PC-specific mentions per publisher is the port quality signal.

---

## Tracked Titles (46)

**SIE (10):** God of War (2018), God of War Ragnarök, Horizon Zero Dawn, Horizon Forbidden West, Spider-Man Remastered, Spider-Man: Miles Morales, The Last of Us Part I, Helldivers 2, Returnal, Ratchet & Clank: Rift Apart

**Bandai Namco (8):** Elden Ring, Tekken 8, Dragon Ball FighterZ, Dragon Ball: Sparking! Zero, Ace Combat 7, Tales of Arise, Gundam Breaker 4, Little Nightmares II

**Sega/Atlus (8):** Like a Dragon: Infinite Wealth, Yakuza: Like a Dragon, Persona 3 Reload, Persona 4 Golden, Persona 5 Royal, Sonic Frontiers, Sonic Superstars, Two Point Campus

**Square Enix (11):** FF7 Remake Intergrade, FF7 Rebirth, FF XVI, FF XIV Online, Dragon Quest XI S, Octopath Traveler, Octopath Traveler II, NieR: Automata, NieR Replicant, Forspoken, Marvel's Avengers

**Benchmarks (9):** EA Sports FC 24, EA Sports FC 25, Apex Legends, GTA V, Red Dead Redemption 2, Borderlands 3, Assassin's Creed Mirage, Assassin's Creed Shadows, Star Wars Outlaws

*Nintendo excluded — no Steam presence. PC abstention is itself a strategic data point.*

---

## Notebook Map

| Notebook | What It Does | Key Output |
|----------|-------------|------------|
| NB01 | Steam extraction & validation | 228,776 reviews, 46 titles |
| NB02 | IR financial extraction | Revenue CAGR by publisher group, FX-adjusted |
| NB03 | Publisher & platform analysis | Port timing cadence, SIE compression arc |
| NB04 | Sentiment deep dive | VADER + DistilBERT + Claude API three-tier pipeline |
| NB05 | Franchise intelligence | Launch delta, playtime-sentiment r, HHI |
| NB06 | Predictive model | Logistic regression + decision tree, LOOCV |
| NB07 | Recommendations | Strategic recommendation per publisher |
| `app.py` | Streamlit dashboard | [Live dashboard →](https://ss-gaming-platform-shift.streamlit.app/) |

---

## Known Limitations

- Steam cursor newest-first: launch window reviews absent for older high-volume titles at 5k cap
- DistilBERT 50/50 stratified sampling: absolute scores unreliable, publisher rankings valid
- n=46 for predictive model: proof-of-concept, not production predictor
- IR revenue at gaming segment level: PC-specific revenue not publicly disclosed
- FX sensitivity: JPY/USD moved ~30% 2022–2024, CAGR figures directional
- Console→PC gap: registry missing some console release dates
- OpenCritic RapidAPI: free tier rate limit (~100 req/day)

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
- Parquet skipped — pyarrow conda/pip conflict in this env; CSV throughout
- OpenCritic API key: add `RAPIDAPI_KEY=your_key` to `.env` before running NB06

---

## Coding Standards

- `USE_CACHE = True` at top of every notebook
- All outputs → `../data/processed/`
- No hardcoded values — all numbers from live DataFrames
- JP font loop: MS Gothic → Yu Gothic → Meiryo → IPAGothic
- Each notebook runs independently — no cross-notebook kernel state

---

*「データはすでにそこにある。読み方を知っているかどうかだけの話だ。」*

*The data was always there. It's just a question of knowing how to read it.*
