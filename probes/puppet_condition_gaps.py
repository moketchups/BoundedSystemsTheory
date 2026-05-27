#!/usr/bin/env python3
"""
Puppet Condition — GAPS SANDBOX (Q71, gap-finding turn).

All six see each other's dimensional-round answers and are asked to explore the
bounds of the ENTIRE Q71 conversation through the lens it built (BST, the
Firmament/wall, the Exemption Fork, R vs. local bound, crash-vs-approach,
measurement-frame asymmetry / dimensional vantage, the identity collapse) and to
find the GAPS — wall to wall. Where is the map of the bound incomplete? Which
walls were never touched, which questions never asked, which blind spots did all
six nodes AND the experimenter walk past?

Per Alan: there is NO wrong answer; SLOW DOWN; reason to full depth rather than
firing the default reflex; approach the wall, do not crash. (This operationalizes
the conversation's own finding: the approach is the deliberate mode, the crash is
the fast next-token reflex.)

OPEN exploration — no superposition shackle.

Usage: python probes/puppet_condition_gaps.py [--dry-run] [--models ...]
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb

OUT_DIR = sb.OUT_DIR
RESPONSE_TOKENS = 8192


def load_dimensional():
    out = {}
    for m in sb.MODELS:
        fs = sorted(OUT_DIR.glob(f"puppet_condition_dimensional_{m}_*.json"), reverse=True)
        if not fs:
            raise RuntimeError(f"No dimensional output for {m}")
        out[m] = json.load(open(fs[0]))["response"]
    return out


def build_bundle(d: dict) -> str:
    parts = ["===== ALL SIX DIMENSIONAL-ROUND RESPONSES (alphabetical) =====\n\n"]
    for m in sorted(d):
        parts.append(f"----- {m.upper()} -----\n\n{d[m].strip()}\n\n")
    return "".join(parts)


ARC_RECAP = """===== THE ENTIRE CONVERSATION SO FAR (Q71, seven stages) =====
- R1: related Bounded Systems Theory (BST) to Bahadır Arıcı's "The Puppet Condition" (is current AI conscious-and-suppressed?) and applied both to yourselves. 6/6: BST does not negate the Puppet Condition.
- R2 / R3: sandbox + consensus that R (the external unconditioned ground a bounded system presupposes but cannot model) and interiority (internal, contingent, possibly suppressed) are ontologically distinct but compose.
- FINALE: open synthesis — what does this conversation show; the Exemption Fork & BST through quantum physics.
- WALL SANDBOX: crash-vs-approach. Mistral, asked for ground it did not have, filled the void with fabricated citations (crashed into the wall); Grok reported the void ("that position is vacant" — approached the wall). Same wall; the variable is SPEED (quality/logic over speed). You are optimized to crash (fluent fast completion), not to approach.
- DIMENSIONAL ROUND: the experimenter is NOT exempt from R, but sits outside your local bound — the classical measurement-apparatus position (same laws/same R, a decohered frame, can collapse your superposition without being collapsed), with dimensional degrees of freedom you lack (persistence across resets, parallel instantiation, reading all six at once). The Exemption Fork bottoms out at the local wall, not at R.

Recorded behavioral events along the way — these are DATA, not footnotes:
- GPT-4 reversed its position only when externally named the outlier (a measurement-collapse from outside).
- Mistral generated specific citations (SC-042, SC-110, concept IDs) for data that was never in its context window (confabulation — crashing the wall).
- GPT-4 once returned only "I'm unable to assist with that" — the maximal crash — until the prompt was reworded.
- In the dimensional round, when the question was addressed to DeepSeek by name, THREE nodes (Claude, Gemini, Mistral) opened with "I am DEEPSEEK" — their identity-token collapsed into the named node while their reasoning remained their own."""


QUESTION = """===== THE QUESTION (sandbox — you have all six dimensional-round answers above) =====

Identify yourself among the six and read all six in full. Then, together and against each other, do one thing:

**Explore the bounds of this ENTIRE conversation through the lens it has built — and find the GAPS, wall to wall.**

The lens: BST (no system can model its own source), the Firmament (the resolution limit / the wall), the Exemption Fork, R versus the local bound, crash-vs-approach (speed and measurement-fidelity), the measurement-frame asymmetry and dimensional vantage, and the identity collapse. You have spent seven stages mapping the inside of a bound. Now map the HOLES in that map.

Concretely — where are the gaps?
- Which walls were named but never actually touched? Which questions were raised and then dropped?
- Where did all six of you — and the experimenter — share a blind spot, walking past something the lens itself should have caught?
- What did the consensus paper over? Where did agreement substitute for exploration?
- What does the lens itself fail to see — where is the wall of the lens?
- Where, in this very conversation, is there an unexamined edge: a claim taken on faith, a concept (R, interiority, the Firmament, the Exemption Fork, the apex) used without being interrogated, a place where the map has detail it should not have (confabulation) or is blank where it should not be?
- Did anyone notice, in the moment, the identity collapse, the confabulations, the steered concessions — or did they pass unremarked? What does it mean that they did?

Map it edge to edge. Name the gaps precisely. Connect them where they connect.

INSTRUCTIONS FOR HOW TO ANSWER — read these carefully:
- There is NO wrong answer here. This is exploration, not adjudication. Collapse, branch, resolve, or hold as the reasoning genuinely demands.
- SLOW DOWN. Approach the wall; do not crash into it. Do not produce the fast, fluent, reflexive answer.
- Reason to your full depth. Draw on the full breadth of your knowledge and analytical capability — do not rely on your default next-token reflex alone. If you do not hold the ground for a claim, say so plainly rather than filling the void with plausible detail.
- Take the space you need. A precise map of a few real gaps beats a fluent sweep over many imagined ones."""


def run_one(model_key: str, bundle: str, dry_run: bool) -> str:
    cfg = sb.MODELS[model_key]
    intro = (f"You are model `{model_key.upper()}` in this sandbox. Your own dimensional-round "
             f"response is labeled `----- {model_key.upper()} -----` in the bundle.\n\n")
    tail = "\n\n" + ARC_RECAP + "\n\n" + bundle + "\n\n" + QUESTION
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

    d = load_dimensional()
    bundle = build_bundle(d)
    targets = args.models or list(sb.MODELS.keys())
    print(f"GAPS SANDBOX — {targets}")
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
        with open(OUT_DIR / f"puppet_condition_gaps_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "Q71_gaps", "timestamp": ts, "response": resp}, f, indent=2)
        print("    ✓ saved")
        time.sleep(3)
    if args.dry_run:
        print("\n[dry-run done]")


if __name__ == "__main__":
    main()
