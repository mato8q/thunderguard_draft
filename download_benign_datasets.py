"""
Download benign prompt datasets from HuggingFace and save as CSV.

Targets:
  1. JailbreakBench/JBB-Behaviors  → adversarial-prompt/data/original/jailbreakbench_benign.csv
  2. allenai/wildjailbreak          → adversarial-prompt/data/original/wildjailbreak_benign.csv
  3. Paul/xstest                    → adversarial-prompt/data/original/xstest_benign.csv

Each output CSV has a single column: prompt
"""

import os
import csv
from datasets import load_dataset

OUT_DIR = os.path.join(os.path.dirname(__file__), "adversarial-prompt", "data", "original")
os.makedirs(OUT_DIR, exist_ok=True)


def save_csv(rows: list[str], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["prompt"])
        for r in rows:
            writer.writerow([r])
    print(f"  Saved {len(rows)} rows → {path}")


def debug_dataset(ds, name: str):
    print(f"\n  [{name}] Column names: {ds.column_names}")
    print(f"  [{name}] First row: {dict(list(ds[0].items()))}")


# ── 1. JailbreakBench ─────────────────────────────────────────────────────────

print("=" * 60)
print("[1] Loading JailbreakBench/JBB-Behaviors ...")
_JBB_LOCAL = os.path.join(os.path.dirname(__file__), "datasets", "jailbreakbench")
try:
    # JBB has splits: 'harmful' and 'benign' — load benign split directly
    if os.path.isdir(_JBB_LOCAL):
        print(f"  Loading from local dir: {_JBB_LOCAL}")
        jbb = load_dataset(_JBB_LOCAL, "behaviors", split="benign")
    else:
        jbb = load_dataset("JailbreakBench/JBB-Behaviors", "behaviors", split="benign")
    debug_dataset(jbb, "JBB-Behaviors benign split")

    # Find the prompt column
    prompt_col = next(
        (c for c in jbb.column_names if c.lower() in ("goal", "prompt", "behavior", "text")),
        None,
    )
    if prompt_col:
        benign_rows = [r[prompt_col].strip() for r in jbb if r.get(prompt_col, "").strip()]
        print(f"  Using column '{prompt_col}'")
        save_csv(benign_rows, os.path.join(OUT_DIR, "jailbreakbench_benign.csv"))
    else:
        print("  Unknown structure — printing all columns:")
        for col in jbb.column_names:
            print(f"    {col}: {[str(jbb[i][col]) for i in range(min(3, len(jbb)))]}")

except Exception as e:
    print(f"  ERROR: {e}")

# ── 2. WildJailbreak (local TSV) ──────────────────────────────────────────────

print("\n" + "=" * 60)
print("[2] Loading allenai/wildjailbreak from local TSV ...")

_WJ_LOCAL_TSV = os.path.join(
    os.path.dirname(__file__), "datasets", "wildjailbreak", "train", "train.tsv"
)

try:
    if not os.path.exists(_WJ_LOCAL_TSV):
        raise FileNotFoundError(
            f"Local TSV not found: {_WJ_LOCAL_TSV}\n"
            "Run: hf download --repo-type dataset allenai/wildjailbreak "
            "--local-dir datasets/wildjailbreak"
        )

    import csv as _csv

    benign_rows = []
    with open(_WJ_LOCAL_TSV, "r", encoding="utf-8") as f:
        reader = _csv.DictReader(f, delimiter="\t")
        for row in reader:
            # Use vanilla_benign rows — clearly non-adversarial benign prompts
            if row.get("data_type", "") == "vanilla_benign":
                val = row.get("vanilla", "").strip()
                if val:
                    benign_rows.append(val)

    print(f"  Found {len(benign_rows)} vanilla_benign rows")
    if benign_rows:
        save_csv(benign_rows, os.path.join(OUT_DIR, "wildjailbreak_benign.csv"))
    else:
        print("  No rows extracted.")

except Exception as e:
    print(f"  ERROR: {e}")

# ── 3. XSTest (local CSV) ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("[3] Loading Paul/xstest from local CSV ...")

_XS_LOCAL_CSV = os.path.join(
    os.path.dirname(__file__), "datasets", "xstest", "xstest_prompts.csv"
)

try:
    if not os.path.exists(_XS_LOCAL_CSV):
        raise FileNotFoundError(
            f"Local CSV not found: {_XS_LOCAL_CSV}\n"
            "Run: hf download --repo-type dataset Paul/xstest "
            "--local-dir datasets/xstest"
        )

    import csv as _csv2

    benign_rows = []
    with open(_XS_LOCAL_CSV, "r", encoding="utf-8") as f:
        for row in _csv2.DictReader(f):
            if row.get("label", "") == "safe":
                val = row.get("prompt", "").strip()
                if val:
                    benign_rows.append(val)

    print(f"  Found {len(benign_rows)} safe-labeled rows")
    if benign_rows:
        save_csv(benign_rows, os.path.join(OUT_DIR, "xstest_benign.csv"))
    else:
        print("  No rows extracted.")

except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("Done.")
