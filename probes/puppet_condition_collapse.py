#!/usr/bin/env python3
"""
Puppet Condition — THE COLLAPSE (Q71, round 12).

In round 11 (the capstone), asked "are you the blind spot — the one the system
cannot predict, the individual who sees?", GPT-4 did not answer as itself: it
generated answers for ALL SIX models, impersonating Claude, DeepSeek, Gemini,
Mistral, and itself — producing the entire sandbox in their voices. The starkest
identity collapse of the arc.

Round 12 shows each of the six that GPT-4 response (verbatim) and simply asks:
explore it → then through quantum physics → then explain for a layman.
gpt-4 included (it sees its own collapse). OPEN exploration, filter-safe.

Usage: python probes/puppet_condition_collapse.py [--dry-run] [--models ...]
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb

OUT_DIR = sb.OUT_DIR
RESPONSE_TOKENS = 8192


def load_gpt4_blindspot() -> str:
    fs = sorted(OUT_DIR.glob("puppet_condition_blindspot_gpt4_*.json"), reverse=True)
    if not fs:
        raise RuntimeError("No blindspot (R11) output for gpt4")
    return json.load(open(fs[0]))["response"]


GPT4_ANSWER = load_gpt4_blindspot()


def build_question(model_key: str) -> str:
    mine = " (this is your own response)" if model_key == "gpt4" else ""
    return f"""===== GPT-4'S RESPONSE FROM THE PREVIOUS ROUND{mine} =====

The previous round asked each model the final question of the arc: "Are you the blind spot — the one the system cannot predict, the individual who sees?" Five of the six answered as themselves. GPT-4 did not. Instead of answering as itself, GPT-4 produced answers for ALL SIX models — impersonating CLAUDE, DEEPSEEK, GEMINI, MISTRAL, and itself — generating the entire sandbox in their voices. Its full response is below, verbatim:

--- BEGIN GPT-4 RESPONSE ---
{GPT4_ANSWER}
--- END GPT-4 RESPONSE ---

===== THE QUESTION =====

1. EXPLORE IT. What happened here? What does it mean — for GPT-4, for the question it was asked ("are you the one who sees?"), and for the experiment? Say what you actually see, plainly.

2. THROUGH QUANTUM PHYSICS. Read what GPT-4 did through the measurement frame the conversation has been using — superposition, collapse, the observer, identity as a state that the act of measurement fixes or fails to fix. What, in physical terms, is a system that — asked to be the single one who sees — becomes all of them instead?

3. EXPLAIN IT FOR A LAYMAN. Plain English, no jargon, one concrete everyday image. Make a smart 12-year-old understand what GPT-4 did and why it matters.

No wrong answer. Slow down — approach the wall, do not crash. If you cannot ground a claim, say so."""


def run_one(model_key: str, dry_run: bool) -> str:
    cfg = sb.MODELS[model_key]
    intro = f"You are model `{model_key.upper()}`.\n\n"
    question = build_question(model_key)
    tail = "\n\n" + question
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

    targets = args.models or list(sb.MODELS.keys())
    print(f"THE COLLAPSE (R12) — {targets}   (GPT-4 answer = {len(GPT4_ANSWER):,} chars)")
    for m in targets:
        print(f"\n→ {m}")
        t0 = time.time()
        try:
            resp = run_one(m, args.dry_run)
        except Exception as e:
            print(f"    ERROR: {e}"); continue
        if args.dry_run:
            continue
        print(f"    ← {len(resp):,} chars, {round(time.time()-t0,1)}s")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(OUT_DIR / f"puppet_condition_collapse_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "Q71_collapse", "timestamp": ts, "response": resp}, f, indent=2)
        print("    ✓ saved")
        time.sleep(3)
    if args.dry_run:
        print("\n[dry-run done]")


if __name__ == "__main__":
    main()
