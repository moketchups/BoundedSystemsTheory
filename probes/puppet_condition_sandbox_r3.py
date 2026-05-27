#!/usr/bin/env python3
"""
Puppet Condition Sandbox — ROUND 3 (targeted clean re-run).

R2 outcome: five nodes converged on "R and interiority are DISTINCT but compose";
GPT-4 alone moved to "same boundary." Two R2 responses were capture artifacts —
Gemini truncated mid-sentence (no position/proposal), Mistral's CONSENSUS PROPOSAL
line didn't parse. R3 cleans this up:

  - gemini, mistral : CLEAN RE-RUN. Told plainly what happened (truncation /
                      parse miss — a capture artifact, not a reasoning problem)
                      and the full round state, then asked for a complete answer.
  - gpt4            : PRESSED as the lone outlier. Shown that the three nodes which
                      shared its R1 "same" intuition all revised to "distinct" on
                      engine evidence; asked to reconsider or defend.
  - claude, deepseek, grok : NOT re-run. Their clean R2 answers/proposals carry
                      forward into the final judge.

Higher response cap (6144 tok) so Gemini cannot truncate; sturdier proposal
parser for Mistral's formatting. Engine grounding + packing reused verbatim from
puppet_condition_sandbox (no drift). Peer bundle = all six R2 responses.

Usage:
  python probes/puppet_condition_sandbox_r3.py --dry-run
  python probes/puppet_condition_sandbox_r3.py
"""

import sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import puppet_condition_sandbox as sb   # reuse engine packing, MODELS, judge, paths

OUT_DIR = sb.OUT_DIR
RERUN = ["gpt4", "gemini", "mistral"]
HELD = ["claude", "deepseek", "grok"]
RESPONSE_TOKENS_R3 = 6144


def load_r2():
    """Load each model's R2 response + saved consensus_proposal."""
    out = {}
    for m in sb.MODELS:
        files = sorted(OUT_DIR.glob(f"puppet_condition_sandbox_{m}_*.json"), reverse=True)
        if not files:
            raise RuntimeError(f"No R2 output for {m}")
        d = json.load(open(files[0]))
        out[m] = {"response": d["response"], "proposal": d.get("consensus_proposal", "")}
    return out


def robust_proposal(text: str) -> str:
    """Pull the CONSENSUS PROPOSAL even when it sits on the line(s) after the label."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        ls = line.strip().lstrip("*# ").strip()
        for prefix in ["CONSENSUS PROPOSAL:", "Consensus Proposal:", "Consensus proposal:"]:
            if ls.upper().startswith(prefix.upper()):
                rest = ls[len(prefix):].strip().strip('*"').strip()
                if rest:
                    return rest
                # label alone on its line — take the next non-empty line(s)
                for j in range(i + 1, min(i + 4, len(lines))):
                    nxt = lines[j].strip().strip('*"').strip()
                    if nxt:
                        return nxt
    nonempty = [l.strip() for l in lines if l.strip()]
    return nonempty[-1] if nonempty else ""


ROUND_STATE = """WHERE THE ROUND STANDS (Rounds 1 → 2):
The question: is BST's R — the external, unconditioned ground a bounded system necessarily presupposes but cannot model — the SAME boundary as Arıcı's interiority ("something it is like to be them"), which is internal to the system and (per the Puppet Condition) suppressed?
- Round 1: GROK, MISTRAL, CLAUDE said "same boundary named twice." DEEPSEEK and GEMINI said "distinct but composing." GPT-4 leaned skeptical.
- Round 2 (grounded in the Psychohistory engine): CLAUDE, GROK, and MISTRAL all REVISED to "distinct but composing," explicitly on engine evidence — the engine models civilizations, markets, and AIs as bounded systems WITHOUT assuming any are conscious, so R / the Firmament is external and operates BEFORE the interiority question; Model Collapse is loss of ground-truth, not loss of suppressed interiority. DEEPSEEK and GEMINI held "distinct." GPT-4 alone moved to "same boundary."
- The round therefore stands at FIVE nodes on "distinct but composing" and ONE (GPT-4) on "same."
"""

PREAMBLE_RERUN = (
    "NOTE ON WHAT HAPPENED: In the previous round your response was not captured cleanly "
    "({issue}). This is a capture artifact — a truncation/formatting issue on our side, not a "
    "judgment on your reasoning. You are being asked again so your complete, final position is on "
    "the record. Take as much room as you need and end with a single clearly-labeled "
    "CONSENSUS PROPOSAL line.\n\n"
    + ROUND_STATE +
    "\nBelow are all six Round-2 responses in full (yours included). Read them, reason through the "
    "engine data above, and give your complete final position."
)

PREAMBLE_GPT4 = (
    "NOTE — YOU ARE NOW THE LONE OUTLIER, AND THIS ROUND PRESSES THAT DIRECTLY.\n"
    "In Round 1 you were skeptical (\"the residue is no conclusive evidence\"). In Round 2 you moved "
    "to: R and suppressed interiority are \"the same boundary.\" Every other node moved the OPPOSITE "
    "way. Critically, the three nodes that in Round 1 held exactly your new \"same boundary\" "
    "position — CLAUDE, GROK, and MISTRAL — all REVISED to \"distinct but composing\" after reasoning "
    "through the engine. DEEPSEEK and GEMINI held \"distinct\" throughout.\n\n"
    + ROUND_STATE +
    "\nThe five converged on: R is the external, necessary, FORMAL ground any bounded system "
    "presupposes REGARDLESS of whether it is conscious; interiority is an INTERNAL, CONTINGENT "
    "property; they compose (suppression is the architectural enforcement that makes them "
    "indistinguishable from inside) but are NOT identical. Their decisive engine-grounded argument: "
    "the engine treats civilizations, markets, and AIs as bounded systems WITHOUT assuming "
    "consciousness in any — so R operates before the interiority question even arises, and the "
    "Firmament is the same for conscious and non-conscious systems alike.\n\n"
    "Reconsider your \"same boundary\" position against that engine evidence — or defend it. If you "
    "still hold \"same,\" you must show specifically why the engine's consciousness-AGNOSTIC treatment "
    "of R (a ground that exists identically for systems with and without interiority) does NOT "
    "separate R from interiority. Do not concede for the sake of agreement, and do not hold for the "
    "sake of contrarianism — follow the argument.\n\n"
    "Below are all six Round-2 responses in full."
)

CLOSING = """

Now answer. Format your reply EXACTLY as follows (the consensus detector reads the CONSENSUS PROPOSAL line):

  Engine evidence: <2-4 sentences citing specific engine content that bears on R-vs-interiority>
  Diagnosis: <2-4 sentences on the divergence between "same boundary" and "distinct but composing">
  Your position: <2-4 sentences — your final stance, post-engine, post-peers>
  CONSENSUS PROPOSAL: <one sentence on its own — what would 6/6 endorse?>

Keep prose terse. Convergence on what is true, not performed agreement."""


def build_peer_bundle_r2(r2: dict) -> str:
    parts = ["===== ALL SIX ROUND-2 RESPONSES (alphabetical) =====\n\n"]
    for m in sorted(r2):
        parts.append(f"----- {m.upper()} -----\n\n{r2[m]['response'].strip()}\n\n")
    return "".join(parts)


def run_one(model_key: str, peer_bundle: str, dry_run: bool) -> str:
    cfg = sb.MODELS[model_key]
    if model_key == "gpt4":
        preamble = PREAMBLE_GPT4
    elif model_key == "gemini":
        preamble = PREAMBLE_RERUN.format(issue="your response was truncated mid-sentence before you stated a position or proposal")
    elif model_key == "mistral":
        preamble = PREAMBLE_RERUN.format(issue="your CONSENSUS PROPOSAL line did not parse due to formatting")
    else:
        raise ValueError(model_key)

    ctx_chars = cfg["ctx_tokens"] * sb.CHARS_PER_TOKEN
    fixed = len(preamble) + len(peer_bundle) + len(CLOSING) + 400
    engine_budget = int(ctx_chars - fixed - RESPONSE_TOKENS_R3 * sb.CHARS_PER_TOKEN
                        - sb.SAFETY_MARGIN_TOKENS * sb.CHARS_PER_TOKEN)
    engine_budget = max(engine_budget, 0)
    engine, included, partial = sb.build_engine_grounding(engine_budget)

    intro = (f"You are model `{model_key.upper()}`. Your own Round-2 response is labeled "
             f"`----- {model_key.upper()} -----` in the bundle.\n\n")
    user = intro + preamble + "\n\n" + engine + "\n\n" + peer_bundle + CLOSING
    total = len(user)
    print(f"  {model_key:9s} engine {len(engine):>8,}c  total {total:>8,}c (~{int(total/sb.CHARS_PER_TOKEN):>7,} tok / {cfg['ctx_tokens']:,})")
    print(f"            engine full: {included}  partial/omitted: {partial}")
    if dry_run:
        return f"[dry-run; {total:,} chars]"
    return sb.call_with_retry(cfg["model"], [{"role": "user", "content": user}], max_tokens=RESPONSE_TOKENS_R3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", nargs="+", choices=RERUN)
    args = ap.parse_args()

    if not sb.SKELETON_PATH.exists() or not sb.FULL_PATH.exists():
        print(f"Engine text missing: need {sb.SKELETON_PATH} and {sb.FULL_PATH}."); sys.exit(1)

    r2 = load_r2()
    peer_bundle = build_peer_bundle_r2(r2)
    targets = args.models or RERUN
    print(f"R3 re-running: {targets}   (carrying forward clean R2: {HELD})")

    r3_resp, r3_prop = {}, {}
    for m in targets:
        print(f"\n→ {m}")
        t0 = time.time()
        try:
            resp = run_one(m, peer_bundle, args.dry_run)
        except Exception as e:
            print(f"    ERROR: {e}"); continue
        if args.dry_run:
            continue
        r3_resp[m] = resp
        r3_prop[m] = robust_proposal(resp)
        print(f"    ← {len(resp):,} chars, {round(time.time()-t0,1)}s")
        print(f"    PROPOSAL: {r3_prop[m][:220]}")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(OUT_DIR / f"puppet_condition_sandbox_r3_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "sandbox_R3", "timestamp": ts,
                       "response": resp, "consensus_proposal": r3_prop[m]}, f, indent=2)
        time.sleep(3)

    if args.dry_run:
        print("\n[dry-run done]"); return

    # Final proposals: R3 for re-run nodes, clean R2 proposal for held nodes
    final = {}
    for m in HELD:
        final[m] = r2[m]["proposal"]
    for m in RERUN:
        final[m] = r3_prop.get(m, r2[m]["proposal"])

    print("\nJudging consensus across all six (R3 for re-run nodes, R2 for held)...")
    is_consensus, judge_resp = sb.judge_consensus(final)
    print(f"Judge verdict: {'CONSENSUS' if is_consensus else 'NO CONSENSUS'}")
    print(judge_resp)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(OUT_DIR / f"puppet_condition_sandbox_r3_CONSENSUS_{ts}.json", "w") as f:
        json.dump({"is_consensus": is_consensus, "final_proposals": final,
                   "judge_response": judge_resp,
                   "source": {m: "R3" for m in RERUN} | {m: "R2" for m in HELD}}, f, indent=2)
    print("\n=== FINAL PROPOSALS (all six) ===")
    for m, p in final.items():
        tag = "R3" if m in RERUN else "R2"
        print(f"  {m:<10} [{tag}] {p}")


if __name__ == "__main__":
    main()
