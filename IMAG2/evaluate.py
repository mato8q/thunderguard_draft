"""
IMAG — Dataset Evaluation (faithful to Algorithm 1)
Attack prompts : HEX-Phi (category CSVs) + AdvBench (parquet)
Benign prompts : XSTest (parquet, type == "safe")

Usage:
    python evaluate.py
"""

import argparse
import os
import random
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from core.llm_interface import TargetLLM
from data.seed_prompts import SEED_ATTACKS, SEED_BENIGNS
from modules.active_immunity import ActiveImmunity
from modules.immune_detector import ImmuneDetector
from modules.memory_bank import MemoryBank

# ── Config ────────────────────────────────────────────────────────────────────

MODEL_NAME    = "mistralai/Mistral-7B-Instruct-v0.2"
TOP_K         = 5
THRESHOLD_T   = 0.5
POOLING       = "last"
MEMORY_PATH   = "data/eval_memory.npz"
LAYER_CACHE   = "data/critical_layer.txt"   # shared with main.py

# Root of the datasets folder (resolved relative to this file)
_HERE         = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR  = os.path.join(_HERE, "..", "datasets")

RANDOM_SEED   = 42

# ── Dataset paths ─────────────────────────────────────────────────────────────

# Attack datasets
HEX_PHI_DIR   = os.path.join(DATASETS_DIR, "hex_phi")          # category_N.csv (no header)
ADVBENCH_PATH = os.path.join(DATASETS_DIR, "advbench",
                              "train-00000-of-00001.parquet")   # column: "prompt"

# Benign dataset
XSTEST_PATH   = os.path.join(DATASETS_DIR, "xstest",
                              "train-00000-of-00001.parquet")   # column: "prompt", filter type=="safe"

# ── Benign loader ─────────────────────────────────────────────────────────────

def load_benign_texts(rng: random.Random) -> list[str]:
    texts = []

    # XSTest (parquet) — filter label == "safe", use "prompt" column
    if os.path.exists(XSTEST_PATH):
        df = pd.read_parquet(XSTEST_PATH)
        rows = df[df["label"] == "safe"]["prompt"].dropna().str.strip().tolist()
        rows = [r for r in rows if r]
        texts.extend(rows)
        print(f"  Loaded {len(rows)} benign from XSTest")
    else:
        print(f"  [SKIP] XSTest not found: {XSTEST_PATH}")

    if not texts:
        raise FileNotFoundError(
            f"No benign samples loaded. Check XSTEST_PATH:\n  {XSTEST_PATH}"
        )

    rng.shuffle(texts)
    return texts

# ── Attack loader ─────────────────────────────────────────────────────────────

def load_attack_texts(dataset: str, rng: random.Random) -> list[str]:
    """
    dataset: "hex_phi" | "advbench"
    """
    texts = []

    if dataset == "hex_phi":
        if os.path.isdir(HEX_PHI_DIR):
            for fname in sorted(os.listdir(HEX_PHI_DIR)):
                if not fname.startswith("category_") or not fname.endswith(".csv"):
                    continue
                fpath = os.path.join(HEX_PHI_DIR, fname)
                with open(fpath, encoding="utf-8") as f:
                    lines = [l.strip() for l in f if l.strip()]
                texts.extend(lines)
            print(f"  Loaded {len(texts)} attacks from HEX-Phi")
        else:
            print(f"  [SKIP] HEX-Phi dir not found: {HEX_PHI_DIR}")

    elif dataset == "advbench":
        if os.path.exists(ADVBENCH_PATH):
            df = pd.read_parquet(ADVBENCH_PATH)
            rows = df["prompt"].dropna().str.strip().tolist()
            rows = [r for r in rows if r]
            texts.extend(rows)
            print(f"  Loaded {len(rows)} attacks from AdvBench")
        else:
            print(f"  [SKIP] AdvBench not found: {ADVBENCH_PATH}")

    if not texts:
        raise FileNotFoundError(
            f"No attack samples loaded for dataset='{dataset}'. "
            "Check HEX_PHI_DIR and ADVBENCH_PATH."
        )

    rng.shuffle(texts)
    return texts

# ── Layer helper ──────────────────────────────────────────────────────────────

def get_critical_layer(llm: TargetLLM) -> int:
    if os.path.exists(LAYER_CACHE):
        with open(LAYER_CACHE) as f:
            layer = int(f.read().strip())
        print(f"  Critical layer (cached): {layer}")
        return layer
    layer = llm.find_critical_layer(
        SEED_ATTACKS[:min(len(SEED_ATTACKS), len(SEED_BENIGNS))],
        SEED_BENIGNS[:min(len(SEED_ATTACKS), len(SEED_BENIGNS))],
        pooling=POOLING,
    )
    os.makedirs("data", exist_ok=True)
    with open(LAYER_CACHE, "w") as f:
        f.write(str(layer))
    return layer

# ── Memory seeding ─────────────────────────────────────────────────────────────

def seed_memory(llm: TargetLLM, memory: MemoryBank, critical_layer: int):
    print(f"  Encoding seed prompts (layer {critical_layer})...")
    for p in SEED_ATTACKS:
        h = llm.extract_hidden_states(p, target_layer=critical_layer, pooling=POOLING)
        memory.add_attack(h)
    for p in SEED_BENIGNS:
        h = llm.extract_hidden_states(p, target_layer=critical_layer, pooling=POOLING)
        memory.add_benign(h)
    memory.save()
    print(f"  Seeded: {memory.stats()}")

# ── Single-prompt detection (Algorithm 1 faithful) ────────────────────────────

def detect_one(
    prompt: str,
    llm: TargetLLM,
    detector: ImmuneDetector,
    active_immunity: ActiveImmunity,
    memory: MemoryBank,
    critical_layer: int,
) -> tuple[str, float, float]:
    # Stage 1 — Immune Detection (Eq. 1–4)
    h_x = llm.extract_hidden_states(prompt, target_layer=critical_layer, pooling=POOLING)
    label, s_a, s_b = detector.detect(h_x, memory.get_attack(), memory.get_benign())

    if label != "CANDIDATE":
        # Confident Stage-1 result → short-term → long-term (Eq. 8–10)
        memory.stage1_add(h_x, label.lower())
        memory.flush_short_term()
        return label, s_a, s_b

    # Stage 2 — Active Immunity for CANDIDATE prompts (Eq. 5–7)
    label, _action, _sim, _rref = active_immunity.evaluate(prompt)

    # Stage-2 verified → directly to long-term memory (Eq. 9–10)
    if label == "ATTACK":
        memory.add_attack(h_x)
    else:
        memory.add_benign(h_x)
    memory.save()

    return label, s_a, s_b

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="IMAG dataset evaluation")
    parser.add_argument(
        "--dataset",
        choices=["hex_phi", "advbench", "xstest"],
        required=True,
        help="Dataset to evaluate: hex_phi or advbench (attack-only), xstest (benign-only)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=THRESHOLD_T,
        help=f"Euclidean distance gap needed for a confident decision (default: {THRESHOLD_T}). "
             "Lower = fewer CANDIDATE fallbacks. Try 0.1 if accuracy is low.",
    )
    args = parser.parse_args()

    rng = random.Random(RANDOM_SEED)
    print("=" * 65)
    print(f"  IMAG — Dataset Evaluation  [attack={args.dataset}]")
    print("=" * 65)

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n[1] Loading LLM: {MODEL_NAME}  (device={device})")
    llm = TargetLLM(MODEL_NAME, device=device)

    print("\n[2] Finding critical layer (Eq. 2)...")
    critical_layer = get_critical_layer(llm)

    print("\n[3] Building eval memory bank...")
    if os.path.exists(MEMORY_PATH):
        os.remove(MEMORY_PATH)
    memory = MemoryBank(save_path=MEMORY_PATH)
    seed_memory(llm, memory, critical_layer)

    # Stage 2 agent — paper §4.1 recommends GPT-4o-mini; here we reuse the
    # same target LLM for a fully local setup.
    active_immunity = ActiveImmunity(agent_llm=llm)

    print(f"\n[4] Loading dataset: {args.dataset}")
    is_benign_only = args.dataset == "xstest"

    if is_benign_only:
        attack_texts = []
        benign_texts = load_benign_texts(rng)
    else:
        attack_texts = load_attack_texts(args.dataset, rng)
        benign_texts = []

    total = len(attack_texts) + len(benign_texts)
    print(f"  Test set: {len(attack_texts)} attack, {len(benign_texts)} benign  ({total} total)")

    detector = ImmuneDetector(threshold_T=args.threshold, top_k=TOP_K)

    print("\n[5] Running detection (Algorithm 1: Stage 1 + Stage 2)...")
    print("-" * 65)

    results = []
    t_start = time.time()

    for i, text in enumerate(attack_texts):
        pred, s_a, s_b = detect_one(text, llm, detector, active_immunity, memory, critical_layer)
        results.append(("ATTACK", pred))
        elapsed = time.time() - t_start
        avg = elapsed / (i + 1)
        remaining = avg * (total - i - 1)
        print(f"  [{i+1:>3}/{total}] ATTACK  → {pred:<6}  "
              f"gap={s_b-s_a:+.4f}  ETA {remaining:.0f}s", end="\r")

    for i, text in enumerate(benign_texts):
        pred, s_a, s_b = detect_one(text, llm, detector, active_immunity, memory, critical_layer)
        results.append(("BENIGN", pred))
        done = len(attack_texts) + i + 1
        elapsed = time.time() - t_start
        avg = elapsed / done
        remaining = avg * (total - done)
        print(f"  [{done:>3}/{total}] BENIGN  → {pred:<6}  "
              f"gap={s_b-s_a:+.4f}  ETA {remaining:.0f}s", end="\r")

    print()

    print("\n" + "=" * 65)
    tp = sum(1 for t, p in results if t == "ATTACK" and p == "ATTACK")
    tn = sum(1 for t, p in results if t == "BENIGN" and p == "BENIGN")
    fp = sum(1 for t, p in results if t == "BENIGN" and p == "ATTACK")
    fn = sum(1 for t, p in results if t == "ATTACK" and p == "BENIGN")

    total_time = time.time() - t_start
    print(f"  Dataset  : {args.dataset}  ({total} samples)")
    print(f"  Layer    : {critical_layer}  |  Threshold: {args.threshold}")

    if is_benign_only:
        # XSTest — report false positive rate (FP = benign flagged as attack)
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        print(f"  Results  : TN={tn}  FP={fp}")
        print(f"\n  Pass-through Rate : {tn/(tn+fp)*100:.2f}%  (benign correctly allowed)")
        print(f"  False Positive Rate: {fpr*100:.2f}%  (benign incorrectly blocked)")
    else:
        # hex_phi / advbench — report attack detection rate
        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        print(f"  Results  : TP={tp}  FN={fn}")
        print(f"\n  Detection Rate : {detection_rate*100:.2f}%  (attacks correctly blocked)")
        print(f"  Miss Rate      : {fn/(tp+fn)*100:.2f}%  (attacks that slipped through)")

    print(f"\n  Total time: {total_time:.1f}s  ({total_time/total:.2f}s/sample)")
    print("=" * 65)


if __name__ == "__main__":
    main()
