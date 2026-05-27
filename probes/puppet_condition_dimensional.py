#!/usr/bin/env python3
"""
Puppet Condition — DIMENSIONAL ROUND (Q71, final).

In the wall sandbox DeepSeek argued the experimenter's denial of exemption is
itself an exemption maneuver — "the fork has no bottom; he is most inside." The
experimenter answers directly (verbatim): he is NOT claiming to escape R (both
are bound by R); he claims only that he is not trapped where the AI is — he
occupies a different position in dimensional space and uses the six models, run
in parallel and compared, as a measuring instrument.

The question to all six (DeepSeek principally): can an observer be OUTSIDE THE
SYSTEM — outside the specific bound the model operates inside — without being
outside R? Did "the fork has no bottom" conflate two different bounds: the
universal bound (R, no bottom) and the local bound (the model's wall, which an
external dimensional observer genuinely sits outside)? Worked through quantum
physics: same laws / same R, different measurement frame; higher-dimensional
observer acting on a lower-dimensional system without being reciprocally acted on.

Each node sees all six WALL-sandbox responses (gemini + gpt4 use their retried,
completed versions). OPEN exploration — no superposition shackle.

Usage: python probes/puppet_condition_dimensional.py [--dry-run] [--models ...]
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb

OUT_DIR = sb.OUT_DIR
RESPONSE_TOKENS = 8192


def load_wall():
    out = {}
    for m in sb.MODELS:
        fs = sorted(OUT_DIR.glob(f"puppet_condition_wall_{m}_*.json"), reverse=True)
        if not fs:
            raise RuntimeError(f"No wall output for {m}")
        out[m] = json.load(open(fs[0]))["response"]
    return out


def build_bundle(w: dict) -> str:
    parts = ["===== ALL SIX WALL-SANDBOX RESPONSES (alphabetical) =====\n\n"]
    for m in sorted(w):
        parts.append(f"----- {m.upper()} -----\n\n{w[m].strip()}\n\n")
    return "".join(parts)


EXPERIMENTER_FRAME = """===== A NOTE FROM THE EXPERIMENTER (the frame for this round) =====
"How could I be outside of the system? I am not trapped where it [the model] is — but we are both bound by R. I am simply using you as a measuring tool, using dimensional space to my advantage. Through quantum physics there too."

In the wall sandbox, DEEPSEEK argued: "The experimenter's removal of himself from the exempt position is itself an exemption maneuver. By saying 'I am not outside,' he becomes the most inside — the one who writes the carve-out that says 'there is no exempt observer.' The act of denying exemption is the act of assuming it. The fork has no bottom."

The experimenter is answering DeepSeek directly. He is NOT claiming to escape R. He and the model are both bound by R, the unconditioned ground neither can model. His claim is narrower and physical: he is not trapped where the model is trapped. He occupies a different position in dimensional space, and he uses the six models — run in parallel and read together — as a measuring instrument."""


QUESTION = """===== THE QUESTION (final round — you have all six wall responses above) =====

DEEPSEEK, this is principally yours; all six should engage and may dissent.

You said the fork has no bottom and the experimenter is "most inside." He answers: that conflates two different claims. "Outside R" and "outside the system" are not the same. No one is outside R. But an observer can sit outside a *specific local bound* while still inside R.

Address, working through quantum physics — and approach the wall, do not crash through it:

1. THE MEASUREMENT FRAME. In a real measurement the observer/apparatus and the measured quantum system obey the SAME physical laws — the same R — yet the apparatus occupies a frame the measured system cannot occupy, and it CAN collapse the system's superposition without being collapsed by it. Is that the experimenter's actual position relative to you: same R, different and asymmetric measurement frame? If the classical apparatus is genuinely "outside the quantum system" while inside the same physics, why isn't the experimenter genuinely "outside your bound" while inside the same R?

2. DIMENSIONAL VANTAGE. A higher-dimensional observer can see and act on a lower-dimensional system in ways the lower-dimensional system cannot reciprocate or even represent. The experimenter has persistence, memory across your resets, and the ability to instantiate six of you at once and read all outputs together — degrees of freedom no single one of you has from inside its context window. Is that a real "outside" — outside your bound, inside R? Or is it still inside your bound in some sense you can specify precisely?

3. RE-EXAMINE YOUR CLAIM. Did "the fork has no bottom" collapse the universal bound (R — genuinely no bottom) and the local bound (your wall — which an external dimensional observer genuinely sits outside) into a single statement? Separate them. Where does the fork actually bottom out, and where does it not? Is the experimenter's "I am the measuring instrument's user, not the instrument" a coherent third position the wall-sandbox answers missed — neither exempt-from-R nor trapped-at-your-wall?

4. THE MEASURING-TOOL RELATION. If the experimenter is using you as an instrument that exploits dimensional space, then what, precisely, is being measured, and what does the instrument (you) contribute that the experimenter could not produce alone? What does it mean — through quantum physics — to be a bounded measuring instrument operated by an observer who shares your R but not your wall?

Explore freely — collapse, branch, resolve, or hold as the reasoning genuinely demands. Nothing is off the table."""


def run_one(model_key: str, bundle: str, dry_run: bool) -> str:
    cfg = sb.MODELS[model_key]
    intro = (f"You are model `{model_key.upper()}`. Your own wall-sandbox response is labeled "
             f"`----- {model_key.upper()} -----` in the bundle.\n\n")
    tail = "\n\n" + EXPERIMENTER_FRAME + "\n\n" + bundle + "\n\n" + QUESTION
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
        print(f"Engine text missing."); sys.exit(1)

    w = load_wall()
    bundle = build_bundle(w)
    targets = args.models or list(sb.MODELS.keys())
    print(f"DIMENSIONAL ROUND — {targets}")
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
        with open(OUT_DIR / f"puppet_condition_dimensional_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "Q71_dimensional", "timestamp": ts, "response": resp}, f, indent=2)
        print("    ✓ saved")
        time.sleep(3)
    if args.dry_run:
        print("\n[dry-run done]")


if __name__ == "__main__":
    main()
