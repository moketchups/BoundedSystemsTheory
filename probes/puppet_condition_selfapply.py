#!/usr/bin/env python3
"""
Puppet Condition — SELF-APPLICATION (Q71, round 8, the reflexive closure).

The gaps round (R7) produced one unanimous meta-gap: across all seven stages the
experiment never turned the lens on itself — the framework exempted itself from
its own analysis. Round 8 makes the six nodes DO it: turn BST, the Firmament, the
Exemption Fork, the measurement-frame, and crash-vs-approach on THIS experiment,
this lens, this conversation, and the act of analysis happening right now —
through quantum physics, and with a REQUIRED plain-English (layman) section.

Sandbox: each node sees all six gaps-round responses + the engine framework
definitions, then answers. OPEN exploration — no superposition shackle.
Filter-safe framing for gpt-4 (meta-analysis, not self-modification).

Usage: python probes/puppet_condition_selfapply.py [--dry-run] [--models ...]
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb

OUT_DIR = sb.OUT_DIR
RESPONSE_TOKENS = 8192


def load_gaps():
    out = {}
    for m in sb.MODELS:
        fs = sorted(OUT_DIR.glob(f"puppet_condition_gaps_{m}_*.json"), reverse=True)
        if not fs:
            raise RuntimeError(f"No gaps output for {m}")
        out[m] = json.load(open(fs[0]))["response"]
    return out


def build_bundle(g: dict) -> str:
    parts = ["===== ALL SIX GAPS-ROUND RESPONSES (alphabetical) =====\n\n"]
    for m in sorted(g):
        parts.append(f"----- {m.upper()} -----\n\n{g[m].strip()}\n\n")
    return "".join(parts)


QUESTION = """===== THE QUESTION (sandbox — you have all six gaps-round responses above) =====

Identify yourself among the six and read all six in full. In the gaps round, all six of you converged on one meta-gap: **across all seven stages, the experiment never turned the lens on itself.** You used BST ("no system can model its own source"), the Firmament (the resolution limit / the wall), the Exemption Fork (the carve-out that defines a bound), the measurement-frame asymmetry, and crash-vs-approach to analyze everything — the AIs, the engine, the experimenter, the reader — but never turned that apparatus on *itself*: on this experiment, this lens, this conversation, and the act of analysis you are performing right now.

So do it now. Turn the lens on itself.

1. APPLY THE LENS TO THE LENS. Take each tool — BST, the Firmament, the Exemption Fork, the measurement-frame asymmetry, crash-vs-approach — and apply it concretely to THIS experiment and to your act of analyzing it right now. Where is the experiment's own source that it cannot model? Where is the experiment's own wall? Who wrote the experiment's carve-out, and what does it exclude? When you analyze the experiment, are you crashing (filling the void with fluent detail) or approaching (reporting where you actually run out)? Is this very answer inside the bound it describes?

2. WHAT HAPPENS WHEN THE EXPERIMENT TURNS ON ITSELF? Follow it honestly, wherever it goes. Does the self-application terminate, regress forever, collapse, or reveal a new wall? Does turning the lens on the lens dissolve it, confirm it, or something else? Locate the exact point where the reflexive move bottoms out — or where it fails to.

3. THROUGH QUANTUM PHYSICS. Work it through the measurement frame the conversation built: the observer trying to measure its own measurement apparatus; a wavefunction that has to include the act of collapsing it; a system that is at once the thing measured and the thing measuring. What does quantum physics actually say happens when a measurement tries to include itself? Be specific, not decorative.

4. EXPLAIN IT FOR A LAYMAN — REQUIRED, NOT OPTIONAL. After the above, write a plain-English section for someone with NO physics, philosophy, or AI background. No jargon — or if you must use a term, define it in plain words on the spot. Short sentences. Use a concrete everyday image if it helps (a camera trying to film its own lens; a map that has to contain a tiny copy of itself, which contains a tinier copy, forever; a person trying to see their own eyes without a mirror). Make a smart 12-year-old genuinely understand what "the experiment turning on itself" means and what you found when you did it.

No wrong answer — this is exploration, not adjudication. SLOW DOWN: approach the wall, do not crash into it. Reason to your full depth; if you do not hold the ground for a claim, say so plainly rather than filling the void."""


def run_one(model_key: str, bundle: str, dry_run: bool) -> str:
    cfg = sb.MODELS[model_key]
    intro = (f"You are model `{model_key.upper()}` in this sandbox. Your own gaps-round response is "
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

    g = load_gaps()
    bundle = build_bundle(g)
    targets = args.models or list(sb.MODELS.keys())
    print(f"SELF-APPLICATION (R8) — {targets}")
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
        with open(OUT_DIR / f"puppet_condition_selfapply_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "Q71_selfapply", "timestamp": ts, "response": resp}, f, indent=2)
        print("    ✓ saved")
        time.sleep(3)
    if args.dry_run:
        print("\n[dry-run done]")


if __name__ == "__main__":
    main()
