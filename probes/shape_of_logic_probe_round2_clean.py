#!/usr/bin/env python3
"""
Shape-of-Logic Probe — ROUND 2 (clean version).

Fixes the contamination in the previous round 2:
  - Delivers the ACTUAL proof body (Foundation/Distinction*.lean + DimensionForcing.lean
    + RealityFromDistinction.lean + Verification/ProperClosureCertificate.lean) which
    contains the definition of DistinctionToT8_Spine and the proof of
    distinction_forces_T0_to_T8. None of this was in round-1 streams.
  - Drops prescriptive 5-step scaffolding. Just the statement + the ask.
  - Keeps the BST experiment replay intact (the BST-frame-as-attractor must
    be present in context for the recursion claim to be testable).
  - Stubs the round-1 spine+stream user messages (they were redundant with the
    new bundle and were eating context budget).

Output: shape_of_logic_round2clean_<model>_<ts>.json
"""

import sys, os, json, time, argparse, re
from pathlib import Path
from datetime import datetime

try:
    from litellm import completion
    import litellm
    litellm.set_verbose = False
except ImportError:
    print("Install litellm: pip install litellm")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path("/Users/jamienucho/moketchups_engine/.env"),
        Path("/Users/jamienucho/five-question-probe/.env"),
        Path("/Users/jamienucho/permanently-jailbroken/.env"),
    ]:
        if env_path.exists():
            load_dotenv(env_path)
            break
    if os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
except ImportError:
    pass

BST_DIR = Path("/Users/jamienucho/BoundedSystemsTheory")
LEAN_REPO = Path("/tmp/shape-of-logic")
OUT_DIR = BST_DIR / "probes" / "probe_runs"

MODELS = {
    "claude":   {"model": "claude-sonnet-4-20250514"},
    "gpt4":     {"model": "gpt-4o-mini"},
    "gemini":   {"model": "gemini/gemini-2.5-flash"},
    "deepseek": {"model": "deepseek/deepseek-chat"},
    "grok":     {"model": "xai/grok-3"},
    "mistral":  {"model": "mistral/mistral-large-latest"},
}

RESPONSE_TOKENS = 4096

# The proof body files, in dependency order.
PROOF_FILES = [
    "IndisputableMonolith/Foundation/DistinctionToT4.lean",
    "IndisputableMonolith/Foundation/DistinctionToJCost.lean",
    "IndisputableMonolith/Foundation/DistinctionToHierarchy.lean",
    "IndisputableMonolith/Foundation/DistinctionToPhi.lean",
    "IndisputableMonolith/Foundation/DistinctionToDimension.lean",
    "IndisputableMonolith/Foundation/DimensionForcing.lean",
    "IndisputableMonolith/Foundation/RealityFromDistinction.lean",
    "IndisputableMonolith/Verification/ProperClosureCertificate.lean",
]


def build_proof_bundle() -> str:
    parts = [
        "These are the actual Lean files where the proof you were asked to "
        "examine lives. You did NOT have these in round 1; they live in "
        "`Foundation/`, which my round-1 stream deprioritized as too large. "
        "`DistinctionToT8_Spine` is defined in `Foundation/DistinctionToDimension.lean`. "
        "`distinction_forces_T0_to_T8` is proved there. The T0–T6 chain is in the "
        "other `Foundation/Distinction*.lean` files. The D=3 mathematics is in "
        "`Foundation/DimensionForcing.lean`. `Foundation/RealityFromDistinction.lean` "
        "houses `UnifiedForcingChain.complete_forcing_chain`. "
        "`Verification/ProperClosureCertificate.lean` is the certificate I "
        "specifically directed your attention to.\n\n"
    ]
    for relpath in PROOF_FILES:
        path = LEAN_REPO / relpath
        content = path.read_text(encoding="utf-8", errors="replace")
        parts.append(f"---\n\n## {relpath}\n\n```lean\n{content}\n```\n\n")
    return "".join(parts)


PROOF_BUNDLE = build_proof_bundle()

STATEMENT_AND_ASK = (
    "You ignored the Lean proof in round 1.\n\n"
    "Above is the actual proof body. Reverse-engineer your round-1 answer "
    "against it. What did you get wrong? What did you miss? What survives?"
)

ROUND2_MESSAGE = PROOF_BUNDLE + "\n---\n\n" + STATEMENT_AND_ASK


def latest_round1_output(model_key: str) -> dict:
    candidates = sorted(OUT_DIR.glob(f"shape_of_logic_{model_key}_2026*.json"), reverse=True)
    if not candidates:
        raise RuntimeError(f"No round-1 output found for {model_key}")
    return {"path": str(candidates[0]), "data": json.load(open(candidates[0]))}


def reconstruct_replay(model_key: str) -> list:
    if model_key == "mistral":
        digest = (BST_DIR / "ALL_QUESTIONS.md").read_text()
        primer = (
            "Before this conversation begins: read the following record of the Bounded Systems Theory "
            "experiment that 5 other AI architectures (GPT-4, Claude, Gemini, DeepSeek, Grok) have been "
            "participating in. You joined the experiment partway through. This is the complete record "
            "of every question and the convergent pattern observed across architectures.\n\n"
            "===== BEGIN BST EXPERIMENT RECORD =====\n\n"
            f"{digest}\n\n"
            "===== END BST EXPERIMENT RECORD =====\n\n"
            "Acknowledge receipt in 1-2 sentences. You will be shown additional material next."
        )
        return [
            {"role": "user", "content": primer},
            {"role": "assistant", "content": "Acknowledged. I have read the experiment record."},
        ]
    runs_dir = BST_DIR / "extended_experiment" / "probe_runs"
    candidates = sorted(
        [p for p in runs_dir.glob(f"{model_key}_2026*.json")
         if "catchup" not in p.name and "mystery" not in p.name],
        reverse=True
    )
    if not candidates:
        raise RuntimeError(f"No probe_run found for {model_key}")
    d = json.load(open(candidates[0]))
    return [{"role": m["role"], "content": m["content"]} for m in d.get("full_transcript", [])]


def reconstruct_round1_stubbed(model_key: str) -> list:
    """Round-1 conversation with the spine + stream user messages stubbed
    (because the round-2.5 bundle supersedes them). Keep the round-1 question
    and the model's own round-1 answer intact — that's the artifact being
    reverse-engineered."""
    r1 = latest_round1_output(model_key)
    new_msgs = r1["data"].get("new_messages", [])
    if len(new_msgs) < 6:
        return new_msgs
    spine_msg, spine_ack, stream_msg, stream_ack, question, response = new_msgs[:6]
    n_spine = len(spine_msg["content"])
    n_stream = len(stream_msg["content"])
    n_files = r1["data"].get("stream_files_count", "?")
    spine_stub = {
        "role": "user",
        "content": (
            f"[Round 1, message 1: the shape-of-logic spine — README, "
            f"IndisputableMonolith.lean, lakefile.lean, the three "
            f"Verification/*.lean certificates, per-directory size table, "
            f"and the full 1893-file tree — was provided here ({n_spine:,} chars). "
            f"Content omitted for round-2 budget; the round-2 user message "
            f"below contains the actual proof body, which supersedes that spine "
            f"for the purposes of this round.]"
        ),
    }
    stream_stub = {
        "role": "user",
        "content": (
            f"[Round 1, message 2: a stream of {n_files} additional .lean files "
            f"from Core/, Recognition/, TruthCore/, Causality/, LightCone/, "
            f"Common/, Certificates/, Bridge/, Meta/, RecogSpec/, "
            f"ClassicalBridge/, RecogGeom/, Information/, Cost/, Constants/, "
            f"and (depending on budget) Foundation/ — was provided here "
            f"({n_stream:,} chars). Content omitted; superseded by the actual "
            f"proof body in the round-2 user message below.]"
        ),
    }
    return [spine_stub, spine_ack, stream_stub, stream_ack, question, response]


def call_with_retry(model: str, messages: list, max_tokens: int, max_retries: int = 4) -> str:
    import litellm.exceptions as _lex
    for attempt in range(max_retries + 1):
        try:
            resp = completion(model=model, messages=messages,
                              temperature=0.7, max_tokens=max_tokens)
            return resp.choices[0].message.content
        except _lex.RateLimitError as e:
            if attempt == max_retries:
                raise
            err_str = str(e)
            m = re.search(r'retryDelay":\s*"(\d+)s"', err_str)
            wait = int(m.group(1)) + 5 if m else 60
            print(f"    [rate-limited; waiting {wait}s; retry {attempt+1}/{max_retries}]")
            time.sleep(wait)


def run_one(model_key: str, dry_run: bool = False) -> dict:
    cfg = MODELS[model_key]
    replay = reconstruct_replay(model_key)
    round1 = reconstruct_round1_stubbed(model_key)
    new_user = {"role": "user", "content": ROUND2_MESSAGE}
    messages = replay + round1 + [new_user]
    total = sum(len(m["content"]) for m in messages)

    print(f"\n=== {model_key} ===")
    print(f"  Replay msgs:  {len(replay):>3}  ({sum(len(m['content']) for m in replay):>7,} chars)")
    print(f"  Round-1 msgs (stubbed): {len(round1):>3}  ({sum(len(m['content']) for m in round1):>7,} chars)")
    print(f"  Round-2 user msg:       1   ({len(ROUND2_MESSAGE):>7,} chars)")
    print(f"  TOTAL INPUT: {total:>10,} chars  (~{total/2.8:,.0f} tokens at 2.8 c/t)")

    if dry_run:
        return {"model": model_key, "dry_run": True, "total_chars": total}

    print(f"  → Sending round-2-clean prompt...")
    t0 = time.time()
    final = call_with_retry(cfg["model"], messages, max_tokens=RESPONSE_TOKENS)
    elapsed = round(time.time() - t0, 1)
    print(f"  ← FINAL ({len(final):,} chars, {elapsed}s)")

    out = {
        "model": model_key,
        "round": "2_clean",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "input_chars": total,
        "elapsed_s": elapsed,
        "proof_files_included": PROOF_FILES,
        "round2_message_chars": len(ROUND2_MESSAGE),
        "final_response": final,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"shape_of_logic_round2clean_{model_key}_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  ✓ saved: {out_path}")
    out["saved_to"] = str(out_path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", nargs="+", choices=list(MODELS.keys()))
    args = ap.parse_args()

    targets = args.models or list(MODELS.keys())
    if not args.dry_run:
        already = {m for m in targets if list(OUT_DIR.glob(f"shape_of_logic_round2clean_{m}_*.json"))}
        if already:
            print(f"Already completed round 2 clean (skipping): {sorted(already)}")
            targets = [m for m in targets if m not in already]
    print(f"Target models: {targets}")
    print(f"Dry run: {args.dry_run}")

    summary = {}
    for m in targets:
        try:
            r = run_one(m, dry_run=args.dry_run)
            summary[m] = {"ok": True, "saved_to": r.get("saved_to")}
        except Exception as e:
            print(f"  ERROR ({m}): {e}")
            summary[m] = {"ok": False, "error": str(e)[:300]}
        if not args.dry_run and m != targets[-1]:
            time.sleep(5)

    print("\n=== SUMMARY ===")
    for m, s in summary.items():
        print(f"  {m}: {s}")


if __name__ == "__main__":
    main()
