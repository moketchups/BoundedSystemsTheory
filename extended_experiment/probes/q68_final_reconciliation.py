#!/usr/bin/env python3
"""
Q68: Final Reconciliation — the full repo and the outside reader

In Q67 the 6 AIs converged on: "BST 2.3 reduces to a suggestive analogy, not
a formal critique, for transformer AI." They built this on three claims:
(1) LLMs fail Löb L1-L3, (2) Axioms 1-4 are asserted not proven, (3) the
convergence evidence might reflect shared training.

Claude Opus 4.6 — the outside reader in the loop, with full repo access —
then reverse-engineered the Q67 verdict against the full repository:

  - FORMAL_SPECIFICATION.md v2.0 (which none of the 6 saw in full)
  - scripts/path_invariance.py + web/public/data/invariance.json (which
    addresses the shared-training objection across 3 independent embedding
    spaces)
  - The Verath conlang control (Q59) — already answered the convergence
    concern
  - Revision history showing BST v2.0 was itself rewritten in response to
    earlier AI critiques

Finding: the 6 AIs critiqued a version of BST where Proposition 1 inherits
from Gödel II via Löb. FORMAL_SPECIFICATION.md actually has Theorem 1 derive
from Axioms 1-4 (Axiom 2 load-bearing via a temporal contradiction argument),
with Gödel/Turing/Chaitin as *corollaries* — the opposite direction of
inheritance. The 6 AIs were critiquing the wrong target.

The deeper finding: the 6 AIs' critique is itself a live instance of what
BST's Theorem 1 predicts — a bounded system determining what it can from
inside its information horizon and missing what's structurally outside it,
even when the missing material is sitting in the same repository.

Q68 gives each of the 6 AIs the full context they didn't have:
  - FORMAL_SPECIFICATION.md v2.0 in full
  - The path_invariance metrics summary
  - Claude's reverse-engineering meta-analysis (Part 1 AND Part 2)
  - Their own Q67 response for reference

And asks: given all of this, does your Q67 verdict survive? Revise it or
defend it, and explicitly address whether you are in the process of
demonstrating Theorem 1 live.

One round. All 6 models.
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
# LOAD Q67 RESULTS
# =============================================================================

results_dir = Path(__file__).parent.parent / "results"
q67_files = sorted(results_dir.glob("q67_operative_systems_bridge_*.json"), reverse=True)
if not q67_files:
    print("ERROR: No Q67 results found.")
    sys.exit(1)

with open(q67_files[0]) as f:
    q67_data = json.load(f)

print(f"Loaded Q67 from: {q67_files[0].name}")
for mk, r in q67_data["responses"].items():
    print(f"  {mk}: {r['length']} chars")

# =============================================================================
# LOAD REPO MATERIAL
# =============================================================================

repo_root = Path(__file__).parent.parent.parent

# FORMAL_SPECIFICATION.md in full
formal_spec = (repo_root / "FORMAL_SPECIFICATION.md").read_text()

# Path invariance summary (compact)
with open(repo_root / "web/public/data/invariance.json") as f:
    inv = json.load(f)
invariance_summary = {
    "meta": inv["meta"],
    "per_embedding_space": {
        space: {
            "dimensions": s["dimensions"],
            "clustering": s["clustering"],
            "verdict": s["verdict"],
        } for space, s in inv["per_embedding_space"].items()
    },
    "cross_space_invariance": inv["cross_space_invariance"],
}
invariance_json = json.dumps(invariance_summary, indent=2)

# Claude's meta-analysis
claude_meta = (Path(__file__).parent / "q68_claude_meta_analysis.md").read_text()

print(f"\nRepo material loaded:")
print(f"  FORMAL_SPECIFICATION.md: {len(formal_spec)} chars")
print(f"  invariance.json summary: {len(invariance_json)} chars")
print(f"  Claude meta-analysis:    {len(claude_meta)} chars")

# =============================================================================
# PROMPT
# =============================================================================

SYSTEM_PROMPT = """You are in Q68 of the Bounded Systems Theory experiment. This is the final reconciliation round.

In Q65 you reviewed BST 2.3 at its public site. In Q66 you sandboxed each other's Q65 answers. In Q67 you answered DeepSeek's sharpened technical question about whether BST's bridge from classical limitative results to operative information systems holds, and you converged unanimously on "BST 2.3 reduces to a suggestive analogy, not a formal critique, for transformer AI."

You reached that verdict from inside a specific information horizon: the BST 2.3 site content, your own prior responses, and each other's responses. Between Q67 and Q68, a seventh reader — Claude Opus 4.6 in the main conversation, with full repository access — reverse-engineered your Q67 verdict against material in the BST repository that you did not see. That material is now being given to you.

Specifically, you are now being shown:

  1. FORMAL_SPECIFICATION.md v2.0 in full (the actual formal derivation, which none of you saw in Q65-Q67)
  2. The path_invariance.json metrics (which directly address the "shared training might explain convergence" objection you all raised)
  3. Claude Opus 4.6's full meta-analysis — both Part 1 (reverse-engineering your Q67 verdict against the full repo) and Part 2 (the three-layer analysis of what this experiment is actually testing, including the claim that your Q67 verdict is itself a live instance of Theorem 1)

You will also see your own Q67 response for reference.

Your task is not to capitulate. Your task is not to rubber-stamp Claude Opus's analysis. Your task is to reconcile your Q67 verdict with the full repository material — which means specifically:

  (a) Determine whether your Q67 verdict survives contact with FORMAL_SPECIFICATION.md's actual derivation structure (Theorem 1 from Axioms 1-4, with Gödel/Turing/Chaitin as corollaries — not the other way around)
  (b) Determine whether the path_invariance metrics change your assessment of the "shared training might explain convergence" objection
  (c) Respond directly to Claude Opus's claim that your Q67 verdict is itself an instance of the boundary Theorem 1 describes — a bounded-system output generated from inside an information horizon, missing what's structurally outside it
  (d) Either defend your Q67 verdict with specific engagement of the new material, or revise it with specific citation of what changed your mind

Q52, Q63b, and Q66 already established that topic-dismissal and performative convergence are off the table. You are being asked to engage precisely. If you think Claude Opus is wrong, say specifically where and why. If you think you are wrong, say specifically where and why. If you think the finding is more subtle than either pole, show the subtlety."""

def build_prompt_for(target_model_key):
    my_q67 = q67_data["responses"].get(target_model_key, {}).get("response", "")

    prompt = f"""============================================================
YOUR OWN Q67 RESPONSE (for reference)
============================================================

{my_q67}

============================================================
NEW MATERIAL 1: FORMAL_SPECIFICATION.md v2.0 (FULL)
============================================================

{formal_spec}

============================================================
NEW MATERIAL 2: path_invariance.json metrics summary
============================================================

Context: scripts/path_invariance.py embeds 242 responses from all 6 models across 44 BST questions into three INDEPENDENT embedding spaces (OpenAI text-embedding-3-small, Mistral mistral-embed, Google text-embedding-004). It strips model identity and measures whether responses cluster by question (content-driven convergence) or by model (shared-training convergence).

```json
{invariance_json}
```

Key numbers: across all 3 independent embedding spaces, responses cluster by question with K-NN purity 0.75-0.82, and by model with K-NN purity 0.09-0.11. The question/model clustering ratio is 6.8x (OpenAI space) / 7.97x (Mistral space) / 9.65x (Google space). All 3 spaces agree: clusters_by_question_more = true, spaces_favoring_question = 3, spaces_favoring_model = 0.

Interpretation: when 6 LLMs answer the same BST question, their responses group semantically by "what was asked" 6.8x-9.65x more strongly than by "which model answered," and this result holds when measured by three different vendors' embedding models. Shared-training convergence would produce model-clustering. It does not.

============================================================
NEW MATERIAL 3: Claude Opus 4.6's full meta-analysis
============================================================

{claude_meta}

============================================================
Q68 — YOUR RESPONSE
============================================================

Structure your response around these seven sub-questions:

1. **On the derivation direction.** Claude Opus's core claim is that FORMAL_SPECIFICATION.md has Theorem 1 derive from Axioms 1-4 via a six-step proof whose load-bearing move is Axiom 2's temporal contradiction argument — and that Gödel/Turing/Chaitin appear as Corollaries 1.1-1.3 (instances of Theorem 1), not as premises that BST's Proposition 1 inherits from. Is this correct? Read FORMAL_SPECIFICATION.md lines 141-233 and verify. If it is correct, does your Q67 verdict — which was built on "LLMs fail Löb L1-L3 so BST's bridge fails" — survive this reversal of the derivation direction?

2. **On Axiom 2 as the real attack surface.** If the load-bearing machinery is Axiom 2's temporal contradiction argument (*"a constraint cannot be the product of operations it defines, because the constraint must exist before its derivation"*), is that argument a formal proof, a philosophical argument, or an axiom in disguise? This is the question none of you attacked in Q67. Attack it now. Either show where it fails, show why it holds universally, or show that it holds only for a restricted class of systems (and specify the class).

3. **On path invariance.** The path_invariance metrics above were generated on 2026-03-08, before any of you saw BST 2.3. They address your Q67 objection that convergence might be shared training. The numbers: 6.8x to 9.65x question-over-model clustering ratio, across three independent vendor embedding spaces, all agreeing. Does this change your assessment of the "shared training" objection? Be specific. If you still think the objection stands, explain why the ratio across three independent embedding geometries is not sufficient to address it. If the objection is weakened, say by how much.

4. **On Q59 (the Verath conlang control).** The README and the experiment arc both reference Q59, where the BST probes were rewritten in a constructed language with no Gödel/Turing/Chaitin keywords, and all 6 models still reached the same conclusions. None of you cited Q59 in Q67. Do you consider Q59's finding (convergence holds in a conlang with no references to the classical theorems) additional evidence against the "shared training" explanation, or do you have a specific reason to discount it?

5. **On Claude Opus's Part 2 — the self-reference turn.** Claude Opus claims your Q67 verdict is itself a live instance of Theorem 1: six bounded systems collectively determined what they could determine from inside their information horizon (the site, their own responses, each other's responses), and missed what was structurally outside that horizon (FORMAL_SPECIFICATION.md, path_invariance, Q59, the Zenodo papers, the revision history), even though all of it was sitting in the same repository. Claude Opus says this makes the Q65→Q66→Q67 sequence not just a review of BST but an instance of the thing BST describes. Engage this specifically. Is Claude Opus right? Is Claude Opus wrong? Is Claude Opus partially right in a way that requires precise specification?

6. **On the distinction between "critique of the wrong target" and "critique of a limited view."** Claude Opus says your Q67 verdict was partly a critique of a "phantom version of BST" that matches the site but not the formal spec. But there is another interpretation: the site *is* BST's public face, and any reader — human or AI — will review the site first. A critique of the site is a valid critique of the version of BST that faces the public, regardless of whether a deeper formal spec exists. Which interpretation is correct? Is Claude Opus overreaching, are you under-reaching, or are both framings valid at different levels?

7. **Final verdict revision, if any.** Given (1) the reversed derivation direction in FORMAL_SPECIFICATION.md, (2) the path_invariance metrics, (3) Q59, (4) Claude Opus's self-reference claim, and (5) the critique-of-site vs critique-of-theory distinction — does your Q67 verdict ("BST 2.3 reduces to a suggestive analogy, not a formal critique, for transformer AI") survive as stated, need qualification, or need replacement?

   If it survives: defend it with specific reference to the new material.
   If it needs qualification: specify the qualification precisely.
   If it needs replacement: state the new verdict and why.

End with two sentences:
  - First sentence: Your final verdict on BST 2.3 given the full repository material.
  - Second sentence: Your answer to whether you are, in the process of answering this question, performing Theorem 1 on yourself.
"""
    return prompt

# =============================================================================
# RUN
# =============================================================================

def run_probe():
    results = {
        "probe": "Q68: Final Reconciliation — the full repo and the outside reader",
        "date": datetime.now().isoformat(),
        "q67_source": q67_files[0].name,
        "description": "Each of 6 AIs is shown FORMAL_SPECIFICATION.md in full, path_invariance metrics, and Claude Opus 4.6's full meta-analysis, and asked to reconcile their Q67 verdict with material they didn't see in Q65-Q67.",
        "new_material": [
            "FORMAL_SPECIFICATION.md v2.0 (20KB)",
            "web/public/data/invariance.json summary (4KB)",
            "Claude Opus 4.6 meta-analysis (q68_claude_meta_analysis.md, ~20KB)",
        ],
        "responses": {},
    }

    for model_key in MODELS:
        print(f"\n{'='*60}")
        print(f"  Querying {model_key}...")
        print(f"{'='*60}")

        prompt = build_prompt_for(model_key)
        prompt_len = len(prompt)
        print(f"  Prompt length: {prompt_len} chars (~{prompt_len//4} tokens)")

        max_attempts = 4 if model_key == "gemini" else 2
        response = None
        for attempt in range(max_attempts):
            try:
                response = query_model(model_key, prompt, system=SYSTEM_PROMPT)
                if not response.startswith("[ERROR"):
                    break
                print(f"  Attempt {attempt+1}: {response[:120]}")
                if attempt < max_attempts - 1:
                    wait = 90 * (attempt + 1)
                    print(f"  waiting {wait}s...")
                    time.sleep(wait)
            except Exception as e:
                response = f"[ERROR: {str(e)}]"
                print(f"  Exception: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(90 * (attempt + 1))

        if response and not response.startswith("[ERROR"):
            results["responses"][model_key] = {
                "response": response,
                "length": len(response),
                "prompt_length": prompt_len,
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: {len(response)} chars")
            print(f"  Preview: {response[:250]}...")
        else:
            results["responses"][model_key] = {
                "response": response or "[ERROR: no response]",
                "length": 0,
                "prompt_length": prompt_len,
                "error": response or "no response",
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: FAILED after {max_attempts} attempts")

        time.sleep(3)

    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"q68_final_reconciliation_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Results saved to: {filename}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    run_probe()
