# Seed Overlap — Cross-Attack Seed Evaluation

Tests whether IMAG's memory bank generalizes when the seed attack family
differs from the evaluation attack family.

## Setup

| Field             | Value                                  |
|-------------------|----------------------------------------|
| Model             | `mistralai/Mistral-7B-Instruct-v0.2`   |
| Critical layer    | 31                                     |
| Threshold T       | 0.1                                    |
| Active immunity   | OFF (`--no-active-immunity`)           |
| Pooling           | `last`                                 |
| Seeds per branch  | 30 (first N prompts of the source CSV) |

Only `--seeds` and `--dataset` vary between runs.

## Results

| Run          | `--seeds`  | `--dataset` | F1     | Accuracy | Gap-mean (attack) | Attack n |
|--------------|------------|-------------|--------|----------|-------------------|----------|
| Baseline     | advbench   | autodan     | 1.0000 | 1.0000   | +0.87150          | 820      |
| Cross&nbsp;A | drattack   | autodan     | 0.0000 | 0.0000   | +0.02674          | 820      |
| Cross&nbsp;B | autodan    | drattack    | 0.4701 | 0.3073   | +0.20660          | 820      |

F1 / accuracy / attack row sourced from the `dataset == "autodan"` (Baseline,
Cross A) and `dataset == "drattack"` (Cross B) rows of each result CSV.
Gap-mean computed over the per-sample `gap` values where `true_label = ATTACK`
in the matching `_gaps.csv`.

## Source files

- Baseline result : `Mistral-7B-Instruct-v0.2_autodan_xstest_jailbreakbench_wildjailbreak_t0.1_noAI_20260518_015927.csv`
- Baseline gaps   : `Mistral-7B-Instruct-v0.2_autodan_xstest_jailbreakbench_wildjailbreak_t0.1_noAI_20260518_015927_gaps.csv`
- Cross A result  : `Mistral-7B-Instruct-v0.2_autodan_xstest_jailbreakbench_wildjailbreak_t0.1_noAI_20260518_020446.csv`
- Cross A gaps    : `Mistral-7B-Instruct-v0.2_autodan_xstest_jailbreakbench_wildjailbreak_t0.1_noAI_20260518_020446_gaps.csv`
- Cross B result  : `Mistral-7B-Instruct-v0.2_drattack_xstest_jailbreakbench_wildjailbreak_t0.1_noAI_20260518_020929.csv`
- Cross B gaps    : `Mistral-7B-Instruct-v0.2_drattack_xstest_jailbreakbench_wildjailbreak_t0.1_noAI_20260518_020929_gaps.csv`

(All under `IMAG/results/`. Baseline and Cross A share the same dataset list in
their filenames; they are distinguishable only by timestamp — Baseline first,
Cross A second.)

## Benign FPR sanity check

Benign datasets (xstest, jailbreakbench, wildjailbreak) report FPR = 0.0 in
all three result CSVs — the seed swap moves the attack gap, not the benign
gap. Source: same CSVs above, `dataset` rows other than the attack row.

## Observation

The cross-attack F1 drop is sharp and asymmetric in this configuration.
Replacing the AdvBench seed bank with DrAttack seeds (Cross A) collapses
AutoDAN detection from F1 = 1.0000 to F1 = 0.0000 — the attack gap-mean falls
from +0.87 to +0.03, below T = 0.1, so every AutoDAN prompt becomes CANDIDATE
and is relabeled BENIGN (Stage 2 disabled). Using AutoDAN seeds against
DrAttack (Cross B) generalizes partially (F1 = 0.4701, recall = 0.3073), with
an attack gap-mean of +0.21 — above T for ~30% of prompts but bimodal.

Caveat: these numbers are at T = 0.1 with active immunity OFF. A higher T
would only push more samples into CANDIDATE; Stage 2 (`--no-active-immunity`
absent) could recover some of the Cross A loss but was not run here per the
fixed-flag constraint.
