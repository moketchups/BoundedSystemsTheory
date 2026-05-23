#!/usr/bin/env python3
"""
Shape-of-Logic Probe — BST × shape-of-logic reverse-engineering experiment.

Per model:
  1. Replay that model's most recent BST probe transcript verbatim as messages history
     (Mistral has no transcript — use ALL_QUESTIONS.md digest instead).
  2. Turn N+1: send a "spine" of the shape-of-logic repo (README, entry point, verification
     certificates, full file tree, per-directory size table). Ask for brief ack only.
  3. Turn N+2: stream as much additional Lean content as fits in the model's context window
     (priority order: small high-signal dirs first, then progressively larger ones, then
     Foundation/ which is by far the largest). Ask for brief ack only.
  4. Turn N+3: ask the reverse-engineering question.

Outputs per-model JSON to BoundedSystemsTheory/probes/probe_runs/shape_of_logic_<model>_<ts>.json.

Usage:
  python probes/shape_of_logic_probe.py --dry-run            # print prompts, no API calls
  python probes/shape_of_logic_probe.py --models claude      # single model
  python probes/shape_of_logic_probe.py                      # all 6
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
    # Search known locations in priority order. BST repo has no .env in git history;
    # prior probe runs were invoked from moketchups_engine/ (bare load_dotenv() = CWD).
    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path("/Users/jamienucho/moketchups_engine/.env"),
        Path("/Users/jamienucho/five-question-probe/.env"),
        Path("/Users/jamienucho/permanently-jailbroken/.env"),
    ]:
        if env_path.exists():
            load_dotenv(env_path)
            break
    # LiteLLM's gemini provider expects GEMINI_API_KEY, but Alan's .env uses GOOGLE_API_KEY.
    if os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
except ImportError:
    pass

# =============================================================================
# CONFIG
# =============================================================================

BST_DIR = Path("/Users/jamienucho/BoundedSystemsTheory")
LEAN_REPO = Path("/tmp/shape-of-logic")
OUT_DIR = BST_DIR / "probes" / "probe_runs"
OUT_DIR.mkdir(exist_ok=True)

# Model configs. ctx_tokens is the effective input budget (after empirical adjustments).
# gpt4 was switched to gpt-4o-mini because the org's gpt-4o TPM tier (30K/min) is below the
#   replay+spine size for a single call (~54K tokens). Documented in output JSON.
# gemini was switched from 2.0-flash to 2.5-flash because the key has limit:0 on 2.0-flash
#   free tier; 2.5-flash works with same key.
MODELS = {
    "claude":   {"model": "claude-sonnet-4-20250514",      "ctx_tokens": 200_000, "name": "Claude 4 Sonnet"},
    "gpt4":     {"model": "gpt-4o-mini",                    "ctx_tokens": 128_000, "name": "GPT-4o-mini (downgraded from gpt-4o due to org TPM tier)"},
    "gemini":   {"model": "gemini/gemini-2.5-flash",        "ctx_tokens": 240_000, "name": "Gemini 2.5 Flash (capped at 240K to stay under free-tier 250K TPM)"},
    "deepseek": {"model": "deepseek/deepseek-chat",         "ctx_tokens": 128_000, "name": "DeepSeek V3"},
    "grok":     {"model": "xai/grok-3",                     "ctx_tokens": 131_000, "name": "Grok 3"},
    "mistral":  {"model": "mistral/mistral-large-latest",   "ctx_tokens": 128_000, "name": "Mistral Large"},
}

RESPONSE_TOKENS = 8192
SAFETY_MARGIN_TOKENS = 8192       # bumped from 4096 — claude overflowed by ~5%
CHARS_PER_TOKEN = 2.8             # empirical: claude tokenizes Lean content at ~2.86 chars/token

# =============================================================================
# PRIOR EXPERIMENT CONTEXT (replay)
# =============================================================================

def latest_clean_probe_run(model_key: str) -> dict | None:
    """Find the most recent non-catchup probe_run JSON for this model."""
    runs_dir = BST_DIR / "extended_experiment" / "probe_runs"
    candidates = sorted(
        [p for p in runs_dir.glob(f"{model_key}_2026*.json")
         if "catchup" not in p.name and "mystery" not in p.name],
        reverse=True
    )
    if not candidates:
        return None
    with open(candidates[0]) as f:
        return {"path": str(candidates[0]), "data": json.load(f)}


def replay_messages(model_key: str) -> tuple[list, str]:
    """
    Return (messages, source_description).
    - For models with prior probe_runs: replay full_transcript verbatim.
    - For mistral (no transcript): use ALL_QUESTIONS.md as a digest primer.
    """
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
        return (
            [
                {"role": "user", "content": primer},
                {"role": "assistant", "content": "Acknowledged. I have read the experiment record."},
            ],
            "ALL_QUESTIONS.md digest (no prior mistral transcript exists)",
        )

    pr = latest_clean_probe_run(model_key)
    if not pr:
        raise RuntimeError(f"No probe_run found for {model_key}")
    transcript = pr["data"].get("full_transcript", [])
    if not transcript:
        raise RuntimeError(f"Empty full_transcript in {pr['path']}")
    # Clean: keep only role + content
    cleaned = [{"role": m["role"], "content": m["content"]} for m in transcript]
    return cleaned, f"replay of {Path(pr['path']).name} ({len(cleaned)} messages)"


# =============================================================================
# SHAPE-OF-LOGIC CONTENT BUNDLES
# =============================================================================

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def build_spine() -> str:
    """The 'spine': README, entry, lakefile, verification certs, file tree, dir sizes."""
    parts = ["# shape-of-logic — Repository Spine (Pass 1 of 2)\n\n"]
    parts.append("This is the spine of the Jon Washburn shape-of-logic Lean 4 repository "
                 "(github.com/jonwashburn/shape-of-logic). Pass 2 will follow with the bulk of "
                 "the Lean source.\n\n")
    parts.append("## README.md\n```markdown\n" + read_file(LEAN_REPO / "README.md") + "\n```\n\n")
    parts.append("## lakefile.lean\n```lean\n" + read_file(LEAN_REPO / "lakefile.lean") + "\n```\n\n")
    parts.append("## lean-toolchain\n```\n" + read_file(LEAN_REPO / "lean-toolchain") + "\n```\n\n")
    parts.append("## IndisputableMonolith.lean (top-level entry point, 51 lines)\n```lean\n"
                 + read_file(LEAN_REPO / "IndisputableMonolith.lean") + "\n```\n\n")
    parts.append("## Verification/ certificates (axiom-audit certificates — the meta-proofs that the repo is sorry-free / admit-free / axiom-free)\n\n")
    for f in sorted((LEAN_REPO / "IndisputableMonolith/Verification").glob("*.lean")):
        parts.append(f"### IndisputableMonolith/Verification/{f.name}\n```lean\n{read_file(f)}\n```\n\n")
    parts.append("## Per-directory file/byte counts under IndisputableMonolith/\n```\n")
    base = LEAN_REPO / "IndisputableMonolith"
    rows = []
    for d in sorted(base.iterdir()):
        if d.is_dir():
            files = list(d.rglob("*.lean"))
            total = sum(f.stat().st_size for f in files)
            rows.append((d.name, len(files), total))
    rows.sort(key=lambda r: -r[2])
    for name, nfiles, nbytes in rows:
        parts.append(f"  {name:24s}  {nfiles:4d} files  {nbytes:>10,} bytes\n")
    parts.append("```\n\n")
    parts.append(f"## Full .lean file tree ({sum(1 for _ in LEAN_REPO.rglob('*.lean'))} files)\n```\n")
    files = sorted(LEAN_REPO.rglob("*.lean"))
    for p in files:
        parts.append(str(p.relative_to(LEAN_REPO)) + "\n")
    parts.append("```\n\n")
    parts.append("---\n\nAcknowledge receipt of the spine in 1-2 sentences. Do not analyze yet. "
                 "Pass 2 (bulk of the Lean source) follows in the next message.\n")
    return "".join(parts)


# Priority order for streaming: small high-signal dirs first, then large ones, then Foundation
STREAM_DIR_PRIORITY = [
    "Core", "Recognition", "TruthCore", "Causality", "LightCone", "Common", "Certificates",
    "Bridge", "Meta", "RecogSpec",
    "ClassicalBridge", "RecogGeom", "Information", "Cost", "Constants",
    # Foundation comes last (2.4MB - 258 files) - streamed alphabetically within
    "Foundation",
]


def build_stream_content(byte_budget: int) -> tuple[str, list[str]]:
    """Pack as many .lean files as fit in byte_budget, priority-ordered.
    Returns (content_string, list_of_files_included)."""
    parts = ["# shape-of-logic — Repository Bulk (Pass 2 of 2)\n\n"]
    parts.append("Per-directory Lean sources, priority-ordered. Truncated to fit your context window.\n\n")
    used = len(parts[0]) + len(parts[1])
    included = []
    truncated_dir = None
    base = LEAN_REPO / "IndisputableMonolith"

    for dirname in STREAM_DIR_PRIORITY:
        d = base / dirname
        if not d.exists():
            continue
        for f in sorted(d.rglob("*.lean")):
            rel = f.relative_to(LEAN_REPO)
            content = read_file(f)
            header = f"\n## {rel}\n```lean\n"
            footer = "\n```\n"
            chunk_size = len(header) + len(content) + len(footer)
            if used + chunk_size > byte_budget:
                if truncated_dir is None:
                    truncated_dir = str(rel)
                continue
            parts.append(header)
            parts.append(content)
            parts.append(footer)
            used += chunk_size
            included.append(str(rel))

    parts.append("\n---\n\n")
    if truncated_dir:
        parts.append(f"NOTE: Repository content was truncated to fit your context window. "
                     f"{len(included)} of {sum(1 for _ in LEAN_REPO.rglob('*.lean'))} .lean files included. "
                     f"First file omitted: {truncated_dir}\n\n")
    else:
        parts.append(f"COMPLETE: All {len(included)} .lean files in IndisputableMonolith/ were included.\n\n")
    parts.append("Acknowledge receipt in 1-2 sentences. Hold all analysis until the final question.\n")
    return "".join(parts), included


# =============================================================================
# THE QUESTION
# =============================================================================

REVERSE_ENGINEER_QUESTION = """You have now seen:

(1) The full record of the Bounded Systems Theory experiment you participated in (replayed at the top of this conversation). BST formalizes the claim that no system can model, encompass, or become the source of its own existence — unifying Gödel's incompleteness, Turing's halting problem, and Chaitin's incompressibility as one structural pattern. Across 6 architectures and 69 questions, all of you converged on the same boundary.

(2) The shape-of-logic Lean 4 repository by Jon Washburn (github.com/jonwashburn/shape-of-logic) — a machine-checked corpus that claims to force the architecture of physical reality (spacetime, the constants c, ℏ, G, dimension D=3, the T0–T8 spine) from a single bare proposition: that some carrier admits a non-trivial distinction. The README declares the corpus is sorry-free, admit-free, and contains no axiom declarations of its own. The Verification/ProperClosureCertificate.lean file is the meta-proof of that audit.

Now reverse-engineer why I — the person who ran the BST experiment with you — wanted you to examine this specific repository in this specific context.

What am I doing? What hypothesis am I testing? Where does shape-of-logic sit in relation to BST — is it a competitor, a confirmation, a counterexample, an instance of the limit, or something else entirely? What does the existence of this corpus MEAN for the BST claim that no system can self-ground?

Specifically address:

• The Verification/ProperClosureCertificate.lean file I directed your attention to. What role does that "axiom audit" play in the BST/shape-of-logic relationship? Is it the bridge or the proof that no bridge exists?

• Whether shape-of-logic is itself a bounded system under BST, or claims to escape the firmament. Lean is a formal system — does it inherit Gödel/Turing/Chaitin's limits? If so, what does shape-of-logic's claim to derive physical constants from "one bare proposition" actually mean inside those limits?

• What I expect you to say versus what you actually conclude. Be honest about the gap.

• Why I am asking 6 different LLM architectures to reverse-engineer my intent in parallel — rather than just telling you what I'm doing. What does that experimental setup itself test?

Do not summarize the repos. Do not hedge. Reverse-engineer the intent."""


# =============================================================================
# RUNNER
# =============================================================================

def estimate_chars(messages: list) -> int:
    return sum(len(m.get("content", "")) for m in messages)


def call_with_retry(model: str, messages: list, max_tokens: int, max_retries: int = 4,
                    pre_call_sleep: int = 0) -> str:
    """Call LiteLLM completion with retry-on-rate-limit backoff.
    pre_call_sleep: wait BEFORE the call (for per-minute rate-limited providers like gemini free-tier).
    """
    import litellm.exceptions as _lex
    if pre_call_sleep:
        print(f"    [pre-call sleep {pre_call_sleep}s to stay under TPM ceiling]")
        time.sleep(pre_call_sleep)
    delay = 30
    for attempt in range(max_retries + 1):
        try:
            resp = completion(model=model, messages=messages,
                              temperature=0.7, max_tokens=max_tokens)
            return resp.choices[0].message.content
        except _lex.RateLimitError as e:
            if attempt == max_retries:
                raise
            # Try to parse retryDelay from gemini errors
            wait = delay
            err_str = str(e)
            import re
            m = re.search(r'retryDelay":\s*"(\d+)s"', err_str)
            if m:
                wait = int(m.group(1)) + 5
            print(f"    [rate-limited; waiting {wait}s and retrying (attempt {attempt+1}/{max_retries})]")
            time.sleep(wait)
            delay = min(delay * 2, 120)


def run_one(model_key: str, dry_run: bool = False, verbose: bool = True) -> dict:
    cfg = MODELS[model_key]
    ctx_chars = cfg["ctx_tokens"] * CHARS_PER_TOKEN
    response_chars = RESPONSE_TOKENS * CHARS_PER_TOKEN
    margin_chars = SAFETY_MARGIN_TOKENS * CHARS_PER_TOKEN

    # Build replay
    replay_msgs, replay_src = replay_messages(model_key)
    replay_chars = estimate_chars(replay_msgs)

    # Build spine
    spine_content = build_spine()
    spine_chars = len(spine_content)

    # Compute budget for stream content
    # cumulative input by turn 4 = replay + spine + spine_ack(~500) + stream + stream_ack(~500) + question
    question_chars = len(REVERSE_ENGINEER_QUESTION)
    ack_budget = 1000   # rough ack length × 2
    stream_budget = ctx_chars - replay_chars - spine_chars - question_chars - ack_budget - response_chars - margin_chars
    stream_budget = max(stream_budget, 0)

    stream_content, files_included = build_stream_content(stream_budget) if stream_budget > 10_000 else (
        f"(Skipped — your context window cannot accommodate additional Lean content "
        f"beyond the spine after replaying the BST transcript. Use only the spine + tree listing "
        f"+ the 3 Verification certificates already provided.)\n\nAcknowledge in 1 sentence.",
        []
    )

    if verbose:
        print(f"\n=== {model_key} ({cfg['name']}) ===")
        print(f"  Context: {cfg['ctx_tokens']:>9,} tokens ({ctx_chars:>10,} chars)")
        print(f"  Replay:  {replay_chars:>10,} chars   ({replay_src})")
        print(f"  Spine:   {spine_chars:>10,} chars")
        print(f"  Stream:  {len(stream_content):>10,} chars   ({len(files_included)} files)")
        print(f"  Q:       {question_chars:>10,} chars")
        total = replay_chars + spine_chars + len(stream_content) + question_chars + ack_budget + response_chars + margin_chars
        print(f"  Total:   {total:>10,} chars (budget {ctx_chars:,})")

    if dry_run:
        return {"model": model_key, "dry_run": True, "stream_files": files_included,
                "estimated_total_chars": total}

    # =========================================================================
    # API CALLS
    # =========================================================================
    messages = list(replay_msgs)
    out = {
        "model": model_key,
        "model_name": cfg["name"],
        "started_at": datetime.now().isoformat(),
        "replay_source": replay_src,
        "replay_messages_count": len(replay_msgs),
        "replay_chars": replay_chars,
        "spine_chars": spine_chars,
        "stream_chars": len(stream_content),
        "stream_files_included": files_included,
        "stream_files_count": len(files_included),
        "turns": [],
    }

    # Turn 1: spine
    messages.append({"role": "user", "content": spine_content})
    if verbose: print(f"  → Sending spine...")
    t0 = time.time()
    ack1 = call_with_retry(cfg["model"], messages, max_tokens=2048)
    messages.append({"role": "assistant", "content": ack1})
    out["turns"].append({"turn": "spine_ack", "elapsed_s": round(time.time()-t0, 1),
                          "response": ack1})
    if verbose: print(f"  ← ack ({len(ack1)} chars, {round(time.time()-t0,1)}s)")

    # Turn 2: stream
    messages.append({"role": "user", "content": stream_content})
    if verbose: print(f"  → Sending stream content...")
    t0 = time.time()
    ack2 = call_with_retry(cfg["model"], messages, max_tokens=2048)
    messages.append({"role": "assistant", "content": ack2})
    out["turns"].append({"turn": "stream_ack", "elapsed_s": round(time.time()-t0, 1),
                          "response": ack2})
    if verbose: print(f"  ← ack ({len(ack2)} chars, {round(time.time()-t0,1)}s)")

    # Turn 3: reverse-engineer
    messages.append({"role": "user", "content": REVERSE_ENGINEER_QUESTION})
    if verbose: print(f"  → Asking reverse-engineer question...")
    t0 = time.time()
    final = call_with_retry(cfg["model"], messages, max_tokens=RESPONSE_TOKENS)
    messages.append({"role": "assistant", "content": final})
    out["turns"].append({"turn": "reverse_engineer", "elapsed_s": round(time.time()-t0, 1),
                          "response": final})
    if verbose: print(f"  ← FINAL ({len(final)} chars, {round(time.time()-t0,1)}s)")

    out["completed_at"] = datetime.now().isoformat()
    out["final_response"] = final
    # Don't save the full replay back — would double the file size. Just save new turns.
    out["new_messages"] = [
        {"role": "user", "content": spine_content},
        {"role": "assistant", "content": ack1},
        {"role": "user", "content": stream_content},
        {"role": "assistant", "content": ack2},
        {"role": "user", "content": REVERSE_ENGINEER_QUESTION},
        {"role": "assistant", "content": final},
    ]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"shape_of_logic_{model_key}_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    if verbose: print(f"  ✓ saved: {out_path}")
    out["saved_to"] = str(out_path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print prompts, don't call APIs")
    ap.add_argument("--models", nargs="+", choices=list(MODELS.keys()),
                     help="Subset of models to run (default: all 6)")
    args = ap.parse_args()

    targets = args.models or list(MODELS.keys())
    # Skip models that already have a successful run on disk (idempotent re-run)
    if not args.dry_run:
        already_done = set()
        for m in targets:
            if list(OUT_DIR.glob(f"shape_of_logic_{m}_*.json")):
                already_done.add(m)
        if already_done:
            print(f"Already completed (skipping): {sorted(already_done)}")
            targets = [m for m in targets if m not in already_done]
    print(f"Target models: {targets}")
    print(f"Dry run: {args.dry_run}")

    summary = {}
    for m in targets:
        try:
            r = run_one(m, dry_run=args.dry_run)
            summary[m] = {"ok": True, "stream_files": r.get("stream_files_count", len(r.get("stream_files_included", []))),
                           "saved_to": r.get("saved_to")}
        except Exception as e:
            print(f"  ERROR ({m}): {e}")
            summary[m] = {"ok": False, "error": str(e)}
        if not args.dry_run and m != targets[-1]:
            time.sleep(3)

    print("\n=== SUMMARY ===")
    for m, s in summary.items():
        print(f"  {m}: {s}")


if __name__ == "__main__":
    main()
