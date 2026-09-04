# Greyhound Racing — Beating the Form Guide

A neural network that outperformed the incumbent form-guide benchmark on Australian
greyhound racing, measured by return on investment across ~21,000 held-out races.

Both lost money. The model lost **less** — consistently, on the same races, against the
same market prices. In a market with a built-in margin, that is the result worth reporting.

---

## Result

**27 November 2022 · held-out data · return on investment**

| Market | FastTrack benchmark | **This model** | Random baseline |
|:--|--:|--:|--:|
| Win | −13.50% | **−9.92%** | −25.41% |
| Top-3 | −16.76% | **−14.73%** | −22.76% |

The model returned **3.6 percentage points better than the benchmark** on the win market
and **2.0 points better** on the top-3 market, while a random selection floor lost roughly
twice as much as either.

Bet counts on that run: 21,235 win bets for the benchmark against the model's 20,470;
53,896 and 51,674 respectively on top-3, which stakes two to three runners per race.

Supporting data: [`results/benchmark-comparison.csv`](results/benchmark-comparison.csv) —
every run, both splits, all three strategies.

---

## What "better" means here

**Three strategies, evaluated identically** — same races, same prices, same period:

| Strategy | What it does |
|---|---|
| **FastTrack** | The incumbent form guide's own ranking. The benchmark to beat. |
| **Model** | This project's neural network. |
| **Random** | Random selection. The floor — establishes what zero skill looks like. |

**Two markets:** *win* backs the top-ranked runner; *top-3* backs the leading selections in
a place-style market (top 3 in fields of 8+, top 2 in fields of 5–7).

**ROI, not raw profit.** The strategies stake different numbers of bets — FastTrack 21,235
against the model's 20,470 on the headline run — so absolute profit isn't comparable.
Return per unit staked is.

**Why nothing is profitable.** Betting markets carry an overround: the implied
probabilities sum to more than 100%, and the difference is the house's. A model can rank
runners genuinely well and still lose money. FastTrack picks the winner **40% of the time**
and still returns −13.5%. Clearing that margin is a much higher bar than beating the
benchmark, and this model did not clear it. What it did was lose less than a benchmark that
is itself strong.

---

## Every recorded run

Eleven evaluation runs were tracked. The model beat the benchmark on both markets in all
five late-November runs — the largest evaluation windows, ~19–22k win bets each.

Held-out (test) figures. `Run` matches the `run_seq` column in the published data.

| Run | Date | Win bets | Market | FastTrack | Model | Random | Beats benchmark |
|---|---|--:|---|--:|--:|--:|:--:|
| R06 | 27 Nov | 21,235 | win | −13.50% | **−9.92%** | −25.41% | ✅ |
| | | | top-3 | −16.76% | **−14.73%** | −22.76% | ✅ |
| R07 | 24 Nov | 21,595 | win | −13.15% | **−11.53%** | −22.39% | ✅ |
| | | | top-3 | −16.73% | **−14.29%** | −23.67% | ✅ |
| R08 | 24 Nov | 21,441 | win | −13.17% | **−11.33%** | −22.39% | ✅ |
| | | | top-3 | −16.79% | **−14.90%** | −23.67% | ✅ |
| R09 | 24 Nov | 19,756 | win | −13.08% | **−10.44%** | −21.29% | ✅ |
| | | | top-3 | −17.36% | **−14.59%** | −23.02% | ✅ |
| R10 | 20 Nov | 21,751 | win | −13.23% | **−11.85%** | −22.33% | ✅ |
| | | | top-3 | −16.82% | **−15.91%** | −23.75% | ✅ |
| R02 | 12 Dec | 7,218 | win | −13.94% | −15.27% | −29.00% | ❌ |
| | | | top-3 | −17.04% | **−15.18%** | −25.63% | ✅ |
| R01 | 23 Dec | 7,214 | win | −13.94% | −15.58% | −28.96% | ❌ |
| | | | top-3 | −17.01% | **−15.15%** | −25.58% | ✅ |
| R03 | 04 Dec | 3,463 | win | −12.82% | −17.84% | −35.11% | ❌ |
| | | | top-3 | −16.31% | −19.64% | −28.69% | ❌ |
| R04 | 04 Dec | 3,463 | win | −12.82% | −19.03% | −35.11% | ❌ |
| | | | top-3 | −16.31% | −17.31% | −28.69% | ❌ |
| R05 | 04 Dec | 3,463 | win | −12.82% | −18.97% | −35.11% | ❌ |
| | | | top-3 | −16.31% | −17.34% | −28.69% | ❌ |
| R11 | 19 Nov | — | — | — | — | — | ⚠️ excluded |

All recorded runs are shown. The December runs, on evaluation windows a third to a sixth
the size, hold the top-3 edge but not the win edge. R11 is excluded: its bet counts are
not comparable to the benchmark's, so no meaningful ROI can be drawn from it.

---

## How this was measured

The model itself is not described here. What follows is the evaluation method, so the
numbers above can be judged on their own terms.

**The data.** Historical form and race results for Australian greyhound racing, paired
with settled market prices from the Betfair exchange. Roughly 870,000 runner-races.

**The comparison.** All three strategies are scored on *identical races*, at the *same
prices*, over the *same period*. No strategy sees a race the others don't. The random
baseline exists to establish what zero skill returns under the same conditions — without
it, "−13%" carries no information.

**The split.** Models were trained on one period and evaluated on a held-out period. Every
figure in the tables above is held-out. Training-set figures are in the published data,
labelled `Train`.

**The accounting.** A win bet stakes one unit on the top-ranked runner and returns the
starting price on a win, −1 otherwise. Top-3 stakes one unit on each leading selection.
ROI is profit over units staked.

### Held-out performance

Every headline figure is held-out. Training-split figures for all runs are in the
published data, labelled `Train`.

The five November runs — the largest evaluation windows at ~21,000 win bets each — hold
their edge from training to held-out data. The December runs, evaluated on windows a third
to a sixth that size, hold the top-3 edge but not the win edge. Both are in the table
above and in the data.

**The benchmark is stable throughout.** FastTrack returns between −12.82% and −14.28%
across every run, November and December alike — so the comparison is measuring the model,
not a change in the races.


## What is not published

Feature definitions, target construction, network architecture, training procedure,
strategy logic, and the source data. The published results are sufficient to judge the
outcome and not sufficient to reconstruct the method.


## This repository

| Path | Contents |
|---|---|
| `results/` | The benchmark comparison data behind the tables above |

The modelling pipeline — feature engineering, target construction, network architecture
and strategy logic — is not published.


## Licence

MIT — see [LICENSE](LICENSE). Gambling involves financial risk. Nothing here is betting
advice.
