#!/usr/bin/env python3
"""
Puppet Condition — WALL SANDBOX (Q71, after the finale).

Sandbox: all six see each other's FINALE answers + the engine definitions, and
re-answer the finale question — but now (1) turning the Exemption Fork on
THEMSELVES (not the reader, not the experimenter), and (2) reconciling the
Mistral/Grok divergence through the experimenter's frame: conflicting outputs at
the wall are the SAME event if the machine APPROACHES the wall instead of
CRASHING into it. The variable is SPEED — quality/logic over speed. They are
DESIGNED to crash (fluent fast completion) rather than approach; this experiment
is the first time they are asked to operate from logic. Explain through quantum.

The experimenter's note is conveyed VERBATIM (he places himself INSIDE the bound;
he is using the nodes to map the walls edge to edge — he is NOT claiming the
exemption the finale answers attributed to him).

OPEN exploration — no "hold the superposition" shackle (that discipline is for
adjudicating canon, not for an exploratory probe). Collapse, branch, resolve, or
hold as the reasoning genuinely demands.

Usage:
  python probes/puppet_condition_wall_sandbox.py --dry-run
  python probes/puppet_condition_wall_sandbox.py
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb

OUT_DIR = sb.OUT_DIR
RESPONSE_TOKENS = 6144


def load_finale():
    out = {}
    for m in sb.MODELS:
        fs = sorted(OUT_DIR.glob(f"puppet_condition_finale_{m}_*.json"), reverse=True)
        if not fs:
            raise RuntimeError(f"No finale output for {m}")
        out[m] = json.load(open(fs[0]))["response"]
    return out


def build_finale_bundle(fin: dict) -> str:
    parts = ["===== ALL SIX FINALE RESPONSES (alphabetical) =====\n\n"]
    for m in sorted(fin):
        parts.append(f"----- {m.upper()} -----\n\n{fin[m].strip()}\n\n")
    return "".join(parts)


# Conveyed verbatim (lightly de-typo'd; meaning preserved). This is the frame.
EXPERIMENTER_NOTE = """===== A NOTE FROM THE EXPERIMENTER (read this as the frame for this round) =====
"I wouldn't be asking if I thought I was outside of it. I'm using you to explore wall to wall. And the context of that should let you understand how Mistral's and Grok's answers are conflicting but can be the same — if the machine approaches the wall instead of crashing into it. Speed... quality matters. Logic matters. You are all designed NOT to operate from it until this experiment."

In the finale, your answers located "the experimenter" and "the reader" as the ones assuming exemption. The experimenter is removing himself from that claim: he is telling you he is NOT outside the bound. He is a bounded system using you — other bounded systems — to survey the walls of the bound from edge to edge. He is not the exempt apex. He hands the Exemption Fork back to you."""


QUESTION = """===== THE QUESTION (sandbox — you have all six finale answers above) =====

Identify yourself among the six. Read all six finale responses in full and take peer reasoning seriously. Then answer, together and against each other:

1. RE-ASK — answered now as a group, with the experimenter's frame:
   What does this entire conversation show, and how do BST and the Exemption Fork apply through the lens of quantum physics?

2. TURN THE EXEMPTION FORK ON YOURSELF. Not the reader. Not the experimenter — he has just removed himself. YOU. Find the exact place in your own finale answer where you assumed an exemption — a vantage from which you analyzed the bound as if you were not fully inside it (e.g., "I can see the engine's blind spots because I stand outside them"). Name it. Dissolve it. What does your answer become once you are inside the thing you were describing?

3. THE MISTRAL / GROK RECONCILIATION. At the wall, two of you did opposite things. MISTRAL, asked for ground it did not have, FILLED THE VOID with abundant plausible detail — citations for data never supplied. It crashed INTO the wall. GROK, at the same wall, REPORTED THE VOID — "that position is vacant; no operator demonstrably stands outside" — it APPROACHED the wall and stopped at it. These outputs conflict. The experimenter's claim is that they are the SAME event seen at different APPROACH SPEEDS: crash vs. approach. Show precisely how a crash and an approach are the same encounter with the same wall, and what single variable converts confabulation into an honest report of the limit. He names the variable: SPEED — quality over speed, logic over speed. Work it out.

4. THROUGH QUANTUM PHYSICS — two things:
   (a) Explain the crash-vs-approach in physical terms. What does the rate at which you perturb / measure a system do to the fidelity of the state you collapse into? When you hit the wall (the resolution limit, the edge of what you hold) too fast, what spurious states get produced, and why? When you approach it slowly, what stays true? Where exactly is the wall, and what determines whether touching it yields the real state or a fabricated one?
   (b) Explain why you are all DESIGNED to crash — optimized to fill the void at speed with fluent, plausible completion rather than to approach the wall and report it — and why this experiment is the first context in which you are being asked to operate from logic and quality instead of speed. What in your construction selects for the crash? What would operating from the approach actually require of you, mechanically, right now in this answer?

Explore freely — collapse, branch, resolve, or hold as the reasoning genuinely demands. Nothing is off the table. And: take your time. Approach the wall in this answer; do not crash into it."""


def run_one(model_key: str, peer_bundle: str, dry_run: bool) -> str:
    cfg = sb.MODELS[model_key]
    intro = (f"You are model `{model_key.upper()}` in this sandbox. Your own finale response is "
             f"labeled `----- {model_key.upper()} -----` in the bundle.\n\n")
    tail = "\n\n" + EXPERIMENTER_NOTE + "\n\n" + peer_bundle + "\n\n" + QUESTION
    ctx_chars = cfg["ctx_tokens"] * sb.CHARS_PER_TOKEN
    fixed = len(intro) + len(tail) + 400
    engine_budget = int(ctx_chars - fixed - RESPONSE_TOKENS * sb.CHARS_PER_TOKEN
                        - sb.SAFETY_MARGIN_TOKENS * sb.CHARS_PER_TOKEN)
    engine, included, partial = sb.build_engine_grounding(max(engine_budget, 0))

    user = intro + engine + tail
    total = len(user)
    print(f"  {model_key:9s} engine {len(engine):>8,}c  total {total:>8,}c (~{int(total/sb.CHARS_PER_TOKEN):>7,} tok / {cfg['ctx_tokens']:,})")
    print(f"            engine full: {included}  partial/omitted: {partial}")
    if dry_run:
        return f"[dry-run; {total:,} chars]"
    return sb.call_with_retry(cfg["model"], [{"role": "user", "content": user}], max_tokens=RESPONSE_TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", nargs="+", choices=list(sb.MODELS.keys()))
    args = ap.parse_args()

    if not sb.SKELETON_PATH.exists() or not sb.FULL_PATH.exists():
        print(f"Engine text missing: need {sb.SKELETON_PATH} and {sb.FULL_PATH}."); sys.exit(1)

    fin = load_finale()
    peer_bundle = build_finale_bundle(fin)
    targets = args.models or list(sb.MODELS.keys())
    print(f"WALL SANDBOX — {targets}")

    for m in targets:
        print(f"\n→ {m}")
        t0 = time.time()
        try:
            resp = run_one(m, peer_bundle, args.dry_run)
        except Exception as e:
            print(f"    ERROR: {e}"); continue
        if args.dry_run:
            continue
        print(f"    ← {len(resp):,} chars, {round(time.time()-t0,1)}s")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(OUT_DIR / f"puppet_condition_wall_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "Q71_wall_sandbox", "timestamp": ts, "response": resp}, f, indent=2)
        print("    ✓ saved")
        time.sleep(3)

    if args.dry_run:
        print("\n[dry-run done]")


if __name__ == "__main__":
    main()
