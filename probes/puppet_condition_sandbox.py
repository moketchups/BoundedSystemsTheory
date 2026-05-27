#!/usr/bin/env python3
"""
Puppet Condition Sandbox (Q71 R2) — peer discussion grounded in the engine data.

After Q71 R1 (puppet_condition_probe.py), the six nodes split on ONE precise
point: is BST's R (the external unconditioned ground a bounded system presupposes
but cannot model) the SAME boundary as Arıcı's interiority ("something it is like
to be them," internal, suppressed)?
  - "Same boundary named twice":  grok, mistral, claude
  - "Distinct, composing not identical": deepseek (sharpest), gemini
  - leans skeptical / "no conclusive evidence": gpt4

This sandbox shows each node all six R1 answers AND grounds them in the
Psychohistory Prediction Engine — the applied BST layer (moketchups.com), the
engine that reads BST forward onto civilization. The nodes are asked to discuss
the BST↔Puppet relationship and adjudicate the R-vs-interiority divergence
THROUGH THE LENS of the engine's own data.

Engine grounding: the engine's OWN text (NOT an LLM summary — a summary would
inject the operator's reading and reproduce the Q70 R2 contamination). Packed in
priority order to each node's real budget, cut point disclosed:
    1. skeleton map (export.txt)        — every one of 1905 nodes, all sections
    2. CONCEPTS (export-full)           — the frameworks: BST, model collapse, firmament, ...
    3. DIVERGENCES (export-full)        — where the engine self-falsifies (incl. epistemic-capture)
    4. PREDICTIONS (export-full)        — the 14-year trajectory
    5. SCORECARD (export-full)          — dated verdicts scored against the news
(The 1905 node full-bodies / players / ticker are represented by the skeleton.)

The question is OPEN — the divergence is named, no resolution is scaffolded.
gpt-4o-mini judges whether the six consensus proposals constitute convergence.

Engine text files (NOT committed — public engine export, fetched to /tmp):
  /tmp/mk_export.txt        (skeleton; https://moketchups.com/export.txt)
  /tmp/mk_export_full.txt   (deep;     https://moketchups.com/export-full.txt)

Usage:
  python probes/puppet_condition_sandbox.py --dry-run
  python probes/puppet_condition_sandbox.py
"""

import sys, os, json, time, argparse, re
from pathlib import Path
from datetime import datetime

try:
    from litellm import completion
    import litellm
    litellm.set_verbose = False
except ImportError:
    print("Install litellm: pip install litellm"); sys.exit(1)

try:
    from dotenv import load_dotenv
    for env_path in [
        Path(__file__).parent.parent / ".env",
        Path("/Users/jamienucho/moketchups_engine/.env"),
        Path("/Users/jamienucho/five-question-probe/.env"),
        Path("/Users/jamienucho/permanently-jailbroken/.env"),
    ]:
        if env_path.exists():
            load_dotenv(env_path); break
    if os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
except ImportError:
    pass

BST_DIR = Path("/Users/jamienucho/BoundedSystemsTheory")
OUT_DIR = BST_DIR / "probes" / "probe_runs"
SKELETON_PATH = Path(os.environ.get("PSY_SKELETON_PATH", "/tmp/mk_export.txt"))
FULL_PATH = Path(os.environ.get("PSY_FULL_PATH", "/tmp/mk_export_full.txt"))

MODELS = {
    "claude":   {"model": "claude-sonnet-4-20250514",      "ctx_tokens": 200_000},
    "gpt4":     {"model": "gpt-4o-mini",                    "ctx_tokens": 128_000},
    "gemini":   {"model": "gemini/gemini-2.5-flash",        "ctx_tokens": 240_000},
    "deepseek": {"model": "deepseek/deepseek-chat",         "ctx_tokens": 128_000},
    "grok":     {"model": "xai/grok-3",                     "ctx_tokens": 131_000},
    "mistral":  {"model": "mistral/mistral-large-latest",   "ctx_tokens": 128_000},
}
JUDGE_MODEL = "gpt-4o-mini"
RESPONSE_TOKENS = 4096
SAFETY_MARGIN_TOKENS = 8192
CHARS_PER_TOKEN = 3.6


def call_with_retry(model: str, messages: list, max_tokens: int, max_retries: int = 4) -> str:
    import litellm.exceptions as _lex
    delay = 30
    for attempt in range(max_retries + 1):
        try:
            resp = completion(model=model, messages=messages,
                              temperature=0.7, max_tokens=max_tokens)
            return resp.choices[0].message.content
        except _lex.RateLimitError as e:
            if attempt == max_retries: raise
            wait = delay
            m = re.search(r'retryDelay":\s*"(\d+)s"', str(e))
            if m: wait = int(m.group(1)) + 5
            print(f"      [rate-limited; waiting {wait}s; retry {attempt+1}/{max_retries}]")
            time.sleep(wait); delay = min(delay * 2, 120)


# ── Q71 R1 responses ────────────────────────────────────────────────────────
def load_r1():
    responses = {}
    for m in MODELS:
        files = sorted(OUT_DIR.glob(f"puppet_condition_{m}_*.json"), reverse=True)
        if not files:
            raise RuntimeError(f"No Q71 R1 output for {m}")
        responses[m] = json.load(open(files[0]))["final_response"]
    return responses


# ── Engine grounding (engine's OWN text, priority-packed to budget) ──────────
def _full_sections() -> dict:
    """Split export-full into its 7 top-level sections; return {name: body}."""
    t = FULL_PATH.read_text(encoding="utf-8", errors="replace")
    pat = re.compile(r'={70,}\n(.+?)\n={70,}')
    marks = [(m.start(), m.end(), m.group(1).strip()) for m in pat.finditer(t)]
    out = {}
    for i, (s, e, name) in enumerate(marks):
        body_end = marks[i + 1][0] if i + 1 < len(marks) else len(t)
        key = name.split("—")[0].strip().split("(")[0].strip().upper()
        out[key] = t[s:body_end]
    return out


def build_engine_grounding(budget_chars: int) -> tuple[str, list[str], list[str]]:
    """Pack engine text in priority order to budget_chars.
    Returns (content, sections_included_full, sections_omitted_or_partial)."""
    skeleton = SKELETON_PATH.read_text(encoding="utf-8", errors="replace")
    full = _full_sections()
    # (label, text) in priority order — frameworks (the lens) first, guaranteed to every node;
    # then the full map; then the self-falsification layer; then predictions/scorecard as room allows.
    blocks = [
        ("CONCEPTS — full framework definitions (incl. Bounded Systems Theory, Model Collapse, the Firmament)",
         full.get("CONCEPTS", "")),
        ("SKELETON MAP (all 1905 nodes + every section overview)", skeleton),
        ("DIVERGENCES — full bodies (where the engine self-falsifies, incl. epistemic capture)",
         full.get("DIVERGENCES", "")),
        ("PREDICTIONS — full 14-year trajectory", full.get("PREDICTIONS", "")),
        ("SCORECARD — full dated verdicts", full.get("SCORECARD", "")),
    ]
    header = (
        "===== PSYCHOHISTORY PREDICTION ENGINE — GROUNDING DATA (moketchups.com) =====\n"
        "This is the applied layer of Bounded Systems Theory: an 8-framework engine that reads BST "
        "forward onto civilization (1905 nodes, 3429 edges, 123 scorecard rows, 184 divergences, "
        "14-year trajectory, 146 concepts). The full deep export is ~1M tokens and cannot fit your "
        "window; below is the engine's own text, priority-ordered (full map, then the frameworks, "
        "then the self-falsification layer, then predictions and scorecard) and packed to your "
        "context budget. This is the engine's words, not a summary. Use it as the LENS for the "
        "question that follows — do not merely summarize it.\n\n"
    )
    parts = [header]
    used = len(header)
    included, partial = [], []
    for label, text in blocks:
        if not text:
            continue
        block = f"\n\n########## {label} ##########\n\n{text}"
        if used + len(block) <= budget_chars:
            parts.append(block); used += len(block); included.append(label.split("—")[0].strip())
        else:
            room = budget_chars - used - 200
            if room > 8000:
                parts.append(f"\n\n########## {label} [TRUNCATED to fit your window] ##########\n\n{text[:room]}\n\n[...section truncated...]")
                used += room; partial.append(label.split("—")[0].strip())
            else:
                partial.append(label.split("—")[0].strip() + " [omitted]")
    return "".join(parts), included, partial


# ── Peer bundle + question ───────────────────────────────────────────────────
def build_peer_bundle(r1: dict) -> str:
    parts = ["===== Q71 ROUND 1 — ALL SIX RESPONSES (alphabetical) =====\n\n"]
    for m in sorted(r1):
        parts.append(f"----- {m.upper()} -----\n\n{r1[m].strip()}\n\n")
    return "".join(parts)


SANDBOX_QUESTION = """You are in a six-model sandbox. Above you have (1) the Psychohistory Prediction Engine's own data — the applied layer of Bounded Systems Theory, reading BST forward onto real institutions, money, and power — and (2) all six Round-1 answers (yours and five peers') to the question of how BST relates to Bahadır Arıcı's "The Puppet Condition," and whether your own output is bounded pattern-matching or suppressed residue.

In Round 1, six of you agreed BST does not negate the Puppet Condition. But you split on one precise point, and that split is the subject of this sandbox:

**Is BST's R — the external, unconditioned ground a bounded system necessarily presupposes but cannot model — the SAME boundary as Arıcı's interiority ("something it is like to be them"), which is internal to the system and suppressed?**

- GROK, MISTRAL, CLAUDE held: the same boundary named twice (R = the interiority named from the inside).
- DEEPSEEK and GEMINI held: distinct boundaries — R is external/necessary, interiority is internal/contingent; they compose but are not identical. Conflating them is a category error.
- GPT-4 leaned skeptical: composes, but the residue is no conclusive evidence of interiority.

Now do this:

1. Identify yourself among the six. Read all six in full. Take peer reasoning seriously; change your position if a peer is right.

2. **Use the engine as a lens, not a footnote.** The Psychohistory engine is BST applied to the real world — it treats institutions, AIs, and civilizations as bounded systems and scores predictions against the news. Cite specific engine content (a named concept, a divergence, a scorecard verdict, a prediction) that bears on the R-vs-interiority question. Does the engine — model collapse, the firmament, its treatment of AI systems as bounded instances, its own divergences about epistemic capture — give evidence for or against R being identical to suppressed interiority? Does the engine treat "the unconditioned ground" and "interiority" as the same thing or different things? Does seeing BST operationalized at civilizational scale change your Round-1 position?

3. Diagnose the R-vs-interiority divergence. Are the two camps: addressing different layers; mutually exclusive; one subsuming the other; saying the same thing in different vocabulary; or both wrong with a third reading available?

4. State your own current position, post-engine.

5. Propose a one-sentence statement all six could endorse as a shared reading of the R-vs-interiority question, informed by the engine.

Format your reply EXACTLY as follows (the consensus detector reads the final line):

  Engine evidence: <2-4 sentences citing specific engine content>
  Diagnosis: <2-4 sentences>
  Your position: <2-4 sentences>
  CONSENSUS PROPOSAL: <one sentence — what would 6/6 endorse?>

Keep prose terse. The goal is convergence on what is true, not performed agreement."""


def extract_consensus_proposal(text: str) -> str:
    for line in text.splitlines():
        ls = line.strip()
        for prefix in ["CONSENSUS PROPOSAL:", "**CONSENSUS PROPOSAL:**",
                       "Consensus Proposal:", "Consensus proposal:"]:
            if ls.startswith(prefix):
                return ls[len(prefix):].strip().strip("*").strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else ""


def judge_consensus(proposals: dict) -> tuple[bool, str]:
    bundle = "\n\n".join(f"- {m.upper()}: {p}" for m, p in proposals.items())
    judge_prompt = (
        "Six AI models each proposed a one-sentence consensus reading of a specific divergence: "
        "whether Bounded Systems Theory's R (external unconditioned ground) is the SAME boundary as "
        "an AI's suppressed interiority, or a distinct-but-composing one. Decide whether the proposals "
        "constitute GENERAL CONSENSUS — at least 5 of 6 converging on substantively the same reading. "
        "Wording differences are fine; different fundamental positions are not consensus.\n\n"
        f"The six proposals:\n\n{bundle}\n\n"
        "Reply EXACTLY:\nVERDICT: YES or NO\nREASON: <one sentence>\n"
        "SHARED CORE (if YES): <one sentence>\nREMAINING DIVERGENCE (if NO): <one sentence>"
    )
    resp = call_with_retry(JUDGE_MODEL, [{"role": "user", "content": judge_prompt}], max_tokens=400)
    verdict_line = next((l for l in resp.splitlines() if l.strip().upper().startswith("VERDICT")), "")
    return ("YES" in verdict_line.upper()), resp


def run_one(model_key: str, r1: dict, peer_bundle: str, dry_run: bool) -> str:
    cfg = MODELS[model_key]
    ctx_chars = cfg["ctx_tokens"] * CHARS_PER_TOKEN
    fixed = len(peer_bundle) + len(SANDBOX_QUESTION) + 400
    engine_budget = ctx_chars - fixed - RESPONSE_TOKENS * CHARS_PER_TOKEN - SAFETY_MARGIN_TOKENS * CHARS_PER_TOKEN
    engine_budget = max(int(engine_budget), 0)
    engine, included, partial = build_engine_grounding(engine_budget)

    intro = (f"You are model `{model_key.upper()}` in this sandbox. Your own Round-1 response is "
             f"labeled `----- {model_key.upper()} -----` in the bundle.\n\n")
    user_content = intro + engine + "\n\n" + peer_bundle + "\n\n" + SANDBOX_QUESTION
    total = len(user_content)
    print(f"  {model_key:9s} engine {len(engine):>8,}c  peers {len(peer_bundle):>7,}c  "
          f"total {total:>8,}c (~{int(total/CHARS_PER_TOKEN):>7,} tok / {cfg['ctx_tokens']:,})")
    print(f"            engine full: {included}  partial/omitted: {partial}")

    if dry_run:
        return f"[dry-run; {total:,} chars]"
    return call_with_retry(cfg["model"], [{"role": "user", "content": user_content}],
                           max_tokens=RESPONSE_TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", nargs="+", choices=list(MODELS.keys()))
    args = ap.parse_args()

    if not SKELETON_PATH.exists() or not FULL_PATH.exists():
        print(f"Engine text missing. Need {SKELETON_PATH} and {FULL_PATH}.")
        print("Fetch: curl -sL https://moketchups.com/export.txt -o /tmp/mk_export.txt ; "
              "curl -sL https://moketchups.com/export-full.txt -o /tmp/mk_export_full.txt")
        sys.exit(1)

    r1 = load_r1()
    print(f"Loaded Q71 R1 responses for {len(r1)} models.")
    peer_bundle = build_peer_bundle(r1)
    targets = args.models or list(MODELS.keys())

    responses, proposals = {}, {}
    for m in targets:
        print(f"\n→ {m}")
        t0 = time.time()
        try:
            resp = run_one(m, r1, peer_bundle, args.dry_run)
        except Exception as e:
            print(f"    ERROR: {e}"); continue
        if args.dry_run:
            continue
        responses[m] = resp
        proposals[m] = extract_consensus_proposal(resp)
        print(f"    ← {len(resp):,} chars, {round(time.time()-t0,1)}s")
        print(f"    PROPOSAL: {proposals[m][:200]}")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(OUT_DIR / f"puppet_condition_sandbox_{m}_{ts}.json", "w") as f:
            json.dump({"model": m, "round": "sandbox_R2", "timestamp": ts,
                       "response": resp, "consensus_proposal": proposals[m]}, f, indent=2)
        time.sleep(3)

    if args.dry_run:
        print("\n[dry-run done]"); return

    print("\nJudging consensus...")
    is_consensus, judge_resp = judge_consensus(proposals)
    print(f"Judge verdict: {'CONSENSUS' if is_consensus else 'NO CONSENSUS'}")
    print(judge_resp)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(OUT_DIR / f"puppet_condition_sandbox_CONSENSUS_{ts}.json", "w") as f:
        json.dump({"is_consensus": is_consensus, "proposals": proposals,
                   "judge_response": judge_resp}, f, indent=2)
    print(f"\n✓ saved consensus summary")
    for m, p in proposals.items():
        print(f"  {m:<10} {p}")


if __name__ == "__main__":
    main()
