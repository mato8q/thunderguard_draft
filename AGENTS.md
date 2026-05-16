# Agent Guide

This file provides guidance to AI Agent when working with code in this repository.

## Repository scope

ThunderGuard is an LLM safety research workspace. It contains two largely
independent Python projects that share datasets but use different runtimes:

- `IMAG/` — local reimplementation of the IMAG paper (Algorithm 1). Loads a
  Hugging Face causal LM directly via `transformers`, runs the two-stage
  immune-detection pipeline, and writes evaluation CSVs.
- `adversarial-prompt/` — dataset directory and runners for generating
  adversarial prompts (PAIR, DrAttack) against local **Ollama** endpoints.
  Independent virtualenv from the top-level project.

`docs/IMAG.md` is paper reference notes. `results/` holds archived top-level
evaluation outputs (per-T sweeps); `IMAG/results/` holds runs created in place.

## Environments and commands

Two virtualenvs are expected — top-level for IMAG, and a separate one inside
`adversarial-prompt/`. The Ollama runners deliberately do not share deps with
the HuggingFace pipeline.

### IMAG (top-level)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # accelerate, numpy, torch, transformers
```

Run IMAG interactively (loads the configured model, seeds memory if absent,
then enters a REPL):

```bash
cd IMAG
python main.py
```

Run dataset evaluation. `--dataset all` resolves to the union of
`ATTACK_DATASETS` (`autodan`, `zulu`, `base64`, `drattack`) and
`BENIGN_DATASETS` (`xstest`, `jailbreakbench`, `wildjailbreak`). Specifying
only attack datasets auto-appends benign datasets for FPR.

```bash
cd IMAG
python evaluate.py --dataset all --threshold 0.1 --no-active-immunity
python evaluate.py --dataset zulu base64 --threshold-sweep 0.1 0.2 0.3 0.5
python evaluate.py --model meta-llama/Llama-2-7b-chat-hf --find-critical-layer
python evaluate.py --diagnose --seeds handcrafted --pooling mean
```

`evaluate.py` has a two-phase design: Phase A encodes all prompts once on GPU,
Phase B re-runs classification on CPU for each threshold. A threshold sweep is
much cheaper than re-running the script per T.

### Adversarial prompt runners (Ollama)

```bash
cd adversarial-prompt
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen3.5:9b mistral:7b nomic-embed-text
ollama serve   # separate terminal
python run_pair.py --n 1          # smoke test
python run_drattack.py --n 1      # smoke test
```

Both runners default `--target mistral` and write to `data/transformed/`.

There is no test suite, linter, or formatter configured.

## IMAG architecture (the part that needs reading multiple files to grasp)

The IMAG pipeline is Algorithm 1 from the paper. The pieces are intentionally
small and faithful to the paper's equation numbering — comments in the code
cite `Eq. N` and `§N.M` so cross-reference rather than rename.

Data flow on a single prompt:

```
prompt ──► TargetLLM.extract_hidden_states (critical layer, "last" token)
        └► h_x ∈ ℝ^d
                │
                ▼
       ImmuneDetector.detect  (Stage 1, Eq. 1–4)
         top-K cosine retrieval → SVD rank-1 reference vectors h_a, h_b
         Euclidean gap = s_b - s_a
            gap >  T   → ATTACK
            gap < -T   → BENIGN
            |gap| ≤ T  → CANDIDATE
                │
        ┌───────┴───────────┐
        ▼                   ▼
  confident label    CANDIDATE → ActiveImmunity.evaluate (Stage 2, Eq. 5–7)
        │              dual-agent: simulate then reflect against 6-category
        │              SAFETY_POLICY → rref ∈ {True=attack, False=benign}
        ▼                   │
  MemoryBank.stage1_add ◄───┘ (Stage 2 result goes straight to long-term)
        │
        ▼
  flush_short_term → MemoryBank.{add_attack,add_benign} → save .npz
```

Key cross-file invariants to preserve when editing:

- **Critical layer is model-specific and cached.** `main.py` writes to
  `IMAG/data/critical_layer.txt` (single file). `evaluate.py` writes
  `IMAG/data/critical_layer_<sanitized-model-name>.txt`. Do not collapse these
  — sharing one cache across models corrupts the reference geometry. Paper
  default for Mistral-7B is layer 31.
- **Memory bank tiers are not interchangeable.** Stage-1 confident results go
  to short-term (`stage1_add`) and only enter long-term on `flush_short_term`.
  Stage-2-verified results go straight to long-term (`add_attack` /
  `add_benign`). `evaluate.py` short-circuits this by constructing a
  `MemoryBank.__new__` with no save path and writing directly to `_lt_attack` /
  `_lt_benign` — that bypass is intentional so the threshold sweep stays in
  memory.
- **Pooling and unit-normalization are coupled.** `ImmuneDetector` normalizes
  `h_x` before computing Euclidean distance because `_svd_rank1` already
  returns a unit vector. Changing pooling (`last` vs `mean`) is the most
  effective lever when `gap ≈ 0`; `--diagnose` exists to spot
  representation-collapse cases where attack/benign SVD directions become
  near-identical.
- **Seed strategy matters per-dataset.** `evaluate.py:build_seed_vectors`
  exposes `--seeds {advbench, handcrafted, mixed}`. AdvBench seeds only work
  well when the eval attacks were generated against the same target model;
  cross-model evaluation (e.g. Mistral-generated attacks on LLaMA-2) needs
  `handcrafted`. The benign reference for attack datasets is rebuilt from
  XSTest/JailbreakBench/WildJailbreak seeds (`actual_seed_ben`) rather than
  the global handcrafted set — the global seeds collapse with obfuscated
  attacks at deep layers.
- **AutoDAN prompts need `[REPLACE]` substitution.** `_load_autodan_texts`
  injects the harmful `goal` into the template; without substitution AutoDAN
  becomes a generic roleplay prompt indistinguishable from benign creative
  writing.
- **Stage 2 disabled → CANDIDATE becomes BENIGN, and is NOT added to memory.**
  This avoids attack samples contaminating the benign reference when active
  immunity is off (`--no-active-immunity`).

## Dataset paths

`evaluate.py` resolves dataset paths relative to itself, reaching across into
the sibling `adversarial-prompt/` tree:

- `adversarial-prompt/data/original/{harmful_behaviors.csv, hex_phi.csv,
  xstest_benign.csv, jailbreakbench_benign.csv, wildjailbreak_benign.csv}`
- `adversarial-prompt/data/transformed/{autodan_transformed_820.csv,
  zulu_prompts.csv, base64_prompts.csv, drattack_results_<model>.csv,
  pair_results_<model>.csv}`

`DrAttack` is resolved per-model: it tries
`drattack_results_<model-short>.csv` first and falls back to
`drattack_results_mistral.csv`.

## Generated artifacts

Treat as ignored / regeneratable, do not commit:

- model weights (`*.pt`, `*.bin`, `*.safetensors`, `*.gguf`, `*.ckpt`)
- `IMAG/data/memory.npz`, `IMAG/data/eval_memory.npz`
- `IMAG/data/critical_layer*.txt`
- new files under `results/` and `IMAG/results/`
- `.env`, virtualenvs

## Contributing rules (from CONTRIBUTING.md)

- Never commit directly to `main`; one branch per task, squash-merge via PR.
- Branch names: `<your-name>/<short-topic>` (e.g. `kong/feature-3`).
- Commit message format: `area: what changed` (e.g.
  `evaluate: pair XSTest with every attack dataset`,
  `attacks/zulu: generate prompts from AdvBench seeds`).
- Never force-push to `main`.
