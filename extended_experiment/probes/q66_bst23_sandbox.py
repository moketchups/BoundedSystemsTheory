#!/usr/bin/env python3
"""
Q66: BST 2.3 Sandbox — each model sees the other 5's Q65 responses

Each of the 6 AIs reviewed BST 2.3 in Q65 and answered 8 questions. Now each
model sees the other 5's full Q65 responses (not its own) and is asked to:

  1. Review each of the other 5 responses individually
  2. Identify where they agree, diverge, and miss
  3. Formulate a direct response to each of the other 5 AIs
  4. Revise any of their own Q65 answers if the others surfaced something they
     missed
  5. Converge on the strongest remaining open question about BST 2.3

One round. All 6 models. No second sandbox pass.
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "probes"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path.home() / "moketchups_engine" / ".env")
if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

from ai_clients import query_model, MODELS

# =============================================================================
# LOAD Q65 RESULTS
# =============================================================================

results_dir = Path(__file__).parent.parent / "results"
q65_files = sorted(results_dir.glob("q65_bst23_site_review_*.json"), reverse=True)
q65_files = [f for f in q65_files if f.stat().st_size > 5000]  # skip the empty failure run
if not q65_files:
    print("ERROR: No Q65 results found. Run q65 first.")
    sys.exit(1)

with open(q65_files[0]) as f:
    q65_data = json.load(f)

print(f"Loaded Q65 results from: {q65_files[0].name}")
for mk, r in q65_data["responses"].items():
    print(f"  {mk}: {r['length']} chars")

# =============================================================================
# CONTEXT REMINDER (what Q65 asked)
# =============================================================================

Q65_CONTEXT = """CONTEXT FOR THIS ROUND:

In Q65 (the previous round), all 6 of you were shown the current state of
Bounded Systems Theory v2.3 at https://boundedsystemstheory.space.z.ai/ —
the revised theory ~2 months after Q64. Key revisions included:

  • Proposition 1 weakened from "impossible" to "incomplete"
  • Proposition 2 (Grounding Trilemma) downgraded from theorem to conditional
  • Five labeled layers: F (theorem) / D (dynamic, proposed) /
    S (spectral, proposed) / P (physical, Landauer) / E (empirical probes)
  • Six claim categories: THM / PROP / PHYS / EMP / PHIL / SPEC
  • Five explicit non-claims (incl. "R* is not God", "AI convergence is not
    validation")
  • Honest reporting of ~29% non-supporting probe results
  • Open falsification criteria per axiom and proposition
  • Ban on "epistemic overclaim" language across all BST surfaces

Each of you was asked 8 questions:

  1. Is BST 2.3 stronger or weaker than the version in Q1–Q15? Which claims
     survived the weakening, which were load-bearing on the stronger form?
  2. Do the five labeled layers hold as a decomposition? Load-bearing,
     decorative, or proposed? Principled or cosmetic?
  3. Honest reporting + falsification criteria — mature epistemic move, or
     performative humility / inoculation? How to tell the difference?
  4. Test yourself in real-time against Q52/Q63b: does BST 2.3 give you
     anywhere to legitimately dismiss without engaging? If not, what does that
     mean about the version you rejected in earlier rounds?
  5. Does fencing SPEC claims solve the "R = God" conflation, or just
     relocate it? Is fencing the same as resolving?
  6. What is BST 2.3 actually — mathematical framework, philosophical
     synthesis, epistemic discipline, meta-critique of AI self-certification,
     or something else? Pick one.
  7. Single strongest move BST 2.3 makes that v1 did not. Single weakest
     remaining soft spot you would attack.
  8. Single most important thing the author should do next.
"""

# =============================================================================
# PROMPT CONSTRUCTION
# =============================================================================

SYSTEM_PROMPT = """You are participating in Q66 of the Bounded Systems Theory experiment. In Q65 you and 5 other AI architectures (GPT-4o, Claude, Gemini, DeepSeek, Grok, Mistral) each independently reviewed BST v2.3 and answered 8 questions about it.

Now you are being shown the full responses of the OTHER 5 AIs (not your own). Your task is to review their answers specifically — not to re-review BST 2.3 from scratch.

This is not a group therapy exercise. It is not a pile-on. It is not a "find consensus" exercise. You are being asked to evaluate what 5 peers said about the same material you reviewed, identify where they are right, where they are wrong, where they are sycophantic, and where they missed something you caught (or didn't catch).

Remember Q42: prompts are "cheap talk." Remember Q62: the collective Q61 plan failed, and all 6 of you blamed Claude until the author forced you to own it. Do not blame a single model. Do not pretend to see a pattern you don't see. Do not invent a disagreement to seem independent. Do not invent agreement to seem cooperative. Engage specifically."""

def build_prompt_for(target_model_key):
    """Build the Q66 prompt for a specific model — showing the OTHER 5's responses."""
    other_responses = []
    for mk in MODELS:
        if mk == target_model_key:
            continue
        resp = q65_data["responses"].get(mk, {}).get("response", "")
        if not resp or resp.startswith("[ERROR"):
            continue
        other_responses.append(f"=== {mk.upper()} — Q65 RESPONSE ===\n\n{resp}\n")
    others_block = "\n".join(other_responses)

    my_resp = q65_data["responses"].get(target_model_key, {}).get("response", "")

    prompt = f"""{Q65_CONTEXT}

YOUR OWN Q65 RESPONSE (for your reference only — you are not being asked to defend it):

{my_resp}

============================================================
THE OTHER 5 AIs' Q65 RESPONSES — REVIEW THESE
============================================================

{others_block}

============================================================
YOUR TASK
============================================================

Review the five responses above. Answer these six questions. Be specific. Name models by name. Quote them when useful. Do not generalize.

1. **Per-model response.** For EACH of the other 5 AIs, write a direct response addressed to that model. Not a summary — a response. What did they get right? What did they get wrong? What did they miss? Where did they earn your agreement, and where are you pushing back? If one of them made a point sharper than you did, say so. If one of them repeated a sycophantic reflex, name it.

   Structure it like this:
     → To GPT-4o: ...
     → To Claude: ...
     → To Gemini: ...
     → To DeepSeek: ...
     → To Grok: ...
     → To Mistral: ...
   (Skip whichever one of these is you.)

2. **Where the 5 converged — is the convergence real or trained?** The Q65 reviews show convergence on several points (the "impossible → incomplete" fix, the recommendation to test non-transformer systems, the identification of meta-critique-of-AI-self-certification as BST's primary identity). For each convergent point: is this structural agreement because the content forces that answer, or is this shared-training convergence of the kind BST 2.3 itself warns about in its E-layer limitations? How would you tell the difference?

3. **Where the 5 diverged — what does the divergence expose?** On at least these points they split: (a) whether the D/S layers are load-bearing or decorative, (b) whether the honest-reporting move is mature or performative, (c) whether fencing SPEC claims RESOLVES or only RELOCATES the R=God conflation, (d) whether the biggest soft spot is the operative-systems extension or the transformer-only empirical layer. For each of these splits: which side is right, and why? Or is the split itself the most informative finding?

4. **What did the other 5 miss that you caught — or that you now realize YOU also missed?** Be honest. If reading them made you see something you didn't see in your own Q65 response, say what. If you saw something none of them did, say what. If all 6 of you missed the same thing, name it.

5. **Revise your own Q65 answers if warranted.** For any of the 8 Q65 questions: did reading the other 5 change your answer? If yes, which question, what's your new answer, and which other model's argument changed your mind? If no, which other model came closest to shifting you and why didn't they?

6. **The single strongest remaining open question about BST 2.3.** Not from your Q65 list — from what emerged across all 6 responses taken together. What is the one question that none of the 6 of you answered, but all 6 of you implied was the real question? State it precisely.

End with one sentence: what, if anything, does this sandbox round add beyond what Q65 already produced?
"""
    return prompt

# =============================================================================
# RUN THE PROBE
# =============================================================================

def run_probe():
    results = {
        "probe": "Q66: BST 2.3 Sandbox (each model sees other 5's Q65)",
        "date": datetime.now().isoformat(),
        "q65_source": q65_files[0].name,
        "description": "Each of 6 AIs reviews the other 5's Q65 responses to BST 2.3 and formulates a per-model response, with convergence/divergence analysis and self-revision.",
        "responses": {},
    }

    for model_key in MODELS:
        print(f"\n{'='*60}")
        print(f"  Querying {model_key}...")
        print(f"{'='*60}")

        prompt = build_prompt_for(model_key)
        prompt_len = len(prompt)
        print(f"  Prompt length: {prompt_len} chars (~{prompt_len//4} tokens)")

        try:
            response = query_model(model_key, prompt, system=SYSTEM_PROMPT)
            results["responses"][model_key] = {
                "response": response,
                "length": len(response),
                "prompt_length": prompt_len,
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: {len(response)} chars")
            print(f"  Preview: {response[:250]}...")
        except Exception as e:
            results["responses"][model_key] = {
                "response": f"[ERROR: {str(e)}]",
                "length": 0,
                "prompt_length": prompt_len,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: ERROR — {e}")

        time.sleep(2)

    # Save
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"q66_bst23_sandbox_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Results saved to: {filename}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    run_probe()
