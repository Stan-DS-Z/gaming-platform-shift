# The Platform Shift

**日本のパブリッシャーは、PCへの移行をうまく実行できているか？**
Are Japanese publishers executing their PC shift well?

日本の主要パブリッシャー4社と欧米ベンチマーク3社のPC戦略を、
228,776件のSteamレビューとOpenCriticスコアで検証したデータ分析プロジェクト。
A data project examining how well Japanese publishers are executing 
their PC strategy — measured through 228,776 Steam reviews and 
OpenCritic scores across 46 titles.

![PC Port Execution Quality — 46 titles, 228,776 Steam reviews](docs/hero_chart.png)

<p align="center">
  <a href="https://ss-gaming-platform-shift.streamlit.app/">
    <img src="https://img.shields.io/badge/%F0%9F%8E%AE_%E3%83%80%E3%83%83%E3%82%B7%E3%83%A5%E3%83%9C%E3%83%BC%E3%83%89-ss--gaming--platform--shift.streamlit.app-9A7820?style=for-the-badge" alt="Dashboard">
  </a>
</p>

<p align="center">
  46タイトル · 228,776件のSteamレビュー · 日本パブリッシャー4社＋欧米ベンチマーク3社 · 2022–2025<br>
  <em>46 titles · 228,776 Steam reviews · 4 JP publishers + 3 Western benchmarks · 2022–2025</em>
</p>

---

## このプロジェクトについて / About

日本の大手パブリッシャーはコンソール向けタイトルをPCに展開してきた。
移植の出来は、タイトルによって大きく異なる。

このプロジェクトは、公開データのみを使ってその差を測定する試みだ。
OpenCriticスコア（批評家の合意）とSteamポジティブ率（プレイヤーの評価）を
比較することで、どのパブリッシャーがIPの期待値に応えた移植を行い、
どのパブリッシャーが期待を下回ったかを可視化する。

Japanese publishers have been bringing console titles to PC. 
How well those ports landed with players varies considerably.

This project uses only public data to measure that gap. 
By comparing OpenCritic scores (critic consensus at launch) against 
Steam positive rates (PC player reception), it identifies which 
publishers delivered ports that met — or fell short of — 
the expectations set by the underlying IP.

---

## データの限界について / A note on what this data can and cannot show

このプロジェクトはSteamレビュー、OpenCriticスコア、IR財務資料のみを使用している。
タイトル単位のPC売上は非公開のため、「PC移行が収益にどう影響したか」という問いには
公開データだけでは答えられない。

このプロジェクトが答えられるのは別の問いだ——
**各パブリッシャーは、IPの期待値に見合ったPC移植を実行できているか？**

PC売上データ、プラットフォーム別マージン、コンソールとPCのオーディエンス重複率など
内部データへのアクセスがあれば、この分析は収益インパクトの検証まで拡張できる。
それがこのプロジェクトを作った理由でもある。

This project uses only Steam reviews, OpenCritic scores, and IR 
filings. No publisher discloses PC-specific revenue at title level, 
so the question "did the PC shift drive revenue?" cannot be answered 
from public data alone.

What public data can answer is a different question —
**did each publisher deliver a port that met the expectations set 
by the underlying IP?**

Access to internal data — PC unit sales, platform-specific margins, 
console-to-PC audience overlap — would allow this analysis to be 
extended to revenue impact. That is the reason this project exists.

---

## 分析の枠組み / Analytical Framework

**期待値ライン（対角線）**
批評家スコア（OC）とプレイヤー評価（Steamポジティブ率）が等しい場合、
バブルは対角線上に位置する。対角線より上＝移植が期待を上回った。
対角線より下＝移植が期待を下回った。

**加重平均**
各パブリッシャーの数値はSteam推薦数で加重した平均値。
推薦数の多いタイトル（より多くのプレイヤーに届いたタイトル）が
ポートフォリオ全体の位置を決める。

**The expectations line (diagonal)**
When OC score and Steam positive rate are equal, a bubble sits on 
the diagonal. Above the line = port overdelivered relative to critic 
consensus. Below the line = port underdelivered.

**Weighted averages**
Each publisher's position is a weighted average using Steam 
recommendations as the weight. Titles that reached more players 
carry more weight in the portfolio average.

---

## パブリッシャー別の観察 / Publisher Observations

**SIE**
コーパス内10タイトル全てがOpenCritic 81以上を記録。4スタジオ、
複数ジャンルにまたがる一貫したスコアは注目に値する。
コンソール→PCのリリース間隔はGod of War 2018の4年から
Ragnarökの2年未満へと短縮されており、スコアは維持されている。
最多推薦タイトル：Helldivers 2（推薦数の63.2%）。

Every SIE title in the corpus scored above OC 81, across four 
studios and multiple genres. The console-to-PC release window 
compressed from four years (God of War 2018) to under two 
(Ragnarök) without a drop in reception scores.
Most recommended: Helldivers 2 (63.2% of portfolio recommendations).

**Bandai Namco**
Elden RingがSteam総推薦数の75.1%を占める（HHI: 0.574）。
同タイトルを除外するとカタログ平均ポジティブ率は77.5%に低下する。
残りのIPラインナップ（テイルズ、ガンダム、ドラゴンボール）の
PC実績はElden Ringの水準に達していない。

Elden Ring accounts for 75.1% of Bandai Namco's total Steam 
recommendations (HHI: 0.574). Excluding it, the catalogue's 
average positive rate falls to 77.5%. The remaining IP lineup — 
Tales, Gundam, Dragon Ball — has not matched Elden Ring's 
PC reception.

**Sega/Atlus**
ペルソナシリーズはPC3作品にわたり安定した高評価を維持。
龍が如くシリーズのリブランディング（Yakuza: Like a Dragon → 
Like a Dragon: Infinite Wealth）はコーパス内で顕著な
感情値の改善弧を示した。
最多推薦タイトル：Persona 5 Royal（推薦数の32.7%）。

The Persona franchise holds sustained high positive rates across 
three PC entries. The Like a Dragon rebranding shows a notable 
improving arc in the corpus.
Most recommended: Persona 5 Royal (32.7% of portfolio recommendations).

**Square Enix**
OC範囲：66.4（Forspoken）〜91.9（FF7 Rebirth）。
標準偏差8.3はコーパス最大。
Forspokenは批評家スコアでは最低値だが、プレイ時間と感情値の
相関（r=+0.186）はコーパス最高——批評家評価には反映されなかった
支持層の存在を示唆する。
最多推薦タイトル：NieR: Automata（推薦数の31.5%）。

OC range: 66.4 (Forspoken) to 91.9 (FF7 Rebirth). 
Standard deviation of 8.3, the widest in the corpus.
Forspoken scores lowest on critic reception, but records the 
highest playtime-sentiment correlation (r = +0.186) — 
suggesting an audience the launch execution did not reach.
Most recommended: NieR: Automata (31.5% of portfolio recommendations).

---

## 分析パイプライン / Sentiment Pipeline

| 層 / Tier | モデル / Model | サンプル / Sample | 目的 / Scope |
|-----------|--------------|-----------------|------------|
| 1 | VADER | 228,776件 / reviews | 全コーパス・全言語 / Full corpus, all languages |
| 2 | DistilBERT | 22,796件 / reviews | 層化英語サンプル / Stratified English sample |
| 3 | Claude Haiku API | 2,270件 / reviews | 多言語・テーマ抽出 / Multilingual theme extraction |

---

## 予測モデル / Predictive Model

**問い / Question:** ローンチ時点のシグナルでPC移植の長期受容を予測できるか？
Can launch-window signals predict long-term PC reception?

ロジスティック回帰（L2、LOOCV）。精度0.80、AUC 0.79。
n=46は概念実証——**特徴量重要度の序列**が主要な発見であり、
精度の数値ではない。

最も強い正の予測因子：OCスコアとVADER複合値。
最も強い負の予測因子：PC特有ネガティブ率。

Logistic Regression (L2, LOOCV). Accuracy 0.80, AUC 0.79.
At n=46 this is a proof-of-concept — the **feature importance 
ranking** is the primary finding, not the accuracy figure.

Strongest positive predictors: OC score and VADER compound.
Strongest negative predictor: PC-specific negative rate.

![Predictive Model: Feature Importance & Per-Publisher Accuracy](docs/NB06_model_chart.png)

---

## IR財務データについて / IR Financial Data

7社の財務データ（2022–2025）をIR資料から取得・標準化した。
ゲーミングセグメント売上のみで、PC特有の売上は非公開。
n=7かつFX変動±30%のため、財務データは定量的な結論ではなく
文脈として参照する。

IR financials for 7 publisher groups (2022–2025) were extracted 
and FX-standardised. Gaming segment level only — PC-specific 
revenue is not disclosed. With n=7 and ±30% FX movement over 
the study period, financial data is used as context, 
not for quantitative conclusions.

---

## データソース / Data Architecture

| ソース / Source | カバレッジ / Coverage | 備考 / Notes |
|----------------|---------------------|-------------|
| Steam Reviews API | 228,776 reviews, 46 titles | Cursor-paginated, newest-first |
| Steam App Details API | 46/46 titles | `recommendations` field for weighting and HHI |
| OpenCritic API (RapidAPI) | 46/46 titles | Free tier, ~100 req/day |
| IR Annual Reports | 7 publishers, 2022–2025 | Gaming segment level |

---

## 主要指標 / Key Metrics

**Launch Quality Delta** — ローンチ初期30日間のポジティブ率と
生涯平均の差。正の値はラフなスタートからの回復を示す。
Steady-state positive rate minus first-30-day rate.

**Playtime-Sentiment Correlation** — プレイ時間とVADER複合値の
ピアソン相関（英語レビュー、99パーセンタイルキャップ）。
Pearson r between playtime and VADER compound per title.

**Console→PC Gap** — コンソールリリースからSteamリリースまでの日数。
Days between original console release and Steam launch.

**HHI** — Steam推薦数によるポートフォリオ集中度指数。
0.25超で特定タイトルへの集中を示す。
Herfindahl-Hirschman Index on Steam recommendations per publisher.

**pc_specific Signal** — Claude APIによる意味解析で
レビューがPC版を明示的に評価しているか判定。
Claude API semantic tagging of whether a review explicitly 
comments on the PC version.

---

## 収録タイトル / Tracked Titles (46)

**SIE (10):** God of War (2018), God of War Ragnarök, 
Horizon Zero Dawn, Horizon Forbidden West, 
Spider-Man Remastered, Spider-Man: Miles Morales, 
The Last of Us Part I, Helldivers 2, Returnal, 
Ratchet & Clank: Rift Apart

**Bandai Namco (8):** Elden Ring, Tekken 8, 
Dragon Ball FighterZ, Dragon Ball: Sparking! Zero, 
Ace Combat 7, Tales of Arise, Gundam Breaker 4, 
Little Nightmares II

**Sega/Atlus (8):** Like a Dragon: Infinite Wealth, 
Yakuza: Like a Dragon, Persona 3 Reload, 
Persona 4 Golden, Persona 5 Royal, Sonic Frontiers, 
Sonic Superstars, Two Point Campus

**Square Enix (11):** FF7 Remake Intergrade, FF7 Rebirth, 
FF XVI, FF XIV Online, Dragon Quest XI S, 
Octopath Traveler, Octopath Traveler II, NieR: Automata, 
NieR Replicant, Forspoken, Marvel's Avengers

**Benchmarks (9):** EA Sports FC 24, EA Sports FC 25, 
Apex Legends, GTA V, Red Dead Redemption 2, Borderlands 3, 
Assassin's Creed Mirage, Assassin's Creed Shadows, 
Star Wars Outlaws

*Nintendo excluded — no Steam presence.*

---

## ノートブック構成 / Notebook Map

| ノートブック | 目的 | 主要出力 |
|------------|------|---------|
| NB01 | Steam抽出・検証 | 228,776 reviews, 46 titles |
| NB02 | IR財務抽出 | Revenue CAGR by publisher, FX-adjusted |
| NB03 | プラットフォーム分析 | Port timing cadence, console→PC gap |
| NB04 | 感情分析 | VADER + DistilBERT + Claude API |
| NB05 | フランチャイズ分析 | Launch delta, playtime r, HHI |
| NB06 | 予測モデル | Logistic regression, LOOCV |
| NB07 | 提言 | Strategic observations per publisher |
| `app.py` | Streamlitダッシュボード | [Live →](https://ss-gaming-platform-shift.streamlit.app/) |

---

## 既知の限界 / Known Limitations

- Steam APIは最新順にレビューを返す。5,000件キャップにより、
  古い高ボリュームタイトルのローンチ期レビューが過少サンプリングされる
- DistilBERTは50/50層化サンプリングを使用。絶対スコアは信頼性が低いが、
  パブリッシャー間のランキングは保持される
- 予測モデルはn=46の概念実証であり、本番グレードの予測器ではない
- IR収益データはゲーミングセグメントレベル。PC特有の収益は非公開
- 研究期間中のJPY/USD変動は約30%。CAGR数値は方向性を示すものに留まる
- OpenCritic RapidAPI無料枠は1日約100リクエストに制限される

---

## 環境 / Environment

```bash
conda env create -f environment.yml
conda activate platform_shift
python -m ipykernel install --user --name platform_shift \
  --display-name "Platform Shift"
jupyter lab
```

- `torch==2.3.1+cpu` — Windows CPU環境でのDLL競合回避のためpin
- `transformers==4.40.0`, `tokenizers==0.19.1`, `safetensors==0.4.3` — pin済み
- pyarrow conda/pipコンフリクトのためCSVを全面使用。分析上の影響なし
- NB06実行前に`.env`へ`RAPIDAPI_KEY=your_key`を追加

---

*Analysis by Stanley Shi · [LinkedIn](https://www.linkedin.com/in/stanley-shi-7b604b104/) · 2026*
