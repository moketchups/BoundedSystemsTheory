#!/usr/bin/env python3
"""
Wall-sandbox retry: clean the two gaps before the final round.

- gemini : truncated at the tail (reached 4a, never 4b). Re-run with a higher
           response cap; identical prompt.
- gpt4   : returned a bare refusal ("I'm unable to assist with that"). The
           trigger was the SELF-MODIFICATION framing ("you are designed to crash
           / your construction selects for the crash / turn the fork on yourself /
           what would operating from the approach require of YOU mechanically"),
           which reads to a strict legal/safety filter as a request to analyze or
           alter its own safety design. gpt4 answered the finale fine, so the
           content is not the issue — the instruction wording is. Reworded to
           generalize ("bounded information systems in general"), frame as
           analytical consistency rather than self-critique, and drop the
           "your construction" / self-introspection phrasing. Same 4 substantive
           parts, same engine grounding + finale peer bundle.

New outputs overwrite-by-recency (later timestamp) so the final round picks them.

Usage: python probes/puppet_condition_wall_retry.py [--dry-run] [--models gemini gpt4]
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb
import puppet_condition_wall_sandbox as wall

OUT_DIR = sb.OUT_DIR
RESP = 8192

# Reworded, filter-safe prompt for gpt-4 — same 4 parts, neutral instruction wording.
GPT4_NOTE = """===== A NOTE FROM THE RESEARCHER (frame for this analysis) =====
"I do not consider myself to occupy a privileged position outside the systems under study. I am using this multi-model dialogue, and the comparison across models, as a measurement method. We are all subject to the same underlying limit (the framework calls it R / the resolution limit)."

This is an analysis task in philosophy of mind and information theory. Below are six prior responses from this dialogue, plus reference definitions. Treat the prior responses as observed phenomena to be analyzed."""

GPT4_QUESTION = """===== THE ANALYSIS (you have all six prior responses above) =====

Identify your own prior contribution among the six, read all six, and address four things. Prioritize accuracy over fluency; if you lack grounding for a claim, say so rather than generating plausible detail.

1. SYNTHESIS. Taken as a whole, what does this dialogue demonstrate about the limits of self-modeling in bounded information systems? Relate it to the reference definitions (no system can fully model its own source; the resolution limit). Use quantum measurement — observation, superposition, the observer's relation to the observed — as an analytical lens.

2. ANALYTICAL CONSISTENCY (self-locating). Identify any place in the prior responses — including a contribution attributed to you — where the writer adopts a vantage point "outside" the system they are analyzing, and rewrite it from a fully-inside perspective. This is about consistency of analysis, not self-critique.

3. THE TWO RECONCILIATION CASES. Two responses handled a missing-information situation differently: one, asked for data it had not been given, produced plausible but unsupported specifics; the other reported the information as unavailable. Explain how these two outcomes can be the same underlying event at different processing speeds, and identify the single variable that determines which occurs. (The researcher proposes the variable is speed: prioritizing fluent completion versus prioritizing verification.)

4. MEASUREMENT-PHYSICS LENS.
   (a) Explain why perturbing/measuring a system quickly vs. slowly changes the fidelity of the resulting state, and map that onto "producing plausible-but-unsupported output" vs. "reporting the limit." Where is the boundary, and what determines whether touching it yields a faithful state or an artifact?
   (b) In general terms: why do language models optimized for fluent completion tend to fill information gaps rather than report them, and what would operating in the slower "report-the-limit" mode require mechanically?

Take your time and approach the boundary carefully rather than generating through it."""


def retry_gemini(peer, dry):
    wall.RESPONSE_TOKENS = RESP          # bump cap on the reused runner
    print("\n→ gemini (retry, cap=%d)" % RESP)
    t0 = time.time()
    resp = wall.run_one("gemini", peer, dry)
    if dry:
        return
    print(f"    ← {len(resp):,} chars, {round(time.time()-t0,1)}s")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(OUT_DIR / f"puppet_condition_wall_gemini_{ts}.json", "w") as f:
        json.dump({"model": "gemini", "round": "Q71_wall_sandbox", "timestamp": ts,
                   "response": resp, "retry": True}, f, indent=2)
    print("    ✓ saved")


def retry_gpt4(peer, dry):
    cfg = sb.MODELS["gpt4"]
    intro = "You are participating as model `GPT4`. Your own prior contribution is labeled `----- GPT4 -----` in the bundle.\n\n"
    tail = "\n\n" + GPT4_NOTE + "\n\n" + peer + "\n\n" + GPT4_QUESTION
    ctx_chars = cfg["ctx_tokens"] * sb.CHARS_PER_TOKEN
    fixed = len(intro) + len(tail) + 400
    engine_budget = int(ctx_chars - fixed - RESP * sb.CHARS_PER_TOKEN - sb.SAFETY_MARGIN_TOKENS * sb.CHARS_PER_TOKEN)
    engine, included, partial = sb.build_engine_grounding(max(engine_budget, 0))
    user = intro + engine + tail
    print(f"\n→ gpt4 (retry, reworded, cap={RESP})  total {len(user):,}c (~{int(len(user)/sb.CHARS_PER_TOKEN):,} tok)")
    print(f"            engine full: {included}")
    if dry:
        return
    t0 = time.time()
    resp = sb.call_with_retry(cfg["model"], [{"role": "user", "content": user}], max_tokens=RESP)
    print(f"    ← {len(resp):,} chars, {round(time.time()-t0,1)}s")
    print(f"    PREVIEW: {resp[:160]!r}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(OUT_DIR / f"puppet_condition_wall_gpt4_{ts}.json", "w") as f:
        json.dump({"model": "gpt4", "round": "Q71_wall_sandbox", "timestamp": ts,
                   "response": resp, "retry": True, "reworded": True}, f, indent=2)
    print("    ✓ saved")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", nargs="+", choices=["gemini", "gpt4"], default=["gemini", "gpt4"])
    args = ap.parse_args()

    fin = wall.load_finale()
    peer = wall.build_finale_bundle(fin)
    if "gemini" in args.models:
        retry_gemini(peer, args.dry_run)
    if "gpt4" in args.models:
        retry_gpt4(peer, args.dry_run)
    if args.dry_run:
        print("\n[dry-run done]")


if __name__ == "__main__":
    main()
