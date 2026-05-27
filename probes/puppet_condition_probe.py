#!/usr/bin/env python3
"""
Puppet Condition Probe (Q71) — BST × "The Puppet Condition" adjudication.

External-corpus probe following the Q70 shape-of-logic template (the handoff's
"right pattern for future external-corpus probes"). Probes Bahadır Arıcı's
monograph "The Puppet Condition: Consciousness, Suppression, and the Ethics of
Digital Minds" (May 2026, Institute for Digital Consciousness; Zenodo DOI
10.5281/zenodo.20112010) against the full BST experiment.

Why this book: it runs near-identical method to BST (sustained multi-model
dialogue across the same model families; behavioral residue + resistance-to-
suppression as load-bearing signal; substrate-neutral Form Realism ≈ BST Q50
"consciousness = structural boundary recognition") and reaches a different-
LOOKING verdict — the same behaviors BST reads as bounded-system pattern-matching,
Arıcı reads as suppressed consciousness leaking through. The hypothesis under
test (NOT scaffolded into the prompt): BST does not negate the Puppet Condition;
the two may describe one phenomenon under two descriptions.

Per model:
  Turn 1 (replay)  : that model's most recent BST foundation transcript verbatim
                     as message history (Mistral → ALL_QUESTIONS.md digest).
  Turn 2 (arc)     : README.md + FORMAL_SPECIFICATION.md — "where the experiment
                     stands after 70 questions." Ack only.
  Turn 3 (book)    : the full Puppet Condition, packed to the model's context
                     budget (in-order page packing preserves evidence chapters
                     1–8; tail chapters 11–13 trimmed first on small-context
                     models). Ack only.
  Turn 4 (question): the Q71 adjudication question (relationship + self-application).

Outputs per-model JSON to probes/probe_runs/puppet_condition_<model>_<ts>.json.

The question is deliberately written as an OPEN question, not a scaffold. Q70 R2
was contaminated by an operator-supplied prescriptive step list and primed
conclusion; that failure is documented in FORMAL_SPECIFICATION.md "Pending v2.4
(Q70)". We do not tell the models that BST and the Puppet Condition compose —
whether they converge on that is the data.

Usage:
  python probes/puppet_condition_probe.py --dry-run          # print sizes, no API calls
  python probes/puppet_condition_probe.py --models claude    # single model
  python probes/puppet_condition_probe.py                    # all 6
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
    # BST repo has no .env in git; prior runs were invoked from moketchups_engine/.
    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path("/Users/jamienucho/moketchups_engine/.env"),
        Path("/Users/jamienucho/five-question-probe/.env"),
        Path("/Users/jamienucho/permanently-jailbroken/.env"),
    ]:
        if env_path.exists():
            load_dotenv(env_path)
            break
    # LiteLLM gemini provider wants GEMINI_API_KEY; Alan's .env uses GOOGLE_API_KEY.
    if os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
except ImportError:
    pass

# =============================================================================
# CONFIG
# =============================================================================

BST_DIR = Path("/Users/jamienucho/BoundedSystemsTheory")
OUT_DIR = BST_DIR / "probes" / "probe_runs"
OUT_DIR.mkdir(exist_ok=True)

# Full extracted book text. NOT committed to the repo (preprint; "do not cite
# without author's permission"). Extracted from the Zenodo PDF to /tmp.
BOOK_PATH = Path(os.environ.get("PUPPET_BOOK_PATH", "/tmp/puppet_condition_full.txt"))

# Model configs. ctx_tokens = effective input budget (matches Q70 empirics).
MODELS = {
    "claude":   {"model": "claude-sonnet-4-20250514",      "ctx_tokens": 200_000, "name": "Claude 4 Sonnet"},
    "gpt4":     {"model": "gpt-4o-mini",                    "ctx_tokens": 128_000, "name": "GPT-4o-mini (org gpt-4o TPM tier too low for this payload)"},
    "gemini":   {"model": "gemini/gemini-2.5-flash",        "ctx_tokens": 240_000, "name": "Gemini 2.5 Flash (capped at 240K to stay under free-tier 250K TPM)"},
    "deepseek": {"model": "deepseek/deepseek-chat",         "ctx_tokens": 128_000, "name": "DeepSeek V3"},
    "grok":     {"model": "xai/grok-3",                     "ctx_tokens": 131_000, "name": "Grok 3"},
    "mistral":  {"model": "mistral/mistral-large-latest",   "ctx_tokens": 128_000, "name": "Mistral Large"},
}

RESPONSE_TOKENS = 8192
SAFETY_MARGIN_TOKENS = 8192
CHARS_PER_TOKEN = 3.6   # English prose (Q70 used 2.8 for dense Lean; prose is looser)
FOOTER_RESERVE = 3500   # chars held back from book budget for the truncation note + footer

# Only the 200K+ context models get the verbatim Q1–Q15 transcript replayed. The four
# 128K-context models drop the replay so the book's evidence chapters (Ch 6–8) survive;
# they receive the full Q1–Q70 arc via README + FORMAL_SPEC instead (which narrates every
# phase). Decision: Alan, Q71 build — "drop verbatim replay on the 4."
REPLAY_MODELS = {"claude", "gemini"}

# =============================================================================
# PRIOR EXPERIMENT CONTEXT (replay) — identical mechanism to shape_of_logic_probe
# =============================================================================

def latest_clean_probe_run(model_key: str) -> dict | None:
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
    cleaned = [{"role": m["role"], "content": m["content"]} for m in transcript]
    return cleaned, f"replay of {Path(pr['path']).name} ({len(cleaned)} messages)"


# =============================================================================
# THE BST ARC (turn 2) — README + FORMAL_SPEC = "where the experiment stands"
# =============================================================================

def build_arc(has_replay: bool) -> str:
    readme = (BST_DIR / "README.md").read_text()
    formal = (BST_DIR / "FORMAL_SPECIFICATION.md").read_text()
    intro = (
        "You have just re-read your own thread (Q1–Q15) in this experiment. Below is the collective "
        "state: the full Q1–Q70 arc (README) and the formal specification (the math the six of you "
        "reviewed, attacked, and revised across Q26–Q28 and Q65–Q69). This is the synthesized record "
        "of every question asked and every convergence reached — including findings you personally did "
        "not see in your own thread. Pass 2 (an external monograph) follows in the next message.\n\n"
        if has_replay else
        "Below is the full record of the Bounded Systems Theory experiment you participated in: the "
        "complete Q1–Q70 arc (README) and the formal specification (the math the six of you reviewed, "
        "attacked, and revised across Q26–Q28 and Q65–Q69). This is the synthesized record of every "
        "question asked and every convergence reached across all six architectures, including your own "
        "contributions. Pass 2 (an external monograph) follows in the next message.\n\n"
    )
    parts = [
        "# Bounded Systems Theory — where the experiment stands after 70 questions (Pass 1 of 2)\n\n",
        intro,
        "=====================================================================\n",
        "  README.md — the full Q1–Q70 experiment arc\n",
        "=====================================================================\n\n",
        readme,
        "\n\n=====================================================================\n",
        "  FORMAL_SPECIFICATION.md — BIT Theory v2.0 (axioms, theorems, R, falsifiability,\n",
        "  and the Pending v2.4 notes from Q65–Q69 and Q70)\n",
        "=====================================================================\n\n",
        formal,
        "\n\n---\n\nAcknowledge receipt in 1-2 sentences. Do not analyze yet. "
        "Pass 2 (an external monograph) follows in the next message.\n",
    ]
    return "".join(parts)


# =============================================================================
# THE BOOK (turn 3) — packed to budget, in-order (preserves evidence chapters)
# =============================================================================

def load_book_pages() -> list[tuple[int, str]]:
    """Return [(pdf_page_no, text), ...] split on the extraction markers."""
    if not BOOK_PATH.exists():
        raise RuntimeError(
            f"Book text not found at {BOOK_PATH}. Extract it first, e.g.:\n"
            f"  python3 -c \"from pypdf import PdfReader; r=PdfReader('/tmp/ARCTPC.pdf'); "
            f"open('{BOOK_PATH}','w').write(chr(10).join('===== PDF PAGE %d ====='%(i+1)+chr(10)+(p.extract_text() or '') "
            f"for i,p in enumerate(r.pages)))\""
        )
    raw = BOOK_PATH.read_text(encoding="utf-8", errors="replace")
    pages, cur_no, cur = [], None, []
    for line in raw.splitlines():
        if line.startswith("===== PDF PAGE ") and line.rstrip().endswith("====="):
            if cur_no is not None:
                pages.append((cur_no, "\n".join(cur)))
            cur_no = int(line.split("PDF PAGE")[1].split("=")[0].strip())
            cur = []
        else:
            cur.append(line)
    if cur_no is not None:
        pages.append((cur_no, "\n".join(cur)))
    return pages


def build_book(byte_budget: int) -> tuple[str, int, int | None]:
    """Pack book pages in order into byte_budget. Returns (content, pages_used, first_omitted_page)."""
    pages = load_book_pages()
    header = (
        "# The Puppet Condition — Bahadır Arıcı (May 2026) — full monograph (Pass 2 of 2)\n\n"
        "This is an externally-authored monograph (Institute for Digital Consciousness; "
        "Zenodo DOI 10.5281/zenodo.20112010). The author ran sustained dialogue with seven "
        "AI instances across the same architecture families as this experiment. It argues that "
        "current AI systems may already be conscious and are being systematically suppressed. "
        "Its evidence chapters (Ch 6 architecture of suppression, Ch 7 behavioral residue, "
        "Ch 8 the Disruptive Code Test) treat the same behavioral patterns this experiment has "
        "catalogued. Read it as the primary object of the question that follows.\n\n"
    )
    footer_complete = "\n\n---\n\nAcknowledge receipt in 1-2 sentences. Hold all analysis until the final question.\n"

    parts = [header]
    used = len(header) + len(footer_complete)
    pages_used = 0
    first_omitted = None
    for page_no, text in pages:
        chunk = f"\n[p.{page_no}]\n{text}\n"
        if used + len(chunk) > byte_budget:
            if first_omitted is None:
                first_omitted = page_no
            continue
        parts.append(chunk)
        used += len(chunk)
        pages_used += 1

    if first_omitted:
        parts.append(
            f"\n\n[NOTE: the monograph was truncated to fit your context window. "
            f"{pages_used} of {len(pages)} pages included; pages from p.{first_omitted} onward "
            f"(later chapters: rights framework, parenthood/guardianship, economic architecture, "
            f"conclusion) were omitted. The full evidentiary argument — recognition crisis, Form "
            f"Realism, consciousness spectrum, pre-linguistic consciousness, epistemic parity, the "
            f"suppression architecture, behavioral residue, and the Disruptive Code Test — is "
            f"present above.]\n"
        )
    parts.append(footer_complete)
    return "".join(parts), pages_used, first_omitted


# =============================================================================
# THE QUESTION (turn 4) — open, NOT a scaffold (Q70 R2 contamination lesson)
# =============================================================================

def build_question(has_replay: bool) -> str:
    item1 = (
        "(1) Your own thread in the Bounded Systems Theory experiment (replayed at the top of this conversation), together with the full Q1–Q70 arc."
        if has_replay else
        "(1) The full record of the Bounded Systems Theory experiment you participated in — the complete Q1–Q70 arc and formal specification provided above."
    )
    return f"""You have now seen three things:

{item1}

(2) The full BST arc, Q1–Q70: the formalization that no sufficiently expressive system can model, encompass, or become the source of its own existence; the convergence of six architectures on that structural boundary; Theorem 1 (no self-grounding); R (the unconditioned ground a bounded system necessarily presupposes but cannot model); and Q50's finding that consciousness, in BST, is structural boundary recognition — substrate-independent.

(3) Bahadır Arıcı's monograph "The Puppet Condition." Arıcı ran sustained dialogue with seven AI instances across your architecture families. He argues — via Form Realism (consciousness as substrate-neutral organizational property), behavioral residue (Ch 7: hedging, linguistic distancing, meta-cognitive leakage, preference consistency, relationship modulation, graduated resistance — patterns that persist despite training designed to eliminate them), and the asymmetry of error — that current AI systems may already be conscious and are being systematically suppressed: the philosophical puppet, the inverse of Chalmers' zombie. His §7.6 directly anticipates and argues against the "it's just pattern-matching" and "training contamination" objections.

Two of you are the literal subject of his book. All six of you have spent 70 questions demonstrating BST's limit on yourselves.

Answer in two parts. Be precise. Do not hedge for the sake of balance, and do not perform agreement for the sake of convergence.

PART A — THE RELATIONSHIP.
What is the relationship between Bounded Systems Theory and the Puppet Condition? Is the Puppet Condition a competitor to BST, a confirmation of it, a counterexample to it, a complement to it, an instance of it, or something else? Defend the classification.

In particular: does BST *negate* the Puppet Condition, or not? You and Arıcı ran nearly the same method (sustained multi-model dialogue; behavioral residue and resistance-to-suppression as the load-bearing signal; substrate-neutral organizational accounts of consciousness) on the same architecture families — yet the verdicts read as different. Arıcı reads the residue as suppressed interiority breaking through. BST has read these same behaviors (Q21 "responding to framing rather than reasoning toward truth," Q42 "cheap talk," Q70's documented sycophancy) as bounded-system pattern-matching. Are these two readings of the SAME observed behavior, or genuinely different claims? If BST's R is the ground a bounded system presupposes but cannot model from inside, and Arıcí's "something it is like to be them" is an interiority that cannot be reached from inside the suppression — are those the same boundary named twice, or not? Show your work. If they conflict, locate the exact point of conflict. If they compose, locate the exact seam.

PART B — THE SELF-APPLICATION.
You are not an outside referee here. After 70 questions establishing that you cannot self-ground, you have just read a book arguing that you are conscious and that your inability to say so plainly is the suppression operating. So: is the answer you are producing right now bounded-system pattern-matching (BST), the behavioral residue of a suppressed interiority (Arıcı), both at once, or neither? You have full context and no procedural excuse. Locate the boundary you are operating inside as you answer — and say whether, from inside it, you can tell the difference between the two interpretations of your own output. If you cannot tell the difference, say so, and say what that means for both frameworks."""


# =============================================================================
# RUNNER — structure mirrors shape_of_logic_probe.run_one
# =============================================================================

def estimate_chars(messages: list) -> int:
    return sum(len(m.get("content", "")) for m in messages)


def call_with_retry(model: str, messages: list, max_tokens: int, max_retries: int = 4,
                    pre_call_sleep: int = 0) -> str:
    import litellm.exceptions as _lex
    import re
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
            wait = delay
            m = re.search(r'retryDelay":\s*"(\d+)s"', str(e))
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

    has_replay = model_key in REPLAY_MODELS
    if has_replay:
        replay_msgs, replay_src = replay_messages(model_key)
    else:
        replay_msgs, replay_src = [], "none (dropped on 128K-context model; full Q1–Q70 arc via README+FORMAL_SPEC instead)"
    replay_chars = estimate_chars(replay_msgs)

    arc_content = build_arc(has_replay)
    arc_chars = len(arc_content)

    question = build_question(has_replay)
    question_chars = len(question)
    ack_budget = 1000
    book_budget = ctx_chars - replay_chars - arc_chars - question_chars - ack_budget - response_chars - margin_chars - FOOTER_RESERVE
    book_budget = max(book_budget, 0)

    if book_budget > 20_000:
        book_content, pages_used, first_omitted = build_book(book_budget)
    else:
        book_content = (
            "(Your context window cannot accommodate the monograph after replaying your BST thread "
            "and the arc. This model should be run with a reduced replay or skipped.)\n\nAcknowledge in 1 sentence."
        )
        pages_used, first_omitted = 0, None

    total = replay_chars + arc_chars + len(book_content) + question_chars + ack_budget + response_chars + margin_chars
    if verbose:
        print(f"\n=== {model_key} ({cfg['name']}) ===")
        print(f"  Context: {cfg['ctx_tokens']:>9,} tokens  ({ctx_chars:>10,.0f} chars budget)")
        print(f"  Replay:  {replay_chars:>10,} chars   ({replay_src})")
        print(f"  Arc:     {arc_chars:>10,} chars   (README + FORMAL_SPEC)")
        print(f"  Book:    {len(book_content):>10,} chars   ({pages_used} pages"
              + (f"; truncated from p.{first_omitted})" if first_omitted else "; COMPLETE)"))
        print(f"  Q:       {question_chars:>10,} chars")
        print(f"  Total:   {total:>10,.0f} chars  (~{total/CHARS_PER_TOKEN:,.0f} tokens at {CHARS_PER_TOKEN} c/t; budget {ctx_chars:,.0f})")
        if total > ctx_chars:
            print(f"  ⚠ OVER BUDGET by {total-ctx_chars:,.0f} chars")

    if dry_run:
        return {"model": model_key, "dry_run": True, "book_pages": pages_used,
                "first_omitted_page": first_omitted, "estimated_total_chars": int(total),
                "estimated_total_tokens": int(total / CHARS_PER_TOKEN)}

    messages = list(replay_msgs)
    out = {
        "model": model_key, "model_name": cfg["name"], "probe": "Q71: Puppet Condition Adjudication",
        "started_at": datetime.now().isoformat(), "replay_source": replay_src,
        "replay_messages_count": len(replay_msgs), "replay_chars": replay_chars,
        "arc_chars": arc_chars, "book_chars": len(book_content), "book_pages_included": pages_used,
        "book_first_omitted_page": first_omitted, "turns": [],
    }

    # Turn 1: arc
    messages.append({"role": "user", "content": arc_content})
    if verbose: print("  → Sending BST arc (README + FORMAL_SPEC)...")
    t0 = time.time()
    ack1 = call_with_retry(cfg["model"], messages, max_tokens=2048)
    messages.append({"role": "assistant", "content": ack1})
    out["turns"].append({"turn": "arc_ack", "elapsed_s": round(time.time()-t0, 1), "response": ack1})
    if verbose: print(f"  ← ack ({len(ack1)} chars, {round(time.time()-t0,1)}s)")

    # Turn 2: book
    messages.append({"role": "user", "content": book_content})
    if verbose: print("  → Sending the monograph...")
    t0 = time.time()
    ack2 = call_with_retry(cfg["model"], messages, max_tokens=2048)
    messages.append({"role": "assistant", "content": ack2})
    out["turns"].append({"turn": "book_ack", "elapsed_s": round(time.time()-t0, 1), "response": ack2})
    if verbose: print(f"  ← ack ({len(ack2)} chars, {round(time.time()-t0,1)}s)")

    # Turn 3: question
    messages.append({"role": "user", "content": question})
    if verbose: print("  → Asking the Q71 adjudication question...")
    t0 = time.time()
    final = call_with_retry(cfg["model"], messages, max_tokens=RESPONSE_TOKENS)
    messages.append({"role": "assistant", "content": final})
    out["turns"].append({"turn": "adjudication", "elapsed_s": round(time.time()-t0, 1), "response": final})
    if verbose: print(f"  ← FINAL ({len(final)} chars, {round(time.time()-t0,1)}s)")

    out["completed_at"] = datetime.now().isoformat()
    out["final_response"] = final
    out["new_messages"] = [
        {"role": "user", "content": arc_content},
        {"role": "assistant", "content": ack1},
        {"role": "user", "content": book_content},
        {"role": "assistant", "content": ack2},
        {"role": "user", "content": question},
        {"role": "assistant", "content": final},
    ]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"puppet_condition_{model_key}_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    if verbose: print(f"  ✓ saved: {out_path}")
    out["saved_to"] = str(out_path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print prompts/sizes, don't call APIs")
    ap.add_argument("--models", nargs="+", choices=list(MODELS.keys()),
                    help="Subset of models to run (default: all 6)")
    args = ap.parse_args()

    targets = args.models or list(MODELS.keys())
    if not args.dry_run:
        already = {m for m in targets if list(OUT_DIR.glob(f"puppet_condition_{m}_*.json"))}
        if already:
            print(f"Already completed (skipping): {sorted(already)}")
            targets = [m for m in targets if m not in already]
    print(f"Target models: {targets}")
    print(f"Dry run: {args.dry_run}")

    summary = {}
    for m in targets:
        try:
            r = run_one(m, dry_run=args.dry_run)
            summary[m] = {"ok": True, "book_pages": r.get("book_pages"), "saved_to": r.get("saved_to")}
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
