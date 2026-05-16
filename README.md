# ThunderGuard

ThunderGuard is a LLM safety research project inspired by the IMAG framework,
with team contributions in forgetting mechanisms, embedding-based detection,
and latency reduction.

This workspace includes:

- `docs/IMAG.md`: paper reference notes for IMAG: An Adaptive Jailbreak
  Detection Framework Inspired by Innate Immune Memory.
- `IMAG/`: local reimplementation of the IMAG paper ideas. It classifies
  prompts as `ATTACK`, `BENIGN`, or `CANDIDATE` using hidden-state memory,
  SVD-based retrieval, and an active-immunity fallback.
- `adversarial-prompt/`: local adversarial prompt datasets and runners for
  generating or evaluating Base64, Zulu, PAIR, DrAttack, AutoDAN, and benign
  prompt sets.

This is not a production network firewall or hosted moderation service.

## Repository Layout

```text
.
├── docs/IMAG.md          # IMAG paper reference notes
├── IMAG/                 # Local IMAG reimplementation and evaluation CLI
├── adversarial-prompt/   # Datasets and local PAIR/DrAttack runners
├── requirements.txt      # Minimal dependencies for IMAG
└── results/              # Generated/archived evaluation outputs
```

## Setup

Use Python 3.10 or newer.

```bash
git clone https://github.com/mato8q/thunderguard_draft.git
cd thunderguard_draft
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install a PyTorch build that matches your platform and CUDA version if the
default wheel is not appropriate for your machine.

The IMAG defaults expect a Hugging Face causal language model:

```bash
cd IMAG
python main.py
```

For dataset evaluation:

```bash
cd IMAG
python evaluate.py --dataset all --threshold 0.1 --no-active-immunity
```

Large model weights, generated memory banks, critical-layer caches, and new
result files are treated as generated artifacts and ignored by default.
