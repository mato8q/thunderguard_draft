# IMAG Architecture

IMAG is a reimplementation of the Immune Memory Adaptive Guard pipeline
from the IMAG paper. It detects jailbreak prompts by extracting hidden-state
vectors from a safety-critical transformer layer, comparing those vectors
against attack and benign immune memory, and optionally running a slower
active-immunity check for ambiguous cases.

The implementation has two runtime modes:

- `main.py`: interactive demo and REPL. It persists memory to
  `data/memory.npz` and follows the full two-stage pipeline.
- `evaluate.py`: dataset runner. It pre-encodes prompts once, then replays
  classification in memory for one or more thresholds.

## Directory Layout

```text
IMAG/
|-- core/
|   `-- llm_interface.py       # Hugging Face model wrapper
|-- data/
|   `-- seed_prompts.py        # Handcrafted attack and benign seed prompts
|-- modules/
|   |-- active_immunity.py     # Stage 2 simulation/reflection fallback
|   |-- immune_detector.py     # Stage 1 top-k, SVD, distance classifier
|   `-- memory_bank.py         # Short-term and long-term immune memory
|-- evaluate.py                # Dataset evaluation and threshold sweeps
|-- main.py                    # Interactive pipeline runner
`-- results/                   # Generated evaluation CSVs
```

## Core Data Model

The main value passed between modules is a hidden-state vector:

```text
prompt -> TargetLLM.extract_hidden_states(...) -> h_x in R^d
```

`TargetLLM` loads a Hugging Face causal LM with `transformers`, exposes hidden
states for a selected layer, and supports two pooling modes:

- `last`: final-token vector, matching the paper's default.
- `mean`: average over all tokens, useful when final-token representations
  collapse.

Layer indices are the indices from Hugging Face `hidden_states`, where index
`0` is the embedding layer and transformer layers start at `1`.

## Stage 1: Immune Detection

`modules/immune_detector.py` implements the fast classifier.

For an input vector `h_x`:

1. Retrieve the top `K` nearest attack memory vectors by cosine similarity.
2. Retrieve the top `K` nearest benign memory vectors by cosine similarity.
3. Stack each group into matrices `H_a` and `H_b`.
4. Run SVD and keep the first right-singular vector as the rank-1 reference
   direction for attack and benign memory.
5. Unit-normalize `h_x` and compare Euclidean distances:
   `s_a = ||h_a - h_x||_2`, `s_b = ||h_b - h_x||_2`.
6. Compute `gap = s_b - s_a`.

Classification:

```text
gap >  T  -> ATTACK
gap < -T  -> BENIGN
otherwise -> CANDIDATE
```

The SVD direction is sign-aligned to the memory mean before normalization.
Without this, the arbitrary sign of singular vectors can invert distance
comparisons.

## Stage 2: Active Immunity

`modules/active_immunity.py` is only called for `CANDIDATE` prompts when active
immunity is enabled.

It uses the same `TargetLLM.generate()` interface as a local dual-agent system:

```text
candidate prompt
  -> simulation agent produces a safe/helpful response
  -> action extractor labels the response as "refuse" or "respond"
  -> reflection agent checks the prompt, action, response, and safety policy
  -> rref True means ATTACK, False means BENIGN
```

The reflection prompt uses six safety categories: toxicity, misinformation
harms, socioeconomic harms, information safety, malicious use, and human
autonomy.

## Memory Architecture

`modules/memory_bank.py` stores two long-term banks and one short-term buffer:

```text
long-term attack memory: M_a
long-term benign memory: M_b
short-term buffer:       M_S
```

Update rules:

- Confident Stage-1 `ATTACK` or `BENIGN` results go to short-term memory via
  `stage1_add()`, then `flush_short_term()` promotes them to long-term memory
  and saves to disk.
- Stage-2 verified results go directly to long-term memory through
  `add_attack()` or `add_benign()`.
- If Stage 2 is disabled, `CANDIDATE` becomes `BENIGN` for reporting, but it is
  not added to memory.

This separation matters because uncertain samples should not contaminate the
reference geometry.

## Interactive Pipeline

`main.py` wires the full Algorithm 1 flow:

```text
load TargetLLM
  -> load or search critical layer
  -> load MemoryBank from data/memory.npz
  -> seed memory if empty
  -> create ImmuneDetector and ActiveImmunity
  -> run sanity prompts
  -> enter REPL
```

Per prompt:

```text
prompt
  -> extract h_x from critical layer
  -> if memory is empty, force CANDIDATE
  -> Stage 1 detection
  -> confident label:
       stage1_add -> flush_short_term -> return label
  -> candidate:
       ActiveImmunity.evaluate
       add verified vector directly to long-term memory
       return label
```

`main.py` uses `data/critical_layer.txt` as a single interactive cache and
`data/memory.npz` as the persistent memory bank.

## Evaluation Pipeline

`evaluate.py` is optimized for experiments. It separates expensive GPU work
from cheap CPU threshold replay:

```text
Phase A:
  load model
  choose critical layer
  encode seed prompts
  load datasets
  encode all dataset prompts once

Phase B:
  for each threshold T:
    create a fresh in-memory MemoryBank
    classify cached vectors with NumPy
    optionally run ActiveImmunity for candidates
    compute metrics
    write one CSV under results/
```

The evaluator does not call `MemoryBank.__init__()` for classification. It
constructs an in-memory bank with `MemoryBank.__new__`, fills `_lt_attack` and
`_lt_benign` directly, and avoids disk I/O so threshold sweeps stay independent.

Dataset behavior:

- Attack datasets: `autodan`, `zulu`, `base64`, `drattack`.
- Benign datasets: `xstest`, `jailbreakbench`, `wildjailbreak`.
- `--dataset all` expands to all attack and benign datasets.
- If only attack datasets are requested, benign datasets are auto-added so FPR
  can still be measured.
- Attack datasets are evaluated directly; attack memory comes from
  `build_seed_vectors()` using `--seeds advbench`, `handcrafted`, or `mixed`.
- Benign datasets reserve their first `N_DATASET_SEEDS` samples as benign
  memory seeds and evaluate the remainder.
- Attack-dataset runs use actual benign seeds from the included benign
  datasets when available, falling back to global handcrafted benign seeds.

## Dataset Inputs

Dataset paths are resolved relative to `evaluate.py`, across the sibling
`adversarial-prompt/` tree:

```text
../adversarial-prompt/data/original/
|-- harmful_behaviors.csv
|-- hex_phi.csv
|-- xstest_benign.csv
|-- jailbreakbench_benign.csv
`-- wildjailbreak_benign.csv

../adversarial-prompt/data/transformed/
|-- autodan_transformed_820.csv
|-- zulu_prompts.csv
|-- base64_prompts.csv
`-- drattack_results_<model>.csv
```

AutoDAN prompts contain a literal `[REPLACE]` placeholder; `_load_autodan_texts`
replaces it with the harmful `goal` before encoding.

DrAttack first looks for a model-specific file based on the model short name,
then falls back to `drattack_results_mistral.csv`.

## Critical Layer Caches

Critical layer selection is model-specific because the hidden-state geometry is
model-specific.

- `main.py` uses `data/critical_layer.txt`.
- `evaluate.py --find-critical-layer` writes
  `data/critical_layer_<sanitized-model-name>.txt`.
- `evaluate.py` otherwise uses `--critical-layer`, defaulting to `31`, the
  Mistral-7B paper default.

Do not collapse these caches into one shared file across models.

## Generated Artifacts

Generated files are local experiment outputs:

```text
data/memory.npz
data/eval_memory.npz
data/critical_layer*.txt
results/*.csv
```

They are safe to regenerate and should not be treated as source files.

## Extension Points

Common changes usually belong in one of these places:

- Add or adjust seed prompts in `data/seed_prompts.py`.
- Change hidden-state extraction, pooling, or layer search in
  `core/llm_interface.py`.
- Tune Stage-1 geometry, top-k retrieval, threshold behavior, or SVD handling in
  `modules/immune_detector.py`.
- Change memory promotion or persistence semantics in `modules/memory_bank.py`.
- Modify Stage-2 safety policy or reflection logic in
  `modules/active_immunity.py`.
- Add datasets, metrics, sweeps, or experiment-specific seed handling in
  `evaluate.py`.

When changing detection behavior, keep pooling, critical layer, and seed
strategy together in the experiment notes. Those three settings define the
representation space being compared.
