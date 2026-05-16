# IMAG

Local reimplementation of **IMAG: Immune Memory Adaptive Guard**, an adaptive
jailbreak-detection pipeline inspired by innate immune memory.

This project loads a Hugging Face causal language model with `transformers`,
extracts hidden states from a safety-critical layer, compares them against an
evolving attack/benign memory bank, and optionally runs an active-immunity
fallback for ambiguous prompts.

For paper notes, see [`../docs/IMAG.md`](../docs/IMAG.md).

## Project Layout

```text
IMAG/
├── core/llm_interface.py        # Hugging Face model wrapper and hidden states
├── data/seed_prompts.py         # Handcrafted attack/benign seed prompts
├── modules/active_immunity.py   # Stage 2 simulation/reflection fallback
├── modules/immune_detector.py   # Stage 1 top-k + SVD + distance classifier
├── modules/memory_bank.py       # Long-term and short-term memory tiers
├── evaluate.py                  # Dataset evaluation and threshold sweeps
└── main.py                      # Interactive demo runner
```

## Setup

Create the top-level environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If needed, install a PyTorch wheel that matches your platform and CUDA version.
The scripts automatically use CUDA when available for dataset evaluation.

## Interactive Run

From this directory:

```bash
python main.py
```

`main.py` uses `mistralai/Mistral-7B-Instruct-v0.2` by default, searches or
loads `data/critical_layer.txt`, seeds `data/memory.npz` if missing, runs a
small prompt sanity check, then opens a REPL.

## Dataset Evaluation

Run all configured attack and benign datasets:

```bash
python evaluate.py --dataset all --threshold 0.1 --no-active-immunity
```

Run selected attack datasets. Benign datasets are auto-appended so false
positive rate can still be measured:

```bash
python evaluate.py --dataset zulu base64 --threshold 0.1 --no-active-immunity
```

Run a threshold sweep. Prompts are encoded once, then classification is replayed
on CPU for each threshold:

```bash
python evaluate.py --dataset all --threshold-sweep 0.1 0.2 0.3 0.5 --no-active-immunity
```

Use a different Hugging Face model:

```bash
python evaluate.py \
  --model meta-llama/Llama-2-7b-chat-hf \
  --dataset all \
  --threshold 0.1 \
  --no-active-immunity
```

Search for the model's critical layer instead of using the default layer `31`:

```bash
python evaluate.py --model meta-llama/Llama-2-7b-chat-hf --find-critical-layer
```

If attack/benign distance gaps collapse near zero, try diagnostics and mean
pooling:

```bash
python evaluate.py --dataset zulu --diagnose --seeds handcrafted --pooling mean
```

## Evaluation Options

- `--dataset`: one or more of `autodan`, `zulu`, `base64`, `drattack`,
  `xstest`, `jailbreakbench`, `wildjailbreak`, or `all`.
- `--threshold`: Euclidean distance-gap threshold for Stage 1.
- `--threshold-sweep`: evaluate multiple thresholds from one encoding pass.
- `--critical-layer`: fixed hidden-state layer index. Defaults to `31`.
- `--find-critical-layer`: search for the layer with strongest seed separation.
- `--pooling`: `last` for final-token pooling or `mean` for token averaging.
- `--seeds`: `advbench`, `handcrafted`, or `mixed` attack-memory seeds.
- `--no-active-immunity`: skip Stage 2; candidates become benign and are not
  added to memory.
- `--diagnose`: print representation-separation diagnostics.

## Pipeline

For each prompt, IMAG follows the paper's Algorithm 1:

1. Extract hidden state `h_x` from the target LLM at the critical layer.
2. Retrieve top-k attack and benign memory vectors by cosine similarity.
3. Build rank-1 attack and benign reference directions with SVD.
4. Compare Euclidean distances to classify as `ATTACK`, `BENIGN`, or
   `CANDIDATE`.
5. If active immunity is enabled, send `CANDIDATE` prompts through
   simulation/reflection and add verified results to long-term memory.
6. Add confident Stage-1 results through short-term memory, then flush them to
   long-term memory.

## Dataset Inputs

`evaluate.py` reads datasets from the sibling `adversarial-prompt/` tree:

```text
../adversarial-prompt/data/original/
├── harmful_behaviors.csv
├── hex_phi.csv
├── xstest_benign.csv
├── jailbreakbench_benign.csv
└── wildjailbreak_benign.csv

../adversarial-prompt/data/transformed/
├── autodan_transformed_820.csv
├── zulu_prompts.csv
├── base64_prompts.csv
└── drattack_results_<model>.csv
```

For DrAttack, evaluation first looks for a model-specific file and falls back
to `drattack_results_mistral.csv`.

## Generated Artifacts

These files are generated locally and should not be committed:

- `data/memory.npz`
- `data/eval_memory.npz`
- `data/critical_layer*.txt`
- new CSVs under `results/`

`main.py` uses `data/critical_layer.txt`. `evaluate.py` uses
model-specific cache files such as `data/critical_layer_meta-llama_Llama-2-7b-chat-hf.txt`
to avoid cross-model geometry contamination.
