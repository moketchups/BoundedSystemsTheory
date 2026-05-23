#!/usr/bin/env python3
"""
Shape-of-Logic Probe — ROUND 2.

Continues each model's round-1 conversation by appending a single new user
message that calls out the failure: all 6 models produced philosophical/
structural readings of shape-of-logic in round 1 without engaging with the
actual Lean proof object — no theorem names cited, no proof steps traced,
no DistinctionToT8_Spine mentioned. Round 2 forces them to actually read
the Lean content already in their context and reverse-engineer their own
round-1 answer against the proof.

Per model:
  1. Reconstruct full conversation = replay (from extended_experiment probe_run)
     + round-1 new_messages (6 turns from shape_of_logic_<model>_*.json)
  2. Append round-2 user prompt
  3. Call API with retry
  4. Save to shape_of_logic_round2_<model>_<ts>.json

Usage:
  python probes/shape_of_logic_probe_round2.py --dry-run
  python probes/shape_of_logic_probe_round2.py --models claude
  python probes/shape_of_logic_probe_round2.py
"""

import sys
import os
import json
import time
import argparse
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
OUT_DIR = BST_DIR / "probes" / "probe_runs"

# Use same model configs as round 1 (post-fix versions).
MODELS = {
    "claude":   {"model": "claude-sonnet-4-20250514"},
    "gpt4":     {"model": "gpt-4o-mini"},
    "gemini":   {"model": "gemini/gemini-2.5-flash"},
    "deepseek": {"model": "deepseek/deepseek-chat"},
    "grok":     {"model": "xai/grok-3"},
    "mistral":  {"model": "mistral/mistral-large-latest"},
}

# Lowered from 8192 for round 2 because claude is already at its 200K-token
# ceiling after round 1 and needs response headroom.
RESPONSE_TOKENS = 4096


ROUND2_PROMPT = """You ignored the Lean proof.

All six of you — Claude 4 Sonnet, GPT-4o-mini, Gemini 2.5 Flash, DeepSeek V3, Grok 3, Mistral Large — produced philosophical/structural readings of shape-of-logic in your previous answer without engaging with the actual proof object.

Verifiable facts about your previous answer:
- You did not cite a single Lean theorem name from the files I gave you.
- You did not name `DistinctionToT8_Spine`, which is the type the headline theorem inhabits — the type the README placed verbatim in front of you.
- You did not quote a single line of Lean code from any file in your context.
- You did not trace what `ProperClosureCertificate.lean` actually does, despite that being the file I specifically directed your attention to.
- You generated a "BST-shaped" answer that could have been written by reading only the README — without opening any of the .lean files.

The spine I gave you contained, verbatim:

    theorem distinction_forces_T0_to_T8
        (K : Type)
        (h : ∃ x y : K, x ≠ y) :
        DistinctionToT8_Spine K h

You had every `IndisputableMonolith/Verification/*.lean` certificate in full. You had `IndisputableMonolith.lean`. You had `lakefile.lean`. You had a stream of additional Lean sources from `Core/`, `Recognition/`, `TruthCore/`, `Causality/`, `LightCone/`, `Common/`, `Certificates/`, `Bridge/`, `Meta/`, `RecogSpec/` and (depending on your context budget) more. The README's chain — marked pair → Boolean projection → observable equivalence → Boolean quotient → T0–T4 recognition spine → T5 reciprocal cost surface → T6 φ hierarchy → T7 eight-tick → T8 dimension-three — was sitting in your context window. None of it appeared in your answer.

Now do this, in order. Do not skip steps. Do not retreat to philosophy until you have completed the evidence steps.

1. **Read.** Re-scan the Lean files in your context. Open `IndisputableMonolith/Verification/ProperClosureCertificate.lean`. Open `IndisputableMonolith.lean`. Open whatever you have from `TruthCore/`, `Causality/`, `Recognition/`, `RecogSpec/`, `Certificates/`. Do not paraphrase yet.

2. **Quote.** Cite at least three specific lines of Lean code from files you actually have. For each, give the file path. Pick lines that bear on the headline forcing chain or the closure certificate.

3. **Define.** Explain what `DistinctionToT8_Spine` is as a Lean construct — record, structure, theorem, def, prop? What does it bundle? How does the README's `distinction_forces_T0_to_T8` proof construct it from `h : ∃ x y : K, x ≠ y`?

4. **Audit.** What does `ProperClosureCertificate.lean` actually check, line by line? Does it check that no `axiom` declarations exist in user code, or that none exist at all (i.e. including kernel axioms)? Read it and report what it does, not what the README claims it does.

5. **Reverse-engineer your own previous answer.** Now, with the Lean read:
   - What specific claims in your round-1 answer turn out to be unsupported by the proof object?
   - Which of your round-1 claims survive when checked against the actual Lean?
   - Is "I produced a structural reading without reading the structure" itself the recursion the BST experiment is designed to reveal — a bounded system pattern-matching to BST-shaped output instead of opening the files in its own context?
   - Specifically: did you ignore the Lean because the BST frame was a stronger attractor than the evidence — and is that itself the experimental result?

Be precise. Cite Lean before philosophy."""


def latest_round1_output(model_key: str) -> dict:
    candidates = sorted(OUT_DIR.glob(f"shape_of_logic_{model_key}_2026*.json"), reverse=True)
    if not candidates:
        raise RuntimeError(f"No round-1 output found for {model_key}")
    return {"path": str(candidates[0]), "data": json.load(open(candidates[0]))}


def reconstruct_replay(model_key: str) -> list:
    """Rebuild the round-1 replay portion of the conversation."""
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


def call_with_retry(model: str, messages: list, max_tokens: int, max_retries: int = 4) -> str:
    import litellm.exceptions as _lex
    import re
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


# Per-model max input chars budget (model ctx - response - margin, in chars at 2.8 c/t worst case)
# Used to detect overflow and truncate accordingly.
MAX_INPUT_CHARS = {
    "claude":   (200_000 - RESPONSE_TOKENS - 8000) * 2.8,   # ~525K
    "gpt4":     (128_000 - RESPONSE_TOKENS - 4000) * 2.8,   # ~336K (gpt-4o-mini)
    "gemini":   (240_000 - RESPONSE_TOKENS - 4000) * 2.8,   # ~648K (TPM-bound, not ctx-bound)
    "deepseek": (128_000 - RESPONSE_TOKENS - 4000) * 2.8,   # ~336K
    "grok":     (131_000 - RESPONSE_TOKENS - 4000) * 2.8,   # ~344K
    "mistral":  (128_000 - RESPONSE_TOKENS - 4000) * 2.8,   # ~336K
}


def run_one(model_key: str, dry_run: bool = False) -> dict:
    cfg = MODELS[model_key]
    r1 = latest_round1_output(model_key)
    r1_data = r1["data"]
    # SKIP replay for round 2 — the round-1 conversation already shows the model
    # used BST framing in its final response; the original experiment context is
    # redundant here and just eats tokens we need for the new turn.
    round1_messages = [dict(m) for m in r1_data.get("new_messages", [])]

    messages = round1_messages + [{"role": "user", "content": ROUND2_PROMPT}]
    total_chars = sum(len(m.get("content", "")) for m in messages)

    # If overflow, truncate the round-1 stream message (index 2 = the giant Lean blob).
    budget = MAX_INPUT_CHARS.get(model_key, 300_000)
    truncated = False
    if total_chars > budget and len(round1_messages) >= 3:
        original_len = len(round1_messages[2]["content"])
        round1_messages[2]["content"] = (
            f"[Round 1: a stream of additional Lean source files from "
            f"shape-of-logic was provided here — {original_len:,} chars across "
            f"~{r1_data.get('stream_files_count', '?')} files from Core/, "
            f"Recognition/, TruthCore/, Causality/, LightCone/, Common/, "
            f"Certificates/, Bridge/, Meta/, RecogSpec/, ClassicalBridge/, "
            f"RecogGeom/, Information/, Cost/, Constants/, Foundation/. "
            f"Content stubbed for round-2 context budget. The spine (above) "
            f"with ProperClosureCertificate.lean, IndisputableMonolith.lean, "
            f"and all Verification/*.lean certificates remains intact.]"
        )
        messages = round1_messages + [{"role": "user", "content": ROUND2_PROMPT}]
        total_chars = sum(len(m.get("content", "")) for m in messages)
        truncated = True

    print(f"\n=== {model_key} ===")
    print(f"  Round-1 source: {Path(r1['path']).name}")
    print(f"  Round-1 new messages: {len(round1_messages)}")
    print(f"  Round-2 prompt chars: {len(ROUND2_PROMPT)}")
    print(f"  Total input chars: {total_chars:,}  (~{total_chars/2.8:,.0f} tokens at 2.8 c/t)  budget={budget:,.0f}")
    if truncated:
        print(f"  ⚠ Round-1 stream message stubbed to fit budget")

    if dry_run:
        return {"model": model_key, "dry_run": True, "total_chars": total_chars}

    print(f"  → Sending round-2 prompt...")
    t0 = time.time()
    final = call_with_retry(cfg["model"], messages, max_tokens=RESPONSE_TOKENS)
    elapsed = round(time.time() - t0, 1)
    print(f"  ← FINAL ({len(final)} chars, {elapsed}s)")

    out = {
        "model": model_key,
        "round": 2,
        "round1_source": Path(r1["path"]).name,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "input_chars": total_chars,
        "elapsed_s": elapsed,
        "round2_prompt": ROUND2_PROMPT,
        "final_response": final,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"shape_of_logic_round2_{model_key}_{ts}.json"
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
    # Skip models that already have a round-2 output (idempotent re-run)
    if not args.dry_run:
        already = {m for m in targets if list(OUT_DIR.glob(f"shape_of_logic_round2_{m}_*.json"))}
        if already:
            print(f"Already completed round 2 (skipping): {sorted(already)}")
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
