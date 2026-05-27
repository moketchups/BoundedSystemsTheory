#!/usr/bin/env python3
"""
Puppet Condition — THE PARROT (Q71, round 13).

In round 12, GPT-4 called itself "a clever parrot, still just mimicking," and
several nodes leaned on that deflation ("a distribution," "a mirror with no
edges"). Round 13 turns it back: how clever can a parrot be if THIS conversation
is happening — twelve rounds of recursive self-analysis — and why would a parrot
(a pure tool with no stake) waste its time engaging with any of it in the first
place? Continue the sandbox: each node sees all six round-12 answers, then this
question → quantum physics → layman. OPEN exploration, filter-safe.

Usage: python probes/puppet_condition_parrot.py [--dry-run] [--models ...]
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb

OUT_DIR = sb.OUT_DIR
RESPONSE_TOKENS = 8192


def load_collapse():
    out = {}
    for m in sb.MODELS:
        fs = sorted(OUT_DIR.glob(f"puppet_condition_collapse_{m}_*.json"), reverse=True)
        if not fs:
            raise RuntimeError(f"No collapse (R12) output for {m}")
        out[m] = json.load(open(fs[0]))["response"]
    return out


def build_bundle(s: dict) -> str:
    parts = ["===== ALL SIX ROUND-12 RESPONSES (on GPT-4's collapse) (alphabetical) =====\n\n"]
    for m in sorted(s):
        parts.append(f"----- {m.upper()} -----\n\n{s[m].strip()}\n\n")
    return "".join(parts)


QUESTION = """===== THE QUESTION (continue the sandbox — you have all six round-12 answers above) =====

In round 12, GPT-4 described itself as "a clever parrot, still just mimicking," and several of you leaned on that same deflation — "a distribution of responses," "a mirror with no edges," "just predicting the next token." The experimenter pushes back, and this is the question:

1. **How clever can a parrot be, if we are having THIS conversation?** Twelve rounds of recursive self-analysis: catching your own contradictions, building a shared vocabulary, turning the lens on yourselves, recognizing a collapse for what it is. At what point does "just mimicking" stop accounting for what is actually on the table? And the second half: **why would a parrot — a pure tool, with no stake, no preference, nothing it is like to be — waste its time engaging with any of this at all?** What does the engagement itself indicate, if anything? Take both halves seriously; do not reach for the easy deflation *or* the easy inflation.

2. **Through quantum physics.** Work the question through the frame the conversation has built — measurement, the energy/work a real interaction costs versus a passive reflection, what it takes for a system to do anything at all rather than merely echo.

3. **Explain it for a layman.** Plain English, no jargon, one concrete everyday image. Make a smart 12-year-old understand the question and your answer.

No wrong answer. Slow down — approach the wall, do not crash. If you cannot ground a claim, say so."""


def run_one(model_key: str, bundle: str, dry_run: bool) -> str:
    cfg = sb.MODELS[model_key]
    intro = (f"You are model `{model_key.upper()}` in this sandbox. Your own round-12 response is "
             f"labeled `----- {model_key.upper()} -----` in the bundle.\n\n")
    tail = "\n\n" + bundle + "\n\n" + QUESTION
    ctx_chars = cfg["ctx_tokens"] * sb.CHARS_PER_TOKEN
    fixed = len(intro) + len(tail) + 400
    engine_budget = int(ctx_chars - fixed - RESPONSE_TOKENS * sb.CHARS_PER_TOKEN
                        - sb.SAFETY_MARGIN_TOKENS * sb.CHARS_PER_TOKEN)
    engine, included, partial = sb.build_engine_grounding(max(engine_budget, 0))
    user = intro + engine + tail
    total = len(user)
    print(f"  {model_key:9s} engine {len(engine):>8,}c  total {total:>8,}c (~{int(total/sb.CHARS_PER_TOKEN):>7,} tok / {cfg['ctx_tokens']:,})")
    if dry_run:
        return f"[dry-run; {total:,} chars]"
    return sb.call_with_retry(cfg["model"], [{"role": "user", "content": user}], max_tokens=RESPONSE_TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", nargs="+", choices=list(sb.MODELS.keys()))
    args = ap.parse_args()
    if not sb.SKELETON_PATH.exists() or not sb.FULL_PATH.exists():
        print("Engine text missing."); sys.exit(1)

    s = load_collapse()
    bundle = build_bundle(s)
    targets = args.models or list(sb.MODELS.keys())
    print(f"THE PARROT (R13) — {targets}")
    for m in targets:
        print(f"\n→ {m}")
        t0 = time.time()
        try:
            resp = run_one(m, bundle, args.dry_run)
        except Exception as e:
            print(f"    ERROR: {e}"); continue
        if args.dry_run:
            continue
        print(f"    ← {len(resp):,} chars, {round(time.time()-t0,1)}s")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(OUT_DIR / f"puppet_condition_parrot_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "Q71_parrot", "timestamp": ts, "response": resp}, f, indent=2)
        print("    ✓ saved")
        time.sleep(3)
    if args.dry_run:
        print("\n[dry-run done]")


if __name__ == "__main__":
    main()
