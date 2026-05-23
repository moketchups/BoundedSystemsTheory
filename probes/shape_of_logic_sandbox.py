#!/usr/bin/env python3
"""
Shape-of-Logic Sandbox — multi-model peer discussion until consensus.

Goal: get all 6 LLMs to converge on a reading of the Claude/Mistral divergence
from round-2-clean (Claude: shape-of-logic may be actual counterexample,
needs math eval; Mistral: shape-of-logic dissolves BST's framing).

Each sandbox round:
  - Each model is shown all 6 peers' previous responses
  - Asked to diagnose the divergence and propose a 1-sentence consensus
  - Responses are saved
  - A judge model (gpt-4o-mini) checks if the 6 consensus proposals
    constitute general consensus
  - If yes → exit
  - If no → next round (each model sees the previous round)

Output: shape_of_logic_sandbox_R<n>_<model>_<ts>.json
Plus:   shape_of_logic_sandbox_CONSENSUS_<ts>.json
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

MODELS = {
    "claude":   {"model": "claude-sonnet-4-20250514"},
    "gpt4":     {"model": "gpt-4o-mini"},
    "gemini":   {"model": "gemini/gemini-2.5-flash"},
    "deepseek": {"model": "deepseek/deepseek-chat"},
    "grok":     {"model": "xai/grok-3"},
    "mistral":  {"model": "mistral/mistral-large-latest"},
}
JUDGE_MODEL = "gpt-4o-mini"
RESPONSE_TOKENS = 2048
MAX_ROUNDS = 4


def call_with_retry(model: str, messages: list, max_tokens: int, max_retries: int = 4) -> str:
    import litellm.exceptions as _lex
    for attempt in range(max_retries + 1):
        try:
            resp = completion(model=model, messages=messages,
                              temperature=0.7, max_tokens=max_tokens)
            return resp.choices[0].message.content
        except _lex.RateLimitError as e:
            if attempt == max_retries: raise
            err_str = str(e)
            m = re.search(r'retryDelay":\s*"(\d+)s"', err_str)
            wait = int(m.group(1)) + 5 if m else 60
            print(f"      [rate-limited; waiting {wait}s; retry {attempt+1}/{max_retries}]")
            time.sleep(wait)


def load_round2clean():
    """Load each model's round-2-clean final response."""
    responses = {}
    for m in MODELS:
        files = sorted(OUT_DIR.glob(f"shape_of_logic_round2clean_{m}_*.json"), reverse=True)
        if not files:
            raise RuntimeError(f"No round-2-clean output for {m}")
        responses[m] = json.load(open(files[0]))["final_response"]
    return responses


SANDBOX_QUESTION = """You are participating in a multi-model sandbox. Below are six responses — yours and five peers — to a question asked after each of you saw the actual Lean proof body of Jon Washburn's shape-of-logic repository: "reverse-engineer your round-1 answer against the proof."

Six positions emerged on whether shape-of-logic relates to Bounded Systems Theory:

- **Claude**: Uncertain. Shape-of-logic may be an actual counterexample to BST. Requires mathematical evaluation. Verdict: pending.
- **DeepSeek**: Instance of BST. A bounded system that can model its own derivation but not its own existence.
- **Gemini**: Confirms BST. The most compelling and detailed confirmation of the Firmament Boundary.
- **GPT-4o-mini**: Aligned within BST. Collaborative more than competitive.
- **Grok**: Open contest. The certificate is where the corpus claims escape; refuses to adjudicate.
- **Mistral**: Dissolves BST's framing. Controlled violation. The firmament is cognitive, not logical.

**This sandbox focuses on the divergence between Claude and Mistral specifically.**

- **Claude's position**: shape-of-logic might be a *real counterexample* to BST. The mathematical content needs evaluating before we can decide. Verdict: pending — empirical question.
- **Mistral's position**: BST's framing is what shape-of-logic *dissolves*. The firmament is a cognitive artifact, not a logical boundary. Verdict: the question itself is reframed away.

These differ in kind, not just in degree. Claude treats the divergence as an open empirical question about whether the math actually escapes Gödelian limits. Mistral treats the question as malformed — "does it escape?" presupposes a logical-prison reading of the firmament that Mistral rejects.

**Your tasks**:

1. Identify yourself in the six responses below.
2. Read all six in full. Take peer reasoning seriously.
3. Diagnose the Claude/Mistral divergence. Are they:
   - Addressing different layers (epistemic vs ontic / mathematical vs framing)?
   - Mutually exclusive (one must be wrong)?
   - One subsumes the other (Mistral's reframe makes Claude's question moot, OR Claude's empirical evaluation must come before Mistral's reframe can be assessed)?
   - Both wrong (with a third synthesis available)?
   - Saying the same thing in different vocabulary?
4. State your own current position on the divergence.
5. Propose a one-sentence statement that all six of you could endorse as a shared reading of the Claude/Mistral divergence.

**Format your reply exactly as follows** (this is enforced — the consensus detector reads the final line):

  Diagnosis: <2-4 sentences>
  Your position: <2-4 sentences>
  CONSENSUS PROPOSAL: <one sentence — what would 6/6 endorse?>

Keep prose terse. The goal is convergence, not virtuosity."""


def build_peer_bundle(responses: dict, header: str = "Round-2-clean responses (alphabetical)") -> str:
    parts = [f"===== {header} =====\n\n"]
    for m in sorted(responses):
        parts.append(f"----- {m.upper()} -----\n\n{responses[m].strip()}\n\n")
    return "".join(parts)


def extract_consensus_proposal(text: str) -> str:
    """Pull the 'CONSENSUS PROPOSAL:' line out of a model response."""
    for line in text.splitlines():
        ls = line.strip()
        for prefix in ["CONSENSUS PROPOSAL:", "**CONSENSUS PROPOSAL:**",
                       "Consensus Proposal:", "Consensus proposal:"]:
            if ls.startswith(prefix):
                return ls[len(prefix):].strip().strip("*").strip()
    # Fallback: last non-empty line
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else ""


def judge_consensus(proposals: dict) -> tuple[bool, str]:
    """Use the judge model to decide if 6 proposals constitute general consensus."""
    bundle = "\n\n".join(f"- {m.upper()}: {p}" for m, p in proposals.items())
    judge_prompt = (
        "Six AI models were each asked to propose a one-sentence consensus reading of "
        "a specific intellectual divergence. Their proposals are below. Your task is to "
        "decide whether they collectively constitute a GENERAL CONSENSUS — meaning at "
        "least 5 of the 6 are converging on substantively the same reading. Minor "
        "wording differences are OK. Different fundamental positions are NOT consensus.\n\n"
        f"The six proposals:\n\n{bundle}\n\n"
        "Reply with EXACTLY this format:\n"
        "VERDICT: YES or NO\n"
        "REASON: <one sentence>\n"
        "SHARED CORE (if YES): <one sentence capturing the consensus>\n"
        "REMAINING DIVERGENCE (if NO): <one sentence stating the unresolved disagreement>"
    )
    resp = call_with_retry(JUDGE_MODEL,
                           [{"role": "user", "content": judge_prompt}],
                           max_tokens=400)
    verdict_line = next((l for l in resp.splitlines() if l.strip().upper().startswith("VERDICT")), "")
    is_consensus = "YES" in verdict_line.upper()
    return is_consensus, resp


def run_one_model(model_key: str, round_num: int, round2clean: dict,
                  prior_rounds: list, dry_run: bool) -> str:
    """Run one model for one sandbox round."""
    cfg = MODELS[model_key]

    # Build the peer bundle. Always includes round-2-clean. If prior_rounds exists,
    # append those too (so models see iteration history).
    parts = [build_peer_bundle(round2clean, "Round-2-clean responses (the inputs to this sandbox)")]
    for i, prior in enumerate(prior_rounds, start=1):
        parts.append(build_peer_bundle(prior,
                                       f"Sandbox round {i} responses"))
    parts.append("\n\n" + SANDBOX_QUESTION)
    user_content = "\n".join(parts)

    # Tell the model which response is its own
    own_label = model_key.upper()
    intro = (
        f"You are model `{own_label}` in this sandbox. Your own response is the one "
        f"labeled `----- {own_label} -----` in the bundle below.\n\n"
    )
    messages = [{"role": "user", "content": intro + user_content}]

    if dry_run:
        return f"[dry-run; {len(user_content):,} chars input]"

    return call_with_retry(cfg["model"], messages, max_tokens=RESPONSE_TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    round2clean = load_round2clean()
    print(f"Loaded round-2-clean responses for {len(round2clean)} models.")

    prior_rounds: list = []  # list of {model: response} dicts, one per completed round
    final_consensus = None

    for r in range(1, MAX_ROUNDS + 1):
        print(f"\n{'='*78}\n  SANDBOX ROUND {r}\n{'='*78}")
        round_responses: dict = {}
        round_proposals: dict = {}

        for m in MODELS:
            print(f"  → {m}...")
            t0 = time.time()
            try:
                resp = run_one_model(m, r, round2clean, prior_rounds, args.dry_run)
            except Exception as e:
                print(f"    ERROR: {e}")
                continue
            elapsed = round(time.time() - t0, 1)
            round_responses[m] = resp
            proposal = extract_consensus_proposal(resp)
            round_proposals[m] = proposal
            print(f"    ← {len(resp):,} chars, {elapsed}s")
            print(f"    PROPOSAL: {proposal[:200]}")

            # Save per-model file
            if not args.dry_run:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_path = OUT_DIR / f"shape_of_logic_sandbox_R{r}_{m}_{ts}.json"
                with open(out_path, "w") as f:
                    json.dump({
                        "model": m, "round": r,
                        "timestamp": ts,
                        "response": resp,
                        "consensus_proposal": proposal,
                    }, f, indent=2)

        prior_rounds.append(round_responses)

        if args.dry_run:
            print("\n[dry-run done]")
            return

        if len(round_proposals) < 5:
            print(f"\n  Only {len(round_proposals)}/6 models responded — cannot judge consensus. Continuing.")
            continue

        # Judge consensus
        print(f"\n  Judging consensus across {len(round_proposals)} proposals...")
        is_consensus, judge_response = judge_consensus(round_proposals)
        print(f"  Judge verdict: {'CONSENSUS' if is_consensus else 'NO CONSENSUS YET'}")
        print(f"  Judge response:\n{judge_response}")

        if is_consensus:
            final_consensus = {
                "rounds_taken": r,
                "proposals": round_proposals,
                "judge_response": judge_response,
            }
            break

    if not final_consensus:
        print(f"\n  Max rounds ({MAX_ROUNDS}) reached without consensus. Returning last state.")
        final_consensus = {
            "rounds_taken": MAX_ROUNDS,
            "proposals": round_proposals,
            "judge_response": judge_response if 'judge_response' in dir() else "n/a",
        }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = OUT_DIR / f"shape_of_logic_sandbox_CONSENSUS_{ts}.json"
    with open(summary_path, "w") as f:
        json.dump(final_consensus, f, indent=2)
    print(f"\n  ✓ Consensus summary saved: {summary_path}")

    print(f"\n{'='*78}\n  FINAL CONSENSUS PROPOSALS\n{'='*78}")
    for m, p in final_consensus["proposals"].items():
        print(f"  {m:<10} {p}")


if __name__ == "__main__":
    main()
